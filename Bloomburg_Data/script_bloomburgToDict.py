# FILE HEADER:
# This script processes a CSV file containing stock data from Bloomberg in the standard exel export format, converting it into a T1 dictionary format.

import pandas as pd
from datetime import datetime, timedelta, time
import numpy as np

DATE_FORMAT = "%m/%d/%Y %H:%M"
TRADE_START_TIME = datetime.strptime("2025/01/01 9:00", "%Y/%m/%d %H:%M") 
TRADE_END_TIME = datetime.strptime("2025/05/01 8:59", "%Y/%m/%d %H:%M")
DECIMAL_PRECISION = 5
BATCH_SIZE = 1000  # Process this many rows at a time

input_path = "Bloomburg_Data/CSV_Files/2025_SPX_Jan1_900_May1_859.csv"


df = pd.read_csv(input_path,low_memory=False)
print(f"Data loaded successfully from {input_path}. Processing...")
final_df = pd.DataFrame()
num_stocks = (df.shape[1] + 1) // 14  # Using integer division
print("Number of stocks to process: ", num_stocks)

def process_row(row):
    """Process a single row to create the dictionary of price data"""
    return dict(
        Open=(
            float(row["Open_bid"]), 
            float(row["Open_ask"]), 
            round(float(row["Open_bid"]) - float(row["Open_ask"]), DECIMAL_PRECISION)
        ),
        Close=(
            float(row["Close_bid"]), 
            float(row["Close_ask"]), 
            round(float(row["Close_bid"]) - float(row["Close_ask"]), DECIMAL_PRECISION)
        ),
        High=(
            float(row["High_bid"]), 
            float(row["High_ask"]), 
            round(float(row["High_bid"]) - float(row["High_ask"]), DECIMAL_PRECISION)
        ),
        Low=(
            float(row["Low_bid"]), 
            float(row["Low_ask"]), 
            round(float(row["Low_bid"]) - float(row["Low_ask"]), DECIMAL_PRECISION)
        ),
        Volume=(
            float(row["Volume_bid"]), 
            float(row["Volume_ask"]), 
            round(float(row["Volume_bid"]) + float(row["Volume_ask"]), DECIMAL_PRECISION)
        )
    )

for i in range(int(num_stocks)):

    local_bid = df.iloc[:, i*14:i*14+6]
    local_ask = df.iloc[:, i*14+7:i*14+13]

    local_stock_name = local_bid.iloc[1, 0]
    print("    Processing stock: ", local_stock_name)
    
    if local_bid.columns[1][0:3] != "Bid":
        print("Error: Data Incomplete (Bid not found in expected location) for stock", local_stock_name)
        continue
    if local_ask.columns[1][0:3] != "Ask":
        print("Error: Data Incomplete (Ask not found in expected location) for stock", local_stock_name)
        continue
    
    local_bid = local_bid.iloc[3:, :].dropna()
    local_ask = local_ask.iloc[3:, :].dropna()
    local_max_entries = max(local_bid.shape[0], local_ask.shape[0])

    print("        Sub-dataframes created for Bid and Ask")
    print("        Dataframe sizes: Bid", local_bid.shape, "Ask", local_ask.shape)
    
    local_bid.columns = ["Dates", "Open", "Close", "High", "Low", "Volume"]
    local_ask.columns = ["Dates", "Open", "Close", "High", "Low", "Volume"]

    # Try merging with datetime conversion to ensure consistent format
    # First, ensure dates are in datetime format
    local_bid_copy = local_bid.copy()
    local_ask_copy = local_ask.copy()

    # Convert to datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(local_bid_copy['Dates']):
        local_bid_copy['Dates'] = pd.to_datetime(local_bid_copy['Dates'])
    
    if not pd.api.types.is_datetime64_any_dtype(local_ask_copy['Dates']):
        local_ask_copy['Dates'] = pd.to_datetime(local_ask_copy['Dates'])

    # Now merge with consistent datetime format
    local_df = pd.merge(local_bid_copy, local_ask_copy, how="outer", on="Dates", suffixes=("_bid", "_ask"))
    print(f"        Dataframes merged Bid and Ask dataframes. New shape: {local_df.shape}")

    local_df.set_index("Dates", inplace=True)
    
    # Initialize the column with None values 
    local_df[local_stock_name] = None
    
    # Process in batches to limit memory usage
    num_rows = local_max_entries
    num_batches = (num_rows + BATCH_SIZE - 1) // BATCH_SIZE  # Calculate number of batches
    
    print(f"        Processing {num_rows} rows in {num_batches} batches of {BATCH_SIZE}")
    
    # Create a list to store the processed data
    processed_data = []
    processed_indices = []
    
    for batch_idx in range(num_batches):
        start_idx = batch_idx * BATCH_SIZE
        end_idx = min((batch_idx + 1) * BATCH_SIZE, num_rows)
        
        # Process this batch
        batch = local_df.iloc[start_idx:end_idx]
        print(f"            Processing batch {batch_idx + 1}/{num_batches} (rows {start_idx} to {end_idx-1})")
        
        # Apply the function to each row in the batch
        for idx, row in batch.iterrows():
            processed_data.append(process_row(row))
            processed_indices.append(idx)
    

    # Create a Series with the processed data and assign it to the dataframe
    local_df[local_stock_name] = pd.Series(processed_data, index=processed_indices)
                
    print("        Dictionaries created for stock")
    
    # Merge with the final dataframe
    final_df = pd.merge(final_df, local_df[[local_stock_name]], "outer", left_index=True, right_index=True)
    
print("Processing completed. Saving to CSV...")
output_path = input_path.split(".")[0] + "_dicts.csv"
final_df.to_csv(output_path, index=True, header=True)
print("CSV saved successfully at: ", output_path)

