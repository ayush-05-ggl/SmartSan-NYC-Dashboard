"""Data models for NYC Department of Sanitation."""
from datetime import datetime
from typing import Optional, List
from bson import ObjectId

class SanitationZone:
    """Represents a sanitation collection zone in NYC."""
    
    @staticmethod
    def create_zone(zone_id: str, name: str, borough: str, 
                   district: str, population: int, area_sq_miles: float,
                   collection_days: List[str], collection_frequency: str = "weekly") -> dict:
        """Create a zone document."""
        return {
            "zone_id": zone_id,
            "name": name,
            "borough": borough,
            "district": district,
            "population": population,
            "area_sq_miles": area_sq_miles,
            "collection_days": collection_days,  # e.g., ["Monday", "Thursday"]
            "collection_frequency": collection_frequency,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

class CollectionRoute:
    """Represents a waste collection route."""
    
    @staticmethod
    def create_route(route_id: str, zone_id: str, route_name: str,
                    vehicle_id: Optional[str] = None, driver_id: Optional[str] = None,
                    estimated_duration_minutes: int = 240,
                    start_time: str = "06:00", status: str = "scheduled") -> dict:
        """Create a route document."""
        return {
            "route_id": route_id,
            "zone_id": zone_id,
            "route_name": route_name,
            "vehicle_id": vehicle_id,
            "driver_id": driver_id,
            "estimated_duration_minutes": estimated_duration_minutes,
            "start_time": start_time,
            "status": status,  # scheduled, in_progress, completed, delayed
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

class CollectionEvent:
    """Represents a waste collection event."""
    
    @staticmethod
    def create_event(route_id: str, zone_id: str, collection_date: datetime,
                    waste_type: str, tonnage: float, volume_cubic_yards: float,
                    collection_time_start: datetime, collection_time_end: Optional[datetime] = None,
                    status: str = "completed", notes: Optional[str] = None) -> dict:
        """Create a collection event document."""
        return {
            "route_id": route_id,
            "zone_id": zone_id,
            "collection_date": collection_date,
            "waste_type": waste_type,  # residential, commercial, recycling, organic
            "tonnage": tonnage,
            "volume_cubic_yards": volume_cubic_yards,
            "collection_time_start": collection_time_start,
            "collection_time_end": collection_time_end,
            "status": status,  # completed, missed, partial
            "notes": notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

class ServiceRequest:
    """Represents a service request/complaint."""
    
    @staticmethod
    def create_request(request_id: str, zone_id: str, request_type: str,
                      description: str, location: dict, priority: str = "normal",
                      status: str = "open", reported_at: datetime = None) -> dict:
        """Create a service request document.
        
        Location can be:
        - {lat: float, lng: float, address: str} - will convert to GeoJSON
        - {type: 'Point', coordinates: [lng, lat], address: str} - GeoJSON format
        """
        # Convert lat/lng to GeoJSON format if needed
        # Only create GeoJSON if we have valid coordinates (not null)
        if 'coordinates' not in location and 'lat' in location and 'lng' in location:
            lat = location.get('lat')
            lng = location.get('lng')
            # Only create GeoJSON Point if coordinates are valid numbers
            if lat is not None and lng is not None:
                try:
                    # Verify they're numbers
                    float(lat)
                    float(lng)
                    location = {
                        'type': 'Point',
                        'coordinates': [float(lng), float(lat)],  # GeoJSON: [longitude, latitude]
                        'address': location.get('address'),
                        'lat': lat,  # Keep for backward compatibility
                        'lng': lng
                    }
                except (ValueError, TypeError):
                    # Invalid coordinates, keep as-is without GeoJSON
                    pass
        
        return {
            "request_id": request_id,
            "zone_id": zone_id,
            "request_type": request_type,  # missed_pickup, overflow, illegal_dumping, etc.
            "description": description,
            "location": location,  # GeoJSON format for geospatial queries
            "priority": priority,  # low, normal, high, urgent
            "status": status,  # open, in_progress, resolved, closed
            "reported_at": reported_at or datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

class PerformanceMetric:
    """Represents performance metrics for a zone or route."""
    
    @staticmethod
    def create_metric(zone_id: str, metric_date: datetime, metric_type: str,
                     value: float, unit: str, target: Optional[float] = None) -> dict:
        """Create a performance metric document."""
        return {
            "zone_id": zone_id,
            "metric_date": metric_date,
            "metric_type": metric_type,  # collection_efficiency, on_time_rate, tonnage_per_capita, etc.
            "value": value,
            "unit": unit,
            "target": target,
            "created_at": datetime.utcnow()
        }

class Vehicle:
    """Represents a sanitation vehicle."""
    
    @staticmethod
    def create_vehicle(vehicle_id: str, vehicle_type: str, capacity_cubic_yards: float,
                     status: str = "available", current_zone: Optional[str] = None,
                     last_maintenance: Optional[datetime] = None) -> dict:
        """Create a vehicle document."""
        return {
            "vehicle_id": vehicle_id,
            "vehicle_type": vehicle_type,  # compactor, recycling_truck, organic_truck
            "capacity_cubic_yards": capacity_cubic_yards,
            "status": status,  # available, in_use, maintenance
            "current_zone": current_zone,
            "last_maintenance": last_maintenance,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

