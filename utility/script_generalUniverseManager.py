# Project Imports
from universes.universe_config import Universe_Config

# General Imports
import os
import json
import pandas as pd
import schwabdev as sd
from pandasgui import show

def create_client():
    """Create a Schwab client with API keys."""
    with open('keys.json', 'r') as f:
        keys = json.load(f)

    return sd.Client(keys['schwab']['app_key'], keys['schwab']['app_secret'])

def get_universe():
    """Prompt user for universe name and validate."""
    universe = input("Enter the universe name: ").strip()

    while universe not in Universe_Config.universe_dict:
        print(f"Universe '{universe}' not found in the configuration.")
        print("Available universes:")
        for key in Universe_Config.universe_dict.keys():
            print(f"- {key}")
        universe = input("Please enter a valid universe name: ").strip()

    return universe


if __name__ == "__main__":

    option = None

    while option not in ['q', 'Q', 'quit', 'Quit']:

        option = input("What Action would you like to perform: ").strip()

        if option in ['h', 'H', 'help', 'Help']:
            print("Options:")
            print("  - [q]uit: Exit the program")
            print("  - [h]elp: Show this help message")
            print("  - gen: Generate a CSV file for the universe")
            print("  - test: Get test list of stocks for the universe and display as PandasGUI")
            print("  - regen: Regenerate the CSV file for the universe")
            print("  - show: Get quotes for the universe and display as PandasGUI")
            continue

        elif option in ['gen', 'Gen']:
            universe = get_universe()
            Universe_Config.gen_csv(universe)
            print(f"CSV files for {universe} has been generated.")

        elif option in ['test', 'Test']:
            universe = get_universe()
            data = Universe_Config.generate_test_print(universe)
            print(f" Total Stocks: {data[0]}")
            show(data[1])

        elif option in ['regen', 'Regen']:
            universe = get_universe()
            Universe_Config.regen_csv(universe)
            print(f"CSV files for {universe} has been regenerated.")

        elif option in ['show', 'Show']:
            print("Fetching quotes for the universe...")
            universe = get_universe()
            data = Universe_Config.return_universe_quotes(universe)
            if isinstance(data, pd.DataFrame):
                show(data)
            else:
                print("Error fetching quotes. Please check the universe configuration.")

        else:
            print("Invalid option. Please try again or type 'h' for help.")
            continue

