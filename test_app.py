#!/usr/bin/env python3
"""
Simple test script for the Transmission Dashboard
"""

import requests
import json
import time

def test_api_endpoints():
    """Test the API endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing Transmission Dashboard API...")
    print("=" * 50)
    
    # Test log files endpoint
    try:
        response = requests.get(f"{base_url}/api/log-files")
        if response.status_code == 200:
            log_files = response.json()
            print(f"✓ Log files endpoint: Found {len(log_files)} log files")
            for file in log_files[:3]:  # Show first 3 files
                print(f"  - {file}")
        else:
            print(f"✗ Log files endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Log files endpoint error: {e}")
    
    print()
    
    # Test stats endpoint
    try:
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Stats endpoint:")
            print(f"  - Total scans: {stats['total_scans']}")
            print(f"  - OK scans: {stats['ok_scans']}")
            print(f"  - NOK scans: {stats['nok_scans']}")
            print(f"  - Success rate: {stats['success_rate']}%")
            print(f"  - Recent scans: {stats['recent_scans']}")
        else:
            print(f"✗ Stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Stats endpoint error: {e}")
    
    print()
    
    # Test data endpoint
    try:
        response = requests.get(f"{base_url}/api/data")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Data endpoint: Found {data['total']} records")
            if data['data']:
                print("  Sample record:")
                sample = data['data'][0]
                print(f"    - ID Scan: {sample['id_scan']}")
                print(f"    - Container: {sample['container_no']}")
                print(f"    - Status: {sample['status']}")
                print(f"    - Scan Time: {sample['scan_time']}")
        else:
            print(f"✗ Data endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Data endpoint error: {e}")
    
    print()
    
    # Test filtered data endpoint
    try:
        response = requests.get(f"{base_url}/api/data?status=OK")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Filtered data endpoint (OK only): {data['total']} records")
        else:
            print(f"✗ Filtered data endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Filtered data endpoint error: {e}")
    
    print()
    print("=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    print("Make sure the Flask app is running on http://localhost:5000")
    print("You can start it with: python app.py")
    print()
    
    # Wait a moment for user to read
    time.sleep(2)
    
    test_api_endpoints()
