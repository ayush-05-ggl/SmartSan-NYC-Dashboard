"""Utility script to import external datasets into MongoDB."""
import json
import csv
import pandas as pd
from database import Database
from datetime import datetime
from models.sanitation import (
    SanitationZone, CollectionEvent, ServiceRequest, PerformanceMetric
)
import sys
import os

def import_csv_to_collections(csv_path, collection_name='collections'):
    """Import CSV file to a MongoDB collection."""
    try:
        db = Database.get_db()
        collection = db[collection_name]
        
        print(f"Reading CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')
        
        # Clean and prepare records
        cleaned_records = []
        for record in records:
            # Remove NaN values
            cleaned = {k: v for k, v in record.items() if pd.notna(v)}
            cleaned_records.append(cleaned)
        
        print(f"Inserting {len(cleaned_records)} records into {collection_name}...")
        result = collection.insert_many(cleaned_records)
        print(f"✅ Inserted {len(result.inserted_ids)} records")
        
        return result
        
    except Exception as e:
        print(f"❌ Error importing CSV: {e}")
        raise

def import_json_to_collections(json_path, collection_name='collections'):
    """Import JSON file to a MongoDB collection."""
    try:
        db = Database.get_db()
        collection = db[collection_name]
        
        print(f"Reading JSON: {json_path}")
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Handle both list and single object
        if isinstance(data, list):
            records = data
        else:
            records = [data]
        
        print(f"Inserting {len(records)} records into {collection_name}...")
        result = collection.insert_many(records)
        print(f"✅ Inserted {len(result.inserted_ids)} records")
        
        return result
        
    except Exception as e:
        print(f"❌ Error importing JSON: {e}")
        raise

def import_311_requests(csv_path):
    """Import NYC 311 service requests related to sanitation."""
    try:
        db = Database.get_db()
        
        print(f"Reading 311 data: {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Filter for DSNY/Sanitation related requests
        if 'agency' in df.columns:
            df = df[df['agency'].str.contains('DSNY|Sanitation', case=False, na=False)]
        elif 'agency_name' in df.columns:
            df = df[df['agency_name'].str.contains('DSNY|Sanitation', case=False, na=False)]
        
        print(f"Found {len(df)} sanitation-related requests")
        
        # Map 311 fields to our schema
        requests = []
        for idx, row in df.iterrows():
            # Extract location
            location = {}
            if 'latitude' in row and 'longitude' in row:
                location = {
                    'lat': float(row['latitude']) if pd.notna(row['latitude']) else None,
                    'lng': float(row['longitude']) if pd.notna(row['longitude']) else None
                }
            if 'incident_address' in row and pd.notna(row['incident_address']):
                location['address'] = str(row['incident_address'])
            
            # Parse dates
            reported_at = None
            if 'created_date' in row and pd.notna(row['created_date']):
                try:
                    reported_at = pd.to_datetime(row['created_date']).to_pydatetime()
                except:
                    pass
            
            # Map complaint type to our request_type
            request_type = 'other'
            complaint_type = str(row.get('complaint_type', '')).lower()
            if 'missed' in complaint_type or 'collection' in complaint_type:
                request_type = 'missed_pickup'
            elif 'overflow' in complaint_type or 'overflowing' in complaint_type:
                request_type = 'overflow'
            elif 'dumping' in complaint_type or 'illegal' in complaint_type:
                request_type = 'illegal_dumping'
            elif 'container' in complaint_type or 'damaged' in complaint_type:
                request_type = 'damaged_container'
            
            # Map status
            status = 'open'
            if 'status' in row:
                status_str = str(row['status']).lower()
                if 'closed' in status_str or 'resolved' in status_str:
                    status = 'closed'
                elif 'in progress' in status_str:
                    status = 'in_progress'
            
            # Priority (default to normal, can be enhanced)
            priority = 'normal'
            if 'priority' in row:
                priority_str = str(row['priority']).lower()
                if 'urgent' in priority_str:
                    priority = 'urgent'
                elif 'high' in priority_str:
                    priority = 'high'
            
            # Get zone_id if available (may need mapping)
            zone_id = None
            if 'community_board' in row:
                # Map community board to zone if possible
                zone_id = f"ZONE-{row['community_board']}"
            
            request = ServiceRequest.create_request(
                request_id=f"SR-311-{row.get('unique_key', idx)}",
                zone_id=zone_id or 'UNKNOWN',
                request_type=request_type,
                description=str(row.get('descriptor', row.get('complaint_type', 'No description'))),
                location=location if location else {'lat': None, 'lng': None},
                priority=priority,
                status=status,
                reported_at=reported_at or datetime.utcnow()
            )
            requests.append(request)
        
        print(f"Inserting {len(requests)} service requests...")
        result = db.requests.insert_many(requests)
        print(f"✅ Inserted {len(result.inserted_ids)} service requests")
        
        return result
        
    except Exception as e:
        print(f"❌ Error importing 311 data: {e}")
        raise

def import_tonnage_data(csv_path):
    """Import tonnage/collection data."""
    try:
        db = Database.get_db()
        
        print(f"Reading tonnage data: {csv_path}")
        df = pd.read_csv(csv_path)
        
        collections = []
        for idx, row in df.iterrows():
            # Parse date
            collection_date = datetime.utcnow()
            if 'date' in row:
                try:
                    collection_date = pd.to_datetime(row['date']).to_pydatetime()
                except:
                    pass
            
            # Get tonnage
            tonnage = 0
            for col in ['tonnage', 'tons', 'weight', 'weight_tons']:
                if col in row and pd.notna(row[col]):
                    tonnage = float(row[col])
                    break
            
            # Get waste type
            waste_type = 'residential'
            for col in ['waste_type', 'type', 'category']:
                if col in row:
                    type_str = str(row[col]).lower()
                    if 'recycling' in type_str:
                        waste_type = 'recycling'
                    elif 'organic' in type_str or 'compost' in type_str:
                        waste_type = 'organic'
                    elif 'commercial' in type_str:
                        waste_type = 'commercial'
            
            # Get zone/district
            zone_id = None
            for col in ['zone_id', 'district', 'zone', 'district_id']:
                if col in row and pd.notna(row[col]):
                    zone_id = str(row[col])
                    break
            
            if not zone_id:
                zone_id = 'UNKNOWN'
            
            collection = CollectionEvent.create_event(
                route_id=f"RT-IMPORT-{idx}",
                zone_id=zone_id,
                collection_date=collection_date,
                waste_type=waste_type,
                tonnage=tonnage,
                volume_cubic_yards=tonnage * 2.0,  # Estimate
                collection_time_start=collection_date,
                collection_time_end=collection_date,
                status='completed',
                notes=f"Imported from dataset"
            )
            collections.append(collection)
        
        print(f"Inserting {len(collections)} collection events...")
        result = db.collections.insert_many(collections)
        print(f"✅ Inserted {len(result.inserted_ids)} collection events")
        
        return result
        
    except Exception as e:
        print(f"❌ Error importing tonnage data: {e}")
        raise

def main():
    """Main function to handle command-line imports."""
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python import_data.py <file_path> <collection_name>")
        print("  python import_data.py <file_path> 311  # For 311 service requests")
        print("  python import_data.py <file_path> tonnage  # For tonnage data")
        print("\nExamples:")
        print("  python import_data.py data.csv collections")
        print("  python import_data.py data.json zones")
        print("  python import_data.py 311_requests.csv 311")
        sys.exit(1)
    
    file_path = sys.argv[1]
    collection_type = sys.argv[2].lower()
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    # Connect to database
    print("Connecting to database...")
    Database.connect()
    
    try:
        if collection_type == '311':
            import_311_requests(file_path)
        elif collection_type == 'tonnage':
            import_tonnage_data(file_path)
        else:
            # Generic import
            if file_path.endswith('.csv'):
                import_csv_to_collections(file_path, collection_type)
            elif file_path.endswith('.json'):
                import_json_to_collections(file_path, collection_type)
            else:
                print("❌ Unsupported file format. Use .csv or .json")
                sys.exit(1)
        
        print("\n✅ Import completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        sys.exit(1)
    finally:
        Database.disconnect()

if __name__ == '__main__':
    main()

