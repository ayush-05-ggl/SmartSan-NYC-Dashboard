"""API routes for service requests."""
from fastapi import APIRouter, HTTPException, Query
from database import Database
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
async def get_requests(
    zone_id: Optional[str] = Query(None, description="Filter by zone ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    request_type: Optional[str] = Query(None, alias="type", description="Filter by request type"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """Get service requests with optional filtering."""
    try:
        db = Database.get_db()
        requests_collection = db.requests
        
        # Build query
        query = {}
        if zone_id:
            query['zone_id'] = zone_id
        if status:
            query['status'] = status
        if priority:
            query['priority'] = priority
        if request_type:
            query['request_type'] = request_type
        
        # Execute query
        requests = list(requests_collection.find(query)
                       .sort('reported_at', -1)
                       .limit(limit)
                       .skip(skip))
        
        # Convert ObjectId and datetime
        for req in requests:
            req['_id'] = str(req['_id'])
            for date_field in ['reported_at', 'created_at', 'updated_at']:
                if date_field in req and req[date_field]:
                    req[date_field] = req[date_field].isoformat()
        
        return {
            'requests': requests,
            'count': len(requests),
            'total': requests_collection.count_documents(query)
        }
        
    except Exception as e:
        logger.error(f"Error fetching requests: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch requests")

@router.get("/urgent")
async def get_urgent_requests():
    """Get urgent and high priority requests - PERSONA-SPECIFIC ENDPOINT.
    
    Returns all urgent and high-priority service requests that are not yet closed.
    Critical for prioritizing immediate action items.
    """
    try:
        db = Database.get_db()
        urgent_requests = list(db.requests.find({
            'priority': {'$in': ['urgent', 'high']},
            'status': {'$ne': 'closed'}
        }).sort('reported_at', -1))
        
        for req in urgent_requests:
            req['_id'] = str(req['_id'])
            for date_field in ['reported_at', 'created_at', 'updated_at']:
                if date_field in req and req[date_field]:
                    req[date_field] = req[date_field].isoformat()
        
        return {
            'urgent_requests': urgent_requests,
            'count': len(urgent_requests)
        }
        
    except Exception as e:
        logger.error(f"Error fetching urgent requests: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch urgent requests")

@router.get("/by-type")
async def get_requests_by_type():
    """Get request counts grouped by type - PERSONA-SPECIFIC ENDPOINT.
    
    Returns aggregated statistics showing:
    - Total requests by type (missed_pickup, overflow, illegal_dumping, etc.)
    - Status breakdown for each type
    """
    try:
        db = Database.get_db()
        
        pipeline = [
            {
                '$group': {
                    '_id': '$request_type',
                    'count': {'$sum': 1},
                    'by_status': {
                        '$push': '$status'
                    }
                }
            },
            {'$sort': {'count': -1}}
        ]
        
        results = list(db.requests.aggregate(pipeline))
        
        # Process results
        request_types = []
        for result in results:
            status_counts = {}
            for status in result['by_status']:
                status_counts[status] = status_counts.get(status, 0) + 1
            
            request_types.append({
                'type': result['_id'],
                'total_count': result['count'],
                'by_status': status_counts
            })
        
        return {
            'request_types': request_types,
            'total': sum(r['total_count'] for r in request_types)
        }
        
    except Exception as e:
        logger.error(f"Error fetching requests by type: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch requests by type")
