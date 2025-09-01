from flask import Blueprint, render_template

api_bp = Blueprint('api', __name__, template_folder='templates', static_folder='static')

@api_bp.route('/api')
def api():
    return render_template('api/api.html')