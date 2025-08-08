#!/usr/bin/env python3
"""
Test script for Poornasree AI API endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, description):
    """Test an API endpoint and print results."""
    print(f"\n🔍 Testing: {description}")
    print(f"Endpoint: {endpoint}")
    print("-" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS")
            print(f"Response Preview: {json.dumps(data, indent=2)[:500]}...")
        else:
            print("❌ FAILED")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print("❌ CONNECTION ERROR")
        print(f"Error: {str(e)}")

def main():
    """Test all available endpoints."""
    print("=" * 80)
    print("🚀 POORNASREE AI API ENDPOINT TESTING")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Test main health endpoint
    test_endpoint("/health", "Main Application Health Check")
    
    # Test database endpoints
    test_endpoint("/api/v1/database/health", "Database Health Check")
    
    # Test AI endpoints
    test_endpoint("/api/v1/ai/health", "AI Services Health Check")
    
    # Test main config endpoint
    test_endpoint("/config", "Application Configuration")
    
    # Test API documentation
    test_endpoint("/docs", "API Documentation (Swagger)")
    
    print("\n" + "=" * 80)
    print("🎉 ENDPOINT TESTING COMPLETED")
    print("=" * 80)
    print("\n📋 Available Endpoints Summary:")
    print("• Main Health: /health")
    print("• Database Health: /api/v1/database/health")
    print("• AI Services Health: /api/v1/ai/health")
    print("• Config: /config")
    print("• API Docs: /docs")
    print("• Redoc: /redoc")
    print("\n🔐 Authenticated Endpoints (require login):")
    print("• Database Stats: /api/v1/database/stats")
    print("• AI Initialize: /api/v1/ai/initialize")
    print("• AI Generate Text: /api/v1/ai/google-ai/generate")

if __name__ == "__main__":
    main()
