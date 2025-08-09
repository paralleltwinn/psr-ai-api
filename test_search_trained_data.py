#!/usr/bin/env python3

"""
Test script to verify that the search endpoint returns actual trained data from Weaviate.
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_service import ai_service

async def test_search_trained_data():
    """Test searching for actual trained data."""
    
    print("🔍 Testing trained data search...")
    
    try:
        # Initialize AI service
        print("Initializing AI service...")
        init_result = await ai_service.initialize()
        print(f"Init result: {init_result}")
        
        if not init_result.get('weaviate'):
            print("❌ Weaviate not available!")
            return
            
        # Test various search queries
        test_queries = [
            "how to upload training data",
            "machine troubleshooting",
            "Poornasree AI features",
            "API documentation",
            "file upload process"
        ]
        
        for query in test_queries:
            print(f"\n📋 Searching for: '{query}'")
            
            # Search using the AI service (same method used by /search endpoint)
            results = await ai_service.search_knowledge_base(query, limit=3)
            
            if results:
                print(f"✅ Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    content = result.get('content', '')[:200] + '...' if len(result.get('content', '')) > 200 else result.get('content', '')
                    score = result.get('score', 0)
                    metadata = result.get('metadata', {})
                    filename = metadata.get('filename', 'Unknown')
                    
                    print(f"  {i}. Score: {score:.3f} | File: {filename}")
                    print(f"     Content: {content}")
                    print()
            else:
                print(f"❌ No results found for '{query}'")
        
        # Test chat response generation
        print("\n💬 Testing chat response generation...")
        test_message = "How do I upload training data to Poornasree AI?"
        
        response = await ai_service.generate_chat_response(
            message=test_message,
            conversation_id="test_conv",
            user_email="test@example.com"
        )
        
        print(f"Question: {test_message}")
        print(f"AI Response: {response}")
        
        await ai_service.cleanup()
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search_trained_data())
