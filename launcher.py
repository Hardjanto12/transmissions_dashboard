#!/usr/bin/env python3
"""
Robust launcher for Transmission Dashboard
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are available"""
    required_packages = [
        'flask', 'openpyxl', 'pystray', 'PIL', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        # For windowed apps, we can't use input() or print()
        # Just try to install missing packages silently
        for package in missing_packages:
            if package == 'PIL':
                package = 'Pillow'
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True, capture_output=True)
            except subprocess.CalledProcessError:
                # If installation fails, we'll handle it in the main app
                pass
    
    return True

def check_files():
    """Check if required files exist"""
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        os.path.join(base_dir, 'app.py'),
        os.path.join(base_dir, 'tray_app.py'),
        os.path.join(base_dir, 'templates', 'dashboard.html')
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            return False
    
    return True

def create_directories():
    """Create necessary directories"""
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    directories = ['logs', 'templates']
    
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        Path(dir_path).mkdir(exist_ok=True)

def show_error_dialog(message):
    """Show error dialog for windowed applications"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Transmission Dashboard Error", message)
        root.destroy()
    except:
        # If tkinter fails, just exit
        pass

def main():
    """Main launcher function"""
    # Change to the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the executable directory
    os.chdir(base_dir)
    
    # Check dependencies silently
    check_dependencies()
    
    # Check required files
    if not check_files():
        show_error_dialog("Missing required files. Please ensure all files are present.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Start the tray application
    try:
        from tray_app import main as tray_main
        tray_main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        show_error_dialog(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
