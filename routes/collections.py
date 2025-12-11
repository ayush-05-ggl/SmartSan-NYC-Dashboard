"""API routes for waste collection events."""
from fastapi import APIRouter, HTTPException, Query
from database import Database
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
async def get_collections(
    zone_id: Optional[str] = Query(None, description="Filter by zone ID"),
    route_id: Optional[str] = Query(None, description="Filter by route ID"),
    waste_type: Optional[str] = Query(None, description="Filter by waste type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """Get collection events with optional filtering."""
    try:
        db = Database.get_db()
        collections_collection = db.collections
        
        # Build query
        query = {}
        if zone_id:
            query['zone_id'] = zone_id
        if route_id:
            query['route_id'] = route_id
        if waste_type:
            query['waste_type'] = waste_type
        if status:
            query['status'] = status
        if start_date or end_date:
            query['collection_date'] = {}
            if start_date:
                query['collection_date']['$gte'] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                query['collection_date']['$lte'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Execute query
        collections = list(collections_collection.find(query)
                          .sort('collection_date', -1)
                          .limit(limit)
                          .skip(skip))
        
        # Convert ObjectId and datetime
        for collection in collections:
            collection['_id'] = str(collection['_id'])
            for date_field in ['collection_date', 'collection_time_start', 'collection_time_end', 'created_at', 'updated_at']:
                if date_field in collection and collection[date_field]:
                    collection[date_field] = collection[date_field].isoformat()
        
        return {
            'collections': collections,
            'count': len(collections),
            'total': collections_collection.count_documents(query)
        }
        
    except Exception as e:
        logger.error(f"Error fetching collections: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch collections")

@router.get("/today")
async def get_today_collections():
    """Get today's collection events - PERSONA-SPECIFIC ENDPOINT.
    
    Returns all collections scheduled for today with summary statistics.
    Critical for daily operations management.
    """
    try:
        db = Database.get_db()
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        collections = list(db.collections.find({
            'collection_date': {
                '$gte': today,
                '$lt': tomorrow
            }
        }).sort('collection_time_start', 1))
        
        # Convert dates
        for collection in collections:
            collection['_id'] = str(collection['_id'])
            for date_field in ['collection_date', 'collection_time_start', 'collection_time_end', 'created_at', 'updated_at']:
                if date_field in collection and collection[date_field]:
                    collection[date_field] = collection[date_field].isoformat()
        
        # Calculate summary
        total_tonnage = sum(c.get('tonnage', 0) for c in collections)
        completed = len([c for c in collections if c.get('status') == 'completed'])
        in_progress = len([c for c in collections if c.get('status') == 'in_progress'])
        
        return {
            'date': today.isoformat(),
            'collections': collections,
            'summary': {
                'total_scheduled': len(collections),
                'completed': completed,
                'in_progress': in_progress,
                'total_tonnage': round(total_tonnage, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching today's collections: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch today's collections")

@router.get("/summary")
async def get_collection_summary(
    days: int = Query(7, ge=1, le=365, description="Number of days to summarize")
):
    """Get collection summary for date range - PERSONA-SPECIFIC ENDPOINT.
    
    Returns aggregated statistics grouped by:
    - Waste type (residential, commercial, recycling, organic)
    - Status (completed, missed, partial)
    - Total tonnage and volume
    """
    try:
        db = Database.get_db()
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Aggregate collections
        pipeline = [
            {
                '$match': {
                    'collection_date': {'$gte': start_date}
                }
            },
            {
                '$group': {
                    '_id': {
                        'waste_type': '$waste_type',
                        'status': '$status'
                    },
                    'count': {'$sum': 1},
                    'total_tonnage': {'$sum': '$tonnage'},
                    'total_volume': {'$sum': '$volume_cubic_yards'}
                }
            }
        ]
        
        results = list(db.collections.aggregate(pipeline))
        
        # Format results
        summary = {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat(),
            'by_waste_type': {},
            'by_status': {},
            'totals': {
                'count': 0,
                'tonnage': 0,
                'volume': 0
            }
        }
        
        for result in results:
            waste_type = result['_id']['waste_type']
            status = result['_id']['status']
            
            # By waste type
            if waste_type not in summary['by_waste_type']:
                summary['by_waste_type'][waste_type] = {
                    'count': 0,
                    'tonnage': 0,
                    'volume': 0
                }
            summary['by_waste_type'][waste_type]['count'] += result['count']
            summary['by_waste_type'][waste_type]['tonnage'] += result['total_tonnage']
            summary['by_waste_type'][waste_type]['volume'] += result['total_volume']
            
            # By status
            if status not in summary['by_status']:
                summary['by_status'][status] = {
                    'count': 0,
                    'tonnage': 0
                }
            summary['by_status'][status]['count'] += result['count']
            summary['by_status'][status]['tonnage'] += result['total_tonnage']
            
            # Totals
            summary['totals']['count'] += result['count']
            summary['totals']['tonnage'] += result['total_tonnage']
            summary['totals']['volume'] += result['total_volume']
        
        # Round numbers
        for key in summary['by_waste_type']:
            summary['by_waste_type'][key]['tonnage'] = round(summary['by_waste_type'][key]['tonnage'], 2)
            summary['by_waste_type'][key]['volume'] = round(summary['by_waste_type'][key]['volume'], 2)
        
        for key in summary['by_status']:
            summary['by_status'][key]['tonnage'] = round(summary['by_status'][key]['tonnage'], 2)
        
        summary['totals']['tonnage'] = round(summary['totals']['tonnage'], 2)
        summary['totals']['volume'] = round(summary['totals']['volume'], 2)
        
        return summary
        
    except Exception as e:
        logger.error(f"Error fetching collection summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch collection summary")
