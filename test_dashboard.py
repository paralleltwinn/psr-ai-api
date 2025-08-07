import requests
import json

# Test the dashboard API endpoint
def test_dashboard_api():
    base_url = "http://localhost:8000"
    
    print("Testing Admin Dashboard API...")
    print("=" * 50)
    
    # First, let's test a simple health check
    try:
        health_response = requests.get(f"{base_url}/health")
        print(f"Health Check - Status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health Response: {health_response.json()}")
        print()
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test dashboard endpoint without auth (should fail)
    try:
        dashboard_response = requests.get(f"{base_url}/api/v1/admin/dashboard")
        print(f"Dashboard (No Auth) - Status: {dashboard_response.status_code}")
        print(f"Response: {dashboard_response.json()}")
        print()
    except Exception as e:
        print(f"Dashboard test failed: {e}")
    
    print("To test with authentication, you'll need to:")
    print("1. Login as super admin in the frontend")
    print("2. Copy the auth token from localStorage")
    print("3. Run the authenticated test manually")

if __name__ == "__main__":
    test_dashboard_api()
