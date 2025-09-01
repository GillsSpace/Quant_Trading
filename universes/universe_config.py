from contextlib import nullcontext
from datetime import datetime
from types import NoneType
from tradingview_screener import Column, Query
import pandas as pd
import os
import json
import schwabdev as sd
import time as tm

from utility.lib_timeFunctions import round_to_nearest_5

class Universe_Config:
    """Base class for universe configurations."""

    universe_dict = {
        "u01": {
                "in": [
                Column('price_52_week_high') < 15,
                Column('price_52_week_low') > 1,
                Column('volume|1W') > 20_000,
                Column('exchange').isin(['AMEX', 'NASDAQ', 'NYSE']),
                ],
                "out": [
                Column('price_52_week_high') > 25,
                Column('price_52_week_low') > 0.25,
                Column('volume|1W') > 5_000,
                Column('exchange').isin(['AMEX', 'NASDAQ', 'NYSE']),
                ]        
            },
        "u00": {
            "in": [
                Column('type') == 'stock',
                Column('exchange').isin(['AMEX', 'NASDAQ', 'NYSE']),
            ],
            "out": [
                Column('type') == 'stock',
                Column('exchange').isin(['AMEX', 'NASDAQ', 'NYSE']),
            ]
        },
    }

    @staticmethod
    def create_client():
        """Create a Schwab client with API keys."""
        with open('keys.json', 'r') as f:
            keys = json.load(f)

        return sd.Client(keys['schwab']['app_key'], keys['schwab']['app_secret'])

    @staticmethod
    def get_universe_test_df(universe):
        """Generates and returns a DataFrame for the specified universe."""
        universe_columns = Universe_Config.universe_dict[universe]['in']
        query = (
            Query()
            .select("name", "sector", "exchange", "industry",'close', 'volume|60', 'price_52_week_high', 'price_52_week_low','market_cap_basic','Value.Traded|60')
            .where(*universe_columns)
            .limit(10_000)
        )
        result =  query.get_scanner_data()
        return result

    @staticmethod
    def return_universe(universe) -> list: 
        "Returns a list of stock tickers for the specified universe."

        universe_df = pd.read_csv(f'universes/{universe}.csv',keep_default_na=False)
        if universe_df.empty:
            return []
        return universe_df['name'].tolist()

    @staticmethod
    def return_universe_quotes_df(universe):
        """Returns a DataFrame of stock quotes for the specified universe."""
        tickers = Universe_Config.return_universe(universe)
    
        # Early return for empty tickers
        if not tickers:
            return None
    
        client = Universe_Config.create_client()
        list_of_quotes = []
        batch_size = 500
    
        # Process tickers in batches
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
        
            try:
                quotes = client.quotes(batch)
                quotes_dict = quotes.json()
            
                # Extend list with processed batch
                list_of_quotes.extend([
                    {"ident": key, **value} 
                    for key, value in quotes_dict.items()
                ])
            
                # Sleep only between batches (not after the last one)
                if i + batch_size < len(tickers):
                    tm.sleep(0.2)
                
            except Exception as e:
                print(f"Error processing batch {i//batch_size + 1}: {e}")
                continue
    
        # Return empty DataFrame if no quotes were retrieved
        if not list_of_quotes:
            return pd.DataFrame()
    
        return pd.json_normalize(list_of_quotes)

    @staticmethod
    def gen_quotes_csv(universe):
        """Generates a CSV file with stock quotes for the specified universe."""
        quotes_df = Universe_Config.return_universe_quotes_df(universe)
        if quotes_df is not None:
            quotes_df.to_csv(f'live_data/{universe}_{round_to_nearest_5(datetime.now())}_quotes.csv', index=False)
        else:
            print(f"No data available for universe: {universe}")

    @staticmethod
    def gen_quotes_parquet(universe):
        """Generates a Parquet file with stock quotes for the specified universe."""
        quotes_df = Universe_Config.return_universe_quotes_df(universe)
        if quotes_df is not None:
            time_stamp = round_to_nearest_5(datetime.now()).strftime('%Y-%m-%d_%H_%M')
            quotes_df.to_parquet(f'live_data/{universe}_quotes_{time_stamp}.parquet', index=False)
        else:
            print(f"No data available for universe: {universe}")

    @staticmethod
    def gen_csv(universe):
        """Generates both a detialed CSV and a simplified CSV for the specified universe."""
        universe_columns = Universe_Config.universe_dict[universe]['in']
        query = (
            Query()
            .select("name", "sector", "exchange", "industry")
            .where(*universe_columns)
            .limit(10_000)
        )
        dt:pd.DataFrame = query.get_scanner_data()[1]
        dt.to_csv(f'universes/{universe}_long.csv', index=False)
        dt['name'].to_csv(f'universes/{universe}.csv', index=False)


    @staticmethod
    def regen_csv(universe):
        in_conditions = Universe_Config.universe_dict[universe]['in']
        out_conditions = Universe_Config.universe_dict[universe]['out']
        
        in_query = (
            Query()
            .select("name", "sector", "exchange", "industry")
            .where(*in_conditions)
        )
        in_result = in_query.get_scanner_data()
        new_stocks_df = pd.DataFrame(in_result[1])
        
        existing_df = pd.DataFrame()
        long_csv_path = f'universes/{universe}_long.csv'
        
        if os.path.exists(long_csv_path):
            existing_df = pd.read_csv(long_csv_path)
            
            out_query = (
                Query()
                .select("name", "sector", "exchange", "industry")
                .where(*out_conditions)
                .limit(10_000)
            )
            out_result = out_query.get_scanner_data()
            out_stocks_df = pd.DataFrame(out_result[1])
            
            if not out_stocks_df.empty and not existing_df.empty:
                existing_out_stocks = existing_df[existing_df['name'].isin(out_stocks_df['name'])]
            else:
                existing_out_stocks = pd.DataFrame()
        else:
            existing_out_stocks = pd.DataFrame()
        
        if not existing_out_stocks.empty and not new_stocks_df.empty:
            combined_df = pd.concat([new_stocks_df, existing_out_stocks], ignore_index=True)
        elif not new_stocks_df.empty:
            combined_df = new_stocks_df
        elif not existing_out_stocks.empty:
            combined_df = existing_out_stocks
        else:
            combined_df = pd.DataFrame()
        
        if not combined_df.empty:
            combined_df = combined_df.drop_duplicates(subset=['name'], keep='first')
        
        if not combined_df.empty:
            combined_df.to_csv(f'universes/{universe}_long.csv', index=False)
            combined_df['name'].to_csv(f'universes/{universe}.csv', index=False)
        else:
            pd.DataFrame(columns=["name", "sector", "exchange", "industry"]).to_csv(f'universes/{universe}_long.csv', index=False)
            pd.DataFrame(columns=["name"]).to_csv(f'universes/{universe}.csv', index=False)
