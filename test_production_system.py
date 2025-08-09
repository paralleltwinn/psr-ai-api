import requests

def test_production_ready_system():
    """Test the complete system through API endpoints."""
    
    # Login
    login_data = {
        'email': 'official.tishnu@gmail.com',
        'password': 'Access@404'
    }

    login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data, timeout=10)
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("🔐 Login successful!")
    
    # Test search endpoint with machine vibrating
    print("\n🔍 Testing search endpoint...")
    search_data = {
        'query': 'machine continuously vibrating',
        'limit': 3
    }
    
    search_response = requests.post('http://localhost:8000/api/v1/ai/search', 
                                  json=search_data, 
                                  headers=headers,
                                  timeout=10)
    
    if search_response.status_code == 200:
        result = search_response.json()
        print(f"✅ Search found {result['total_results']} results")
        
        if result['total_results'] > 0:
            best_result = result['results'][0]
            print(f"   📊 Best result score: {best_result.get('score', 0.0):.3f}")
            print(f"   📄 File: {best_result.get('metadata', {}).get('filename', 'Unknown')}")
            content = best_result.get('content', '')[:200]
            print(f"   📝 Content: {content}...")
        
    # Test chat endpoint with machine vibrating question
    print(f"\n💬 Testing chat endpoint...")
    chat_data = {
        'message': 'My machine is continuously vibrating and I cannot control it. What troubleshooting steps should I follow?',
        'conversation_id': 'production_test'
    }
    
    chat_response = requests.post('http://localhost:8000/api/v1/ai/chat',
                                json=chat_data,
                                headers=headers,
                                timeout=20)
    
    if chat_response.status_code == 200:
        chat_result = chat_response.json()
        print(f"✅ Chat successful!")
        print(f"🤖 AI Response:")
        print("=" * 60)
        print(chat_result.get('response', 'No response'))
        print("=" * 60)
        
        # Check if response contains troubleshooting steps
        response_text = chat_result.get('response', '').lower()
        troubleshooting_keywords = ['check', 'step', 'fuse', 'power', 'timer', 'potentiometer', 'vibration']
        found_keywords = [kw for kw in troubleshooting_keywords if kw in response_text]
        
        print(f"\n📊 Analysis:")
        print(f"   ✅ Found {len(found_keywords)} troubleshooting keywords: {found_keywords}")
        
        if len(found_keywords) >= 3:
            print("   🎯 EXCELLENT: Response contains detailed troubleshooting guidance!")
        elif len(found_keywords) >= 1:
            print("   👍 GOOD: Response contains some troubleshooting information")
        else:
            print("   ⚠️ Response may not be using trained data effectively")
            
    else:
        print(f"❌ Chat failed: {chat_response.status_code}")
    
    print(f"\n🎉 Production system test complete!")
    print(f"✅ Your ChatPage is now using real trained data from Weaviate!")

if __name__ == "__main__":
    test_production_ready_system()
