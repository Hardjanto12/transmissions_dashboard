#!/usr/bin/env python3
"""
System Tray Application for Transmission Dashboard
"""

import os
import sys
import threading
import time
import webbrowser
import signal
import atexit
from pathlib import Path

try:
    import pystray
    from PIL import Image, ImageDraw
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("Installing required packages for system tray...")
    os.system("pip install pystray pillow")
    import pystray
    from PIL import Image, ImageDraw
    import tkinter as tk
    from tkinter import messagebox

# Import Flask app and settings
try:
    from app import app, app_settings
except ImportError:
    print("Error: Could not import Flask app. Make sure app.py is in the same directory.")
    sys.exit(1)

class TransmissionDashboardTray:
    def __init__(self):
        self.app = app
        self.server_thread = None
        self.running = False
        self.icon = None
        self.shutdown_event = threading.Event()
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def create_icon_image(self):
        """Create a simple icon for the system tray"""
        # Create a 64x64 image with a simple dashboard icon
        width = 64
        height = 64
        
        # Create image with transparent background
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a simple dashboard icon
        # Background circle
        draw.ellipse([8, 8, 56, 56], fill=(102, 126, 234, 255), outline=(255, 255, 255, 255), width=2)
        
        # Chart bars
        draw.rectangle([20, 35, 25, 45], fill=(255, 255, 255, 255))
        draw.rectangle([28, 30, 33, 45], fill=(255, 255, 255, 255))
        draw.rectangle([36, 25, 41, 45], fill=(255, 255, 255, 255))
        
        # Title text
        draw.text((32, 15), "TD", fill=(255, 255, 255, 255))
        
        return image
    
    def start_server(self):
        """Start the Flask server in a separate thread"""
        if not self.running:
            self.running = True
            self.shutdown_event.clear()
            
            def run_server():
                try:
                    self.app.run(
                        debug=False,
                        host='0.0.0.0',
                        port=5000,
                        use_reloader=False,
                        threaded=True
                    )
                except Exception as e:
                    self.running = False
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            time.sleep(3)  # Give server time to start
            
            # Verify server is running
            if not self.is_server_running():
                pass  # Server may not be ready yet
    
    def stop_server(self):
        """Stop the Flask server"""
        if self.running:
            self.running = False
            self.shutdown_event.set()
            
            # Try to shutdown Flask gracefully
            try:
                import requests
                requests.get('http://localhost:5000/shutdown', timeout=2)
            except:
                pass  # Server might not have shutdown endpoint
            
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5)
    
    def is_server_running(self):
        """Check if the server is running"""
        try:
            import requests
            response = requests.get('http://localhost:5000', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.stop_server()
            if self.icon:
                self.icon.stop()
        except Exception as e:
            pass  # Ignore cleanup errors
    
    def open_dashboard(self, icon=None, item=None):
        """Open the dashboard in the default web browser"""
        try:
            if not self.running:
                self.show_error("Server is not running. Please restart the application.")
                return
            
            # Check if server is actually accessible
            if not self.is_server_running():
                self.show_error("Server is not responding. Please check the application status.")
                return
                
            webbrowser.open('http://localhost:5000')
        except Exception as e:
            self.show_error(f"Failed to open dashboard: {e}")
    
    def show_status(self, icon=None, item=None):
        """Show current status"""
        try:
            status = "🟢 Running" if self.running else "🔴 Stopped"
            server_status = "✅ Responding" if self.is_server_running() else "❌ Not responding"
            logs_dir = app_settings.get('logs_directory', 'logs')
            
            # Create a simple status window
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            message = f"""Transmission Dashboard Status

Application Status: {status}
Server Status: {server_status}
Logs Directory: {logs_dir}
URL: http://localhost:5000

The dashboard is accessible in your web browser.
Click 'Open Dashboard' to launch it now."""
            
            messagebox.showinfo("Dashboard Status", message)
            root.destroy()
        except Exception as e:
            self.show_error(f"Failed to show status: {e}")
    
    def show_error(self, message):
        """Show error message"""
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Transmission Dashboard Error", message)
            root.destroy()
        except Exception as e:
            pass  # Ignore error display errors
    
    def show_settings(self, icon=None, item=None):
        """Open settings in browser"""
        try:
            if not self.running:
                self.show_error("Server is not running. Please restart the application.")
                return
                
            if not self.is_server_running():
                self.show_error("Server is not responding. Please check the application status.")
                return
                
            webbrowser.open('http://localhost:5000/#settings')
        except Exception as e:
            self.show_error(f"Failed to open settings: {e}")
    
    def quit_app(self, icon=None, item=None):
        """Quit the application"""
        try:
            # Show confirmation dialog
            root = tk.Tk()
            root.withdraw()
            result = messagebox.askyesno("Quit Application", 
                                     "Are you sure you want to quit Transmission Dashboard?")
            root.destroy()
            
            if result:
                self.cleanup()
                sys.exit(0)
        except Exception as e:
            sys.exit(1)
    
    def create_menu(self):
        """Create the system tray menu"""
        return pystray.Menu(
            pystray.MenuItem("📊 Open Dashboard", self.open_dashboard, default=True),
            pystray.MenuItem("⚙️ Settings", self.show_settings),
            pystray.MenuItem("ℹ️ Status", self.show_status),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Quit", self.quit_app)
        )
    
    def run(self):
        """Run the system tray application"""
        try:
            # Create the system tray icon
            icon_image = self.create_icon_image()
            
            self.icon = pystray.Icon(
                "TransmissionDashboard",
                icon_image,
                "Transmission Dashboard",
                self.create_menu()
            )
            
            # Start the Flask server
            self.start_server()
            
            # Wait a bit for server to start
            time.sleep(2)
            
            # Show initial status (non-blocking)
            threading.Thread(target=self.show_status, daemon=True).start()
            
            # Run the system tray icon
            self.icon.run()
            
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            self.show_error(f"Failed to start application: {e}")
            self.cleanup()
            sys.exit(1)

def main():
    """Main entry point"""
    # For windowed applications, we can't use print() reliably
    # Just start the application silently
    
    # Create and run the tray application
    try:
        tray_app = TransmissionDashboardTray()
        tray_app.run()
    except Exception as e:
        # Show error dialog if something goes wrong
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Transmission Dashboard Error", 
                               f"Failed to start application: {e}")
            root.destroy()
        except:
            pass
        sys.exit(1)

if __name__ == '__main__':
    main()
