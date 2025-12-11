"""Import DSNY tonnage data from CSV with support for uncollected tonnage."""
import csv
from database import Database
from models.sanitation import CollectionEvent
from datetime import datetime
import sys
import os

def import_tonnage_csv(csv_path):
    """Import DSNY tonnage data from CSV file.
    
    Expected columns:
    - Month/Date
    - Borough
    - CommunityDistrict (optional)
    - Collected tonnage fields (refusetonscollected, papertonscollected, etc.)
    - Uncollected tonnage fields (refusetonsnotcollected, papertonsnotcollected, etc.)
    - Or: total fields and collected fields (uncollected = total - collected)
    """
    try:
        db = Database.get_db()
        
        print(f"Reading tonnage CSV: {csv_path}")
        
        collections = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            print(f"CSV columns: {reader.fieldnames}")
            
            for idx, row in enumerate(reader):
                # Parse month/date
                collection_date = None
                for date_col in ['month', 'date', 'collection_date', 'period', 'month_year', 'Month', 'Date']:
                    if date_col in row and row[date_col]:
                        try:
                            date_str = str(row[date_col]).strip()
                            # Handle "2025 / 10" format
                            if ' / ' in date_str:
                                year, month = date_str.split(' / ')
                                collection_date = datetime(int(year), int(month), 1)
                            # Handle "2025-10" format
                            elif len(date_str) == 7 and '-' in date_str:
                                collection_date = datetime.strptime(date_str + '-01', '%Y-%m-%d')
                            # Handle "10/2025" format
                            elif '/' in date_str:
                                parts = date_str.split('/')
                                if len(parts) == 2:
                                    collection_date = datetime.strptime(f"{parts[1]}-{parts[0]}-01", '%Y-%m-%d')
                            else:
                                collection_date = datetime.strptime(date_str, '%Y-%m-%d')
                            break
                        except:
                            continue
                
                if not collection_date:
                    collection_date = datetime.utcnow()
                
                # Get borough
                borough = None
                for borough_col in ['borough', 'boro', 'Borough', 'Boro']:
                    if borough_col in row and row[borough_col]:
                        borough = str(row[borough_col]).strip()
                        break
                
                if not borough:
                    continue
                
                # Get zone_id
                zone_id = f"{borough[:3].upper()}-AGG"
                existing_zone = db.zones.find_one({'borough': borough})
                if existing_zone:
                    zone_id = existing_zone['zone_id']
                
                # Get collected tonnage
                collected_tonnage = 0
                collected_fields = [
                    'refusetonscollected', 'papertonscollected', 'mgptonscollected',
                    'resorganicstons', 'schoolorganictons', 'leavestonscollected',
                    'otherorganicstons', 'RefuseTonsCollected', 'PaperTonsCollected'
                ]
                for field in collected_fields:
                    if field in row and row[field]:
                        try:
                            collected_tonnage += float(str(row[field]).replace(',', ''))
                        except:
                            pass
                
                # Get uncollected tonnage - check for various field name patterns
                uncollected_tonnage = 0
                uncollected_field_patterns = [
                    'notcollected', 'uncollected', 'missed', 'not_collected', 
                    'un_collected', 'NotCollected', 'Uncollected'
                ]
                
                for field_name, field_value in row.items():
                    field_lower = field_name.lower()
                    if any(pattern in field_lower for pattern in uncollected_field_patterns):
                        if field_value:
                            try:
                                uncollected_tonnage += float(str(field_value).replace(',', ''))
                            except:
                                pass
                
                # Check for total vs collected calculation
                if uncollected_tonnage == 0:
                    total_tonnage = 0
                    for field_name, field_value in row.items():
                        field_lower = field_name.lower()
                        if 'total' in field_lower and 'ton' in field_lower and 'collected' not in field_lower:
                            try:
                                total_tonnage = float(str(field_value).replace(',', ''))
                                break
                            except:
                                pass
                    
                    if total_tonnage > 0 and collected_tonnage > 0:
                        uncollected_tonnage = max(0, total_tonnage - collected_tonnage)
                
                # Create collected collection event
                if collected_tonnage > 0:
                    waste_type = 'residential'
                    if 'paper' in str(row).lower():
                        waste_type = 'recycling'
                    elif 'organic' in str(row).lower():
                        waste_type = 'organic'
                    
                    collection = CollectionEvent.create_event(
                        route_id=f"RT-CSV-{collection_date.strftime('%Y-%m')}-COLLECTED-{idx}",
                        zone_id=zone_id,
                        collection_date=collection_date,
                        waste_type=waste_type,
                        tonnage=round(collected_tonnage, 2),
                        volume_cubic_yards=round(collected_tonnage * 2.0, 2),
                        collection_time_start=collection_date,
                        collection_time_end=collection_date,
                        status='completed',
                        notes=f"CSV import - {borough} - Collected"
                    )
                    collection['borough'] = borough
                    collection['_data_source'] = 'CSV Import'
                    collections.append(collection)
                
                # Create uncollected collection event
                if uncollected_tonnage > 0:
                    waste_type = 'residential'
                    if 'paper' in str(row).lower():
                        waste_type = 'recycling'
                    elif 'organic' in str(row).lower():
                        waste_type = 'organic'
                    
                    uncollected = CollectionEvent.create_event(
                        route_id=f"RT-CSV-{collection_date.strftime('%Y-%m')}-UNCOLLECTED-{idx}",
                        zone_id=zone_id,
                        collection_date=collection_date,
                        waste_type=waste_type,
                        tonnage=round(uncollected_tonnage, 2),
                        volume_cubic_yards=round(uncollected_tonnage * 2.0, 2),
                        collection_time_start=collection_date,
                        collection_time_end=collection_date,
                        status='missed',
                        notes=f"CSV import - {borough} - Uncollected"
                    )
                    uncollected['borough'] = borough
                    uncollected['_data_source'] = 'CSV Import'
                    collections.append(uncollected)
        
        print(f"\nPrepared {len(collections)} collection events")
        print(f"  Collected: {len([c for c in collections if c['status'] == 'completed'])}")
        print(f"  Uncollected: {len([c for c in collections if c['status'] == 'missed'])}")
        
        # Insert into database
        inserted = 0
        for coll in collections:
            result = db.collections.replace_one(
                {
                    'route_id': coll['route_id'],
                    'zone_id': coll['zone_id'],
                    'collection_date': coll['collection_date']
                },
                coll,
                upsert=True
            )
            if result.upserted_id or result.modified_count > 0:
                inserted += 1
        
        print(f"✅ Inserted {inserted} collection events")
        return inserted
        
    except Exception as e:
        print(f"❌ Error importing CSV: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_tonnage_csv.py <csv_file_path>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)
    
    import_tonnage_csv(csv_path)

