"""API routes for performance metrics."""
from fastapi import APIRouter, HTTPException, Query
from database import Database
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
async def get_metrics(
    zone_id: Optional[str] = Query(None, description="Filter by zone ID"),
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """Get performance metrics with optional filtering."""
    try:
        db = Database.get_db()
        metrics_collection = db.metrics
        
        # Build query
        query = {}
        if zone_id:
            query['zone_id'] = zone_id
        if metric_type:
            query['metric_type'] = metric_type
        if start_date or end_date:
            query['metric_date'] = {}
            if start_date:
                query['metric_date']['$gte'] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                query['metric_date']['$lte'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Execute query
        metrics = list(metrics_collection.find(query)
                      .sort('metric_date', -1)
                      .limit(limit)
                      .skip(skip))
        
        # Convert ObjectId and datetime
        for metric in metrics:
            metric['_id'] = str(metric['_id'])
            if 'metric_date' in metric and metric['metric_date']:
                metric['metric_date'] = metric['metric_date'].isoformat()
            if 'created_at' in metric and metric['created_at']:
                metric['created_at'] = metric['created_at'].isoformat()
        
        return {
            'metrics': metrics,
            'count': len(metrics),
            'total': metrics_collection.count_documents(query)
        }
        
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")

@router.get("/dashboard")
async def get_dashboard_metrics(
    days: int = Query(7, ge=1, le=365, description="Number of days for metrics")
):
    """Get comprehensive dashboard metrics - PERSONA-SPECIFIC ENDPOINT.
    
    Returns high-level KPIs for executive dashboard including:
    - Total zones and active routes
    - Collection efficiency and tonnage
    - Service request status
    - Performance indicators
    """
    try:
        db = Database.get_db()
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get collection efficiency
        collections = list(db.collections.find({
            'collection_date': {'$gte': start_date}
        }))
        
        total_collections = len(collections)
        completed = len([c for c in collections if c.get('status') == 'completed'])
        missed_collections = len([c for c in collections if c.get('status') == 'missed'])
        efficiency = (completed / total_collections * 100) if total_collections > 0 else 0
        
        # Get total tonnage
        total_tonnage = sum(c.get('tonnage', 0) for c in collections)
        
        # Get today's missed collections (for "Missed Pickups (today)")
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
        today_end = today_start + timedelta(days=1)
        today_missed = db.collections.count_documents({
            'collection_date': {
                '$gte': today_start,
                '$lt': today_end
            },
            'status': 'missed'
        })
        
        # Get open service requests
        open_requests = db.requests.count_documents({
            'status': {'$in': ['open', 'in_progress']}
        })
        urgent_requests = db.requests.count_documents({
            'priority': 'urgent',
            'status': {'$ne': 'closed'}
        })
        
        # Get active routes
        active_routes = db.routes.count_documents({
            'status': {'$in': ['scheduled', 'in_progress']}
        })
        
        # Get zones count
        total_zones = db.zones.count_documents({})
        
        # Get average tonnage per zone
        avg_tonnage_per_zone = total_tonnage / total_zones if total_zones > 0 else 0
        
        dashboard_metrics = {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat(),
            'overview': {
                'total_zones': total_zones,
                'active_routes': active_routes,
                'total_collections': total_collections,
                'completed_collections': completed,
                'missed_collections': missed_collections,
                'today_missed_collections': today_missed,
                'collection_efficiency_pct': round(efficiency, 2),
                'total_tonnage': round(total_tonnage, 2),
                'avg_tonnage_per_zone': round(avg_tonnage_per_zone, 2)
            },
            'service_requests': {
                'open': open_requests,
                'urgent': urgent_requests
            },
            'performance': {
                'on_time_rate': round(efficiency, 2),
                'collection_efficiency': round(efficiency, 2)
            }
        }
        
        return dashboard_metrics
        
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard metrics")
