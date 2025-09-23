import os
from waitress import serve
from app import app

# Configuration
FLASK_PORT = 5000
FLASK_HOST = '0.0.0.0' # Listen on all interfaces

if __name__ == '__main__':
    print(f"Starting Flask server on http://{FLASK_HOST}:{FLASK_PORT}")
    serve(app, host=FLASK_HOST, port=FLASK_PORT)
