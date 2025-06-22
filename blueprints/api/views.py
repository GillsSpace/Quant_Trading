from flask import Blueprint, render_template

api_pb = Blueprint('api', __name__, template_folder='templates', static_folder='static')

@api_pb.route('/')
def page_index():
    return render_template('api.html')
