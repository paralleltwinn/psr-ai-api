#!/usr/bin/env python3

from app.services.ai_service import ai_service
from fastapi import UploadFile
import asyncio
import io

async def test_processing():
    # Create a proper UploadFile object
    content = '{"test": "content for training"}'
    content_bytes = content.encode('utf-8')
    
    # Create a BytesIO object to simulate file upload
    file_obj = io.BytesIO(content_bytes)
    
    # Create UploadFile instance
    upload_file = UploadFile(
        filename="test.json", 
        file=file_obj, 
        headers={"content-type": "application/json"}
    )
    
    files = [upload_file]
    
    print("Testing process_training_files with proper UploadFile...")
    result = await ai_service.process_training_files(files, 'test@example.com')
    print(f'Result: {result}')

if __name__ == "__main__":
    asyncio.run(test_processing())
