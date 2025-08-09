import PyPDF2
import os

def test_existing_pdf_extraction():
    """Test PDF extraction on existing uploaded files."""
    
    uploads_dir = "uploads/training"
    
    if not os.path.exists(uploads_dir):
        print("❌ Uploads directory not found")
        return
    
    pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
    
    print(f"Found {len(pdf_files)} PDF files in uploads/training")
    
    if pdf_files:
        test_file = pdf_files[0]
        file_path = os.path.join(uploads_dir, test_file)
        
        print(f"\n🧪 Testing extraction on: {test_file}")
        
        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                print(f"📄 Pages: {len(pdf_reader.pages)}")
                
                # Extract first few pages
                extracted_text = ""
                for page_num, page in enumerate(pdf_reader.pages[:3]):  # First 3 pages
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            extracted_text += f"\n--- Page {page_num + 1} ---\n"
                            extracted_text += page_text[:500]  # First 500 chars per page
                            extracted_text += "\n"
                    except Exception as page_error:
                        print(f"⚠️ Error on page {page_num + 1}: {page_error}")
                
                print(f"📝 Total extracted text length: {len(extracted_text)} characters")
                print(f"📝 Sample extracted text:")
                print("=" * 50)
                print(extracted_text[:800])
                print("=" * 50)
                
                # Check if this looks like readable text
                readable_chars = sum(1 for c in extracted_text if c.isalnum() or c.isspace())
                total_chars = len(extracted_text)
                
                if total_chars > 0:
                    readability_ratio = readable_chars / total_chars
                    print(f"📊 Readability ratio: {readability_ratio:.2f} ({readable_chars}/{total_chars})")
                    
                    if readability_ratio > 0.7 and total_chars > 100:
                        print("✅ PDF extraction produces readable text!")
                        return True
                    else:
                        print("⚠️ PDF extraction may have encoding issues")
                        return False
                else:
                    print("❌ No text extracted")
                    return False
                    
        except Exception as e:
            print(f"❌ Error extracting PDF: {e}")
            return False
    else:
        print("❌ No PDF files found to test")
        return False

if __name__ == "__main__":
    test_existing_pdf_extraction()
