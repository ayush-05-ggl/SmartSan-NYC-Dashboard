"""API routes for vehicles."""
from fastapi import APIRouter, HTTPException, Query
from database import Database
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
async def get_vehicles(
    status: Optional[str] = Query(None, description="Filter by status"),
    vehicle_type: Optional[str] = Query(None, alias="type", description="Filter by vehicle type"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """Get all vehicles with optional filtering."""
    try:
        db = Database.get_db()
        vehicles_collection = db.vehicles
        
        # Build query
        query = {}
        if status:
            query['status'] = status
        if vehicle_type:
            query['vehicle_type'] = vehicle_type
        
        # Execute query
        vehicles = list(vehicles_collection.find(query).limit(limit).skip(skip))
        
        # Convert ObjectId to string
        for vehicle in vehicles:
            vehicle['_id'] = str(vehicle['_id'])
            if 'last_maintenance' in vehicle and vehicle['last_maintenance']:
                vehicle['last_maintenance'] = vehicle['last_maintenance'].isoformat()
            if 'created_at' in vehicle:
                vehicle['created_at'] = vehicle['created_at'].isoformat()
            if 'updated_at' in vehicle:
                vehicle['updated_at'] = vehicle['updated_at'].isoformat()
        
        return {
            'vehicles': vehicles,
            'count': len(vehicles),
            'total': vehicles_collection.count_documents(query)
        }
        
    except Exception as e:
        logger.error(f"Error fetching vehicles: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch vehicles")

@router.get("/available")
async def get_available_vehicles():
    """Get available vehicles - PERSONA-SPECIFIC ENDPOINT.
    
    Returns all vehicles currently available for route assignment.
    Essential for fleet management and route planning.
    """
    try:
        db = Database.get_db()
        available_vehicles = list(db.vehicles.find({
            'status': 'available'
        }))
        
        for vehicle in available_vehicles:
            vehicle['_id'] = str(vehicle['_id'])
            if 'last_maintenance' in vehicle and vehicle['last_maintenance']:
                vehicle['last_maintenance'] = vehicle['last_maintenance'].isoformat()
            if 'created_at' in vehicle:
                vehicle['created_at'] = vehicle['created_at'].isoformat()
            if 'updated_at' in vehicle:
                vehicle['updated_at'] = vehicle['updated_at'].isoformat()
        
        return {
            'available_vehicles': available_vehicles,
            'count': len(available_vehicles)
        }
        
    except Exception as e:
        logger.error(f"Error fetching available vehicles: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch available vehicles")
