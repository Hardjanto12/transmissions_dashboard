#!/usr/bin/env python3
"""
Build script for creating Transmission Dashboard executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """Install required packages for building"""
    print("📦 Installing build requirements...")
    
    requirements = [
        'pyinstaller',
        'pystray',
        'pillow',
        'flask',
        'openpyxl'
    ]
    
    for req in requirements:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', req], 
                          check=True, capture_output=True)
            print(f"✅ Installed {req}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {req}: {e}")
            return False
    
    return True

def create_icon():
    """Create a simple icon file if it doesn't exist"""
    icon_path = Path('icon.ico')
    if not icon_path.exists():
        print("🎨 Creating application icon...")
        try:
            from PIL import Image, ImageDraw
            
            # Create a 64x64 icon
            img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw dashboard icon
            draw.ellipse([8, 8, 56, 56], fill=(102, 126, 234, 255))
            draw.rectangle([20, 35, 25, 45], fill=(255, 255, 255, 255))
            draw.rectangle([28, 30, 33, 45], fill=(255, 255, 255, 255))
            draw.rectangle([36, 25, 41, 45], fill=(255, 255, 255, 255))
            draw.text((32, 15), "TD", fill=(255, 255, 255, 255))
            
            img.save('icon.ico', format='ICO')
            print("✅ Created icon.ico")
        except Exception as e:
            print(f"⚠️ Could not create icon: {e}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    try:
        # Build the executable
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name=TransmissionDashboard',
            '--add-data=app.py;.',
            '--add-data=tray_app.py;.',
            '--add-data=templates;templates',
            '--add-data=logs;logs',
            '--add-data=requirements.txt;.',
            '--add-data=README.md;.',
            '--hidden-import=flask',
            '--hidden-import=openpyxl',
            '--hidden-import=openpyxl.styles',
            '--hidden-import=openpyxl.utils',
            '--hidden-import=pystray',
            '--hidden-import=PIL',
            '--hidden-import=tkinter',
            '--hidden-import=requests',
            '--hidden-import=threading',
            '--hidden-import=signal',
            '--hidden-import=atexit',
            '--icon=icon.ico' if os.path.exists('icon.ico') else '',
            'launcher.py'
        ]
        
        # Remove empty icon parameter if no icon exists
        if not os.path.exists('icon.ico'):
            cmd = [arg for arg in cmd if arg != '--icon=icon.ico']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable built successfully!")
            return True
        else:
            print(f"❌ Build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_deployment_package():
    """Create a deployment package with all necessary files"""
    print("📦 Creating deployment package...")
    
    deploy_dir = Path('deployment')
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_path = Path('dist/TransmissionDashboard.exe')
    if exe_path.exists():
        shutil.copy2(exe_path, deploy_dir / 'TransmissionDashboard.exe')
        print("✅ Copied executable")
    
    # Create logs directory
    logs_dir = deploy_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Create templates directory and copy template
    templates_dir = deploy_dir / 'templates'
    templates_dir.mkdir(exist_ok=True)
    if os.path.exists('templates/dashboard.html'):
        shutil.copy2('templates/dashboard.html', templates_dir / 'dashboard.html')
        print("✅ Copied dashboard template")
    
    # Create sample settings
    settings_file = deploy_dir / 'settings.json'
    if not settings_file.exists():
        with open(settings_file, 'w') as f:
            f.write('''{
  "logs_directory": "logs",
  "auto_refresh_interval": 30
}''')
        print("✅ Created default settings.json")
    
    # Create a simple launcher batch file
    launcher_bat = deploy_dir / 'start_dashboard.bat'
    with open(launcher_bat, 'w') as f:
        f.write('''@echo off
echo Starting Transmission Dashboard...
echo The application will run in the system tray.
echo Right-click the tray icon to access options.
echo.
TransmissionDashboard.exe
''')
    print("✅ Created launcher batch file")
    
    # Create README for deployment
    readme_file = deploy_dir / 'README_DEPLOYMENT.txt'
    with open(readme_file, 'w') as f:
        f.write('''Transmission Dashboard - Portable Deployment Package
=======================================================

This is a completely portable package that can be copied to any Windows server.

QUICK START:
1. Copy this entire folder to your server (any location)
2. Place your Transmission.log files in the 'logs' folder
3. Double-click 'TransmissionDashboard.exe' or 'start_dashboard.bat'
4. The application will appear in your system tray
5. Right-click the tray icon and select "Open Dashboard"
6. Access the dashboard at: http://localhost:5000

PORTABLE FEATURES:
- No installation required - just copy and run
- No Python installation needed
- No dependencies to install
- Works from any directory
- All files included in this package

FILES INCLUDED:
- TransmissionDashboard.exe    # Main application
- start_dashboard.bat         # Easy launcher
- logs/                       # Directory for your log files
- templates/                  # Web interface templates
- settings.json              # Configuration file
- README_DEPLOYMENT.txt      # This file

SETTINGS:
- Edit settings.json to configure logs directory
- Default logs directory: ./logs/
- Auto-refresh interval: 30 seconds

TROUBLESHOOTING:
- If the dashboard doesn't open, check Windows Firewall settings
- Ensure port 5000 is not blocked
- Check that log files are in the correct directory
- Right-click tray icon and select "Status" for diagnostics
- The application works from any directory - no need to run from specific location

For support, check the main README.md file.
''')
    print("✅ Created deployment README")
    
    print(f"\n🎉 Portable deployment package created in: {deploy_dir.absolute()}")
    print("📁 Contents:")
    for item in deploy_dir.iterdir():
        print(f"   - {item.name}")
    print("\n🚀 This package is now completely portable!")
    print("   Just copy the entire 'deployment' folder to any server and run.")

def main():
    """Main build process"""
    print("=" * 60)
    print("🔨 Transmission Dashboard - Executable Builder")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    # Create icon
    create_icon()
    
    # Build executable
    if not build_executable():
        print("❌ Build failed")
        sys.exit(1)
    
    # Create deployment package
    create_deployment_package()
    
    print("\n" + "=" * 60)
    print("✅ Build completed successfully!")
    print("📦 Deployment package ready in 'deployment' folder")
    print("🚀 Copy the deployment folder to your server and run TransmissionDashboard.exe")
    print("=" * 60)

if __name__ == '__main__':
    main()
