#!/usr/bin/env python3

import weaviate
import os
from dotenv import load_dotenv

def check_weaviate_data():
    """Check what data is stored in Weaviate."""
    load_dotenv()

    # Connect to Weaviate
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv('WEAVIATE_URL'),
        auth_credentials=weaviate.auth.AuthApiKey(os.getenv('WEAVIATE_API_KEY'))
    )

    print('✅ Connected to Weaviate')

    try:
        # Check collections
        collections = client.collections.list_all()
        print(f'📁 Available collections: {list(collections.keys())}')

        # Check TrainingDocuments collection
        if 'TrainingDocuments' in collections:
            training_docs = client.collections.get('TrainingDocuments')
            
            # Get object count
            count_result = training_docs.aggregate.over_all(total_count=True)
            total_count = count_result.total_count
            print(f'📊 Total documents in collection: {total_count}')
            
            if total_count > 0:
                # Get first few documents
                docs = training_docs.query.fetch_objects(limit=3)
                print(f'📄 Sample documents:')
                for i, doc in enumerate(docs.objects):
                    props = doc.properties
                    file_id = props.get('file_id', 'N/A')
                    content = props.get('content', 'N/A')
                    metadata = props.get('metadata', {})
                    
                    print(f'  {i+1}. File ID: {file_id}')
                    print(f'     Content preview: {content[:100]}...')
                    print(f'     Metadata: {metadata}')
                    print()
            else:
                print('📄 No documents found in collection')
        else:
            print('❌ TrainingDocuments collection not found')

    except Exception as e:
        print(f'❌ Error checking Weaviate: {e}')
    finally:
        client.close()
        print('🔐 Connection closed')

if __name__ == "__main__":
    check_weaviate_data()
