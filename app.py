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
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
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
                            
                            # Handle failed responses (resultCode: false)
                            elif (response_data.get('resultCode') == False and 
                                  response_data.get('resultData') == '-'):
                                
                                # Extract container number from response description if available
                                container_no = "Failed!"
                                desc = response_data.get('resultDesc', '')
                                if 'Container' in desc:
                                    # Try to extract container number from description
                                    container_match = re.search(r'Container[^:]*:?\s*([A-Z0-9]+)', desc)
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
                                
                        except (json.JSONDecodeError, KeyError):
                            continue
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")
        
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

# Initialize log parser
log_parser = LogParser()


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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
