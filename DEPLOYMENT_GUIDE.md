# Transmission Dashboard - Deployment Guide

This guide explains how to create and deploy a standalone executable version of the Transmission Dashboard.

## 🚀 Quick Start

### Building the Executable

1. **Run the build script:**
   ```bash
   python build_exe.py
   ```
   
   Or use the batch file on Windows:
   ```cmd
   build.bat
   ```

2. **The build process will:**
   - Install required dependencies
   - Create an application icon
   - Build a standalone executable
   - Create a deployment package

3. **Output location:**
   - Executable: `deployment/TransmissionDashboard.exe`
   - All necessary files in the `deployment/` folder

### Deploying to Server

1. **Copy the entire `deployment/` folder to your server**
2. **Place your log files in the `logs/` subfolder**
3. **Run `TransmissionDashboard.exe`**
4. **Access the dashboard at: http://localhost:5000**

## 📦 Deployment Package Contents

```
deployment/
├── TransmissionDashboard.exe    # Main executable
├── logs/                        # Directory for log files
├── settings.json               # Configuration file
└── README_DEPLOYMENT.txt       # Quick start guide
```

## 🎯 Features

### System Tray Integration
- **Minimize to Tray**: Application runs in system tray
- **Right-click Menu**: Access dashboard, settings, and status
- **Auto-start**: Can be configured to start with Windows

### Enhanced UI
- **Activity Indicators**: Real-time processing indicators
- **Status Notifications**: Success/error notifications
- **Online/Offline Status**: Connection status indicator
- **Responsive Design**: Works on all screen sizes

### Configuration
- **Logs Directory**: Configurable via settings page
- **Auto-refresh**: Adjustable refresh intervals
- **Port Configuration**: Default port 5000

## 🔧 System Requirements

### Server Requirements
- **OS**: Windows 10/11 or Windows Server 2016+
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk**: 100MB free space
- **Network**: Port 5000 available

### No Additional Software Required
- ✅ No Python installation needed
- ✅ No pip packages to install
- ✅ No virtual environments
- ✅ Just copy and run!

## 🚀 Usage Instructions

### Starting the Application

1. **Double-click `TransmissionDashboard.exe`**
2. **The application will:**
   - Start the web server
   - Appear in system tray
   - Show a welcome notification
   - Open dashboard in browser (optional)

### System Tray Menu

Right-click the tray icon to access:
- **📊 Open Dashboard** - Launch web interface
- **⚙️ Settings** - Open settings page
- **ℹ️ Status** - View current status
- **❌ Quit** - Close application

### Web Interface

1. **Navigate to: http://localhost:5000**
2. **Use the dashboard features:**
   - Overview with statistics
   - Detail logs (OK/NOK)
   - Statistics and charts
   - Settings configuration

## ⚙️ Configuration

### Settings Page
Access via web interface or tray menu:
- **Logs Directory**: Set path to your log files
- **Auto-refresh**: Adjust refresh interval (10-300 seconds)
- **Directory Validation**: Verify log file location

### Manual Configuration
Edit `settings.json`:
```json
{
  "logs_directory": "logs",
  "auto_refresh_interval": 30
}
```

## 🔍 Troubleshooting

### Common Issues

**Dashboard won't open:**
- Check Windows Firewall settings
- Ensure port 5000 is not blocked
- Verify the application is running (check system tray)

**No data displayed:**
- Verify log files are in the correct directory
- Check log file format (should contain "Transmission.log")
- Use the settings page to configure logs directory

**Application won't start:**
- Check if another instance is already running
- Verify Windows compatibility
- Check system tray for error messages

### Log Files
- **Location**: `logs/` folder (configurable)
- **Format**: `Transmission.log*` files
- **Content**: JSON responses with transmission data

## 🛡️ Security Considerations

### Network Access
- **Default**: Only accessible from localhost (127.0.0.1)
- **Production**: Configure firewall rules as needed
- **Authentication**: Add authentication for production use

### File Permissions
- **Logs Directory**: Ensure read access to log files
- **Settings**: Application needs write access to settings.json
- **Temporary Files**: Creates temp files for Excel exports

## 📊 Performance

### Resource Usage
- **Memory**: ~50-100MB typical usage
- **CPU**: Low usage, spikes during data processing
- **Network**: Minimal, only web interface traffic

### Optimization
- **Large Log Files**: Consider log rotation
- **Many Files**: Application handles multiple log files efficiently
- **Auto-refresh**: Adjust interval based on update frequency

## 🔄 Updates

### Updating the Application
1. **Stop the current instance** (right-click tray → Quit)
2. **Replace the executable** with new version
3. **Restart the application**
4. **Settings are preserved** in settings.json

### Data Migration
- **Settings**: Preserved in settings.json
- **Log Files**: No migration needed
- **Database**: No database, all data from log files

## 📞 Support

### Getting Help
1. **Check the status** (tray menu → Status)
2. **Verify log files** are in correct location
3. **Check Windows Event Viewer** for errors
4. **Review the main README.md** for detailed documentation

### Log Files Location
- **Application Logs**: Check Windows Event Viewer
- **Web Server Logs**: Displayed in console (if running from command line)
- **Error Messages**: Shown in notifications and status dialogs

## 🎉 Success!

Once deployed, you'll have:
- ✅ Standalone executable (no dependencies)
- ✅ System tray integration
- ✅ Real-time dashboard
- ✅ Configurable settings
- ✅ Professional UI with activity indicators
- ✅ Easy deployment to any Windows server

The application is now ready for production use!
