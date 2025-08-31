from datetime import datetime, time, date, timedelta
import pandas as pd

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

def convert_schwab_timestamps(df):
    datetime_cols = [
        'regular.regularMarketTradeTime',
        'extended.quoteTime',
        'extended.tradeTime', 
        'quote.askTime',
        'quote.bidTime',
        'quote.quoteTime',
        'quote.tradeTime'
    ]
    cols = df.columns
    tz = 'America/New_York'

    for col in datetime_cols:
        if col not in cols:
            continue
        else:
            df[col] = pd.to_datetime(df[col], unit='ms', utc=True).map(lambda x: x.tz_convert(tz))

    return df
        
