"""API routes for collection routes."""
from fastapi import APIRouter, HTTPException, Query
from database import Database
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
async def get_routes(
    zone_id: Optional[str] = Query(None, description="Filter by zone ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """Get all routes with optional filtering."""
    try:
        db = Database.get_db()
        routes_collection = db.routes
        
        # Build query
        query = {}
        if zone_id:
            query['zone_id'] = zone_id
        if status:
            query['status'] = status
        
        # Execute query
        routes = list(routes_collection.find(query).limit(limit).skip(skip))
        
        # Convert ObjectId to string
        for route in routes:
            route['_id'] = str(route['_id'])
            if 'created_at' in route:
                route['created_at'] = route['created_at'].isoformat()
            if 'updated_at' in route:
                route['updated_at'] = route['updated_at'].isoformat()
        
        return {
            'routes': routes,
            'count': len(routes),
            'total': routes_collection.count_documents(query)
        }
        
    except Exception as e:
        logger.error(f"Error fetching routes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch routes")

@router.get("/{route_id}")
async def get_route(route_id: str):
    """Get a specific route by ID."""
    try:
        db = Database.get_db()
        route = db.routes.find_one({'route_id': route_id})
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        route['_id'] = str(route['_id'])
        if 'created_at' in route:
            route['created_at'] = route['created_at'].isoformat()
        if 'updated_at' in route:
            route['updated_at'] = route['updated_at'].isoformat()
        
        return route
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching route: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch route")

@router.get("/active")
async def get_active_routes():
    """Get currently active routes - PERSONA-SPECIFIC ENDPOINT.
    
    Returns routes that are currently scheduled or in progress.
    Essential for real-time operations monitoring.
    """
    try:
        db = Database.get_db()
        active_routes = list(db.routes.find({
            'status': {'$in': ['scheduled', 'in_progress']}
        }))
        
        for route in active_routes:
            route['_id'] = str(route['_id'])
            if 'created_at' in route:
                route['created_at'] = route['created_at'].isoformat()
            if 'updated_at' in route:
                route['updated_at'] = route['updated_at'].isoformat()
        
        return {
            'active_routes': active_routes,
            'count': len(active_routes)
        }
        
    except Exception as e:
        logger.error(f"Error fetching active routes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch active routes")
