from flask import Blueprint, render_template

api_bp = Blueprint('api', __name__, template_folder='templates', static_folder='static')

@api_bp.route('/')
def page_index():
    return render_template('api/api.html')
