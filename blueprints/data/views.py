from flask import Blueprint, render_template
from universes.universe_config import Universe_Config
import json

data_bp = Blueprint('data', __name__, template_folder='templates', static_folder='static')

@data_bp.route('/')
def page_index():
    """Render the index page."""

    json_data = Universe_Config.universe_dict

    return render_template('data/data.html', content=json_data)
