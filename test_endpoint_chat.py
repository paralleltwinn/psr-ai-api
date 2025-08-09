import requests
import json

def test_chat_endpoint():
    """Test the chat endpoint with authentication to verify trained data integration."""
    
    # Test the chat endpoint with authentication
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
        
        # Test chat endpoint
        chat_data = {
            'message': 'How do I upload training data to the system?',
            'conversation_id': 'test_conv_123'
        }
        
        print("💬 Testing chat endpoint...")
        chat_response = requests.post('http://localhost:8000/api/v1/ai/chat', 
                                    json=chat_data, 
                                    headers=headers)
        
        print(f'Chat Response Status: {chat_response.status_code}')
        
        if chat_response.status_code == 200:
            result = chat_response.json()
            print(f'✅ Chat successful!')
            print(f'Conversation ID: {result["conversation_id"]}')
            print(f'Response: {result["response"]}')
            print()
            return True
        else:
            print(f'❌ Chat failed: {chat_response.text}')
            return False
    else:
        print(f'❌ Login failed: {login_response.text}')
        return False

if __name__ == "__main__":
    test_chat_endpoint()
