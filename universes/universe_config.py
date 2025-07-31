from contextlib import nullcontext
from types import NoneType
from tradingview_screener import Column, Query
import pandas as pd
import os
import json
import schwabdev as sd
import time as tm

class Universe_Config:
    """Base class for universe configurations."""

    universe_dict = {
        "u01": {
                "in": [
                Column('market_cap_basic') > 1_000_000_000,
                Column('price_52_week_high') < 15,
                Column('price_52_week_low') > 1,
                ],
                "out": [
                Column('market_cap_basic') > 500_000_000,
                Column('price_52_week_high') > 25,
                ]        
            },
        "u00": {
            "in": [
                Column('market_cap_basic') < 400_000_000,
                Column('price_52_week_high') < 10,
                Column('price_52_week_low') > 1,
                Column('country') == 'United States',
                Column('type') == 'stock',
                Column('volume|1W').between(2_000_000, 8_000_000),
                Column('exchange').isin(['AMEX', 'NASDAQ', 'NYSE']),
            ],
            "out": [
                Column('market_cap_basic') < 70_000_000,
                Column('price_52_week_high') < 25,
                Column('price_52_week_low') > 0.25,
                Column('country') == 'United States',
                Column('type') == 'stock',
                Column('volume|1W').between(500_000, 10_000_000),
                Column('exchange').isin(['AMEX', 'NASDAQ', 'NYSE']),
            ]
        },
    }

    def create_client():
        """Create a Schwab client with API keys."""
        with open('keys.json', 'r') as f:
            keys = json.load(f)

        return sd.Client(keys['schwab']['app_key'], keys['schwab']['app_secret'])

    def generate_test_print(universe):
        """Generates and returns a DataFrame for the specified universe."""
        universe_columns = Universe_Config.universe_dict[universe]['in']
        query = (
            Query()
            .select("name", "sector", "exchange", "industry")
            .where(*universe_columns)
            .limit(10_000)
        )
        result =  query.get_scanner_data()
        return result

    def return_universe(universe):
        "Returns a list of stock tickers for the specified universe."

        universe_df = pd.read_csv(f'universes/{universe}.csv')
        if universe_df.empty:
            return []
        return universe_df['name'].tolist()

    def return_universe_quotes(universe):
        """Returns a DataFrame of stock quotes for the specified universe."""

        tickers = Universe_Config.return_universe(universe)
        client = Universe_Config.create_client()

        if len(tickers) == 0:
            return NoneType
        if len(tickers) <= 500:
            quotes = client.quotes(tickers)
            quotes_dict = quotes.json()
            list_of_quotes = [{"ident":key, **value} for key, value in quotes_dict.items()]
        if len(tickers) > 500:
            list_of_quotes = []
            for i in range(0, len(tickers), 500):
                quotes = client.quotes(tickers[i:i+500])
                quotes_dict = quotes.json()
                list_of_quotes.extend([{"ident":key, **value} for key, value in quotes_dict.items()])
                tm.sleep(0.2)

        return pd.json_normalize(list_of_quotes)
            
    def gen_csv(universe):
        """Generates both a detialed CSV and a simplified CSV for the specified universe."""
        universe_columns = Universe_Config.universe_dict[universe]['in']
        query = (
            Query()
            .select("name", "sector", "exchange", "industry")
            .where(*universe_columns)
            .limit(10_000)
        )
        dt:pd.DataFrame = query.get_scanner_data()[1]
        dt.to_csv(f'universes/{universe}_long.csv', index=False)
        dt['name'].to_csv(f'universes/{universe}.csv', index=False)


    def regen_csv(universe):
        in_conditions = Universe_Config.universe_dict[universe]['in']
        out_conditions = Universe_Config.universe_dict[universe]['out']
        
        in_query = (
            Query()
            .select("name", "sector", "exchange", "industry")
            .where(*in_conditions)
        )
        in_result = in_query.get_scanner_data()
        new_stocks_df = pd.DataFrame(in_result[1])
        
        existing_df = pd.DataFrame()
        long_csv_path = f'universes/{universe}_long.csv'
        
        if os.path.exists(long_csv_path):
            existing_df = pd.read_csv(long_csv_path)
            
            out_query = (
                Query()
                .select("name", "sector", "exchange", "industry")
                .where(*out_conditions)
                .limit(10_000)
            )
            out_result = out_query.get_scanner_data()
            out_stocks_df = pd.DataFrame(out_result[1])
            
            if not out_stocks_df.empty and not existing_df.empty:
                existing_out_stocks = existing_df[existing_df['name'].isin(out_stocks_df['name'])]
            else:
                existing_out_stocks = pd.DataFrame()
        else:
            existing_out_stocks = pd.DataFrame()
        
        if not existing_out_stocks.empty and not new_stocks_df.empty:
            combined_df = pd.concat([new_stocks_df, existing_out_stocks], ignore_index=True)
        elif not new_stocks_df.empty:
            combined_df = new_stocks_df
        elif not existing_out_stocks.empty:
            combined_df = existing_out_stocks
        else:
            combined_df = pd.DataFrame()
        
        if not combined_df.empty:
            combined_df = combined_df.drop_duplicates(subset=['name'], keep='first')
        
        if not combined_df.empty:
            combined_df.to_csv(f'universes/{universe}_long.csv', index=False)
            combined_df['name'].to_csv(f'universes/{universe}.csv', index=False)
        else:
            pd.DataFrame(columns=["name", "sector", "exchange", "industry"]).to_csv(f'universes/{universe}_long.csv', index=False)
            pd.DataFrame(columns=["name"]).to_csv(f'universes/{universe}.csv', index=False)
