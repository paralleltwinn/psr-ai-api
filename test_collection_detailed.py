#!/usr/bin/env python3
"""
Enhanced test for Weaviate collection creation with detailed debugging.
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

async def test_collection_creation_detailed():
    """Test collection creation with detailed debugging."""
    print("=" * 60)
    print("ENHANCED WEAVIATE COLLECTION CREATION TEST")
    print("=" * 60)
    
    try:
        # 1. Connect to Weaviate
        print("\n1. Connecting to Weaviate...")
        print(f"Using URL: {settings.weaviate_url}")
        print(f"Using API Key: {settings.weaviate_api_key[:20]}...")
        
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=settings.weaviate_url,
            auth_credentials=weaviate.auth.AuthApiKey(settings.weaviate_api_key)
        )
        
        print(f"Connected: {client.is_ready()}")
        
        # 2. Check existing collections
        print("\n2. Checking existing collections...")
        try:
            collections = list(client.collections.list_all())
            print(f"Existing collections: {[col.name for col in collections]}")
        except Exception as e:
            print(f"Error listing collections: {e}")
        
        # 3. Delete collection if it exists (for clean test)
        print("\n3. Cleaning up existing collection...")
        try:
            existing_collection = client.collections.get("TrainingDocuments")
            print("Found existing TrainingDocuments collection - deleting it")
            client.collections.delete("TrainingDocuments")
            print("Deleted existing collection")
        except Exception as e:
            print(f"No existing collection to delete (this is normal): {e}")
        
        # 4. Create collection with detailed logging
        print("\n4. Creating new collection...")
        
        # Vector index config
        vector_config = wvc.config.Configure.VectorIndex.hnsw(
            distance_metric=wvc.config.VectorDistances.COSINE
        )
        print("Created vector config")
        
        # Define properties
        properties = [
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
        print(f"Defined {len(properties)} properties")
        
        # Create collection
        print("Creating collection...")
        collection = client.collections.create(
            name="TrainingDocuments",
            vector_index_config=vector_config,
            properties=properties
        )
        print(f"Collection creation returned: {collection}")
        
        # 5. Verify collection exists
        print("\n5. Verifying collection exists...")
        try:
            test_collection = client.collections.get("TrainingDocuments")
            print(f"Successfully retrieved collection: {test_collection}")
            print(f"Collection config: {test_collection.config}")
        except Exception as e:
            print(f"Error retrieving collection: {e}")
        
        # 6. List all collections again
        print("\n6. Listing all collections after creation...")
        try:
            collections = list(client.collections.list_all())
            print(f"All collections: {[col.name for col in collections]}")
        except Exception as e:
            print(f"Error listing collections: {e}")
        
        # 7. Insert test data
        print("\n7. Inserting test data...")
        try:
            test_data = {
                "chunk_id": "test_chunk_001",
                "file_id": "test_file_001",
                "content": "This is a test content chunk for Weaviate storage verification.",
                "chunk_index": 0,
                "filename": "test_document.txt",
                "file_type": "txt",
                "upload_date": datetime.utcnow().isoformat()
            }
            
            result = test_collection.data.insert(test_data)
            print(f"Insert result: {result}")
            
        except Exception as e:
            print(f"Error inserting test data: {e}")
            import traceback
            traceback.print_exc()
        
        # 8. Query collection stats
        print("\n8. Checking collection stats...")
        try:
            aggregate = test_collection.aggregate.over_all(total_count=True)
            print(f"Total objects in collection: {aggregate.total_count}")
        except Exception as e:
            print(f"Error getting collection stats: {e}")
        
        # 9. Test search
        print("\n9. Testing search...")
        try:
            response = test_collection.query.fetch_objects(limit=5)
            print(f"Objects in collection: {len(response.objects)}")
            for obj in response.objects:
                print(f"  - UUID: {obj.uuid}, Properties: {obj.properties}")
        except Exception as e:
            print(f"Error searching collection: {e}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED")
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
    asyncio.run(test_collection_creation_detailed())
