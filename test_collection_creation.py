#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service

async def test_collection_creation():
    """Test Weaviate collection creation directly."""
    print("🧪 TESTING WEAVIATE COLLECTION CREATION")
    print("=" * 50)
    
    try:
        # Initialize AI service first
        print("1. Initializing AI service...")
        init_result = await ai_service.initialize()
        print(f"   Initialization result: {init_result}")
        
        # Check connection
        print("\n2. Testing Weaviate connection...")
        if ai_service.weaviate.is_connected:
            print("   ✅ Weaviate is connected")
        else:
            print("   ❌ Weaviate is NOT connected")
            # Try to connect manually
            print("   🔄 Attempting manual connection...")
            connect_result = await ai_service.weaviate.connect()
            print(f"   Connection result: {connect_result}")
        
        # Check existing collections
        print("\n3. Checking existing collections...")
        status = await ai_service.weaviate.health_check()
        print(f"   Collections: {status.get('collections', [])}")
        print(f"   Object count: {status.get('count', 0)}")
        
        # Test collection creation
        print("\n4. Testing collection creation...")
        result = await ai_service._ensure_collection_exists()
        print(f"   Collection creation result: {result}")
        
        # Check collections after creation attempt
        print("\n5. Checking collections after creation...")
        status = await ai_service.weaviate.health_check()
        print(f"   Collections: {status.get('collections', [])}")
        print(f"   Object count: {status.get('count', 0)}")
        
        # Test document storage
        print("\n6. Testing document storage...")
        test_data = {
            "filename": "test.txt",
            "content": "This is test content for the training system. It should be stored in Weaviate and chunked properly.",
            "file_type": "text/plain",
            "uploaded_by": "test@example.com",
            "upload_date": "2025-08-09T12:00:00",
            "file_size": 100
        }
        
        await ai_service._store_training_document("test_123", test_data)
        print("   ✅ Document storage completed")
        
        # Final status check
        print("\n7. Final status check...")
        status = await ai_service.weaviate.health_check()
        print(f"   Collections: {status.get('collections', [])}")
        print(f"   Object count: {status.get('count', 0)}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_collection_creation())
