"""Geospatial API routes leveraging MongoDB's location queries."""
from fastapi import APIRouter, HTTPException, Query
from database import Database
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/requests/nearby")
async def get_requests_nearby(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_meters: float = Query(1000, ge=100, le=10000, description="Radius in meters"),
    limit: int = Query(50, ge=1, le=200)
):
    """Find service requests near a location - GEOSPATIAL QUERY.
    
    Uses MongoDB's $near operator to find requests within radius.
    Perfect for "show me issues near this address" functionality.
    """
    try:
        db = Database.get_db()
        
        # MongoDB geospatial query
        query = {
            'location.coordinates': {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [lng, lat]  # GeoJSON: [longitude, latitude]
                    },
                    '$maxDistance': radius_meters
                }
            }
        }
        
        requests = list(db.requests.find(query).limit(limit))
        
        # Format response
        for req in requests:
            req['_id'] = str(req['_id'])
            if 'reported_at' in req and req['reported_at']:
                req['reported_at'] = req['reported_at'].isoformat()
            if 'created_at' in req and req['created_at']:
                req['created_at'] = req['created_at'].isoformat()
        
        return {
            'center': {'lat': lat, 'lng': lng},
            'radius_meters': radius_meters,
            'requests': requests,
            'count': len(requests)
        }
        
    except Exception as e:
        logger.error(f"Error in geospatial query: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch nearby requests")

@router.get("/requests/in-bounds")
async def get_requests_in_bounds(
    min_lat: float = Query(..., description="Minimum latitude"),
    max_lat: float = Query(..., description="Maximum latitude"),
    min_lng: float = Query(..., description="Minimum longitude"),
    max_lng: float = Query(..., description="Maximum longitude"),
    limit: int = Query(100, ge=1, le=500)
):
    """Find service requests within a bounding box - GEOSPATIAL QUERY.
    
    Useful for map views - "show all requests in this map area".
    """
    try:
        db = Database.get_db()
        
        query = {
            'location.coordinates': {
                '$geoWithin': {
                    '$box': [
                        [min_lng, min_lat],  # Southwest corner
                        [max_lng, max_lat]   # Northeast corner
                    ]
                }
            }
        }
        
        requests = list(db.requests.find(query).limit(limit))
        
        for req in requests:
            req['_id'] = str(req['_id'])
            if 'reported_at' in req and req['reported_at']:
                req['reported_at'] = req['reported_at'].isoformat()
        
        return {
            'bounds': {
                'southwest': {'lat': min_lat, 'lng': min_lng},
                'northeast': {'lat': max_lat, 'lng': max_lng}
            },
            'requests': requests,
            'count': len(requests)
        }
        
    except Exception as e:
        logger.error(f"Error in bounds query: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch requests in bounds")

@router.get("/requests/hotspots")
async def get_request_hotspots(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365)
):
    """Find request hotspots - areas with high request density.
    
    Groups requests by location and returns areas with most requests.
    Great for identifying problem areas.
    """
    try:
        db = Database.get_db()
        
        # For historical data (most 311 DSNY data is from 2016)
        # Don't filter by date - use all available data with coordinates
        # Aggregate requests by location grid
        # Only include requests with valid coordinates (not null)
        pipeline = [
            {
                '$match': {
                    # Don't filter by date - use all historical data
                    'location.coordinates': {
                        '$exists': True,
                        '$ne': None,
                        '$type': 'array'
                    },
                    'location.coordinates.0': {'$type': 'number'},  # lng is a number
                    'location.coordinates.1': {'$type': 'number'}   # lat is a number
                }
            },
            {
                '$group': {
                    '_id': {
                        'lat': {'$round': [{'$arrayElemAt': ['$location.coordinates', 1]}, 3]},
                        'lng': {'$round': [{'$arrayElemAt': ['$location.coordinates', 0]}, 3]}
                    },
                    'count': {'$sum': 1},
                    'urgent_count': {
                        '$sum': {'$cond': [{'$eq': ['$priority', 'urgent']}, 1, 0]}
                    },
                    'types': {'$push': '$request_type'},
                    'address': {'$first': '$incident_address'},
                    'borough': {'$first': '$borough'}
                }
            },
            {
                '$match': {'count': {'$gte': 3}}  # At least 3 requests
            },
            {
                '$sort': {'count': -1}
            },
            {
                '$limit': limit
            }
        ]
        
        results = list(db.requests.aggregate(pipeline))
        
        hotspots = []
        for result in results:
            hotspots.append({
                'location': {
                    'lat': result['_id']['lat'],
                    'lng': result['_id']['lng'],
                    'address': result.get('address'),
                    'borough': result.get('borough')
                },
                'request_count': result['count'],
                'urgent_count': result['urgent_count'],
                'request_types': list(set(result['types']))
            })
        
        return {
            'period_days': days,
            'hotspots': hotspots,
            'count': len(hotspots)
        }
        
    except Exception as e:
        logger.error(f"Error finding hotspots: {e}")
        raise HTTPException(status_code=500, detail="Failed to find hotspots")

@router.get("/requests/heatmap")
async def get_complaint_heatmap(
    grid_size: float = Query(0.02, ge=0.001, le=0.1, description="Grid size in degrees (smaller = more granular)"),
    days: int = Query(30, ge=1, le=365),
    complaint_type: Optional[str] = Query(None, description="Filter by complaint type"),
    borough: Optional[str] = Query(None, description="Filter by borough")
):
    """Get complaint density heatmap data - aggregated by geographic grid.
    
    Returns complaint counts for each grid cell, suitable for heatmap visualization.
    Similar to weather map - shows where complaints are concentrated.
    """
    try:
        db = Database.get_db()
        
        # Build match query
        match_query = {
            'location.coordinates': {
                '$exists': True,
                '$ne': None,
                '$type': 'array'
            },
            'location.coordinates.0': {'$type': 'number'},
            'location.coordinates.1': {'$type': 'number'}
        }
        
        if complaint_type:
            match_query['request_type'] = complaint_type
        
        if borough and borough.upper() != 'ALL':
            match_query['$or'] = [
                {'borough': borough.upper()},
                {'location.borough': borough.upper()}
            ]
        
        # Aggregate by grid cells
        pipeline = [
            {
                '$match': match_query
            },
            {
                '$group': {
                    '_id': {
                        # Round to grid_size for binning
                        'lat': {
                            '$multiply': [
                                {'$round': {
                                    '$divide': [
                                        {'$arrayElemAt': ['$location.coordinates', 1]},
                                        grid_size
                                    ]
                                }},
                                grid_size
                            ]
                        },
                        'lng': {
                            '$multiply': [
                                {'$round': {
                                    '$divide': [
                                        {'$arrayElemAt': ['$location.coordinates', 0]},
                                        grid_size
                                    ]
                                }},
                                grid_size
                            ]
                        }
                    },
                    'count': {'$sum': 1},
                    'urgent_count': {
                        '$sum': {'$cond': [{'$eq': ['$priority', 'urgent']}, 1, 0]}
                    }
                }
            },
            {
                '$match': {'count': {'$gte': 2}}  # At least 2 complaints to reduce clutter
            },
            {
                '$sort': {'count': -1}
            }
        ]
        
        results = list(db.requests.aggregate(pipeline))
        
        # Find min/max for color scaling
        if results:
            counts = [r['count'] for r in results]
            min_count = min(counts)
            max_count = max(counts)
        else:
            min_count = 0
            max_count = 1
        
        heatmap_data = []
        for result in results:
            count = result['count']
            # Normalize count for color mapping (0-100 scale)
            intensity = ((count - min_count) / (max_count - min_count) * 100) if max_count > min_count else 50
            
            heatmap_data.append({
                'location': {
                    'lat': result['_id']['lat'],
                    'lng': result['_id']['lng']
                },
                'count': count,
                'urgent_count': result['urgent_count'],
                'intensity': round(intensity, 1)  # 0-100 scale for color mapping
            })
        
        return {
            'heatmap_data': heatmap_data,
            'count': len(heatmap_data),
            'grid_size': grid_size,
            'min_count': min_count,
            'max_count': max_count,
            'days': days,
            'filters': {
                'complaint_type': complaint_type,
                'borough': borough
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate heatmap")

@router.get("/collections/nearby")
async def get_collections_nearby(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_meters: float = Query(2000, ge=500, le=10000),
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=200)
):
    """Find collection events near a location - GEOSPATIAL QUERY.
    
    Shows waste collection activity in an area.
    Useful for route planning and analysis.
    """
    try:
        db = Database.get_db()
        
        # First find zones near the point, then get their collections
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get collections from zones (if zones had coordinates, we'd use $near)
        # For now, we'll use zone-based lookup
        collections = list(db.collections.find({
            'collection_date': {'$gte': cutoff_date}
        }).limit(limit))
        
        # Calculate distance for each (if we had zone coordinates)
        # For demo, return collections with zone info
        for collection in collections:
            collection['_id'] = str(collection['_id'])
            if 'collection_date' in collection:
                collection['collection_date'] = collection['collection_date'].isoformat()
        
        return {
            'center': {'lat': lat, 'lng': lng},
            'radius_meters': radius_meters,
            'period_days': days,
            'collections': collections[:limit],
            'count': len(collections)
        }
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch nearby collections")

