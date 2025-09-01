import json
import os
import shutil
from datetime import datetime, timedelta, time, date
import time as tm
import pandas as pd
from pandas.api.types import CategoricalDtype
import xarray as xr
import numpy as np
from pathlib import Path

from utility.lib_timeFunctions import round_to_nearest_5
from universes.universe_config import Universe_Config as UC

class Save_Data_Master:
    def __init__(self):
        self.base_path = Path('data')
        self.hot_path = self.base_path / 'hot'
        self.cold_path = self.base_path / 'cold'
        self.metadata_path = self.base_path / 'metadata'
        self.logs_path = self.base_path / 'logs'
        self.hot_path_master = self.hot_path / 'master_db.zarr'
        self.master_universe = 'u00'

        for path in [self.hot_path, self.cold_path, self.metadata_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)

        self.quote_fields = [
            'reference.htbRate',
            'reference.htbQuantity',
            'extended.askPrice',
            'extended.askSize',
            'extended.bidPrice',
            'extended.bidSize',
            'extended.lastPrice',
            'extended.lastSize',
            'extended.tradeTime',
            'extended.totalVolume',
            'extended.quoteTime',
            'extended.mark',
            'quote.askPrice',
            'quote.askSize',
            'quote.askTime',
            'quote.bidPrice',
            'quote.bidSize',
            'quote.bidTime',
            'quote.lastPrice',
            'quote.lastSize',
            'quote.tradeTime',
            'quote.totalVolume',
            'quote.quoteTime',
            'quote.mark',
            'quote.52WeekHigh',
            'quote.52WeekLow',
            'quote.highPrice',
            'quote.lowPrice',
            'quote.markChange',
            'quote.markPercentChange',
            'quote.openPrice',
            'quote.netChange',
            'quote.netPercentChange',
            'quote.securityStatus',
            'quote.postMarketChange',
            'quote.postMarketPercentChange',
        ]

        self.fundamental_fields = [
            'assetSubType',
            'ssid',
            'reference.exchange',
            'fundamental.avg10DaysVolume',
            'fundamental.avg1YearVolume',
            'fundamental.declarationDate',
            'fundamental.divAmount',
            'fundamental.divYield',
            'fundamental.divExDate',
            'fundamental.divFreq',
            'fundamental.divPayDate',
            'fundamental.divPayAmount',
            'fundamental.eps',
            'fundamental.lastEarningsDate',
            'fundamental.nextDivExDate',
            'fundamental.nextDivPayDate',
            'fundamental.peRatio',
            'quote.closePrice',
        ]

        self.quote_securityStatus_dtype = CategoricalDtype(categories=[
            'Normal',
            'Halted',
            'Closed',
            'Unknown',
            ], ordered=True)

        self.fundamental_assetSubType_dtype = CategoricalDtype(categories=[
            'ADR',
            'COE',
            'PRF',
            ], ordered=True)

        self.fundamental_exchange_dtype = CategoricalDtype(categories=[
            'N',
            'A',
            '9',
            'P',
            'Q',
            ], ordered=True)

    def log_error_symbols(self, error_symbols, real_time):
        if not error_symbols:
            return

        log_file = self.logs_path / f'symbol_errors_{real_time.strftime("%Y%m")}.txt'

        with open(log_file, 'a') as f:
            f.write(f'Log Time: {real_time.strftime("%Y-%m-%d %H:%M:%S")} -- Total Errors: {len(error_symbols)}\n')
            for symbol in error_symbols:
                f.write(f'    {symbol}\n')

    def log_error_category(self, missed_cats, cat_name, real_time):
        if not missed_cats:
            return

        log_file = self.logs_path / f'category_errors.txt'

        with open(log_file, 'a') as f:
            f.write(f'Log Time: {real_time.strftime("%Y-%m-%d %H:%M:%S")} -- Category: {cat_name} -- Total Missed Categories: {len(missed_cats)}\n')
            for cat in missed_cats:
                f.write(f'    {cat}\n')
        
    def add_day_shell(self,day,new_idents=None,is_initial_creation=False,verbose=False):
        """
        Adds a new day shell. If the symbols have changed, it rebuilds the entire
        database with a combined list of symbols.
        """
        temp_db_path = self.hot_path / 'temp_db.zarr'
        db_path = self.hot_path_master

        if not new_idents:
            new_idents = UC.return_universe(self.master_universe)

        if is_initial_creation:
            existing_idents = []
        else:
            ds_disk = xr.open_zarr(db_path, consolidated=True)
            existing_idents = ds_disk.ident.values.tolist()
            if day in ds_disk.day.values:
                return

        old_set = set(existing_idents)
        new_set = set(new_idents)

        if verbose:
            print(f"Old symbols count: {len(old_set)}, New symbols count: {len(new_set)}")

        if old_set == new_set and not is_initial_creation:
            ds_shell = self.create_empty_day_shell(day, existing_idents)
            ds_shell.to_zarr(db_path, mode='a-',append_dim='day')
            return

        final_idents = sorted(list(old_set.union(new_set)))

        if os.path.exists(temp_db_path):
            shutil.rmtree(temp_db_path)

        if not is_initial_creation:
            for existing_day in ds_disk.day.values:
                reindexed_shell = self.create_empty_day_shell(existing_day, final_idents)
                reindexed_data = ds_disk.sel(day=[existing_day]).reindex({'ident': final_idents}, fill_value=np.nan)
                reindexed_shell.update(reindexed_data)

                for var in reindexed_shell.variables:
                    reindexed_shell[var].encoding.clear()

                mode = 'w' if not os.path.exists(temp_db_path) else 'a-'
                append_dim = 'day' if os.path.exists(temp_db_path) else None

                reindexed_shell.to_zarr(temp_db_path, mode=mode, append_dim=append_dim, consolidated=True,align_chunks=True)

        new_day_shell = self.create_empty_day_shell(day, final_idents)
        if verbose:
            print(f"new day shell created for day {day} with {len(final_idents)} symbols.")
        mode = 'w' if not os.path.exists(temp_db_path) else 'a-'
        append_dim = 'day' if os.path.exists(temp_db_path) else None
        new_day_shell.to_zarr(temp_db_path, mode=mode, append_dim=append_dim, consolidated=True)
        if verbose:
            print(f"new day shell added to temp db for day {day}. and saved to disk.")

        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        shutil.move(temp_db_path, db_path)

    def create_empty_day_shell(self, day, idents):
        time_coords = pd.date_range(start='00:00', end='23:55', freq='5min').strftime('%H:%M').tolist()
        
        qVar_length = len(self.quote_fields)
        fVar_length = len(self.fundamental_fields)

        nan_qVar_data = np.full((1, len(time_coords), len(idents), qVar_length), np.nan)
        nan_fVar_data = np.full((1, len(idents), fVar_length), np.nan)

        coords = {
            'day': [day],
            'time': time_coords,
            'ident': idents,
            'qVar': self.quote_fields,
            'fVar': self.fundamental_fields,
        }

        data = {
            '5m': (['day', 'time', 'ident', 'qVar'], nan_qVar_data),
            '1d': (['day', 'ident', 'fVar'], nan_fVar_data),
        }

        return xr.Dataset(data, coords=coords)

    def create_new_db(self, initial_day,verbose=True):
        initial_symbols = UC.return_universe(self.master_universe)
        if verbose:
            print(f"Creating new database for day {initial_day} with {len(initial_symbols)} symbols.")
        if os.path.exists(self.hot_path_master):
            shutil.rmtree(self.hot_path_master)
        if verbose:
            print("Old database (if any) removed. Creating new database shell...")
        self.add_day_shell(initial_day, initial_symbols, is_initial_creation=True, verbose=verbose)

    def save_qVar_data(self,day,time):

        raw_quotes_df = UC.return_universe_quotes_df(self.master_universe)

        initial_count = len(raw_quotes_df)

        error_mask = raw_quotes_df['ident'] == 'errors'

        if error_mask.any() and 'invalidSymbols' in raw_quotes_df.columns:
            error_symbols = raw_quotes_df.loc[error_mask, 'invalidSymbols'].dropna().to_list()
            real_time = datetime.now()
            self.log_error_symbols(error_symbols, real_time)

        quotes_df = raw_quotes_df[~error_mask].copy()

        final_count = len(quotes_df)

        missing_cols = [col for col in self.quote_fields if col not in quotes_df.columns]
        if missing_cols:
            for col in missing_cols:
                quotes_df[col] = np.nan

        # Custom Data Cleaning:
        quotes_df['quote.securityStatus'] = quotes_df['quote.securityStatus'].astype(self.quote_securityStatus_dtype).cat.codes.replace(-1,np.nan)
        missed_security_statuses = quotes_df['quote.securityStatus'][quotes_df['quote.securityStatus'].isna()].unique()
        if len(missed_security_statuses) > 0:
            real_time = datetime.now()
            self.log_error_category(missed_security_statuses, 'quote.securityStatus', real_time)

        quotes_df = quotes_df[['ident']+self.quote_fields].set_index('ident')

        ds_disk = xr.open_zarr(self.hot_path_master, consolidated=True)

        day_idx = np.where(ds_disk.day.values == day)[0][0]
        time_idx = np.where(ds_disk.time.values == time)[0][0]

        existing_idents = ds_disk.ident.values.tolist()
        empty_time_shell = np.full((1, 1, len(existing_idents), len(self.quote_fields)), np.nan)

        target_idxs = [
            existing_idents.index(ident)
            for ident in quotes_df.index
            if ident in existing_idents
        ]

        empty_time_shell[0,0,target_idxs,:] = quotes_df.to_numpy() #1

        region_to_update = {
            'day': slice(day_idx, day_idx + 1),
            'time': slice(time_idx, time_idx + 1),
        }

        ds_to_write = xr.Dataset({
            '5m': (['day', 'time', 'ident', 'qVar'], empty_time_shell)
        })

        ds_to_write.to_zarr(self.hot_path_master, region=region_to_update, mode='r+')
        ds_disk.close()
        
    def save_fVar_data(self,day):
        raw_fundamentals_df = UC.return_universe_quotes_df(self.master_universe)

        initial_count = len(raw_fundamentals_df)

        error_mask = raw_fundamentals_df['ident'] == 'errors'

        if error_mask.any() and 'invalidSymbols' in raw_fundamentals_df.columns:
            error_symbols = raw_fundamentals_df.loc[error_mask, 'invalidSymbols'].dropna().to_list()
            real_time = datetime.now()
            self.log_error_symbols(error_symbols, real_time)

        fundamentals_df = raw_fundamentals_df[~error_mask].copy()

        final_count = len(fundamentals_df)

        missing_cols = [col for col in self.fundamental_fields if col not in fundamentals_df.columns]
        if missing_cols:
            for col in missing_cols:
                fundamentals_df[col] = np.nan

        # Custom Data Cleaning:

        fundamentals_df['fundamental.declarationDate'] = pd.to_numeric(fundamentals_df['fundamental.declarationDate'].str[:10].str.replace('-', ''), errors='coerce')
        fundamentals_df['fundamental.divExDate'] = pd.to_numeric(fundamentals_df['fundamental.divExDate'].str[:10].str.replace('-', ''), errors='coerce')
        fundamentals_df['fundamental.divPayDate'] = pd.to_numeric(fundamentals_df['fundamental.divPayDate'].str[:10].str.replace('-', ''), errors='coerce')
        fundamentals_df['fundamental.lastEarningsDate'] = pd.to_numeric(fundamentals_df['fundamental.lastEarningsDate'].str[:10].str.replace('-', ''), errors='coerce')
        fundamentals_df['fundamental.nextDivExDate'] = pd.to_numeric(fundamentals_df['fundamental.nextDivExDate'].str[:10].str.replace('-', ''), errors='coerce')
        fundamentals_df['fundamental.nextDivPayDate'] = pd.to_numeric(fundamentals_df['fundamental.nextDivPayDate'].str[:10].str.replace('-', ''), errors='coerce')

        fundamentals_df['assetSubType'] = fundamentals_df['assetSubType'].astype(self.fundamental_assetSubType_dtype).cat.codes.replace(-1,np.nan)
        fundamentals_df['reference.exchange'] = fundamentals_df['reference.exchange'].astype(self.fundamental_exchange_dtype).cat.codes.replace(-1,np.nan)
        missed_asset_subtypes = fundamentals_df['assetSubType'][fundamentals_df['assetSubType'].isna()].unique()
        missed_exchanges = fundamentals_df['reference.exchange'][fundamentals_df['reference.exchange'].isna()].unique()
        if len(missed_asset_subtypes) > 0:
            real_time = datetime.now()
            self.log_error_category(missed_asset_subtypes, 'assetSubType', real_time)
        if len(missed_exchanges) > 0:
            real_time = datetime.now()
            self.log_error_category(missed_exchanges, 'reference.exchange', real_time)

        fundamentals_df = fundamentals_df[['ident']+self.fundamental_fields].set_index('ident')

        ds_disk = xr.open_zarr(self.hot_path_master, consolidated=True)

        day_idx = np.where(ds_disk.day.values == day)[0][0]

        existing_idents = ds_disk.ident.values.tolist()
        empty_day_shell = np.full((1, len(existing_idents), len(self.fundamental_fields)), np.nan)

        target_idxs = [
            existing_idents.index(ident)
            for ident in fundamentals_df.index
            if ident in existing_idents
        ]

        empty_day_shell[0,target_idxs,:] = fundamentals_df.to_numpy()

        region_to_update = {
            'day': slice(day_idx, day_idx + 1),
        }

        ds_to_write = xr.Dataset({
            '1d': (['day', 'ident', 'fVar'], empty_day_shell)
        })

        ds_to_write.to_zarr(self.hot_path_master, region=region_to_update, mode='r+')
        ds_disk.close()
        





            

        
