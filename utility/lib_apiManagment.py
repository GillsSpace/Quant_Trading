import schwabdev as sd
import json

def create_client():
    """Create a Schwab client with API keys."""
    with open('keys.json', 'r') as f:
        keys = json.load(f)

    return sd.Client(keys['schwab']['app_key'], keys['schwab']['app_secret'])

def create_client_gcloud_storage():
    """Create a Schwab client with API keys from Google Cloud Storage."""
    from google.cloud import storage as gcs

    with open('keys.json', 'r') as f:
        keys = json.load(f)

    return gcs.Client(project=keys['gcloud']['project_id'],)
