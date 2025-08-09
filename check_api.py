#!/usr/bin/env python3
"""
Quick API status check script
"""

import requests
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
ADMIN_CREDENTIALS = {
    "email": "official.tishnu@gmail.com",
    "password": "Access@404"
}

def check_api_status():
    """Check API status and training jobs."""
    print("🔍 Checking API Status...")
    
    try:
        # Step 1: Authenticate
        print("\n1. Authenticating...")
        response = requests.post(f"{API_BASE_URL}/api/v1/auth/login", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            user = data["user"]
            print(f"✅ Authenticated as: {user['first_name']} {user['last_name']} ({user['role']})")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return
        
        # Step 2: Check AI health
        print("\n2. Checking AI Services...")
        response = requests.get(f"{API_BASE_URL}/api/v1/ai/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ AI Status: {health.get('overall_status', 'unknown')}")
        else:
            print(f"⚠️  AI health check failed: {response.status_code}")
        
        # Step 3: Check training jobs
        print("\n3. Checking Training Jobs...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/api/v1/ai/training-jobs", headers=headers)
        if response.status_code == 200:
            jobs_data = response.json()
            jobs = jobs_data.get("jobs", [])
            print(f"✅ Found {len(jobs)} training jobs")
            
            for i, job in enumerate(jobs[:5], 1):  # Show first 5 jobs
                status = job.get("status", "unknown")
                progress = job.get("progress", 0)
                name = job.get("name", "Unknown")
                job_id = job.get("job_id", "unknown")
                print(f"   {i}. {name} ({job_id}): {status} - {progress}%")
        else:
            print(f"❌ Training jobs check failed: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {error_data.get('detail', 'Unknown error')}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Please ensure server is running at: http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ API check failed: {e}")

if __name__ == "__main__":
    check_api_status()
