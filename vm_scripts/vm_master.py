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
from main_classes.Universe_Config import Universe_Config as UC
from main_classes.Save_Data_Master import Save_Data_Master as SDM

def main():
    datetime_raw = datetime.now()
    datetime_rounded = round_to_nearest_5(datetime_raw)
    date_str = datetime_rounded.strftime("%Y-%m-%d")
    time_str = datetime_rounded.strftime("%H:%M")

    # Always Run;
    sdm = SDM()
    sdm.save_qVar_data(date_str, time_str)

    if time_str == "23:40":
        next_day = (datetime_rounded + timedelta(days=1)).strftime("%Y-%m-%d")
        UC.regen_csv('u00')
        sdm.add_day_shell(next_day)

    if time_str == "04:00":
        sdm.save_fVar_data(date_str)

if __name__ == "__main__":
    main()
