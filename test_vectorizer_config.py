#!/usr/bin/env python3
"""
Test the actual vectorizer configuration in Weaviate cloud.
"""

import asyncio
import logging
import weaviate
import weaviate.classes as wvc
from datetime import datetime
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import settings
from app.config import settings

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_vectorizer_config():
    """Test what vectorizers are available in the Weaviate cloud instance."""
    print("=" * 60)
    print("WEAVIATE VECTORIZER CONFIGURATION TEST")
    print("=" * 60)
    
    try:
        # 1. Connect to Weaviate
        print("\n1. Connecting to Weaviate...")
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=settings.weaviate_url,
            auth_credentials=weaviate.auth.AuthApiKey(settings.weaviate_api_key)
        )
        
        print(f"Connected: {client.is_ready()}")
        
        # 2. Check available modules
        print("\n2. Checking available modules...")
        try:
            meta_info = client.get_meta()
            print("Meta information:", meta_info)
            
            if 'modules' in meta_info:
                print("Available modules:")
                for module_name, module_info in meta_info['modules'].items():
                    print(f"  - {module_name}: {module_info}")
            else:
                print("No modules information found")
                
        except Exception as e:
            print(f"Error getting meta info: {e}")
        
        # 3. Clean up existing collection
        print("\n3. Cleaning up existing collection...")
        try:
            client.collections.delete("TrainingDocuments")
            print("Deleted existing collection")
        except Exception as e:
            print(f"No existing collection to delete: {e}")
        
        # 4. Test different vectorizer configurations
        vectorizer_tests = [
            ("none", None),
            ("text2vec-openai", wvc.config.Configure.Vectorizer.text2vec_openai()),
            ("text2vec-transformers", wvc.config.Configure.Vectorizer.text2vec_transformers()),
            ("text2vec-cohere", wvc.config.Configure.Vectorizer.text2vec_cohere()),
        ]
        
        for vectorizer_name, vectorizer_config in vectorizer_tests:
            print(f"\n4.{vectorizer_tests.index((vectorizer_name, vectorizer_config)) + 1} Testing vectorizer: {vectorizer_name}")
            
            try:
                # Vector index config
                vector_config = wvc.config.Configure.VectorIndex.hnsw(
                    distance_metric=wvc.config.VectorDistances.COSINE
                )
                
                # Create collection arguments
                create_args = {
                    "name": "TestCollection",
                    "vector_index_config": vector_config,
                    "properties": [
                        wvc.config.Property(
                            name="content",
                            data_type=wvc.config.DataType.TEXT,
                            description="Test content"
                        )
                    ]
                }
                
                # Add vectorizer config if provided
                if vectorizer_config:
                    create_args["vectorizer_config"] = vectorizer_config
                
                # Try to create collection
                collection = client.collections.create(**create_args)
                print(f"  ✅ SUCCESS: {vectorizer_name} vectorizer works")
                
                # Test data insertion
                test_data = {
                    "content": "This is a test content for vectorization"
                }
                
                result = collection.data.insert(test_data)
                print(f"  ✅ Data inserted with UUID: {result}")
                
                # Check if vectors were generated
                obj = collection.query.fetch_objects(limit=1).objects[0]
                if hasattr(obj, 'vector') and obj.vector:
                    print(f"  ✅ Vector generated: {len(obj.vector)} dimensions")
                else:
                    print(f"  ❌ No vector generated")
                
                # Clean up
                client.collections.delete("TestCollection")
                print(f"  🧹 Cleaned up test collection")
                
                # If this vectorizer works, we found our solution
                if vectorizer_config:
                    print(f"\n🎉 SOLUTION FOUND: Use {vectorizer_name} vectorizer")
                    break
                    
            except Exception as e:
                print(f"  ❌ FAILED: {vectorizer_name} - {e}")
                continue
        
        print("\n" + "=" * 60)
        print("VECTORIZER TEST COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"Critical error in test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            client.close()
            print("Closed Weaviate connection")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_vectorizer_config())
