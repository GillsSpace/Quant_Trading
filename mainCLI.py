#Project Imports
from utility.lib_apiManagment import create_client, create_client_gcloud_storage

#Python Imports
import os
import sys
import schwabdev as sd
import numpy as np
import pandas as pd

DEFAULT_BUCKET_NAME = "bucket-quant-1"

def main():
    option = ""
    print("Welcome to the Quant Trading CLI by Wills Erda!")
    machine_type = input("Local or VM: ").strip().lower()
    if machine_type not in ["local", "vm"]:
        print("Invalid input. Please enter 'local' or 'vm'.")
        return

    while option.lower() not in ["exit", "quit","e"]:
        print()
        option = input("Please enter a command: ").strip()
        
        if option.lower() in ["help", "h"]:
            print("Available commands:")
            print("   - 'gen-keys': Generate API keys for Schwab via Schwabdev script.")
            print("   - ('s-lb')'storage-list-buckets': List all Google Cloud Storage buckets.")
            print("   - ('s-lf')'storage-list-files': List files in a specified Google Cloud Storage bucket.")
            print("   - ('e')'exit', 'quit': Exit the program.")


        elif option.lower() == "gen-keys":
            if machine_type == 'vm':
                print("This command is not available on VM. Please run it on your local machine.")
                continue
            client = create_client()
            client.tokens.update_tokens(True,True)


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

        elif option.lower() in ["s-sk", "storage-sync-keys"]:
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


        elif option.lower() in ["exit", "quit", "e"]:
            print("Exiting the program. Goodbye!")

        else:
            print(f"Unknown command: {option}. Type 'help' for available commands.")


if __name__ == "__main__":
    main()
    sys.exit(0)
