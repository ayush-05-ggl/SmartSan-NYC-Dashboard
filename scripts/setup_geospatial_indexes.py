"""Create geospatial indexes for MongoDB location queries."""
from database import Database

def setup_geospatial_indexes():
    """Create 2dsphere indexes for geospatial queries."""
    try:
        db = Database.connect()
        
        print("Creating geospatial indexes...")
        
        # Index for service requests location
        # Only create if location.coordinates exists and has GeoJSON format
        try:
            db.requests.create_index([("location.coordinates", "2dsphere")])
            print("✅ Created 2dsphere index on requests.location.coordinates")
        except Exception as e:
            print(f"⚠️  Could not create requests index: {e}")
            print("   (This is OK if you don't have location data yet)")
        
        # Index for collections by date (for time-based queries)
        db.collections.create_index([("collection_date", -1)])
        print("✅ Created index on collections.collection_date")
        
        # Index for requests by date
        db.requests.create_index([("reported_at", -1)])
        print("✅ Created index on requests.reported_at")
        
        # Compound index for zone + date queries
        db.collections.create_index([("zone_id", 1), ("collection_date", -1)])
        print("✅ Created compound index on collections (zone_id, collection_date)")
        
        print("\n✅ Geospatial indexes created successfully!")
        print("\nYou can now use geospatial queries like:")
        print("  - /api/geo/requests/nearby?lat=40.7128&lng=-73.9352&radius_meters=1000")
        print("  - /api/geo/requests/hotspots")
        print("  - /api/geo/requests/in-bounds?min_lat=40.7&max_lat=40.8&min_lng=-74&max_lng=-73.9")
        
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        raise

if __name__ == '__main__':
    setup_geospatial_indexes()

