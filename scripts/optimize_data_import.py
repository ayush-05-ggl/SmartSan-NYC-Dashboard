"""Smart data import - filters and aggregates data to fit 512MB limit."""
import csv
from database import Database
from models.sanitation import CollectionEvent, ServiceRequest
from datetime import datetime, timedelta
import sys
import os

def import_optimized_tonnage(csv_path, months_back=12, sample_rate=0.1):
    """Import DSNY tonnage data with smart filtering.
    
    Args:
        csv_path: Path to CSV file
        months_back: Only import last N months (default: 12)
        sample_rate: Import only X% of data (0.1 = 10%, default: 10%)
    """
    try:
        db = Database.get_db()
        
        print(f"Reading DSNY tonnage data: {csv_path}")
        print(f"Filtering: Last {months_back} months, {sample_rate*100}% sample")
        
        cutoff_date = datetime.utcnow() - timedelta(days=months_back * 30)
        
        collections = []
        total_rows = 0
        imported_rows = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for idx, row in enumerate(reader):
                total_rows += 1
                
                # Sample rate - skip rows randomly
                import random
                if random.random() > sample_rate:
                    continue
                
                # Parse date
                collection_date = None
                for date_col in ['month', 'date', 'collection_date', 'period', 'month_year']:
                    if date_col in row and row[date_col]:
                        try:
                            date_str = str(row[date_col]).strip()
                            if len(date_str) == 7 and '-' in date_str:
                                collection_date = datetime.strptime(date_str + '-01', '%Y-%m-%d')
                            elif '/' in date_str:
                                parts = date_str.split('/')
                                if len(parts) == 2:
                                    collection_date = datetime.strptime(f"{parts[1]}-{parts[0]}-01", '%Y-%m-%d')
                            else:
                                collection_date = datetime.strptime(date_str, '%Y-%m-%d')
                            break
                        except:
                            continue
                
                if not collection_date or collection_date < cutoff_date:
                    continue  # Skip old data
                
                # Get tonnage
                tonnage = 0
                for ton_col in ['tonnage', 'tons', 'total_tons', 'weight_tons']:
                    if ton_col in row and row[ton_col]:
                        try:
                            tonnage = float(str(row[ton_col]).replace(',', ''))
                            break
                        except:
                            continue
                
                if tonnage == 0:
                    continue
                
                # Aggregate by month/borough/type to reduce records
                # Instead of daily records, create monthly aggregates
                month_key = collection_date.strftime('%Y-%m')
                
                # Waste type
                waste_type = 'residential'
                for type_col in ['waste_type', 'type', 'category']:
                    if type_col in row and row[type_col]:
                        type_str = str(row[type_col]).lower()
                        if 'recycling' in type_str:
                            waste_type = 'recycling'
                        elif 'organic' in type_str:
                            waste_type = 'organic'
                        elif 'commercial' in type_str:
                            waste_type = 'commercial'
                        break
                
                # Zone
                zone_id = None
                borough = None
                for zone_col in ['community_district', 'district', 'zone_id']:
                    if zone_col in row and row[zone_col]:
                        zone_id = str(row[zone_col]).strip()
                        break
                
                for borough_col in ['borough', 'boro']:
                    if borough_col in row and row[borough_col]:
                        borough = str(row[borough_col]).strip()
                        break
                
                if not zone_id and borough:
                    existing_zone = db.zones.find_one({'borough': borough})
                    if existing_zone:
                        zone_id = existing_zone['zone_id']
                    else:
                        borough_abbr = borough[:3].upper() if len(borough) >= 3 else borough.upper()
                        zone_id = f"{borough_abbr}-AGG"
                
                if not zone_id:
                    zone_id = 'UNKNOWN'
                
                # Create aggregated collection (monthly instead of daily)
                collection = CollectionEvent.create_event(
                    route_id=f"RT-AGG-{month_key}",
                    zone_id=zone_id,
                    collection_date=collection_date.replace(day=1),  # First of month
                    waste_type=waste_type,
                    tonnage=round(tonnage, 2),
                    volume_cubic_yards=round(tonnage * 2.0, 2),
                    collection_time_start=collection_date.replace(day=1),
                    collection_time_end=collection_date.replace(day=1),
                    status='completed',
                    notes=f"Aggregated monthly data - {borough or 'Unknown'}"
                )
                collections.append(collection)
                imported_rows += 1
                
                # Insert in batches
                if len(collections) >= 500:
                    db.collections.insert_many(collections)
                    print(f"  Inserted batch: {len(collections)} records (Total: {imported_rows}/{total_rows})")
                    collections = []
        
        # Insert remaining
        if collections:
            db.collections.insert_many(collections)
            print(f"  Inserted final batch: {len(collections)} records")
        
        print(f"✅ Imported {imported_rows} records from {total_rows} total ({(imported_rows/total_rows*100):.1f}%)")
        return imported_rows
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

def import_optimized_311(csv_path, months_back=6, limit=5000):
    """Import 311 data with filtering.
    
    Args:
        csv_path: Path to CSV file
        months_back: Only import last N months
        limit: Maximum number of records to import
    """
    try:
        db = Database.get_db()
        
        print(f"Reading 311 data: {csv_path}")
        print(f"Filtering: Last {months_back} months, max {limit} records")
        
        cutoff_date = datetime.utcnow() - timedelta(days=months_back * 30)
        
        requests = []
        total = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                total += 1
                
                if len(requests) >= limit:
                    break
                
                # Filter for DSNY
                agency = str(row.get('agency', '') or row.get('agency_name', '')).lower()
                if 'dsny' not in agency and 'sanitation' not in agency:
                    continue
                
                # Parse date
                reported_at = None
                for date_col in ['created_date', 'date', 'incident_date']:
                    if date_col in row and row[date_col]:
                        try:
                            reported_at = datetime.strptime(row[date_col][:19], '%Y-%m-%dT%H:%M:%S')
                            if reported_at < cutoff_date:
                                continue
                        except:
                            try:
                                reported_at = datetime.strptime(row[date_col][:10], '%Y-%m-%d')
                                if reported_at < cutoff_date:
                                    continue
                            except:
                                continue
                        break
                
                if not reported_at:
                    continue
                
                # Location
                location = {}
                if 'latitude' in row and 'longitude' in row:
                    try:
                        lat = float(row['latitude'])
                        lng = float(row['longitude'])
                        if -90 <= lat <= 90 and -180 <= lng <= 180:
                            location = {
                                'lat': lat,
                                'lng': lng,
                                'type': 'Point',
                                'coordinates': [lng, lat]  # GeoJSON format: [longitude, latitude]
                            }
                    except:
                        pass
                
                if 'incident_address' in row and row['incident_address']:
                    location['address'] = str(row['incident_address'])
                
                # Request type
                request_type = 'other'
                complaint = str(row.get('complaint_type', '')).lower()
                if 'missed' in complaint or 'collection' in complaint:
                    request_type = 'missed_pickup'
                elif 'overflow' in complaint:
                    request_type = 'overflow'
                elif 'dumping' in complaint or 'illegal' in complaint:
                    request_type = 'illegal_dumping'
                
                # Priority
                priority = 'normal'
                if 'urgent' in complaint or 'emergency' in complaint:
                    priority = 'urgent'
                elif 'high' in complaint:
                    priority = 'high'
                
                # Zone
                zone_id = 'UNKNOWN'
                if 'community_board' in row and row['community_board']:
                    zone_id = f"ZONE-{row['community_board']}"
                
                request = ServiceRequest.create_request(
                    request_id=f"SR-311-{row.get('unique_key', total)}",
                    zone_id=zone_id,
                    request_type=request_type,
                    description=str(row.get('descriptor', row.get('complaint_type', 'No description')))[:200],
                    location=location if location else {'lat': None, 'lng': None},
                    priority=priority,
                    status='open' if 'open' in str(row.get('status', '')).lower() else 'closed',
                    reported_at=reported_at
                )
                requests.append(request)
        
        print(f"Inserting {len(requests)} service requests...")
        if requests:
            db.requests.insert_many(requests)
        
        print(f"✅ Imported {len(requests)} requests from {total} total rows")
        return len(requests)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python optimize_data_import.py <csv_file> <type> [options]")
        print("\nTypes:")
        print("  tonnage  - Import DSNY tonnage data (optimized)")
        print("  311      - Import 311 requests (optimized)")
        print("\nExamples:")
        print("  python optimize_data_import.py dsny_tonnage.csv tonnage")
        print("  python optimize_data_import.py 311_requests.csv 311")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    import_type = sys.argv[2].lower()
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)
    
    Database.connect()
    
    try:
        if import_type == 'tonnage':
            import_optimized_tonnage(csv_path, months_back=12, sample_rate=0.1)
        elif import_type == '311':
            import_optimized_311(csv_path, months_back=6, limit=5000)
        else:
            print(f"❌ Unknown type: {import_type}")
            sys.exit(1)
        
        print("\n✅ Import completed!")
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        sys.exit(1)
    finally:
        Database.disconnect()

