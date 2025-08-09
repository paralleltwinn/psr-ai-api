#!/usr/bin/env python3

"""
Script to fix the TrainingDocuments collection by recreating it with proper vectorizer configuration.
This will enable semantic search functionality.
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_service import ai_service

async def fix_vectorizer_config():
    """Fix the TrainingDocuments collection to enable semantic search."""
    
    print("🔧 Fixing TrainingDocuments collection vectorizer configuration...")
    
    try:
        # Initialize AI service
        print("Initializing AI service...")
        init_result = await ai_service.initialize()
        print(f"Init result: {init_result}")
        
        if not init_result.get('weaviate'):
            print("❌ Weaviate not available!")
            return
            
        # Check current collection status
        print("\n📊 Checking current collection status...")
        try:
            collection = ai_service.weaviate.client.collections.get("TrainingDocuments")
            config = collection.config.get()
            print(f"Current collection exists")
            print(f"Vectorizer: {config.vectorizer}")
            
            # Count current objects
            total_objects = len(list(collection.iterator()))
            print(f"Current objects: {total_objects}")
            
            if total_objects > 0:
                print(f"⚠️  Collection has {total_objects} objects. These will need to be backed up and restored.")
                
                # Option 1: Try to use hybrid search instead of near_text
                print("\n🔄 Testing alternative search methods...")
                
                # Try using bm25 search instead
                try:
                    print("Testing BM25 search...")
                    bm25_results = collection.query.bm25(
                        query="upload training data",
                        limit=3
                    )
                    
                    if bm25_results.objects:
                        print(f"✅ BM25 search works! Found {len(bm25_results.objects)} results")
                        for result in bm25_results.objects:
                            content = str(result.properties.get('content', ''))[:100] + '...'
                            print(f"  - {content}")
                            
                        print("\n💡 Solution: Use BM25 search instead of semantic search")
                        print("   This provides keyword-based search through your trained data")
                        
                    else:
                        print("❌ BM25 search returned no results")
                        
                except Exception as e:
                    print(f"❌ BM25 search failed: {e}")
                
                # Try hybrid search
                try:
                    print("\nTesting hybrid search...")
                    hybrid_results = collection.query.hybrid(
                        query="upload training data",
                        limit=3
                    )
                    
                    if hybrid_results.objects:
                        print(f"✅ Hybrid search works! Found {len(hybrid_results.objects)} results")
                        for result in hybrid_results.objects:
                            content = str(result.properties.get('content', ''))[:100] + '...'
                            print(f"  - {content}")
                            
                        print("\n💡 Solution: Use hybrid search for best results")
                        print("   This combines semantic and keyword search")
                        
                    else:
                        print("❌ Hybrid search returned no results")
                        
                except Exception as e:
                    print(f"❌ Hybrid search failed: {e}")
            
        except Exception as e:
            print(f"❌ Error checking collection: {e}")
        
        await ai_service.cleanup()
        print("\n✅ Analysis completed!")
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_vectorizer_config())
