from pathlib import Path
import zarr
import xarray as xr
import pandas as pd

class DataManager:

    def __init__(self):
        self.hot_path = Path("data/hot/master_db.zarr")
        self.cold_path = Path("data/cold")

    def return_qVar_slice(self, day, time):
        zarr_store = xr.open_zarr(self.hot_path, mode='r')
        qVar_slice = zarr_store['5m'].sel(day=day, time=time)
        qVar_df = qVar_slice.to_dataframe()
        qVar_df = qVar_df.pivot_table(index='ident',columns='qVar',values='5m')
        qVar_df['day'] = day
        qVar_df['time'] = time
        return qVar_df

    def _convert_df_dates(self, df):
        df_cols = df.columns.tolist()
        if 'extended.quoteTime' in df_cols:
            df['extended.quoteTime'] = pd.to_datetime(df['extended.quoteTime'])
