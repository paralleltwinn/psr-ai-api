#!/usr/bin/env python3

from app.services.ai_service import ai_service
import asyncio

async def test_document_storage():
    print('Initializing services...')
    init_result = await ai_service.initialize()
    print(f'Init result: {init_result}')
    
    # Test storing a simple document
    test_doc = {
        "filename": "test_document.txt",
        "content": "This is a test document for checking if Weaviate storage works properly. It contains some sample text that should be stored as chunks.",
        "file_type": "text/plain",
        "uploaded_by": "test_user",
        "upload_date": "2025-08-09T10:00:00Z",
        "file_size": 100
    }
    
    try:
        print('Attempting to store test document...')
        await ai_service._store_training_document("test_file_001", test_doc)
        print('Document storage completed successfully!')
        
        # Check status after storage
        print('Checking status after storage...')
        status = await ai_service.get_vector_database_status()
        print(f'Status after storage: {status}')
        
    except Exception as e:
        print(f'Error during document storage: {e}')
        import traceback
        print(f'Full traceback: {traceback.format_exc()}')
    
    await ai_service.weaviate.disconnect()

if __name__ == "__main__":
    asyncio.run(test_document_storage())
