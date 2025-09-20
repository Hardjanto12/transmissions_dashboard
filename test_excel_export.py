#!/usr/bin/env python3
"""
Test script to verify Excel export functionality
"""

import requests
import os

def test_excel_export():
    """Test Excel export functionality"""
    print("=" * 60)
    print("📊 Testing Excel Export Functionality")
    print("=" * 60)
    print()
    
    base_url = "http://localhost:5000"
    
    # Test export endpoint
    try:
        print("🔍 Testing Excel export endpoint...")
        response = requests.get(f"{base_url}/api/export/excel?status=OK")
        
        if response.status_code == 200:
            print("✅ Excel export endpoint working!")
            print(f"📁 Content-Type: {response.headers.get('Content-Type')}")
            print(f"📁 Content-Disposition: {response.headers.get('Content-Disposition')}")
            print(f"📊 File size: {len(response.content)} bytes")
            
            # Save the file for inspection
            filename = "test_export.xlsx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"💾 Test file saved as: {filename}")
            
            # Check if file exists and has content
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                print("✅ Excel file created successfully!")
                print(f"📊 File size: {os.path.getsize(filename)} bytes")
            else:
                print("❌ Excel file creation failed!")
                
        else:
            print(f"❌ Excel export failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing Excel export: {e}")
    
    print()
    
    # Test with different filters
    try:
        print("🔍 Testing Excel export with filters...")
        
        # Test with search filter
        response = requests.get(f"{base_url}/api/export/excel?status=OK&search=62001")
        if response.status_code == 200:
            print("✅ Excel export with search filter working!")
        else:
            print(f"❌ Excel export with search filter failed: {response.status_code}")
            
        # Test with log file filter
        response = requests.get(f"{base_url}/api/export/excel?status=OK&log_file=Transmission.log")
        if response.status_code == 200:
            print("✅ Excel export with log file filter working!")
        else:
            print(f"❌ Excel export with log file filter failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing filtered Excel export: {e}")
    
    print()
    print("=" * 60)
    print("Test completed!")

if __name__ == '__main__':
    print("Make sure the Flask app is running on http://localhost:5000")
    print()
    test_excel_export()
