"""Test script to pull real NYC data."""
from services.nyc_open_data import NYCOpenDataClient
from database import Database
from routes.data_refresh import refresh_311_data
import asyncio

def test_api():
    """Test NYC Open Data API directly."""
    print("Testing NYC Open Data API...")
    client = NYCOpenDataClient()
    
    # Try getting recent DSNY data
    data = client.get_311_requests(agency='DSNY', days_back=30, limit=50)
    print(f"✅ Got {len(data)} real DSNY records from NYC Open Data API")
    
    if data:
        print("\nSample record:")
        sample = data[0]
        print(f"  Agency: {sample.get('agency_name', 'N/A')}")
        print(f"  Complaint: {sample.get('complaint_type', 'N/A')}")
        print(f"  Created: {sample.get('created_date', 'N/A')}")
        print(f"  Address: {sample.get('incident_address', 'N/A')}")
    
    return len(data) > 0

async def test_refresh():
    """Test the refresh endpoint."""
    print("\n" + "="*50)
    print("Testing data refresh endpoint...")
    
    Database.connect()
    try:
        result = await refresh_311_data()
        print(f"✅ Refresh result: {result}")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        Database.disconnect()

if __name__ == '__main__':
    # Test API first
    if test_api():
        print("\n" + "="*50)
        print("API works! Now testing database refresh...")
        result = asyncio.run(test_refresh())
        if result:
            print("\n✅ SUCCESS! Real data is now in your database!")
            print(f"   Records inserted: {result.get('records_inserted', 0)}")
        else:
            print("\n⚠️  API works but refresh failed. Check error above.")
    else:
        print("\n❌ API test failed. Check NYC Open Data API connection.")

