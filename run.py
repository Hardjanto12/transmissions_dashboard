#!/usr/bin/env python3
"""
Startup script for Transmission Dashboard
"""

import os
import sys
import webbrowser
import time
import threading
from app import app

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

def main():
    """Main function to start the application"""
    print("=" * 60)
    print("🚀 Starting Transmission Dashboard")
    print("=" * 60)
    print()
    print("📊 Dashboard Features:")
    print("  • Real-time log monitoring")
    print("  • Data filtering and search")
    print("  • Statistics and analytics")
    print("  • Modern responsive UI")
    print()
    print("🌐 Access the dashboard at: http://localhost:5000")
    print("📁 Log files directory: logs/")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Start Flask app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("Thank you for using Transmission Dashboard!")
        sys.exit(0)

if __name__ == '__main__':
    main()
