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

async def reprocess_existing_pdfs():
    """Re-process existing PDF files with proper text extraction."""
    
    print("🔧 Re-processing existing PDF files with proper text extraction...")
    
    # Initialize AI service
    print("📡 Initializing AI service...")
    init_result = await ai_service.initialize()
    if not init_result.get('weaviate'):
        print("❌ Failed to connect to Weaviate")
        return
    
    print("✅ Connected to Weaviate")
    
    # Find all PDF files in uploads
    uploads_dir = Path("uploads/training")
    pdf_files = list(uploads_dir.glob("*.pdf"))
    
    print(f"📁 Found {len(pdf_files)} PDF files to reprocess")
    
    if not pdf_files:
        print("❌ No PDF files found")
        return
    
    # Process each PDF
    for i, pdf_path in enumerate(pdf_files):
        print(f"\n📄 Processing {i+1}/{len(pdf_files)}: {pdf_path.name}")
        
        try:
            # Extract text properly
            extracted_text = ""
            with open(pdf_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                print(f"   📄 Pages: {len(pdf_reader.pages)}")
                
                for page_num, page in enumerate(pdf_reader.pages):
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
                
                # Determine original filename from file_id
                file_id = pdf_path.stem  # Remove .pdf extension
                original_filename = f"{file_id}.pdf"  # We'll use the file_id as filename
                
                # Store in Weaviate with proper content
                document_data = {
                    "filename": original_filename,
                    "content": extracted_text.strip(),
                    "file_type": "application/pdf",
                    "uploaded_by": "system_reprocessing",
                    "upload_date": datetime.now(timezone.utc).isoformat(),
                    "file_size": len(extracted_text)
                }
                
                await ai_service._store_training_document(file_id, document_data)
                print(f"   ✅ Re-stored in Weaviate with proper content")
                
            else:
                print(f"   ⚠️ No text could be extracted from {pdf_path.name}")
                
        except Exception as e:
            print(f"   ❌ Error processing {pdf_path.name}: {e}")
            continue
    
    print(f"\n🎉 Reprocessing complete! Processed {len(pdf_files)} PDF files")
    
    # Test search after reprocessing
    print("\n🔍 Testing search after reprocessing...")
    search_results = await ai_service.search_knowledge_base("machine vibrating troubleshooting", limit=3)
    
    print(f"✅ Found {len(search_results)} results for 'machine vibrating troubleshooting'")
    for i, result in enumerate(search_results):
        print(f"  {i+1}. Score: {result.get('score', 0.0):.3f}")
        print(f"     File: {result.get('metadata', {}).get('filename', 'Unknown')}")
        content = result.get('content', '')[:200]
        print(f"     Content: {content}...")
        print()

if __name__ == "__main__":
    asyncio.run(reprocess_existing_pdfs())
