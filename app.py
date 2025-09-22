from flask import Flask, render_template, request, jsonify, send_file
import os
import re
import json
from datetime import datetime
import glob
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import tempfile

app = Flask(__name__)

# Settings configuration
SETTINGS_FILE = 'settings.json'

def load_settings():
    """Load settings from JSON file"""
    default_settings = {
        'logs_directory': 'logs',
        'auto_refresh_interval': 30
    }

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except (json.JSONDecodeError, IOError):
            pass

    # Create default settings file
    save_settings(default_settings)
    return default_settings

def save_settings(settings):
    """Save settings to JSON file"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, TypeError):
        return False


# Load initial settings
app_settings = load_settings()


class LogParser:
    def __init__(self, logs_dir="logs"):
        self.logs_dir = logs_dir
        
    def get_log_files(self):
        """Get all log files sorted by modification time (newest first)"""
        pattern = os.path.join(self.logs_dir, "Transmission.log*")
        log_files = glob.glob(pattern)
        return sorted(log_files, key=os.path.getmtime, reverse=True)
    
    def parse_log_file(self, file_path):
        """Parse a single log file and extract JSON data"""
        data = []
        provisional_entries = {}
        completed_task_ids = set()

        def parse_task_time(raw_value):
            """Convert datetime.datetime(...) text to a formatted string."""
            if not raw_value:
                return None
            parts = [part.strip() for part in raw_value.split(',')]
            try:
                if len(parts) < 3:
                    return None
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                hour = int(parts[3]) if len(parts) > 3 else 0
                minute = int(parts[4]) if len(parts) > 4 else 0
                second = int(parts[5]) if len(parts) > 5 else 0
                dt_obj = datetime(year, month, day, hour, minute, second)
                return dt_obj.strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError, IndexError):
                return None

        def extract_upload_info(line):
            """Extract task details from upload related log lines."""
            if ('Task.py-build_upload_data' not in line and
                    'XmlParse.py-parse_xml' not in line):
                return None

            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
                                        line)
            log_timestamp = timestamp_match.group(1) if timestamp_match else None

            task_no_match = (re.search(r"'task_no':\s*'([^']+)'", line) or
                             re.search(r"'pic_no':\s*'([^']+)'", line))
            image_path_match = (re.search(r"'image_path':\s*'([^']*)'", line) or
                                re.search(r"'img_dir_path':\s*'([^']*)'", line))
            retry_match = re.search(r"'retry_(?:count|time)':\s*(\d+)", line)
            task_time_match = re.search(
                r"'task_time':\s*datetime\.datetime\(([^)]+)\)", line)

            task_time = parse_task_time(task_time_match.group(1)
                                        if task_time_match else None)

            if not task_no_match:
                return None

            return {
                'task_no': task_no_match.group(1),
                'image_path': image_path_match.group(1)
                if image_path_match else '',
                'retry_count': int(retry_match.group(1))
                if retry_match else 0,
                'task_time': task_time,
                'log_timestamp': log_timestamp
            }

        def update_provisional_entry(info):
            """Create or update provisional entries for upload events."""
            task_no = info.get('task_no')
            if not task_no or task_no in completed_task_ids:
                return

            log_timestamp = info.get('log_timestamp')
            scan_time = info.get('task_time') or log_timestamp or 'N/A'
            image_path = info.get('image_path', '')
            retry_count = info.get('retry_count', 0)

            entry = provisional_entries.get(task_no)
            if entry:
                if scan_time and scan_time != 'N/A':
                    entry['scan_time'] = scan_time
                if log_timestamp:
                    entry['update_time'] = log_timestamp
                    entry['log_timestamp'] = log_timestamp
                raw_data = entry.setdefault('raw_data', {})
                raw_data['task_no'] = task_no
                if image_path:
                    raw_data['image_path'] = image_path
                if retry_count or 'retry_count' not in raw_data:
                    raw_data['retry_count'] = retry_count
                if scan_time and scan_time != 'N/A':
                    raw_data['task_time'] = scan_time
                if log_timestamp:
                    raw_data['log_timestamp'] = log_timestamp
                return

            raw_data = {
                'task_no': task_no,
                'image_path': image_path,
                'retry_count': retry_count,
                'task_time': scan_time,
                'source': 'upload'
            }
            if log_timestamp:
                raw_data['log_timestamp'] = log_timestamp

            provisional_entries[task_no] = {
                'id_scan': task_no,
                'container_no': '',
                'scan_time': scan_time,
                'scan_duration': 'N/A',
                'overall_time': 'N/A',
                'update_time': log_timestamp or 'N/A',
                'time_difference': 'N/A',
                'image_count': 0,
                'status': 'NOK',
                'log_timestamp': log_timestamp,
                'file_name': os.path.basename(file_path),
                'raw_data': raw_data
            }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    upload_info = extract_upload_info(line)
                    if upload_info:
                        update_provisional_entry(upload_info)
                        continue

                    # Look for lines with response text (both success and failure)
                    if 'response text:' in line and 'center response:' in line:
                        try:
                            # Extract the ID from center response
                            id_match = re.search(r'center response:([^,]+)', line)
                            response_id = id_match.group(1) if id_match else ''
                            
                            # Extract JSON from the line
                            json_start = line.find('response text: ') + len('response text: ')
                            json_str = line[json_start:].strip()
                            
                            # Parse the JSON
                            response_data = json.loads(json_str)
                            
                            # Extract timestamp from log line
                            pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
                            timestamp_match = re.search(pattern, line)
                            log_timestamp = (timestamp_match.group(1) 
                                           if timestamp_match else None)
                            
                            # Handle successful responses (resultCode: true)
                            if (response_data.get('resultCode') and 
                                    response_data.get('resultData') and
                                    response_data.get('resultData') != '-'):
                                result_data = response_data['resultData']
                                
                                # Calculate scan duration
                                scan_duration = self.calculate_scan_duration(
                                    result_data)
                                
                                # Calculate time difference
                                time_diff = self.calculate_time_difference(
                                    result_data)
                                
                                # Count images
                                image_count = self.count_images(result_data)
                                
                                # Determine status
                                status = ("OK" if result_data.get('RESPON_TPS_API') 
                                         == 'OK' else "NOK")
                                
                                entry = {
                                    'id_scan': result_data.get('PICNO', ''),
                                    'container_no': result_data.get('CONTAINER_NO', ''),
                                    'scan_time': result_data.get('SCANTIME', ''),
                                    'scan_duration': scan_duration,
                                    'overall_time': scan_duration,
                                    'update_time': result_data.get('UPDATE_TIME', ''),
                                    'time_difference': time_diff,
                                    'image_count': image_count,
                                    'status': status,
                                    'log_timestamp': log_timestamp,
                                    'file_name': os.path.basename(file_path),
                                    'raw_data': result_data
                                }
                                data.append(entry)
                                if entry['id_scan']:
                                    completed_task_ids.add(entry['id_scan'])
                                    provisional_entries.pop(entry['id_scan'], None)
                                elif response_id:
                                    completed_task_ids.add(response_id)
                                    provisional_entries.pop(response_id, None)

                            # Handle failed responses (resultCode: false)
                            elif (response_data.get('resultCode') is False and
                                  response_data.get('resultData') == '-'):

                                # Extract container number from response description if available
                                container_no = "Failed!"
                                desc = response_data.get('resultDesc', '')
                                if 'Container' in desc:
                                    # Try to extract container number from description
                                    container_match = re.search(
                                        r'Container[^:]*:?\s*([A-Z0-9]+)', desc)
                                    if container_match:
                                        container_no = container_match.group(1)
                                
                                entry = {
                                    'id_scan': response_id,
                                    'container_no': container_no,
                                    'scan_time': log_timestamp or 'N/A',
                                    'scan_duration': 'N/A',
                                    'overall_time': 'N/A',
                                    'update_time': log_timestamp or 'N/A',
                                    'time_difference': 'N/A',
                                    'image_count': 0,
                                    'status': 'NOK',
                                    'log_timestamp': log_timestamp,
                                    'file_name': os.path.basename(file_path),
                                    'raw_data': response_data,
                                    'error_description': desc
                                }
                                data.append(entry)
                                if response_id:
                                    completed_task_ids.add(response_id)
                                    provisional_entries.pop(response_id, None)

                        except (json.JSONDecodeError, KeyError):
                            continue
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")

        data.extend(provisional_entries.values())

        return data
    
    def calculate_scan_duration(self, data):
        """Calculate scan duration from TIME_SCANSTART and TIME_SCAN_STOP"""
        try:
            start_time = data.get('TIME_SCANSTART', 0)
            stop_time = data.get('TIME_SCAN_STOP', 0)
            if start_time and stop_time:
                duration = int(stop_time) - int(start_time)
                return f"{duration} detik"
        except (ValueError, TypeError):
            pass
        return "N/A"
    
    def calculate_time_difference(self, data):
        """Calculate time difference between UPDATE_TIME and SCANTIME"""
        try:
            scan_time = data.get('SCANTIME', '')
            update_time = data.get('UPDATE_TIME', '')
            
            if scan_time and update_time:
                scan_dt = datetime.strptime(scan_time, '%Y-%m-%d %H:%M:%S')
                update_dt = datetime.strptime(update_time, '%Y-%m-%d %H:%M:%S')
                diff = update_dt - scan_dt
                
                if diff.days < 0:
                    hours = diff.seconds // 3600
                    minutes = (diff.seconds % 3600) // 60
                    seconds = diff.seconds % 60
                    return (f"-{abs(diff.days)} day, "
                            f"{hours:02d}:{minutes:02d}:{seconds:02d}")
                else:
                    hours = diff.seconds // 3600
                    minutes = (diff.seconds % 3600) // 60
                    seconds = diff.seconds % 60
                    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except (ValueError, TypeError):
            pass
        return "N/A"
    
    def count_images(self, data):
        """Count the number of images"""
        count = 0
        for i in range(1, 8):  # IMAGE1_PATH to IMAGE7_PATH
            if data.get(f'IMAGE{i}_PATH'):
                count += 1
        return count
    
    def get_all_data(self, status_filter=None, search_term=None, 
                     log_file=None):
        """Get all data from all log files with optional filtering"""
        all_data = []
        
        log_files = self.get_log_files()
        
        # Filter by specific log file if specified
        if log_file:
            log_files = [f for f in log_files 
                        if os.path.basename(f) == log_file]
        
        for file_path in log_files:
            file_data = self.parse_log_file(file_path)
            all_data.extend(file_data)
        
        # Remove duplicates based on ID scan (keep the latest one)
        seen_ids = set()
        unique_data = []
        
        # Sort by scan time first to ensure we keep the latest entry
        all_data.sort(key=lambda x: x['scan_time'], reverse=True)
        
        for entry in all_data:
            if entry['id_scan'] and entry['id_scan'] not in seen_ids:
                seen_ids.add(entry['id_scan'])
                unique_data.append(entry)
        
        # Apply filters after deduplication
        if status_filter:
            unique_data = [entry for entry in unique_data 
                          if entry['status'] == status_filter]
        
        if search_term:
            search_term = search_term.lower()
            unique_data = [entry for entry in unique_data if 
                          search_term in entry['id_scan'].lower() or 
                          search_term in entry['container_no'].lower()]
        
        return unique_data

# Initialize log parser with settings
log_parser = LogParser(app_settings['logs_directory'])


@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/data')
def get_data():
    """API endpoint to get log data"""
    status_filter = request.args.get('status')
    search_term = request.args.get('search')
    log_file = request.args.get('log_file')
    
    data = log_parser.get_all_data(status_filter, search_term, log_file)
    
    return jsonify({
        'data': data,
        'total': len(data)
    })


@app.route('/api/log-files')
def get_log_files():
    """API endpoint to get available log files"""
    log_files = log_parser.get_log_files()
    file_list = [os.path.basename(f) for f in log_files]
    return jsonify(file_list)


@app.route('/api/stats')
def get_stats():
    """API endpoint to get statistics"""
    all_data = log_parser.get_all_data()
    
    total_scans = len(all_data)
    ok_scans = len([d for d in all_data if d['status'] == 'OK'])
    nok_scans = len([d for d in all_data if d['status'] == 'NOK'])
    
    # Get recent scans (last 24 hours)
    recent_scans = []
    now = datetime.now()
    for entry in all_data:
        try:
            scan_time = datetime.strptime(entry['scan_time'], 
                                        '%Y-%m-%d %H:%M:%S')
            if (now - scan_time).total_seconds() < 86400:  # 24 hours
                recent_scans.append(entry)
        except (ValueError, TypeError):
            continue
    
    success_rate = (round((ok_scans / total_scans * 100), 2) 
                   if total_scans > 0 else 0)
    
    return jsonify({
        'total_scans': total_scans,
        'ok_scans': ok_scans,
        'nok_scans': nok_scans,
        'success_rate': success_rate,
        'recent_scans': len(recent_scans)
    })


@app.route('/api/export/excel')
def export_excel():
    """API endpoint to export data to Excel"""
    # Get filter parameters
    status_filter = request.args.get('status', 'OK')
    search_term = request.args.get('search')
    log_file = request.args.get('log_file')
    
    # Get filtered data
    data = log_parser.get_all_data(status_filter, search_term, log_file)
    
    # Create Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Transmission Log Data"
    
    # Define headers
    headers = [
        'ID Scan', 'Nomor Container', 'Jam Scan', 'Scan Time', 
        'Overall Time', 'Jam Update', 'Selisih Waktu', 
        'Jumlah Gambar', 'Status'
    ]
    
    # Style for headers
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", 
                             fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    # Add headers
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
    
    # Add data rows
    for row, entry in enumerate(data, 2):
        ws.cell(row=row, column=1, value=entry['id_scan'])
        ws.cell(row=row, column=2, value=entry['container_no'])
        ws.cell(row=row, column=3, value=entry['scan_time'])
        ws.cell(row=row, column=4, value=entry['scan_duration'])
        ws.cell(row=row, column=5, value=entry['overall_time'])
        ws.cell(row=row, column=6, value=entry['update_time'])
        ws.cell(row=row, column=7, value=entry['time_difference'])
        ws.cell(row=row, column=8, value=entry['image_count'])
        ws.cell(row=row, column=9, value=entry['status'])
    
    # Auto-adjust column widths
    for col in range(1, len(headers) + 1):
        column_letter = get_column_letter(col)
        max_length = 0
        
        for row in range(1, len(data) + 2):
            cell_value = ws[f"{column_letter}{row}"].value
            if cell_value:
                max_length = max(max_length, len(str(cell_value)))
        
        ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    wb.save(temp_file.name)
    temp_file.close()
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transmission_log_{status_filter}_{timestamp}.xlsx"
    
    return send_file(
        temp_file.name,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/api/settings')
def get_settings():
    """API endpoint to get current settings"""
    return jsonify(app_settings)


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """API endpoint to update settings"""
    global app_settings, log_parser
    
    try:
        new_settings = request.get_json()
        
        # Validate logs directory
        if 'logs_directory' in new_settings:
            logs_dir = new_settings['logs_directory']
            if not os.path.exists(logs_dir):
                return jsonify({'error': 'Logs directory does not exist'}), 400
            
            # Update log parser with new directory
            log_parser = LogParser(logs_dir)
        
        # Update settings
        app_settings.update(new_settings)
        
        # Save to file
        if save_settings(app_settings):
            return jsonify({'message': 'Settings updated successfully'})
        else:
            return jsonify({'error': 'Failed to save settings'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/validate-directory')
def validate_directory():
    """API endpoint to validate if a directory exists and contains log files"""
    directory = request.args.get('directory', '')
    
    if not directory:
        return jsonify({'valid': False, 'message': 'Directory path is required'})
    
    if not os.path.exists(directory):
        return jsonify({'valid': False, 'message': 'Directory does not exist'})
    
    if not os.path.isdir(directory):
        return jsonify({'valid': False, 'message': 'Path is not a directory'})
    
    # Check for log files
    pattern = os.path.join(directory, "Transmission.log*")
    log_files = glob.glob(pattern)
    
    if not log_files:
        return jsonify({
            'valid': False, 
            'message': 'No Transmission log files found in this directory'
        })
    
    return jsonify({
        'valid': True, 
        'message': f'Found {len(log_files)} log file(s)',
        'log_files': [os.path.basename(f) for f in log_files]
    })


@app.route('/shutdown')
def shutdown():
    """Shutdown endpoint for graceful server shutdown"""
    import threading
    import time
    
    def shutdown_server():
        time.sleep(1)
        import os
        import signal
        os.kill(os.getpid(), signal.SIGTERM)
    
    threading.Thread(target=shutdown_server).start()
    return 'Server shutting down...', 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)