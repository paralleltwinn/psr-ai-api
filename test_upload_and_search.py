import requests
import json

def test_file_upload_and_search():
    """Test uploading a file and then searching for its content."""
    
    # Login first
    login_data = {
        'email': 'official.tishnu@gmail.com',
        'password': 'Access@404'
    }

    print("🔐 Logging in...")
    login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data, timeout=10)
    
    if login_response.status_code != 200:
        print(f'❌ Login failed: {login_response.text}')
        return
    
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Login successful!")
    
    # Upload the test file
    print("\n📤 Uploading test troubleshooting guide...")
    
    with open('test_troubleshooting_guide.txt', 'rb') as f:
        files = {'files': ('test_troubleshooting_guide.txt', f, 'text/plain')}
        
        upload_response = requests.post(
            'http://localhost:8000/api/v1/ai/upload-training-data',
            files=files,
            headers=headers,
            timeout=30
        )
    
    if upload_response.status_code == 200:
        upload_result = upload_response.json()
        print(f"✅ Upload successful! Files processed: {upload_result.get('files_processed', 0)}")
    else:
        print(f"❌ Upload failed: {upload_response.status_code} - {upload_response.text}")
        return
    
    # Wait a moment for processing
    import time
    print("⏳ Waiting 3 seconds for processing...")
    time.sleep(3)
    
    # Now test search for the new content
    print("\n🔍 Testing search for 'machine continuously vibrating'...")
    
    search_data = {
        'query': 'machine continuously vibrating',
        'limit': 5
    }
    
    search_response = requests.post('http://localhost:8000/api/v1/ai/search', 
                                  json=search_data, 
                                  headers=headers,
                                  timeout=10)
    
    if search_response.status_code == 200:
        result = search_response.json()
        total_results = result['total_results']
        print(f'✅ Search successful! Found {total_results} results')
        
        for i, res in enumerate(result['results'][:3]):
            print(f"\n📄 Result {i+1}:")
            print(f"  Score: {res.get('score', 'N/A')}")
            print(f"  File: {res.get('metadata', {}).get('filename', 'Unknown')}")
            content = res.get('content', '')[:200]
            print(f"  Content: {content}...")
            
    else:
        print(f"❌ Search failed: {search_response.status_code} - {search_response.text}")
    
    # Also test chat
    print("\n💬 Testing chat with the question...")
    
    chat_data = {
        'message': 'My machine is continuously vibrating. What should I check?',
        'conversation_id': 'test_troubleshooting'
    }
    
    chat_response = requests.post('http://localhost:8000/api/v1/ai/chat',
                                json=chat_data,
                                headers=headers,
                                timeout=15)
    
    if chat_response.status_code == 200:
        chat_result = chat_response.json()
        print(f"✅ Chat successful!")
        print(f"Response: {chat_result.get('response', 'No response')}")
    else:
        print(f"❌ Chat failed: {chat_response.status_code} - {chat_response.text}")

if __name__ == "__main__":
    test_file_upload_and_search()
