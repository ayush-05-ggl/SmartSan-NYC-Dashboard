#!/usr/bin/env python3
"""Analyze complaint types in the database to see what we're missing."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import Database
from collections import Counter

def analyze_complaint_types():
    """Show what complaint types are actually in the database."""
    db = Database.get_db()
    
    # Get all complaint types and their counts
    pipeline = [
        {
            '$group': {
                '_id': {
                    'complaint_type': '$complaint_type',
                    'request_type': '$request_type',
                    'descriptor': '$descriptor'
                },
                'count': {'$sum': 1}
            }
        },
        {'$sort': {'count': -1}},
        {'$limit': 100}
    ]
    
    results = list(db.requests.aggregate(pipeline))
    
    print("=" * 80)
    print("COMPLAINT TYPE ANALYSIS")
    print("=" * 80)
    print(f"\nTotal unique complaint type combinations: {len(results)}\n")
    
    # Group by request_type
    by_request_type = {}
    for result in results:
        req_type = result['_id'].get('request_type', 'unknown')
        if req_type not in by_request_type:
            by_request_type[req_type] = []
        by_request_type[req_type].append({
            'complaint_type': result['_id'].get('complaint_type', 'N/A'),
            'descriptor': result['_id'].get('descriptor', 'N/A')[:50],
            'count': result['count']
        })
    
    # Show breakdown by request_type
    print("\nBREAKDOWN BY REQUEST_TYPE:")
    print("-" * 80)
    for req_type, items in sorted(by_request_type.items(), key=lambda x: sum(i['count'] for i in x[1]), reverse=True):
        total = sum(i['count'] for i in items)
        print(f"\n{req_type.upper()}: {total} total")
        print(f"  Top 5 complaint types:")
        for item in items[:5]:
            print(f"    - {item['complaint_type']} ({item['count']} records)")
            if item['descriptor'] != 'N/A':
                print(f"      Descriptor: {item['descriptor']}")
    
    # Show "other" requests in detail
    print("\n" + "=" * 80)
    print("DETAILED VIEW: 'other' REQUEST TYPES")
    print("=" * 80)
    other_items = by_request_type.get('other', [])
    if other_items:
        print(f"\nFound {len(other_items)} unique 'other' complaint types:")
        for item in other_items[:20]:  # Show top 20
            print(f"\n  Complaint Type: {item['complaint_type']}")
            print(f"  Descriptor: {item['descriptor']}")
            print(f"  Count: {item['count']}")
    else:
        print("\nNo 'other' requests found!")
    
    # Show most common complaint_type values overall
    print("\n" + "=" * 80)
    print("MOST COMMON COMPLAINT_TYPES (regardless of mapping)")
    print("=" * 80)
    complaint_type_pipeline = [
        {
            '$group': {
                '_id': '$complaint_type',
                'count': {'$sum': 1}
            }
        },
        {'$sort': {'count': -1}},
        {'$limit': 20}
    ]
    
    complaint_types = list(db.requests.aggregate(complaint_type_pipeline))
    for ct in complaint_types:
        print(f"  {ct['_id']}: {ct['count']} records")

if __name__ == '__main__':
    analyze_complaint_types()

