# FILE HEADER:
# This library is used to manage data retrival from varioius data sources.
from datetime import datetime, timedelta, time
import numpy as np
import pandas as pd
import os
import ast


class T1_DataSeries:
    """
    Class to manage a T1 data series for a specific universe or universe subset.
    """

    def db_retrieve(start_date_time,end_date_time):
        """
        Retrieves T1 data from the database for a given date range.
        :param start_date_time: Start datetime for the data series.
        :param end_date_time: End datetime for the data series.
        :return: A DataFrame containing the T1 data.
        """
        # Placeholder for database retrieval logic
        raise NotImplementedError("Database retrieval not implemented.")

    def __init__(self, start_date_time, end_date_time, universe="U1"):
        """
        Initializes the T1_DataSeries with a date range and universe.
        :param start_date_time: Start datetime for the data series.
        :param end_date_time: End datetime for the data series.
        :param universe: The universe of the data (default is "U1").
        """
        self.symbols_list = None
        self.universe = universe



        self.data = None

    def __init__(self, symbols_list, start_date_time, end_date_time, universe="U1"):
        """
        Initializes the T1_DataSeries with a list of symbols and a date range.
        :param symbols_list: List of stock symbols to retrieve data for.
        :param start_date_time: Start datetime for the data series.
        :param end_date_time: End datetime for the data series.
        :param universe: The universe of the data (default is "U1").
        """
        self.symbols_list = symbols_list
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.universe = universe
        self.data = None

    def load_data(self, date_time):
        """
        Loads T1 data for the given symbol and date_time.
        :param date_time: The datetime for which to load the data.
        """
        self.data = get_T1_entry(self.symbol, date_time, self.universe)


def get_T1_entry(symbol, date_time, universe="U1"):
    """
    Retrieves T1 entry data for a given symbol, date_time, and universe.
    :param symbol: The stock symbol to retrieve data for.
    :param date_time: The datetime for which to retrieve the data.
    :param universe: The universe of the data (default is "U1").
    :return: A dictionary containing the T1 entry data or None if not found.
    :rtype: dict or None
    :example: get_T1_entry("AAPL", datetime.strptime("2025/01/02 9:40", "%Y/%m/%d %H:%M"))
    """
    if universe == "U1":
        symbol1 = f"{symbol.upper()} UN Equity"
        symbol2 = f"{symbol.upper()} UW Equity"
        if date_time >= datetime.strptime("2025/01/01 9:00", "%Y/%m/%d %H:%M") and date_time <= datetime.strptime("2025/05/01 8:59", "%Y/%m/%d %H:%M"):
            df = pd.read_csv("Bloomburg_Data/CSV_Files/2025_SPX_Jan1_900_May1_859_dicts.csv", low_memory=False)
            df.set_index(df.columns[0], inplace=True)
            try:
                return ast.literal_eval(df.loc[date_time.strftime("%Y-%m-%d %H:%M:%S"), symbol1])
            except KeyError:
                try:
                    return ast.literal_eval(df.loc[date_time.strftime("%Y-%m-%d %H:%M:%S"), symbol2])
                except KeyError:
                    return None


