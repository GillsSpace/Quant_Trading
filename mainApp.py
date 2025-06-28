from flask import Flask, render_template
from flask_socketio import SocketIO
from blueprints.schwab.views import schwab_bp
from blueprints.api.views import api_bp

import datetime
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Register blueprints
app.register_blueprint(schwab_bp, url_prefix='/schwab')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def page_index():
    return render_template('index.html')

@app.route('/reference')
def page_reference():
    return render_template('reference.html')

class UtilityThreadFunctions():
    @staticmethod
    def start_background_thread(function):
        """Start a background thread for a given function"""
        thread = threading.Thread(target=function)
        thread.daemon = True
        thread.start()
        
    def send_time():
        """Background thread to send time updates every second"""
        while True:
            now = datetime.datetime.now()
            time_str = now.strftime('%H:%M:%S')
            date_str = now.strftime('%A, %B %d') # alternate format: %A, %B %d, %Y

            socketio.emit('time_update', {
                'time': time_str,
                'date': date_str
            })

            time.sleep(1)


if __name__ == '__main__':
    # Start Background threads
    UtilityThreadFunctions.start_background_thread(UtilityThreadFunctions.send_time)

    # Start the Flask-SocketIO server
    socketio.run(app, debug=True)
