#!/usr/bin/env python3
"""
Simple test script to check API connectivity.
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
ADMIN_EMAIL = "official4tishnu@gmail.com"
ADMIN_PASSWORD = "Access@404"

def test_health():
    """Test basic health endpoint."""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
    except Exception as e:
        print(f"Health check failed: {e}")
    return False

def test_auth():
    """Test authentication."""
    try:
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"Auth Test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Role: {data['user']['role']}")
            return data.get('access_token')
        else:
            print(f"Auth failed: {response.text}")
    except Exception as e:
        print(f"Auth error: {e}")
    return None

def test_ai_health(token):
    """Test AI health endpoint."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/ai/health",
            headers=headers,
            timeout=10
        )
        
        print(f"AI Health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"AI Status: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"AI Health failed: {response.text}")
    except Exception as e:
        print(f"AI Health error: {e}")
    return False

def main():
    print("🧪 Simple API Test")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing Health Endpoint...")
    if not test_health():
        print("❌ Server not responding")
        return
    
    # Test 2: Authentication
    print("\n2. Testing Authentication...")
    token = test_auth()
    if not token:
        print("❌ Authentication failed")
        return
    
    # Test 3: AI Health
    print("\n3. Testing AI Health...")
    if test_ai_health(token):
        print("✅ AI services accessible")
    else:
        print("⚠️ AI services may have issues")
    
    print("\n✅ Basic tests completed!")

if __name__ == "__main__":
    main()
