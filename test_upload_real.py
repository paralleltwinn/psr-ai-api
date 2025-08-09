#!/usr/bin/env python3

import requests
import tempfile
import json
import os

def test_actual_upload():
    # Authenticate
    response = requests.post('http://127.0.0.1:8000/api/v1/auth/login', json={
        'email': 'official4tishnu@gmail.com', 
        'password': 'Access@404'
    })
    token = response.json()['access_token']
    
    # Create a temporary file similar to the production trainer
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        test_data = {
            "test": "content for training",
            "description": "Test training data"
        }
        json.dump(test_data, temp_file, indent=2)
        temp_filename = temp_file.name
    
    try:
        # Upload the file exactly like the production trainer
        with open(temp_filename, 'rb') as f:
            files = {'files': ('test_training.json', f, 'application/json')}
            headers = {'Authorization': f'Bearer {token}'}
            
            print("Uploading file...")
            response = requests.post(
                'http://127.0.0.1:8000/api/v1/ai/upload-training-data', 
                files=files, 
                headers=headers
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
    finally:
        # Clean up
        os.unlink(temp_filename)

if __name__ == "__main__":
    test_actual_upload()
