#!/usr/bin/env python3
"""
Service Guide Training Status Checker
=====================================
Quick script to check training job status and system health.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"
ADMIN_EMAIL = "official4tishnu@gmail.com"
ADMIN_PASSWORD = "Access@404"

def login():
    """Authenticate with the API."""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def check_system_health():
    """Check overall system health."""
    print("🏥 System Health Check")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Environment: {data.get('environment', 'unknown')}")
        else:
            print(f"❌ API Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")

def check_ai_services(token):
    """Check AI services health."""
    print("\n🤖 AI Services Health")
    print("-" * 30)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE}/ai/health", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Overall Status: {data.get('overall_status', 'unknown')}")
            
            services = data.get('services', {})
            for service_name, service_info in services.items():
                status = service_info.get('status', 'unknown')
                emoji = "✅" if status == "healthy" else "❌" if status == "unhealthy" else "⚠️"
                print(f"   {emoji} {service_name.title()}: {status}")
        else:
            print(f"❌ AI Services Check Failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ AI Services Error: {e}")

def check_training_jobs(token):
    """Check training job status."""
    print("\n📊 Training Jobs Status")
    print("-" * 30)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE}/ai/training-jobs", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            
            if not jobs:
                print("ℹ️  No training jobs found")
                return
            
            print(f"📋 Found {len(jobs)} training job(s):")
            
            for i, job in enumerate(jobs, 1):
                job_id = job.get('job_id', 'unknown')
                name = job.get('name', 'Unnamed Job')
                status = job.get('status', 'unknown')
                progress = job.get('progress', 0)
                started_by = job.get('started_by', 'Unknown')
                
                status_emoji = {
                    'queued': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌',
                    'cancelled': '⚠️'
                }.get(status, '❓')
                
                print(f"\n   {i}. {status_emoji} {name}")
                print(f"      Job ID: {job_id}")
                print(f"      Status: {status}")
                print(f"      Progress: {progress}%")
                print(f"      Started by: {started_by}")
                
                if status == 'failed':
                    error_msg = job.get('error_message', 'No error details')
                    print(f"      Error: {error_msg}")
        else:
            print(f"❌ Training Jobs Check Failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Training Jobs Error: {e}")

def check_training_files(token):
    """Check uploaded training files."""
    print("\n📁 Training Files")
    print("-" * 30)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE}/ai/training-files", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            
            if not files:
                print("ℹ️  No training files found")
                return
            
            print(f"📄 Found {len(files)} training file(s):")
            
            for i, file_info in enumerate(files, 1):
                file_id = file_info.get('file_id', 'unknown')
                filename = file_info.get('filename', 'Unknown')
                size = file_info.get('size', 0)
                uploaded_by = file_info.get('uploaded_by', 'Unknown')
                upload_date = file_info.get('upload_date', 'Unknown')
                
                print(f"   {i}. 📄 {filename}")
                print(f"      File ID: {file_id}")
                print(f"      Size: {size:,} bytes")
                print(f"      Uploaded by: {uploaded_by}")
                print(f"      Upload date: {upload_date}")
        else:
            print(f"❌ Training Files Check Failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Training Files Error: {e}")

def main():
    """Main status checker function."""
    print("🔍 Service Guide Training System Status")
    print("=" * 50)
    print(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check system health
    check_system_health()
    
    # Login and get token
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    print(f"\n✅ Authentication successful")
    
    # Check AI services
    check_ai_services(token)
    
    # Check training jobs
    check_training_jobs(token)
    
    # Check training files
    check_training_files(token)
    
    print("\n" + "=" * 50)
    print("🎯 Status check completed!")
    print("\nNext steps:")
    print("1. If training is complete, run the Q&A session")
    print("2. If training is still running, wait and check again")
    print("3. If training failed, review logs and restart")

if __name__ == "__main__":
    main()
