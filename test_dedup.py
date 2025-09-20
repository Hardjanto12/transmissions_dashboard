#!/usr/bin/env python3
"""
Test script to verify deduplication is working
"""

from app import LogParser

def test_deduplication():
    """Test deduplication functionality"""
    print("=" * 60)
    print("🔍 Testing Deduplication")
    print("=" * 60)
    print()
    
    # Initialize parser
    parser = LogParser()
    
    # Get all data
    all_data = parser.get_all_data()
    
    print(f"📊 Total unique records: {len(all_data)}")
    print()
    
    # Check for duplicates
    id_scans = [entry['id_scan'] for entry in all_data if entry['id_scan']]
    unique_ids = set(id_scans)
    
    print(f"🔢 Total ID scans: {len(id_scans)}")
    print(f"🔢 Unique ID scans: {len(unique_ids)}")
    
    if len(id_scans) != len(unique_ids):
        print("❌ Duplicates found!")
        duplicates = []
        seen = set()
        for id_scan in id_scans:
            if id_scan in seen:
                duplicates.append(id_scan)
            else:
                seen.add(id_scan)
        print(f"Duplicate IDs: {duplicates[:10]}")  # Show first 10 duplicates
    else:
        print("✅ No duplicates found!")
    
    print()
    
    # Show sample data
    print("📋 Sample Records:")
    print("-" * 60)
    for i, record in enumerate(all_data[:5], 1):
        print(f"Record {i}:")
        print(f"  ID Scan: {record['id_scan']}")
        print(f"  Status: {record['status']}")
        print(f"  Jam Scan: {record['scan_time']}")
        print()
    
    # Test statistics
    ok_count = len([d for d in all_data if d['status'] == 'OK'])
    nok_count = len([d for d in all_data if d['status'] == 'NOK'])
    success_rate = (ok_count / len(all_data) * 100) if all_data else 0
    
    print("📊 Statistics (after deduplication):")
    print("-" * 60)
    print(f"Total Scans: {len(all_data)}")
    print(f"OK Scans: {ok_count}")
    print(f"NOK Scans: {nok_count}")
    print(f"Success Rate: {success_rate:.1f}%")

if __name__ == '__main__':
    test_deduplication()
