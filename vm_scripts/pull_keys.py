from utility.lib_apiManagment import create_client, create_client_gcloud_storage

DEFAULT_BUCKET_NAME = "bucket-quant-1"


if __name__ == "__main__":
    storage_client = create_client_gcloud_storage()
    bucket = storage_client.get_bucket(DEFAULT_BUCKET_NAME)
    blob_keys = bucket.get_blob("keys.json")
    blob_tokens = bucket.get_blob("tokens.json")
    if blob_keys is None or blob_tokens is None:
        print("    Keys or tokens not found in the bucket.")
    else:
        blob_keys.download_to_filename("keys.json")
        blob_tokens.download_to_filename("tokens.json")
        print("    Keys and tokens pulled from Google Cloud Storage.")
