#!/usr/bin/env python3
"""
Test Weaviate's built-in vectorizer.
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_weaviate_vectorizer():
    """Test Weaviate's built-in vectorizer."""
    print("=" * 60)
    print("WEAVIATE VECTORIZER TEST")
    print("=" * 60)
    
    try:
        # 1. Connect to Weaviate
        print("\n1. Connecting to Weaviate...")
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=settings.weaviate_url,
            auth_credentials=weaviate.auth.AuthApiKey(settings.weaviate_api_key)
        )
        
        print(f"Connected: {client.is_ready()}")
        
        # 2. Clean up existing collection
        try:
            client.collections.delete("TrainingDocuments")
            print("Deleted existing TrainingDocuments collection")
        except Exception as e:
            print(f"No existing collection to delete: {e}")
        
        # 3. Create collection with Weaviate vectorizer
        print("\n3. Creating collection with Weaviate vectorizer...")
        
        vector_config = wvc.config.Configure.VectorIndex.hnsw(
            distance_metric=wvc.config.VectorDistances.COSINE
        )
        
        collection = client.collections.create(
            name="TrainingDocuments",
            vector_index_config=vector_config,
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_weaviate(),
            properties=[
                wvc.config.Property(
                    name="chunk_id",
                    data_type=wvc.config.DataType.TEXT,
                    description="Unique identifier for the text chunk"
                ),
                wvc.config.Property(
                    name="file_id", 
                    data_type=wvc.config.DataType.TEXT,
                    description="ID of the source file"
                ),
                wvc.config.Property(
                    name="content",
                    data_type=wvc.config.DataType.TEXT,
                    description="The actual text content to be embedded"
                ),
                wvc.config.Property(
                    name="chunk_index",
                    data_type=wvc.config.DataType.INT,
                    description="Index of the chunk within the file"
                ),
                wvc.config.Property(
                    name="filename",
                    data_type=wvc.config.DataType.TEXT,
                    description="Original filename"
                ),
                wvc.config.Property(
                    name="file_type",
                    data_type=wvc.config.DataType.TEXT,
                    description="File type/extension"
                ),
                wvc.config.Property(
                    name="upload_date",
                    data_type=wvc.config.DataType.TEXT,
                    description="Date when file was uploaded"
                )
            ]
        )
        
        print("✅ Collection created successfully!")
        print(f"Collection config vectorizer: {collection.config.get().vectorizer}")
        
        # 4. Insert test data
        print("\n4. Inserting test data...")
        test_data = {
            "chunk_id": "test_chunk_001",
            "file_id": "test_file_001",
            "content": "This is a test content about LED troubleshooting and power supply issues. The 12V output is normal but the 24V output is low or zero, indicating a potential power supply fault in electronic equipment.",
            "chunk_index": 0,
            "filename": "test_service_guide.txt",
            "file_type": "txt",
            "upload_date": datetime.now().isoformat()
        }
        
        result = collection.data.insert(test_data)
        print(f"✅ Data inserted with UUID: {result}")
        
        # 5. Wait a moment for vectorization
        print("\n5. Waiting for vectorization...")
        import time
        time.sleep(5)
        
        # 6. Check if vectors were generated
        print("\n6. Checking vectors...")
        try:
            obj = collection.query.fetch_objects(limit=1, include_vector=True).objects[0]
            if hasattr(obj, 'vector') and obj.vector and len(obj.vector) > 0:
                print(f"✅ Vector generated: {len(obj.vector)} dimensions")
                print(f"   First 10 values: {obj.vector[:10]}")
            else:
                print(f"❌ No vector generated")
                print(f"   Object: {obj}")
        except Exception as e:
            print(f"Error checking vectors: {e}")
        
        # 7. Test semantic search
        print("\n7. Testing semantic search...")
        try:
            search_results = collection.query.near_text(
                query="power supply problem 24V voltage issue",
                limit=1
            )
            
            if search_results.objects:
                obj = search_results.objects[0]
                print(f"✅ Search successful!")
                print(f"   Content: {obj.properties['content'][:100]}...")
                if hasattr(obj.metadata, 'distance'):
                    print(f"   Distance: {obj.metadata.distance}")
            else:
                print("❌ No search results")
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
        
        # 8. Collection stats
        print("\n8. Collection statistics...")
        try:
            aggregate = collection.aggregate.over_all(total_count=True)
            print(f"Total objects: {aggregate.total_count}")
        except Exception as e:
            print(f"Error getting stats: {e}")
        
        print("\n🎉 WEAVIATE VECTORIZER TEST COMPLETED!")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            client.close()
            print("Closed Weaviate connection")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_weaviate_vectorizer())
