import PyPDF2
import os

def test_pdf_extraction():
    """Test PDF extraction on existing files."""
    
    training_data_dir = "training_data"
    pdf_files = [f for f in os.listdir(training_data_dir) if f.endswith('.pdf')]
    
    print(f"Found {len(pdf_files)} PDF files in training_data")
    
    # Test the first PDF file
    if pdf_files:
        test_file = pdf_files[0]
        file_path = os.path.join(training_data_dir, test_file)
        
        print(f"\n🧪 Testing extraction on: {test_file}")
        
        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                print(f"📄 Pages: {len(pdf_reader.pages)}")
                
                # Extract first page as test
                if len(pdf_reader.pages) > 0:
                    first_page = pdf_reader.pages[0]
                    page_text = first_page.extract_text()
                    
                    print(f"📝 First page text length: {len(page_text)} characters")
                    print(f"📝 First 200 characters:")
                    print(f"'{page_text[:200]}'")
                    
                    # Check if text looks reasonable
                    if page_text.strip() and len(page_text.strip()) > 50:
                        print("✅ PDF extraction looks good!")
                        return True
                    else:
                        print("⚠️ PDF extraction returned minimal text")
                        return False
                else:
                    print("❌ PDF has no pages")
                    return False
                    
        except Exception as e:
            print(f"❌ Error extracting PDF: {e}")
            return False
    else:
        print("❌ No PDF files found to test")
        return False

if __name__ == "__main__":
    test_pdf_extraction()
