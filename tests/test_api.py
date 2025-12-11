"""Quick test script to verify API endpoints are working."""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, description=""):
    """Test an API endpoint and print results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    if description:
        print(f"Description: {description}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            
            # Pretty print response
            if isinstance(data, dict):
                # Show key stats for dashboard/metrics
                if 'overview' in data:
                    print("\n📊 Overview:")
                    for key, value in data['overview'].items():
                        print(f"  {key}: {value}")
                
                # Show summary for collections
                if 'summary' in data:
                    print("\n📊 Summary:")
                    for key, value in data['summary'].items():
                        print(f"  {key}: {value}")
                
                # Show count if available
                if 'count' in data:
                    print(f"\n📈 Count: {data['count']}")
                elif 'total' in data:
                    print(f"\n📈 Total: {data['total']}")
                
                # Show first item if it's a list
                for key in ['zones', 'collections', 'routes', 'requests', 'vehicles', 'metrics']:
                    if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                        print(f"\n📋 Sample {key[:-1]} (first item):")
                        sample = data[key][0]
                        for k, v in list(sample.items())[:5]:  # Show first 5 fields
                            print(f"  {k}: {v}")
                        break
            else:
                print(f"Response: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the server running?")
        print("   Start server with: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 API Testing Script")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test endpoints in order of importance
    tests = [
        ("Health Check", f"{BASE_URL}/api/health", "Verify server and database are running"),
        ("API Info", f"{BASE_URL}/api", "Get API information"),
        ("Dashboard Metrics", f"{BASE_URL}/api/metrics/dashboard", "High-level KPIs - GREAT FOR DEMO"),
        ("Today's Collections", f"{BASE_URL}/api/collections/today", "Real-time operations"),
        ("Collection Summary", f"{BASE_URL}/api/collections/summary?days=7", "Aggregated collection data"),
        ("Urgent Requests", f"{BASE_URL}/api/requests/urgent", "High-priority issues"),
        ("All Zones", f"{BASE_URL}/api/zones?limit=5", "Get zones (limited to 5)"),
        ("Boroughs", f"{BASE_URL}/api/zones/boroughs", "Borough summary"),
        ("Active Routes", f"{BASE_URL}/api/routes/active", "Currently active routes"),
        ("Available Vehicles", f"{BASE_URL}/api/vehicles/available", "Fleet availability"),
    ]
    
    for name, url, description in tests:
        test_endpoint(name, url, description)
    
    print("\n" + "="*60)
    print("✅ Testing Complete!")
    print("="*60)
    print("\n💡 Tips:")
    print("  - Visit http://localhost:8000/docs for interactive API docs")
    print("  - Use /api/metrics/dashboard for your demo")
    print("  - All endpoints work with generated test data")
    print("\n")

if __name__ == "__main__":
    main()

