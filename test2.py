from flask import Flask, render_template_string
from flask_socketio import SocketIO
import datetime
import threading
import time
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# HTML template with stock price display
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Real-time Clock & Stock Tracker</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            transition: all 0.3s ease;
            padding: 20px;
            box-sizing: border-box;
        }
        
        /* Dark theme (default) */
        body.dark {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        /* Light theme */
        body.light {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: #333;
        }
        
        .main-container {
            display: flex;
            flex-direction: column;
            gap: 30px;
            align-items: center;
            width: 100%;
            max-width: 800px;
        }
        
        .clock-container, .stock-container {
            text-align: center;
            padding: 30px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            position: relative;
            width: 100%;
            max-width: 400px;
        }
        
        body.dark .clock-container,
        body.dark .stock-container {
            background: rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        body.light .clock-container,
        body.light .stock-container {
            background: rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .time {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        body.light .time {
            text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.3);
        }
        
        .date {
            font-size: 1.2em;
            opacity: 0.8;
        }
        
        .stock-symbol {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stock-price {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stock-change {
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .positive {
            color: #4CAF50;
        }
        
        .negative {
            color: #f44336;
        }
        
        .stock-info {
            font-size: 0.9em;
            opacity: 0.7;
            margin-top: 10px;
        }
        
        .theme-toggle {
            position: absolute;
            top: 15px;
            right: 15px;
            background: none;
            border: 2px solid;
            border-radius: 25px;
            width: 50px;
            height: 50px;
            cursor: pointer;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        
        body.dark .theme-toggle {
            border-color: rgba(255, 255, 255, 0.3);
            color: white;
        }
        
        body.light .theme-toggle {
            border-color: rgba(0, 0, 0, 0.3);
            color: #333;
        }
        
        .theme-toggle:hover {
            transform: scale(1.1);
        }
        
        body.dark .theme-toggle:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        body.light .theme-toggle:hover {
            background: rgba(0, 0, 0, 0.1);
        }
        
        .status {
            margin-top: 15px;
            font-size: 0.9em;
            opacity: 0.7;
        }
        
        body.dark .connected {
            color: #4CAF50;
        }
        
        body.dark .disconnected {
            color: #f44336;
        }
        
        body.light .connected {
            color: #2e7d32;
        }
        
        body.light .disconnected {
            color: #d32f2f;
        }
        
        @media (min-width: 768px) {
            .main-container {
                flex-direction: row;
                justify-content: center;
            }
        }
    </style>
</head>
<body class="dark">
    <div class="main-container">
        <div class="clock-container">
            <button class="theme-toggle" id="themeToggle" title="Toggle theme">🌙</button>
            <div class="time" id="time">--:--:--</div>
            <div class="date" id="date">Loading...</div>
            <div class="status" id="status">Connecting...</div>
        </div>
        
        <div class="stock-container">
            <div class="stock-symbol">AAPL</div>
            <div class="stock-price" id="stockPrice">$---.--</div>
            <div class="stock-change" id="stockChange">---.-- (---%)</div>
            <div class="stock-info" id="stockInfo">Loading...</div>
        </div>
    </div>

    <script>
        const socket = io();
        const timeEl = document.getElementById('time');
        const dateEl = document.getElementById('date');
        const statusEl = document.getElementById('status');
        const stockPriceEl = document.getElementById('stockPrice');
        const stockChangeEl = document.getElementById('stockChange');
        const stockInfoEl = document.getElementById('stockInfo');
        const themeToggle = document.getElementById('themeToggle');
        const body = document.body;

        // Theme toggle functionality
        themeToggle.addEventListener('click', function() {
            if (body.classList.contains('dark')) {
                body.classList.remove('dark');
                body.classList.add('light');
                themeToggle.textContent = '☀️';
                localStorage.setItem('theme', 'light');
            } else {
                body.classList.remove('light');
                body.classList.add('dark');
                themeToggle.textContent = '🌙';
                localStorage.setItem('theme', 'dark');
            }
        });

        // Load saved theme on page load
        const savedTheme = localStorage.getItem('theme') || 'dark';
        body.classList.remove('dark', 'light');
        body.classList.add(savedTheme);
        themeToggle.textContent = savedTheme === 'light' ? '☀️' : '🌙';

        socket.on('connect', function() {
            statusEl.textContent = 'Connected';
            statusEl.className = 'status connected';
        });

        socket.on('disconnect', function() {
            statusEl.textContent = 'Disconnected';
            statusEl.className = 'status disconnected';
        });

        socket.on('time_update', function(data) {
            timeEl.textContent = data.time;
            dateEl.textContent = data.date;
        });

        socket.on('stock_update', function(data) {
            if (data.error) {
                stockPriceEl.textContent = 'Error';
                stockChangeEl.textContent = da eta.error;
                stockInfoEl.textContent = 'Failed to fetch data';
                return;
            }
            
            stockPriceEl.textContent = `$${data.price}`;
            
            const changeClass = data.change >= 0 ? 'positive' : 'negative';
            const changeSymbol = data.change >= 0 ? '+' : '';
            stockChangeEl.textContent = `${changeSymbol}${data.change} (${changeSymbol}${data.change_percent}%)`;
            stockChangeEl.className = `stock-change ${changeClass}`;
            
            stockInfoEl.textContent = `Last updated: ${data.timestamp}`;
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

def send_time():
    """Background thread to send time updates every second"""
    while True:
        now = datetime.datetime.now()
        time_str = now.strftime('%H:%M:%S')
        date_str = now.strftime('%A, %B %d, %Y')
        
        socketio.emit('time_update', {
            'time': time_str,
            'date': date_str
        })
        
        time.sleep(1)

def send_stock_updates():
    """Background thread to send stock price updates every 30 seconds"""
    while True:
        try:
            # Using Alpha Vantage API (free tier allows 5 calls per minute)
            # You'll need to get a free API key from https://www.alphavantage.co/support/#api-key
            API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your actual API key
            
            # Alternative: Using a mock/demo endpoint for testing
            # For production, you'd use a real stock API
            symbol = 'AAPL'
            
            # Mock data for demonstration (replace with real API call)
            mock_data = {
                'price': '150.25',
                'change': '2.45',
                'change_percent': '1.66',
                'timestamp': datetime.datetime.now().strftime('%H:%M:%S')
            }
            
            # Real API call example (uncomment when you have an API key):
            # url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
            # response = requests.get(url, timeout=10)
            # data = response.json()
            # 
            # if 'Global Quote' in data:
            #     quote = data['Global Quote']
            #     stock_data = {
            #         'price': float(quote['05. price']),
            #         'change': float(quote['09. change']),
            #         'change_percent': quote['10. change percent'].rstrip('%'),
            #         'timestamp': datetime.datetime.now().strftime('%H:%M:%S')
            #     }
            # else:
            #     raise Exception("API limit reached or invalid response")
            
            socketio.emit('stock_update', mock_data)
            
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            socketio.emit('stock_update', {
                'error': 'Unable to fetch stock data',
                'timestamp': datetime.datetime.now().strftime('%H:%M:%S')
            })
        
        time.sleep(30)  # Update every 30 seconds

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send current time immediately
    now = datetime.datetime.now()
    time_str = now.strftime('%H:%M:%S')
    date_str = now.strftime('%A, %B %d, %Y')
    
    socketio.emit('time_update', {
        'time': time_str,
        'date': date_str
    })
    
    # Send current stock data immediately (mock data)
    mock_stock_data = {
        'price': '150.25',
        'change': '2.45',
        'change_percent': '1.66',
        'timestamp': datetime.datetime.now().strftime('%H:%M:%S')
    }
    socketio.emit('stock_update', mock_stock_data)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    # Start the time update thread
    time_thread = threading.Thread(target=send_time)
    time_thread.daemon = True
    time_thread.start()
    
    # Start the stock update thread
    stock_thread = threading.Thread(target=send_stock_updates)
    stock_thread.daemon = True
    stock_thread.start()
    
    print("Starting server with time and stock updates...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
