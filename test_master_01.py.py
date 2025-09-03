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

from main_classes.Save_Data_Master import Save_Data_Master as SDM

sdm = SDM()
zarr_store = xr.open_dataset(sdm.hot_path_master)

STOCK = 'AAPL'
DAY = '2025-09-02'

stock_marks = zarr_store['5m'].sel(ident=STOCK,day=DAY,qVar='quote.mark')
stock_marks['time'] = datetimes = pd.to_datetime(DAY + ' ' + stock_marks['time'].values)

plt.figure(figsize=(10,5))
stock_marks.plot(label='mark')

plt.title("Marks over Time")
plt.xlabel("Time")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.gcf().autofmt_xdate() # Rotate labels for readability
plt.tight_layout()
plt.show()