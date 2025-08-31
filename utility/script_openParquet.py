import pandas as pd
from pandasgui.gui import show
import sys

from utility.lib_timeFunctions import convert_schwab_timestamps

if __name__ == "__main__":

    args = sys.argv[1:]
    file_path = args[0]
    # Load the Parquet file
    df = pd.read_parquet(file_path)

    df = convert_schwab_timestamps(df)

    # Display the DataFrame using PandasGUI
    gui = show(df)
    # Optionally, you can save the GUI state or interact with it further
    # gui.save_state('gui_state.pkl')  # Uncomment to save the GUI state if needed
