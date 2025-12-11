"""API route for refreshing DSNY tonnage data."""
from fastapi import APIRouter, HTTPException
from services.nyc_open_data import NYCOpenDataClient
from database import Database
from models.sanitation import CollectionEvent
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/refresh-tonnage")
async def refresh_tonnage_data():
    """Refresh DSNY tonnage data from NYC Open Data API - LIVE DATA.
    
    Pulls latest DSNY monthly tonnage data and updates database.
    """
    try:
        client = NYCOpenDataClient()
        db = Database.get_db()
        
        # Fetch from API
        logger.info("Fetching DSNY tonnage from NYC Open Data API...")
        api_data = client.get_dsny_tonnage(months_back=12, limit=1000)
        
        if not api_data:
            return {
                'status': 'success',
                'message': 'No new data available',
                'records_fetched': 0
            }
        
        # Convert to our schema
        collections = []
        for idx, record in enumerate(api_data):
            # Parse month (format: "2025 / 10")
            month_str = record.get('month', '')
            collection_date = None
            try:
                if ' / ' in month_str:
                    year, month = month_str.split(' / ')
                    collection_date = datetime(int(year), int(month), 1)
                else:
                    collection_date = datetime.utcnow()
            except:
                collection_date = datetime.utcnow()
            
            # Get collected tonnage
            collected_tonnage = 0
            collected_fields = ['refusetonscollected', 'papertonscollected', 'mgptonscollected', 
                               'resorganicstons', 'schoolorganictons', 'leavestonscollected', 
                               'otherorganicstons']
            for ton_field in collected_fields:
                if ton_field in record and record[ton_field]:
                    try:
                        collected_tonnage += float(str(record[ton_field]).replace(',', ''))
                    except:
                        pass
            
            # Get uncollected tonnage - check for various field name patterns
            uncollected_tonnage = 0
            uncollected_fields = []
            for field_name, field_value in record.items():
                field_lower = field_name.lower()
                # Look for fields indicating uncollected/missed/not collected
                if any(keyword in field_lower for keyword in ['notcollected', 'uncollected', 'missed', 'not_collected', 'un_collected']):
                    uncollected_fields.append(field_name)
                    if field_value:
                        try:
                            uncollected_tonnage += float(str(field_value).replace(',', ''))
                        except:
                            pass
            
            # If no explicit uncollected field, check if there's a total vs collected difference
            # Some datasets have "total" and "collected" fields where uncollected = total - collected
            total_tonnage = 0
            for field_name, field_value in record.items():
                field_lower = field_name.lower()
                if 'total' in field_lower and 'ton' in field_lower and 'collected' not in field_lower:
                    try:
                        total_tonnage = float(str(field_value).replace(',', ''))
                        break
                    except:
                        pass
            
            # If we have total and collected, calculate uncollected
            if total_tonnage > 0 and collected_tonnage > 0 and uncollected_tonnage == 0:
                uncollected_tonnage = max(0, total_tonnage - collected_tonnage)
            
            # Skip if both are zero
            if collected_tonnage == 0 and uncollected_tonnage == 0:
                continue
            
            # Get borough/zone
            borough = record.get('borough', 'Unknown')
            zone_id = f"{borough[:3].upper()}-AGG"
            
            # Check if zone exists, if not use generic
            existing_zone = db.zones.find_one({'borough': borough})
            if existing_zone:
                zone_id = existing_zone['zone_id']
            
            # Create collection event for COLLECTED tonnage
            if collected_tonnage > 0:
                # Determine waste type from the record
                waste_type = 'residential'
                if 'paper' in str(record).lower() or 'papertonscollected' in record:
                    waste_type = 'recycling'
                elif 'organic' in str(record).lower() or any('organic' in f for f in record.keys()):
                    waste_type = 'organic'
                
                collection = CollectionEvent.create_event(
                    route_id=f"RT-TONNAGE-{month_str.replace(' / ', '-')}-COLLECTED-{idx}",
                    zone_id=zone_id,
                    collection_date=collection_date,
                    waste_type=waste_type,
                    tonnage=round(collected_tonnage, 2),
                    volume_cubic_yards=round(collected_tonnage * 2.0, 2),
                    collection_time_start=collection_date,
                    collection_time_end=collection_date,
                    status='completed',
                    notes=f"Real DSNY tonnage data - {borough} - {month_str} - Collected"
                )
                collection['_data_source'] = 'NYC Open Data - DSNY Monthly Tonnage'
                collection['_fetched_at'] = datetime.utcnow().isoformat()
                collection['borough'] = borough  # Store borough for easier querying
                collections.append(collection)
            
            # Create collection event for UNCOLLECTED tonnage
            if uncollected_tonnage > 0:
                waste_type = 'residential'  # Default for uncollected
                if 'paper' in str(record).lower():
                    waste_type = 'recycling'
                elif 'organic' in str(record).lower():
                    waste_type = 'organic'
                
                uncollected_collection = CollectionEvent.create_event(
                    route_id=f"RT-TONNAGE-{month_str.replace(' / ', '-')}-UNCOLLECTED-{idx}",
                    zone_id=zone_id,
                    collection_date=collection_date,
                    waste_type=waste_type,
                    tonnage=round(uncollected_tonnage, 2),
                    volume_cubic_yards=round(uncollected_tonnage * 2.0, 2),
                    collection_time_start=collection_date,
                    collection_time_end=collection_date,
                    status='missed',  # Mark as missed for uncollected
                    notes=f"Real DSNY tonnage data - {borough} - {month_str} - Uncollected"
                )
                uncollected_collection['_data_source'] = 'NYC Open Data - DSNY Monthly Tonnage'
                uncollected_collection['_fetched_at'] = datetime.utcnow().isoformat()
                uncollected_collection['borough'] = borough
                collections.append(uncollected_collection)
        
        # Insert (upsert based on route_id + zone_id + date to avoid duplicates)
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
        
        return {
            'status': 'success',
            'records_fetched': len(api_data),
            'records_inserted': inserted,
            'data_source': 'NYC Open Data - DSNY Monthly Tonnage',
            'last_updated': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error refreshing tonnage data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to refresh data: {str(e)}")

