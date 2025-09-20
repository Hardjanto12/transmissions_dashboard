#!/usr/bin/env python3
"""
Demo script to show sample data structure
"""

import json
from app import LogParser

def show_sample_data():
    """Display sample data from the logs"""
    print("=" * 60)
    print("📊 Transmission Dashboard - Sample Data")
    print("=" * 60)
    print()
    
    # Initialize parser
    parser = LogParser()
    
    # Get sample data
    data = parser.get_all_data()
    
    if not data:
        print("❌ No data found in log files")
        print("Make sure you have log files in the 'logs/' directory")
        return
    
    print(f"📈 Found {len(data)} total records")
    print()
    
    # Show first few records
    print("🔍 Sample Records:")
    print("-" * 60)
    
    for i, record in enumerate(data[:3], 1):
        print(f"Record {i}:")
        print(f"  ID Scan: {record['id_scan']}")
        print(f"  Container: {record['container_no']}")
        print(f"  Scan Time: {record['scan_time']}")
        print(f"  Status: {record['status']}")
        print(f"  Images: {record['image_count']}")
        print(f"  Duration: {record['scan_duration']}")
        print(f"  Time Diff: {record['time_difference']}")
        print()
    
    # Show statistics
    print("📊 Statistics:")
    print("-" * 60)
    
    ok_count = len([r for r in data if r['status'] == 'OK'])
    nok_count = len([r for r in data if r['status'] == 'NOK'])
    success_rate = (ok_count / len(data) * 100) if data else 0
    
    print(f"Total Scans: {len(data)}")
    print(f"OK Scans: {ok_count}")
    print(f"NOK Scans: {nok_count}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    # Show available log files
    log_files = parser.get_log_files()
    print("📁 Available Log Files:")
    print("-" * 60)
    for file_path in log_files:
        filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
        print(f"  • {filename}")
    print()
    
    print("✅ Sample data loaded successfully!")
    print("🚀 Run 'python run.py' to start the dashboard")

if __name__ == '__main__':
    show_sample_data()
