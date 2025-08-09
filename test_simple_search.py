import requests

def test_simple_search():
    """Test search with a query we know works."""
    
    # Login
    login_data = {
        'email': 'official.tishnu@gmail.com',
        'password': 'Access@404'
    }

    login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data, timeout=10)
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test the search that worked before
    search_data = {
        'query': 'troubleshooting',
        'limit': 3
    }
    
    search_response = requests.post('http://localhost:8000/api/v1/ai/search', 
                                  json=search_data, 
                                  headers=headers,
                                  timeout=10)
    
    if search_response.status_code == 200:
        result = search_response.json()
        print(f"✅ Found {result['total_results']} results for 'troubleshooting'")
        
        if result['total_results'] > 0:
            # Now test chat with a troubleshooting question
            chat_data = {
                'message': 'I need help with troubleshooting my machine',
                'conversation_id': 'test_chat'
            }
            
            chat_response = requests.post('http://localhost:8000/api/v1/ai/chat',
                                        json=chat_data,
                                        headers=headers,
                                        timeout=15)
            
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                print(f"\n💬 AI Response:")
                print(f"{chat_result.get('response', 'No response')}")
            else:
                print(f"❌ Chat failed: {chat_response.status_code}")
        
    else:
        print(f"❌ Search failed: {search_response.status_code}")

if __name__ == "__main__":
    test_simple_search()
