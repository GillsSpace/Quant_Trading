import schwabdev as sd
import json

def create_client():
    """Create a Schwab client with API keys."""
    with open('keys.json', 'r') as f:
        keys = json.load(f)

    return sd.Client(keys['schwab']['app_key'], keys['schwab']['app_secret'])
