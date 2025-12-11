"""API routes for sanitation zones."""
from fastapi import APIRouter, HTTPException, Query
from database import Database
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
async def get_zones(
    borough: Optional[str] = Query(None, description="Filter by borough"),
    district: Optional[str] = Query(None, description="Filter by district"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    skip: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get all zones with optional filtering by borough and district."""
    try:
        db = Database.get_db()
        zones_collection = db.zones
        
        # Build query
        query = {}
        if borough:
            query['borough'] = borough
        if district:
            query['district'] = district
        
        # Execute query
        zones = list(zones_collection.find(query).limit(limit).skip(skip))
        
        # Convert ObjectId to string and format dates
        for zone in zones:
            zone['_id'] = str(zone['_id'])
            if 'created_at' in zone:
                zone['created_at'] = zone['created_at'].isoformat()
            if 'updated_at' in zone:
                zone['updated_at'] = zone['updated_at'].isoformat()
        
        return {
            'zones': zones,
            'count': len(zones),
            'total': zones_collection.count_documents(query)
        }
        
    except Exception as e:
        logger.error(f"Error fetching zones: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch zones")

@router.get("/boroughs")
async def get_boroughs():
    """Get list of all boroughs with zone counts - PERSONA-SPECIFIC ENDPOINT.
    
    Returns aggregated data by borough including:
    - Number of zones per borough
    - Total population per borough
    """
    try:
        db = Database.get_db()
        boroughs = db.zones.aggregate([
            {
                '$group': {
                    '_id': '$borough',
                    'zone_count': {'$sum': 1},
                    'total_population': {'$sum': '$population'}
                }
            },
            {'$sort': {'_id': 1}}
        ])
        
        result = [{
            'borough': b['_id'],
            'zone_count': b['zone_count'],
            'total_population': b['total_population']
        } for b in boroughs]
        
        return {'boroughs': result}
        
    except Exception as e:
        logger.error(f"Error fetching boroughs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch boroughs")

@router.get("/{zone_id}")
async def get_zone(zone_id: str):
    """Get a specific zone by ID."""
    try:
        db = Database.get_db()
        zone = db.zones.find_one({'zone_id': zone_id})
        
        if not zone:
            raise HTTPException(status_code=404, detail="Zone not found")
        
        zone['_id'] = str(zone['_id'])
        if 'created_at' in zone:
            zone['created_at'] = zone['created_at'].isoformat()
        if 'updated_at' in zone:
            zone['updated_at'] = zone['updated_at'].isoformat()
        
        return zone
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching zone: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch zone")

@router.get("/{zone_id}/stats")
async def get_zone_stats(zone_id: str):
    """Get statistics for a specific zone - PERSONA-SPECIFIC ENDPOINT.
    
    Returns comprehensive performance metrics for a zone including:
    - Total tonnage collected
    - Collection completion rates
    - Service request status
    - Average collection times
    """
    try:
        db = Database.get_db()
        
        # Get zone
        zone = db.zones.find_one({'zone_id': zone_id})
        if not zone:
            raise HTTPException(status_code=404, detail="Zone not found")
        
        # Get collection stats for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        collections = list(db.collections.find({
            'zone_id': zone_id,
            'collection_date': {'$gte': thirty_days_ago}
        }))
        
        # Calculate metrics
        total_tonnage = sum(c.get('tonnage', 0) for c in collections)
        total_collections = len(collections)
        completed_collections = len([c for c in collections if c.get('status') == 'completed'])
        on_time_rate = (completed_collections / total_collections * 100) if total_collections > 0 else 0
        
        # Get open service requests
        open_requests = db.requests.count_documents({
            'zone_id': zone_id,
            'status': {'$in': ['open', 'in_progress']}
        })
        
        # Get average collection time
        avg_collection_time = None
        completed_with_times = [c for c in collections 
                               if c.get('status') == 'completed' 
                               and c.get('collection_time_start') 
                               and c.get('collection_time_end')]
        if completed_with_times:
            times = [(c['collection_time_end'] - c['collection_time_start']).total_seconds() / 3600 
                    for c in completed_with_times]
            avg_collection_time = sum(times) / len(times)
        
        stats = {
            'zone_id': zone_id,
            'zone_name': zone.get('name'),
            'period': 'last_30_days',
            'metrics': {
                'total_tonnage': round(total_tonnage, 2),
                'total_collections': total_collections,
                'completed_collections': completed_collections,
                'on_time_rate': round(on_time_rate, 2),
                'open_service_requests': open_requests,
                'avg_collection_time_hours': round(avg_collection_time, 2) if avg_collection_time else None
            },
            'population': zone.get('population'),
            'tonnage_per_capita': round(total_tonnage / zone.get('population', 1), 4) if zone.get('population') else None
        }
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching zone stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch zone statistics")
