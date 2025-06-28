from flask import Blueprint, render_template
import schwabdev
import json

schwab_bp = Blueprint('schwab', __name__, template_folder='templates', static_folder='static')

def create_client():
    """Create a Schwab client with API keys."""
    with open('keys.json', 'r') as f:
        keys = json.load(f)

    return schwabdev.Client(keys['schwab']['app_key'], keys['schwab']['app_secret'])

@schwab_bp.route('/')
def page_index():

    client = create_client()

    accounts = client.account_linked()
    account_hash = accounts.json()[0]['hashValue']

    account_details = client.account_details(account_hash,fields='positions')

    return render_template('schwab/schwab.html', content=account_details.json())
