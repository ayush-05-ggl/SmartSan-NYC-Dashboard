"""Import DSNY Monthly Tonnage Data from NYC Open Data."""
import csv
from database import Database
from models.sanitation import CollectionEvent
from datetime import datetime
import sys
import os

def import_dsny_tonnage(csv_path):
    """Import DSNY Monthly Tonnage Data.
    
    Expected columns (may vary):
    - Month, Borough, CommunityDistrict, WasteType, Tonnage
    - Or similar variations
    """
    try:
        db = Database.get_db()
        
        print(f"Reading DSNY tonnage data: {csv_path}")
        
        collections = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for idx, row in enumerate(reader):
                # Map common column name variations
                # Date/Month
                collection_date = None
                for date_col in ['month', 'date', 'collection_date', 'period', 'month_year']:
                    if date_col in row and row[date_col]:
                        try:
                            # Try various date formats
                            date_str = str(row[date_col]).strip()
                            # Common formats: "2024-01", "01/2024", "2024-01-01"
                            if len(date_str) == 7 and '-' in date_str:  # "2024-01"
                                collection_date = datetime.strptime(date_str + '-01', '%Y-%m-%d')
                            elif '/' in date_str:  # "01/2024"
                                parts = date_str.split('/')
                                if len(parts) == 2:
                                    collection_date = datetime.strptime(f"{parts[1]}-{parts[0]}-01", '%Y-%m-%d')
                            else:
                                collection_date = datetime.strptime(date_str, '%Y-%m-%d')
                            break
                        except:
                            continue
                
                if not collection_date:
                    collection_date = datetime.utcnow()  # Default to now if can't parse
                
                # Tonnage
                tonnage = 0
                for ton_col in ['tonnage', 'tons', 'total_tons', 'weight_tons', 'refuse_tons_collected']:
                    if ton_col in row and row[ton_col]:
                        try:
                            tonnage = float(str(row[ton_col]).replace(',', ''))
                            break
                        except:
                            continue
                
                if tonnage == 0:
                    continue  # Skip rows with no tonnage
                
                # Waste Type
                waste_type = 'residential'
                for type_col in ['waste_type', 'type', 'category', 'material']:
                    if type_col in row and row[type_col]:
                        type_str = str(row[type_col]).lower()
                        if 'recycling' in type_str or 'recycl' in type_str:
                            waste_type = 'recycling'
                        elif 'organic' in type_str or 'compost' in type_str or 'food' in type_str:
                            waste_type = 'organic'
                        elif 'commercial' in type_str:
                            waste_type = 'commercial'
                        elif 'residential' in type_str or 'refuse' in type_str:
                            waste_type = 'residential'
                        break
                
                # Zone/District
                zone_id = None
                borough = None
                for zone_col in ['community_district', 'district', 'zone_id', 'zone', 'cd']:
                    if zone_col in row and row[zone_col]:
                        zone_id = str(row[zone_col]).strip()
                        break
                
                for borough_col in ['borough', 'boro']:
                    if borough_col in row and row[borough_col]:
                        borough = str(row[borough_col]).strip()
                        break
                
                # Create zone_id from borough + district if needed
                if not zone_id and borough:
                    # Try to find matching zone in database
                    existing_zone = db.zones.find_one({'borough': borough})
                    if existing_zone:
                        zone_id = existing_zone['zone_id']
                    else:
                        # Create a zone_id from borough abbreviation
                        borough_abbr = borough[:3].upper() if len(borough) >= 3 else borough.upper()
                        if 'district' in row and row['district']:
                            zone_id = f"{borough_abbr}-{row['district']}"
                        else:
                            zone_id = f"{borough_abbr}-UNKNOWN"
                
                if not zone_id:
                    zone_id = 'UNKNOWN'
                
                # Create collection event
                collection = CollectionEvent.create_event(
                    route_id=f"RT-DSNY-{idx}",
                    zone_id=zone_id,
                    collection_date=collection_date,
                    waste_type=waste_type,
                    tonnage=round(tonnage, 2),
                    volume_cubic_yards=round(tonnage * 2.0, 2),  # Estimate: 1 ton ≈ 2 cubic yards
                    collection_time_start=collection_date,
                    collection_time_end=collection_date,
                    status='completed',
                    notes=f"Imported from DSNY Monthly Tonnage Data - {borough or 'Unknown'} - {waste_type}"
                )
                collections.append(collection)
        
        print(f"Prepared {len(collections)} collection events")
        print(f"Inserting into database...")
        
        # Insert in batches to avoid memory issues
        batch_size = 1000
        total_inserted = 0
        for i in range(0, len(collections), batch_size):
            batch = collections[i:i + batch_size]
            result = db.collections.insert_many(batch)
            total_inserted += len(result.inserted_ids)
            print(f"  Inserted batch {i//batch_size + 1}: {len(result.inserted_ids)} records")
        
        print(f"✅ Successfully inserted {total_inserted} collection events")
        return total_inserted
        
    except Exception as e:
        print(f"❌ Error importing DSNY tonnage data: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_dsny_tonnage.py <csv_file_path>")
        print("\nExample:")
        print("  python import_dsny_tonnage.py dsny_monthly_tonnage.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)
    
    print("Connecting to database...")
    Database.connect()
    
    try:
        import_dsny_tonnage(csv_path)
        print("\n✅ Import completed successfully!")
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        sys.exit(1)
    finally:
        Database.disconnect()

