from copy import Error
import polygon
import json
import sys
import pandas as pd
import datetime

from schwabdev import client

def get_key():
    """Retrieve the API key from a JSON file."""
    with open('keys.json', 'r') as f:
        keys = json.load(f)
    return keys['polygon_key']

def main():

    key = get_key()

    client = polygon.RESTClient(key)

    date = sys.argv[1]

    if not date:
        print("Please provide a date in the format YYYY-MM-DD.")
        return

    if len(date) != 10 or date[4] != '-' or date[7] != '-':
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    date_object = datetime.datetime.strptime(date, '%Y-%m-%d')

    day_of_week = date_object.strftime('%A')

    if day_of_week in ['Saturday', 'Sunday']:
        print(f"Data is not available for weekends. Please provide a weekday date. [{date} is a {day_of_week}]")
        return

    print(f"Fetching data for {date}...")

    try:
        responce = client.get_grouped_daily_aggs(
            date,
            adjusted=True,
        )
    except polygon.exceptions.BadResponse as e:
        print(f"Error fetching data: {e}")
        return

    df = pd.DataFrame([agg.__dict__ for agg in responce])
    df.to_csv(f"polygon_market_data/daily_aggregates_{date}.csv", index=False)

    print(f"Data for {date} saved to daily_aggregates_{date}.csv")

main()
