#!/usr/bin/env python3
"""
Test script to verify NOK data parsing
"""

from app import LogParser

def test_nok_data():
    """Test NOK data parsing"""
    print("=" * 60)
    print("🔍 Testing NOK Data Parsing")
    print("=" * 60)
    print()
    
    # Initialize parser
    parser = LogParser()
    
    # Get all data
    all_data = parser.get_all_data()
    
    # Filter NOK data
    nok_data = [entry for entry in all_data if entry['status'] == 'NOK']
    
    print(f"📊 Total records: {len(all_data)}")
    print(f"❌ NOK records: {len(nok_data)}")
    print()
    
    if nok_data:
        print("🔍 NOK Records Sample:")
        print("-" * 60)
        
        for i, record in enumerate(nok_data[:5], 1):  # Show first 5 NOK records
            print(f"Record {i}:")
            print(f"  ID Scan: {record['id_scan']}")
            print(f"  Jam Scan: {record['scan_time']}")
            print(f"  Status: {record['status']}")
            print(f"  Container: {record['container_no']}")
            if 'error_description' in record:
                print(f"  Error: {record['error_description']}")
            print()
    else:
        print("❌ No NOK records found")
        print("This might be because all transmissions in the logs are successful")
        print()
        
        # Show sample of all data to verify parsing
        print("📋 Sample of all data:")
        print("-" * 60)
        for i, record in enumerate(all_data[:3], 1):
            print(f"Record {i}:")
            print(f"  ID Scan: {record['id_scan']}")
            print(f"  Status: {record['status']}")
            print(f"  Jam Scan: {record['scan_time']}")
            print()

if __name__ == '__main__':
    test_nok_data()
