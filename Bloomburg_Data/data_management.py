import arcticdb as adb
import pandas as pd
import numpy as np
from datetime import datetime


uri = "lmdb://./arcticdb_storage"
ac = adb.Arctic(uri)

library = ac.get_library("test1", create_if_missing=True)

with open('./2025_SPX_Jan1_900_May1_859.csv', 'r') as f:
    pass
