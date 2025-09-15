#Project Imports
from utility.lib_apiManagment import create_client, create_client_gcloud_storage
from main_classes.UniverseManager import UniverseManager as UM
from main_classes.DataManager import DataManager as DM

#Python Imports
import os
import sys
import schwabdev as sd
import numpy as np
import pandas as pd
import time as tm
from pathlib import Path

DEFAULT_BUCKET_NAME = "bucket-quant-1"

def main():
    option = ""
    print("Welcome to the Quant Trading CLI by Wills Erda!")
    machine_type = input("Local or VM: ").strip().lower()
    if machine_type == "" or machine_type == 'l':
        machine_type = "local"
    elif machine_type == 'v':
        machine_type = "vm"
    if machine_type not in ["local", "vm"]:
        print("Invalid input. Please enter 'local' or 'vm'.")
        return

    if machine_type == 'local':
        import pandasgui

    while option.lower() not in ["exit", "quit","e"]:
        print()
        option = input("Please enter a command: ").strip()
        
        if option.lower() in ["help", "h"]:
            print("Available commands:")
            print("   [KEY MANAGEMENT]")
            print("   - ('k-g') keys-gen:       Generate API keys for Schwab via Schwabdev script.")
            print("   - ('k-s') keys-sync:      Synchronize keys with Google Cloud Storage.")
            print("   - ('k-p') keys-pull:      Pull keys and tokens from Google Cloud Storage to the vm.")
            print("   [DATABASE MANAGEMENT]")
            print("   - ('db-c-h')'db-create-hot': Create a new database for hot storage with an initial day.")
            print("   [DATA TESTING]")
            print("   - ('g-q-c')'gen-current-quotes-csv': Generate current quotes and save as CSV file.")
            print("   - ('g-q-p')'gen-current-quotes-parquet': Generate current quotes and save as Parquet file.")
            print("   - ('d-ut')'universe-test': Test a universe configuration and display the resulting DataFrame.")
            print("   - ('d-ug') 'universe-gen': Generate univrese csv files")
            print("   [GOOGLE CLOUD STORAGE MANAGEMENT]")
            print("   - ('s-lb')'storage-list-buckets': List all Google Cloud Storage buckets.")
            print("   - ('s-lf')'storage-list-files': List files in a specified Google Cloud Storage bucket.")
            print("   [GENERAL]")
            print("   - ('e')'exit', 'quit': Exit the program.")


        ### KEY MANAGEMENT ###
        elif option.lower() in ['keys-gen','k-g']:
            if machine_type == 'vm':
                print("This command is not available on VM. Please run it on your local machine.")
                continue
            client = create_client()
            client.tokens.update_tokens(True,True)

        elif option.lower() in ["keys-sync", "k-s"]:
            if machine_type == 'vm':
                print("This command is not available on VM. Please run it on your local machine.")
                continue
            client = create_client_gcloud_storage()
            bucket = client.get_bucket(DEFAULT_BUCKET_NAME)
            blob_keys = bucket.get_blob("keys.json")
            blob_tokens = bucket.get_blob("tokens.json")
            if not blob_keys:
                print("Keys blob does not exist in the bucket. Creating a new one.")
                blob_keys = bucket.blob("keys.json")
            if not blob_tokens:
                print("Tokens blob does not exist in the bucket. Creating a new one.")
                blob_tokens = bucket.blob("tokens.json")
            blob_tokens.upload_from_filename("tokens.json")
            blob_keys.upload_from_filename("keys.json")
            print("Keys and tokens synchronized with Google Cloud Storage.")

        elif option.lower() in ["k-p", "keys-pull"]:
            if machine_type == 'local':
                print("This command is not available on local machine. Please run it on your VM.")
                continue
            client = create_client_gcloud_storage()
            bucket = client.get_bucket(DEFAULT_BUCKET_NAME)
            blob_keys = bucket.get_blob("keys.json")
            blob_tokens = bucket.get_blob("tokens.json")
            if not blob_keys:
                print("Keys blob does not exist in the bucket. Please run 'storage-sync-keys' first.")
                continue
            if not blob_tokens:
                print("Tokens blob does not exist in the bucket. Please run 'storage-sync-keys' first.")
                continue
            blob_keys.download_to_filename("keys.json")
            blob_tokens.download_to_filename("tokens.json")
            print("Keys and tokens pulled from Google Cloud Storage.")

        elif option.lower() in ["gen-current-quotes-csv", "g-q-c"]:
            if machine_type == 'vm':
                print("This command is not available on VM. Please run it on your local machine.")
                continue
            universe = input("Enter the universe (e.g., u01, u00): ").strip()
            if universe == "":
                universe = "u00"
            print(f"Generating current qoutes for universe: {universe}")
            st = tm.time()
            UM.gen_quotes_csv(universe)
            et = tm.time()
            print(f"Quotes for universe '{universe}' generated in {et - st:.2f} seconds.")

        elif option.lower() in ["gen-current-quotes-parquet", "g-q-p"]:
            if machine_type == 'vm':
                print("This command is not available on VM. Please run it on your local machine.")
                continue
            universe = input("Enter the universe (e.g., u01, u00): ").strip()
            if universe == "":
                universe = "u00"
            print(f"Generating current quotes for universe: {universe}")
            st = tm.time()
            UM.gen_quotes_parquet(universe)
            et = tm.time()
            print(f"Quotes for universe '{universe}' generated in {et - st:.2f} seconds.")
            
        elif option.lower() in ['db-create-hot','db-c-h']:
            smd = DM()
            date_input = input("Enter the initial day for the new database 'YYYY-MM-DD' (e.g. '2025-08-31'): ").strip()
            smd.create_new_db(initial_day=date_input)
            print("Database created successfully for initial day:", date_input)

        elif option.lower() in ['storage-list-buckets','s-lb']:
            print("Listing files in Google Cloud Storage bucket:")
            storage_client = create_client_gcloud_storage()
            output = storage_client.list_buckets()
            print([bucket.name for bucket in output])

        elif option.lower() in ['storage-list-files', 's-lf']:
            bucket_name = input("Enter the name of the bucket: ").strip()
            if bucket_name == "":
                bucket_name = DEFAULT_BUCKET_NAME
            print(f"Listing files in bucket: {bucket_name}")
            storage_client = create_client_gcloud_storage()
            try:
                bucket = storage_client.get_bucket(bucket_name)
                output = storage_client.list_blobs(bucket)
                print([blob.name for blob in output])
            except Exception as e:
                print(f"Error listing files in bucket '{bucket_name}': {e}")

        elif option.lower() in ['universe-test','d-ut']:
            if machine_type == 'vm':
                print("This command is not available on VM. Please run it on your local machine.")
                continue
            universe = input("Enter the universe to test (e.g., u01, u00): ").strip()
            if universe == "":
                universe = "u00"
            print(f"Testing universe configuration for: {universe}")
            st = tm.time()
            df = UM.return_universe_quotes_df(universe)
            et = tm.time()
            if df is not None and not df.empty:
                print(f"Universe '{universe}' DataFrame:")
                print(f"DataFrame shape: {df.shape}")
                pandasgui.show(df)
            else:
                print(f"No data available for universe: {universe}")
            print(f"Universe test completed in {et - st:.2f} seconds.")

        elif option.lower() in ['universe-gen','d-ug']:
            if machine_type == 'vm':
                print("This command is not available on VM. Please run it on your local machine.")
                continue
            universe = input("Enter the universe to generate files for (e.g., u01, u00): ").strip()
            if universe == "":
                universe = "u00"
            print(f"Generating universe files for: {universe}")
            st = tm.time()
            UM.gen_csv(universe)
            et = tm.time()
            print(f"Universe files for '{universe}' generated in {et - st:.2f} seconds.")


        elif option.lower() in ["exit", "quit", "e"]:
            print("Exiting the program. Goodbye!")

        else:
            print(f"Unknown command: {option}. Type 'help' for available commands.")


if __name__ == "__main__":
    main()
    sys.exit(0)
