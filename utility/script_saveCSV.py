import sys
import time
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
import schwabdev as sd
import time as tm
import zarr
import shutil
import os

import warnings

warnings.filterwarnings('ignore', message="The data type .* does not have a Zarr V3 specification.*")
warnings.filterwarnings('ignore', message="Consolidated metadata is currently not part in the Zarr format 3 specification.*")

from main_classes.DataManager import DataManager as DM
from utility.lib_apiManagment import create_client as CC



if __name__ == "__main__":
    args = sys.argv
    dm = DM()

    if len(args) != 3:
        print("Usage: python script_saveCSV.py <day> <qVar>")
        sys.exit(1)

    if args[1] == "help" or args[1] == "--help":
        print("Usage: python script_saveCSV.py <day> <qVar>")
        print("Example: python script_saveCSV.py 2023-10-05 quote.mark")
        print(f"Possible qVars: {dm.quote_fields}")
        sys.exit(0)

    day = args[1]
    var = args[2]

    zarr_store = xr.open_dataset(dm.hot_db_path)
    data = zarr_store['5m'].sel(day=day,qVar=var)
    df = data.to_dataframe().pivot_table(index='time',columns='ident',values='5m')
    df.to_csv(f'DT_{day}_{var}.csv')