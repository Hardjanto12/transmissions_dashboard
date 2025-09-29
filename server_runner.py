import os
import threading
from waitress import create_server
from app import app

FLASK_PORT = 5050
FLASK_HOST = '0.0.0.0'  # Listen on all interfaces
SHUTDOWN_TOKEN = os.environ.get('TRANSMISSION_SHUTDOWN_TOKEN', 'transmission-shutdown')


if __name__ == '__main__':
    shutdown_event = threading.Event()
    app.config['SHUTDOWN_EVENT'] = shutdown_event
    app.config['SHUTDOWN_TOKEN'] = SHUTDOWN_TOKEN

    server = create_server(app, host=FLASK_HOST, port=FLASK_PORT)

    def _monitor_shutdown():
        shutdown_event.wait()
        print('Shutdown signal received. Closing server...')
        server.close()

    monitor_thread = threading.Thread(target=_monitor_shutdown, daemon=True)
    monitor_thread.start()

    print(f"Starting Flask server on http://{FLASK_HOST}:{FLASK_PORT}")
    try:
        server.run()
    except KeyboardInterrupt:
        print('KeyboardInterrupt received. Shutting down server...')
        shutdown_event.set()
    finally:
        try:
            server.close()
        except Exception:
            pass
        monitor_thread.join(timeout=1)
        print('Server stopped.')
