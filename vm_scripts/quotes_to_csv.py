# Global Imports
import json
import pandas as pd
import sys
from datetime import datetime, date, time, timedelta
import time as tm

# Local Imports
from universes import universe_config as uc

def round_to_nearest_5(dt):
    """Rounds a datetime object to the nearest 5 minutes."""
    # Minutes since the start of the hour
    minutes = dt.minute
    seconds = dt.second

    # Total minutes (including fractional from seconds)
    total_minutes = minutes + seconds / 60

    # Nearest multiple of 5
    rounded_minutes = round(total_minutes / 5) * 5

    # Handle overflow to next hour
    if rounded_minutes == 60:
        dt = dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        dt = dt.replace(minute=rounded_minutes, second=0, microsecond=0)

    return dt

if __name__ == "__main__":

    st = tm.time()

    args = sys.argv
    print(f"    Arguments: {args}")

    date = datetime.now()
    date_str = date.strftime("%Y-%m-%d")
    time_str = round_to_nearest_5(datetime.now()).strftime("%H:%M")

    # Fetch quotes from the API
    quotes_df = uc.Universe_Config.return_universe_quotes_df(args[1])

    quotes_df.to_csv(f"live_data/{args[1]}_{date_str}_{time_str}.csv", index=False)

    et = tm.time()
    print(f"    Time taken: {et - st} seconds")
