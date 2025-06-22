import pandas as pb
import numpy as np
import arcticdb as adb

FILE_TO_ADD = ""
SATRT_DATE_TIME = None
END_DATE_TIME = None


uri = "lmdb://./arcticdb_storage"
ac = adb.Arctic(uri)

lib_t1u1 = ac.get_library("T1_U1", create_if_missing=True)


with open('Bloomburg_Data/CSV_Files/2025_SPX_Jan1_900_May1_859.csv', 'r') as f:
    pass

