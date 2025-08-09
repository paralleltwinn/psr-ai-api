import requests
import json

def test_search_endpoint():
    """Test the search endpoint with authentication to verify trained data retrieval."""
    
    # Test the search endpoint with authentication
    login_data = {
        'email': 'official.tishnu@gmail.com',
        'password': 'Access@404'
    }

    # First login to get token
    print("🔐 Logging in...")
    login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("✅ Login successful!")
        
        # Test search endpoint
        search_data = {
            'query': 'how to upload training data',
            'limit': 3
        }
        
        print("🔍 Testing search endpoint...")
        search_response = requests.post('http://localhost:8000/api/v1/ai/search', 
                                      json=search_data, 
                                      headers=headers)
        
        print(f'Search Response Status: {search_response.status_code}')
        
        if search_response.status_code == 200:
            result = search_response.json()
            print(f'✅ Search successful!')
            print(f'Total Results: {result["total_results"]}')
            print(f'Query: "{result["query"]}"')
            print()
            
            for i, res in enumerate(result['results'][:2]):
                print(f'📄 Result {i+1}:')
                print(f'  Score: {res.get("score", "N/A")}')
                content = res.get("content", "N/A")
                print(f'  Content: {content[:150]}...')
                print()
                
            return True
        else:
            print(f'❌ Search failed: {search_response.text}')
            return False
    else:
        print(f'❌ Login failed: {login_response.text}')
        return False

if __name__ == "__main__":
    test_search_endpoint()
