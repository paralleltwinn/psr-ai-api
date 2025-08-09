import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.ai_service import ai_service
import PyPDF2
from datetime import datetime, timezone

async def simple_reprocess_test():
    """Simple test to reprocess one PDF with proper text extraction."""
    
    print("🧪 Testing PDF reprocessing with one file...")
    
    # Initialize AI service
    print("📡 Initializing AI service...")
    init_result = await ai_service.initialize()
    if not init_result.get('weaviate'):
        print("❌ Failed to connect to Weaviate")
        return
    
    print("✅ Connected to Weaviate")
    
    # Find one PDF file
    uploads_dir = Path("uploads/training")
    pdf_files = list(uploads_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found")
        return
    
    # Test with first PDF
    pdf_path = pdf_files[0]
    print(f"\n📄 Testing with: {pdf_path.name}")
    
    try:
        # Extract text properly
        extracted_text = ""
        with open(pdf_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            print(f"   📄 Pages: {len(pdf_reader.pages)}")
            
            for page_num, page in enumerate(pdf_reader.pages[:5]):  # First 5 pages
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        extracted_text += f"\n--- Page {page_num + 1} ---\n"
                        extracted_text += page_text
                        extracted_text += "\n"
                except Exception as page_error:
                    print(f"   ⚠️ Error on page {page_num + 1}: {page_error}")
                    continue
        
        if extracted_text.strip():
            print(f"   ✅ Extracted {len(extracted_text)} characters")
            print(f"   📝 Sample content:")
            print("=" * 60)
            print(extracted_text[:800])
            print("=" * 60)
            
            # Store with new file_id to avoid conflicts
            new_file_id = f"reprocessed_{pdf_path.stem}"
            
            document_data = {
                "filename": "Comprehensive Technical Troubleshooting Guide.pdf",
                "content": extracted_text.strip(),
                "file_type": "application/pdf",
                "uploaded_by": "system_reprocessing",
                "upload_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "file_size": len(extracted_text)
            }
            
            await ai_service._store_training_document(new_file_id, document_data)
            print(f"   ✅ Stored as '{new_file_id}' in Weaviate")
            
            # Test search immediately
            print(f"\n🔍 Testing search for 'machine vibrating'...")
            search_results = await ai_service.search_knowledge_base("machine vibrating", limit=5)
            
            print(f"✅ Found {len(search_results)} results")
            for i, result in enumerate(search_results):
                score = result.get('score', 0.0)
                filename = result.get('metadata', {}).get('filename', 'Unknown')
                content = result.get('content', '')[:200].replace('\n', ' ')
                print(f"  {i+1}. Score: {score:.3f} | File: {filename}")
                print(f"     Content: {content}...")
                print()
                
            # Test chat
            print(f"💬 Testing chat with machine vibrating question...")
            chat_response = await ai_service.generate_chat_response(
                message="My machine is continuously vibrating. What should I check according to the troubleshooting guide?",
                conversation_id="test_reprocessing",
                user_email="test@example.com"
            )
            
            print(f"🤖 AI Response:")
            print(chat_response)
            
        else:
            print(f"   ⚠️ No meaningful text extracted")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Close connection
    if hasattr(ai_service.weaviate, 'client'):
        ai_service.weaviate.client.close()

if __name__ == "__main__":
    asyncio.run(simple_reprocess_test())
