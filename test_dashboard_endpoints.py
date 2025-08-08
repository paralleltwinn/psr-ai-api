#!/usr/bin/env python3
"""
Test script to verify admin dashboard endpoints are working correctly.
"""

import requests
import json

def test_login_and_dashboard():
    """Test login and dashboard endpoints."""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Admin Dashboard Endpoints")
    print("=" * 50)
    
    # Step 1: Login to get token
    print("1. Testing Login...")
    login_data = {
        "email": "official.tishnu@gmail.com",
        "password": "Access@404"
    }
    
    login_response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result['access_token']
        user_role = login_result['user']['role']
        print(f"✅ Login successful! Role: {user_role}")
    else:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return False
    
    # Step 2: Test Super Admin Dashboard
    print("\n2. Testing Super Admin Dashboard...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    dashboard_response = requests.get(f"{base_url}/admin/dashboard", headers=headers)
    
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        print("✅ Super Admin Dashboard endpoint working!")
        print("📊 Stats returned:")
        stats = dashboard_data.get('stats', {})
        for key, value in stats.items():
            print(f"   • {key}: {value}")
    else:
        print(f"❌ Dashboard failed: {dashboard_response.status_code} - {dashboard_response.text}")
    
    # Step 3: Test Admin Stats
    print("\n3. Testing Admin Stats...")
    stats_response = requests.get(f"{base_url}/admin/stats", headers=headers)
    
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        print("✅ Admin Stats endpoint working!")
        print("📊 Stats returned:")
        stats = stats_data.get('stats', {})
        for key, value in stats.items():
            print(f"   • {key}: {value}")
    else:
        print(f"❌ Stats failed: {stats_response.status_code} - {stats_response.text}")
    
    # Step 4: Test Pending Engineers
    print("\n4. Testing Pending Engineers...")
    pending_response = requests.get(f"{base_url}/admin/engineers/pending", headers=headers)
    
    if pending_response.status_code == 200:
        pending_data = pending_response.json()
        print("✅ Pending Engineers endpoint working!")
        if isinstance(pending_data, list):
            print(f"📋 Found {len(pending_data)} pending engineer applications")
        else:
            print(f"📋 Response: {pending_data}")
    else:
        print(f"❌ Pending Engineers failed: {pending_response.status_code} - {pending_response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 API Endpoint Testing Complete!")
    return True

if __name__ == "__main__":
    test_login_and_dashboard()
