import weaviate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_weaviate_collection():
    """Check what's actually stored in the Weaviate collection."""
    
    # Connect to Weaviate
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY"))
    )
    
    if not client.is_ready():
        print("❌ Failed to connect to Weaviate")
        return
    
    print("✅ Connected to Weaviate")
    
    # Get the collection
    collection = client.collections.get("TrainingDocuments")
    
    # Count total documents
    print(f"\n📊 Total documents in collection: {collection.aggregate.over_all(total_count=True).total_count}")
    
    # Get some recent documents
    print("\n📄 Recent documents:")
    recent_docs = collection.query.fetch_objects(limit=10)
    
    for i, doc in enumerate(recent_docs.objects):
        filename = doc.properties.get("filename", "Unknown")
        content = doc.properties.get("content", "")[:100]
        upload_date = doc.properties.get("upload_date", "Unknown")
        
        print(f"  {i+1}. File: {filename}")
        print(f"     Date: {upload_date}")
        print(f"     Content: {content}...")
        print()
    
    # Search for our new content specifically
    print("\n🔍 Searching for 'troubleshooting guide':")
    search_results = collection.query.bm25(
        query="troubleshooting guide",
        limit=5,
        return_metadata=["score"]
    )
    
    print(f"Found {len(search_results.objects)} results:")
    for i, result in enumerate(search_results.objects):
        filename = result.properties.get("filename", "Unknown")
        content = result.properties.get("content", "")[:150]
        score = result.metadata.score if hasattr(result.metadata, 'score') else 0.0
        
        print(f"  {i+1}. Score: {score}")
        print(f"     File: {filename}")
        print(f"     Content: {content}...")
        print()
    
    client.close()

if __name__ == "__main__":
    check_weaviate_collection()
