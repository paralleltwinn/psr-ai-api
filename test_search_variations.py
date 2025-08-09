import requests
import json

def test_different_search_queries():
    """Test different search queries to understand what's in the trained data."""
    
    # Login first
    login_data = {
        'email': 'official.tishnu@gmail.com',
        'password': 'Access@404'
    }

    print("🔐 Logging in...")
    login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
    
    if login_response.status_code != 200:
        print(f'❌ Login failed: {login_response.text}')
        return
    
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Login successful!")
    
    # Test various search queries
    test_queries = [
        "machine vibrating",
        "troubleshooting",
        "service guide",
        "upload",
        "training",
        "file",
        "data",
        "problem",
        "error",
        "maintenance"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        
        search_data = {
            'query': query,
            'limit': 3
        }
        
        search_response = requests.post('http://localhost:8000/api/v1/ai/search', 
                                      json=search_data, 
                                      headers=headers)
        
        if search_response.status_code == 200:
            result = search_response.json()
            total_results = result['total_results']
            print(f'  Results found: {total_results}')
            
            if total_results > 0:
                print(f'  Top result score: {result["results"][0].get("score", "N/A")}')
                content = result["results"][0].get("content", "")[:100]
                print(f'  Content preview: {content}...')
            else:
                print('  No results found')
        else:
            print(f'  ❌ Search failed: {search_response.status_code}')
            
        # Stop at first successful query to avoid spam
        if search_response.status_code == 200 and result['total_results'] > 0:
            print("\n✅ Found working query, stopping test")
            break

if __name__ == "__main__":
    test_different_search_queries()
