"""API routes for complaint type filtering and analysis."""
from fastapi import APIRouter, HTTPException, Query
from database import Database
from typing import Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Sanitation-related complaint types
SANITATION_COMPLAINT_TYPES = [
    'illegal_dumping',
    'missed_pickup',
    'overflow',
    'rodent',
    'dirty_condition',
    'trash_issue',
    'litter_basket',
    'damaged_container',
    'vendor_enforcement',
    'obstruction',
    'graffiti',
    'unsanitary_condition',
    'air_quality',
    'water_quality',
    'hazardous_materials',
    'sweeping',
    'mosquitoes',
    'mold',
    'snow',
    'other'
]

@router.get("/types")
async def get_complaint_types():
    """Get all available complaint types with counts."""
    try:
        db = Database.get_db()
        
        pipeline = [
            {
                '$group': {
                    '_id': '$request_type',
                    'count': {'$sum': 1},
                    'open_count': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'open']}, 1, 0]}
                    },
                    'urgent_count': {
                        '$sum': {'$cond': [{'$eq': ['$priority', 'urgent']}, 1, 0]}
                    }
                }
            },
            {'$sort': {'count': -1}}
        ]
        
        results = list(db.requests.aggregate(pipeline))
        
        complaint_types = []
        for result in results:
            complaint_types.append({
                'type': result['_id'],
                'total': result['count'],
                'open': result['open_count'],
                'urgent': result['urgent_count'],
                'is_sanitation': result['_id'] in SANITATION_COMPLAINT_TYPES
            })
        
        return {
            'complaint_types': complaint_types,
            'total': sum(r['total'] for r in complaint_types),
            'sanitation_types': SANITATION_COMPLAINT_TYPES
        }
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch complaint types")

@router.get("/by-type/{complaint_type}")
async def get_requests_by_complaint_type(
    complaint_type: str,
    borough: Optional[str] = Query(None, description="Filter by borough"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """Get requests filtered by complaint type.
    
    Shows requests for a specific complaint type (e.g., illegal_dumping, rodent, etc.)
    with full details including addresses.
    """
    try:
        db = Database.get_db()
        
        query = {'request_type': complaint_type}
        
        if borough:
            query['borough'] = borough.upper()
        
        if status:
            query['status'] = status
        
        requests = list(db.requests.find(query)
                       .sort('reported_at', -1)
                       .limit(limit)
                       .skip(skip))
        
        # Format response
        for req in requests:
            req['_id'] = str(req['_id'])
            if 'reported_at' in req and req['reported_at']:
                req['reported_at'] = req['reported_at'].isoformat()
            if 'closed_date' in req and req['closed_date']:
                req['closed_date'] = req['closed_date'].isoformat()
        
        return {
            'complaint_type': complaint_type,
            'requests': requests,
            'count': len(requests),
            'total': db.requests.count_documents(query)
        }
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch requests")

@router.get("/by-borough")
async def get_requests_by_borough(
    complaint_type: Optional[str] = Query(None, description="Filter by complaint type")
):
    """Get request counts grouped by borough."""
    try:
        db = Database.get_db()
        
        match_stage = {}
        if complaint_type:
            match_stage['request_type'] = complaint_type
        
        pipeline = [
            {'$match': match_stage} if match_stage else {'$match': {}},
            {
                '$group': {
                    '_id': '$borough',
                    'count': {'$sum': 1},
                    'open_count': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'open']}, 1, 0]}
                    },
                    'types': {'$addToSet': '$request_type'}
                }
            },
            {'$sort': {'count': -1}}
        ]
        
        results = list(db.requests.aggregate(pipeline))
        
        boroughs = []
        for result in results:
            boroughs.append({
                'borough': result['_id'] or 'Unknown',
                'total': result['count'],
                'open': result['open_count'],
                'complaint_types': result['types']
            })
        
        return {
            'by_borough': boroughs,
            'total': sum(b['total'] for b in boroughs),
            'filter': {'complaint_type': complaint_type} if complaint_type else None
        }
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch borough breakdown")

@router.get("/stats")
async def get_complaint_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """Get comprehensive complaint statistics."""
    try:
        db = Database.get_db()
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                '$match': {
                    'reported_at': {'$gte': cutoff_date}
                }
            },
            {
                '$group': {
                    '_id': '$request_type',
                    'count': {'$sum': 1},
                    'avg_resolution_days': {
                        '$avg': {
                            '$cond': [
                                {'$and': [
                                    {'$ne': ['$closed_date', None]},
                                    {'$ne': ['$reported_at', None]}
                                ]},
                                {'$divide': [
                                    {'$subtract': ['$closed_date', '$reported_at']},
                                    86400000  # milliseconds to days
                                ]},
                                None
                            ]
                        }
                    },
                    'by_borough': {
                        '$push': '$borough'
                    },
                    'by_status': {
                        '$push': '$status'
                    }
                }
            },
            {'$sort': {'count': -1}}
        ]
        
        results = list(db.requests.aggregate(pipeline))
        
        stats = []
        for result in results:
            # Count by borough
            borough_counts = {}
            for b in result['by_borough']:
                if b:
                    borough_counts[b] = borough_counts.get(b, 0) + 1
            
            # Count by status
            status_counts = {}
            for s in result['by_status']:
                status_counts[s] = status_counts.get(s, 0) + 1
            
            stats.append({
                'complaint_type': result['_id'],
                'total': result['count'],
                'avg_resolution_days': round(result['avg_resolution_days'], 1) if result['avg_resolution_days'] else None,
                'by_borough': borough_counts,
                'by_status': status_counts
            })
        
        return {
            'period_days': days,
            'stats': stats,
            'total_requests': sum(s['total'] for s in stats)
        }
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")

