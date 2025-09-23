# Transmission Dashboard

A Flask-based web dashboard for monitoring transmission log data from X-ray scanning systems.

## Features

- **Real-time Dashboard**: Monitor transmission logs with live updates
- **Data Filtering**: Filter by status (OK/NOK), search terms, and log files
- **Statistics**: View success rates, scan counts, and performance metrics
- **Responsive Design**: Modern, mobile-friendly interface
- **Auto-refresh**: Automatic data updates every 30 seconds
- **Configurable Settings**: Customize logs directory and refresh intervals
- **FTP Connectivity Monitoring**: Track availability of up to two FTP endpoints with scheduled health checks

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application (choose one method):

**Method 1: Using the startup script (recommended)**
```bash
python run.py
```

**Method 2: Direct execution**
```bash
python app.py
```

**Method 3: Windows batch file**
```cmd
start_dashboard.bat
```

3. The dashboard will automatically open in your browser at:
```
http://localhost:5000
```

## Quick Start

1. Place your log files in the `logs/` directory
2. Run `python run.py`
3. The dashboard will open automatically in your browser
4. Navigate between different sections using the sidebar

## Usage

### Dashboard Sections

1. **Overview**: Main dashboard with statistics and recent activity
2. **Detail Log OK**: View successful transmission logs
3. **Detail Log NOK**: View failed transmission logs
4. **Statistics**: Charts and analytics
5. **Settings**: Configure logs directory and application settings

### Data Fields

- **ID Scan**: Unique scan identifier (PICNO)
- **Nomor Container**: Container number
- **Jam Scan**: Scan timestamp
- **Scan Time**: Duration of the scan
- **Overall Time**: Total processing time
- **Jam Update**: Last update timestamp
- **Selisih Waktu**: Time difference between update and scan
- **Jumlah Gambar**: Number of images
- **Status**: OK or NOK

### Filtering Options

- **Log File**: Select specific log file to analyze
- **Search**: Search by ID Scan or Container Number
- **Status**: Filter by OK or NOK status

## Log File Structure

The application reads log files from the `logs/` directory. It looks for lines containing:
- `resultCode":true` for successful transmissions
- `response text:` followed by JSON data

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/data` - Get log data with optional filtering
- `GET /api/log-files` - Get available log files
- `GET /api/stats` - Get statistics
- `GET /api/settings` - Get current application settings
- `POST /api/settings` - Update application settings
- `GET /api/validate-directory` - Validate logs directory path
- `GET /api/ftp-status` - Get cached FTP connectivity status

## Configuration

### Settings Page

The application includes a settings page where you can:

1. **Configure Logs Directory**: Set the path to your Transmission log files
2. **Auto-refresh Interval**: Adjust how often the dashboard updates (10-300 seconds)
3. **FTP Targets**: Define up to two FTP host/port pairs for connectivity checks
4. **FTP Ping Interval**: Configure how often the background worker pings the FTP endpoints
5. **Directory Validation**: Verify that your logs directory contains valid log files

### Default Configuration

- **Logs Directory**: `logs/` (relative to application directory)
- **Auto-refresh**: 30 seconds
- **FTP Targets**: `ftp.primary.example.com:21` and `ftp.backup.example.com:21`
- **FTP Ping Interval**: 60 seconds
- **Log File Pattern**: `Transmission.log*`

### Settings File

Settings are automatically saved to `settings.json` in the application directory. You can also manually edit this file if needed. The key values include:

- `logs_directory`: Absolute or relative path to the Transmission logs
- `auto_refresh_interval`: Dashboard auto-refresh cadence in seconds
- `ftp_targets`: An array of two objects (`host` and `port`) representing the primary and backup FTP endpoints. Leave a host blank to disable monitoring for that slot.
- `ftp_ping_interval`: Ping cadence (seconds) used by the background FTP status worker

### FTP Monitoring

The overview dashboard displays a dedicated FTP connectivity widget that refreshes on the same cadence as the background worker. Each configured FTP endpoint is probed on the configured interval and reported as **Online**, **Offline**, or **Not configured**. Connection issues are logged server-side for troubleshooting while keeping the dashboard responsive.

## Requirements

- Python 3.7+
- Flask 2.3.3
- Modern web browser with JavaScript enabled
