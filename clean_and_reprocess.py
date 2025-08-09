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

async def clean_and_reprocess_pdfs():
    """Clean old corrupted entries and reprocess PDFs with proper text extraction."""
    
    print("🧹 Cleaning and re-processing PDF files with proper text extraction...")
    
    # Initialize AI service
    print("📡 Initializing AI service...")
    init_result = await ai_service.initialize()
    if not init_result.get('weaviate'):
        print("❌ Failed to connect to Weaviate")
        return
    
    print("✅ Connected to Weaviate")
    
    # Get collection
    collection = ai_service.weaviate.client.collections.get("TrainingDocuments")
    
    # First, let's identify PDF entries to replace
    print("🔍 Finding existing PDF entries...")
    
    pdf_entries = collection.query.fetch_objects(
        where={
            "path": ["file_type"],
            "operator": "Equal",
            "valueText": "application/pdf"
        },
        limit=1000  # Get all PDF entries
    )
    
    print(f"📄 Found {len(pdf_entries.objects)} existing PDF entries in Weaviate")
    
    # Delete existing PDF entries
    if pdf_entries.objects:
        print("🗑️ Deleting old corrupted PDF entries...")
        for entry in pdf_entries.objects:
            try:
                collection.data.delete_by_id(entry.uuid)
                print(f"   ✅ Deleted entry: {entry.properties.get('filename', 'Unknown')}")
            except Exception as e:
                print(f"   ⚠️ Error deleting entry: {e}")
    
    # Find all PDF files in uploads
    uploads_dir = Path("uploads/training")
    pdf_files = list(uploads_dir.glob("*.pdf"))
    
    print(f"\n📁 Found {len(pdf_files)} PDF files to reprocess")
    
    if not pdf_files:
        print("❌ No PDF files found")
        return
    
    # Process each PDF with proper extraction
    successful_extractions = 0
    
    for i, pdf_path in enumerate(pdf_files):
        print(f"\n📄 Processing {i+1}/{len(pdf_files)}: {pdf_path.name}")
        
        try:
            # Extract text properly using our improved method
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
            
            if extracted_text.strip() and len(extracted_text.strip()) > 100:
                print(f"   ✅ Extracted {len(extracted_text)} characters of readable text")
                
                # Determine original filename
                file_id = pdf_path.stem
                
                # Use a more descriptive filename based on content preview
                content_preview = extracted_text.strip()[:200].replace('\n', ' ')
                if "Comprehensive Technical Troubleshooting Guide" in content_preview:
                    original_filename = "Comprehensive Technical Troubleshooting Guide.pdf"
                elif "Service Guide" in content_preview:
                    original_filename = "Service Guide.pdf"
                else:
                    original_filename = f"{file_id}.pdf"
                
                # Store in Weaviate with proper content and RFC3339 date
                document_data = {
                    "filename": original_filename,
                    "content": extracted_text.strip(),
                    "file_type": "application/pdf",
                    "uploaded_by": "system_reprocessing",
                    "upload_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "file_size": len(extracted_text)
                }
                
                await ai_service._store_training_document(file_id, document_data)
                print(f"   ✅ Successfully stored '{original_filename}' in Weaviate")
                successful_extractions += 1
                
            else:
                print(f"   ⚠️ No meaningful text could be extracted from {pdf_path.name}")
                
        except Exception as e:
            print(f"   ❌ Error processing {pdf_path.name}: {e}")
            continue
    
    print(f"\n🎉 Reprocessing complete!")
    print(f"   📄 Total PDFs processed: {len(pdf_files)}")
    print(f"   ✅ Successful extractions: {successful_extractions}")
    
    # Test search after reprocessing
    print(f"\n🔍 Testing search after reprocessing...")
    
    test_queries = [
        "machine continuously vibrating",
        "troubleshooting guide",
        "VIBRO system",
        "power supply"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Testing: '{query}'")
        search_results = await ai_service.search_knowledge_base(query, limit=2)
        
        print(f"   ✅ Found {len(search_results)} results")
        for i, result in enumerate(search_results):
            score = result.get('score', 0.0)
            filename = result.get('metadata', {}).get('filename', 'Unknown')
            content = result.get('content', '')[:150].replace('\n', ' ')
            print(f"   {i+1}. Score: {score:.3f} | File: {filename}")
            print(f"      Content: {content}...")
    
    # Close Weaviate connection properly
    if hasattr(ai_service.weaviate, 'client'):
        ai_service.weaviate.client.close()

if __name__ == "__main__":
    asyncio.run(clean_and_reprocess_pdfs())
