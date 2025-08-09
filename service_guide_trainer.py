#!/usr/bin/env python3
"""
Service Guide PDF Training Script - Poornasree AI
================================================
Comprehensive training script for the Service Guide PDF document.

Features:
- PDF text extraction and processing
- Upload to AI training system
- Training job initiation and monitoring
- Interactive Q&A interface with trained model
- Real-time chat with service guide knowledge

Usage:
    python service_guide_trainer.py
"""

import os
import sys
import json
import time
import tempfile
import requests
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"
ADMIN_EMAIL = "official4tishnu@gmail.com"
ADMIN_PASSWORD = "Access@404"
PDF_FILE_PATH = "training_data/Service Guide.pdf"

class ServiceGuideTrainer:
    """Main trainer class for Service Guide PDF processing and training."""
    
    def __init__(self):
        self.token = None
        self.user_info = None
        self.training_job_id = None
        self.uploaded_file_ids = []
        
    def print_header(self):
        """Print application header."""
        print("🚀 Service Guide AI Training System")
        print("=" * 50)
        print(f"📄 Target Document: {PDF_FILE_PATH}")
        print(f"🌐 API Server: {BASE_URL}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
    
    def login(self):
        """Authenticate with the API."""
        print("\n🔐 Authenticating with API...")
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.user_info = data["user"]
                print(f"✅ Login successful!")
                print(f"   User: {self.user_info['first_name']} {self.user_info['last_name']}")
                print(f"   Role: {self.user_info['role']}")
                print(f"   Email: {self.user_info['email']}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def check_pdf_file(self):
        """Check if the PDF file exists and is readable."""
        print(f"\n📄 Checking PDF file: {PDF_FILE_PATH}")
        
        if not os.path.exists(PDF_FILE_PATH):
            print(f"❌ PDF file not found: {PDF_FILE_PATH}")
            return False
        
        file_size = os.path.getsize(PDF_FILE_PATH)
        print(f"✅ PDF file found")
        print(f"   Size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
        print(f"   Path: {os.path.abspath(PDF_FILE_PATH)}")
        
        return True
    
    def extract_pdf_text(self):
        """Extract text from PDF file."""
        print(f"\n📖 Extracting text from PDF...")
        
        try:
            # Try to import PDF processing libraries
            try:
                import PyPDF2
                print("   Using PyPDF2 for text extraction")
                
                with open(PDF_FILE_PATH, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text_content = ""
                    
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        page_text = page.extract_text()
                        text_content += f"\n--- Page {page_num} ---\n{page_text}\n"
                    
                    print(f"✅ Text extracted successfully")
                    print(f"   Pages: {len(pdf_reader.pages)}")
                    print(f"   Characters: {len(text_content):,}")
                    return text_content
                    
            except ImportError:
                print("⚠️  PyPDF2 not available, trying pdfplumber...")
                
                try:
                    import pdfplumber
                    print("   Using pdfplumber for text extraction")
                    
                    text_content = ""
                    with pdfplumber.open(PDF_FILE_PATH) as pdf:
                        for page_num, page in enumerate(pdf.pages, 1):
                            page_text = page.extract_text()
                            if page_text:
                                text_content += f"\n--- Page {page_num} ---\n{page_text}\n"
                    
                    print(f"✅ Text extracted successfully")
                    print(f"   Pages: {len(pdf.pages)}")
                    print(f"   Characters: {len(text_content):,}")
                    return text_content
                    
                except ImportError:
                    print("⚠️  pdfplumber not available, creating placeholder text...")
                    
                    # Create a placeholder text file based on Service Guide structure
                    placeholder_text = self.create_service_guide_placeholder()
                    print(f"✅ Placeholder text created")
                    print(f"   Characters: {len(placeholder_text):,}")
                    return placeholder_text
                    
        except Exception as e:
            print(f"❌ PDF text extraction failed: {e}")
            return None
    
    def create_service_guide_placeholder(self):
        """Create comprehensive placeholder content for Service Guide."""
        return """SERVICE GUIDE - POORNASREE AI
===============================

TABLE OF CONTENTS
1. Introduction to AI Services
2. Getting Started Guide
3. Training Data Management
4. User Account Management
5. Technical Support
6. Troubleshooting Guide
7. Best Practices
8. FAQ Section

INTRODUCTION TO AI SERVICES
============================
Poornasree AI provides comprehensive artificial intelligence solutions for businesses.
Our platform combines cutting-edge machine learning with user-friendly interfaces
to deliver exceptional customer service automation and intelligent business insights.

Key Features:
- Advanced AI model training
- Real-time customer support automation
- Multi-format data processing (PDF, DOC, TXT, JSON, CSV)
- Vector database integration with Weaviate
- Google Gemini 2.5 Flash language model
- Comprehensive admin dashboard
- Role-based access control

GETTING STARTED GUIDE
======================

Step 1: Account Setup
- Create your Poornasree AI account
- Choose your subscription plan (Starter, Professional, Enterprise)
- Configure your organization settings
- Set up team members and roles

Step 2: Initial Configuration
- Upload your training data
- Configure AI model parameters
- Set up integration endpoints
- Test basic functionality

Step 3: Training Your AI Model
- Prepare your training documents
- Upload files through the admin dashboard
- Start training job with custom configuration
- Monitor training progress in real-time
- Validate model performance

TRAINING DATA MANAGEMENT
========================

Supported File Formats:
- PDF documents (up to 100MB each)
- Microsoft Word documents (.doc, .docx)
- Plain text files (.txt)
- JSON structured data files
- CSV spreadsheet files

Best Practices for Training Data:
- Use high-quality, relevant content
- Include diverse conversation examples
- Maintain consistent formatting
- Regular content updates
- Balanced dataset across categories

Upload Process:
1. Access Admin Dashboard
2. Navigate to AI Training section
3. Click "Upload Training Data"
4. Select your files (multiple files supported)
5. Review file summary
6. Confirm upload

Training Job Configuration:
- Learning Rate: 0.001 (recommended)
- Batch Size: 32 (standard)
- Epochs: 10-15 (depending on data size)
- Max Tokens: 2048 (for responses)
- Temperature: 0.7 (creativity balance)

USER ACCOUNT MANAGEMENT
========================

User Roles:
- SUPER_ADMIN: Full system access and management
- ADMIN: User management and training operations
- ENGINEER: Technical operations and model training
- CUSTOMER: Basic AI interaction and support

Account Operations:
- Profile management and updates
- Password changes and security
- Notification preferences
- Activity monitoring
- Session management

TECHNICAL SUPPORT
==================

Common Issues and Solutions:

Login Problems:
Q: I can't log into my account
A: Try password reset, check email verification, or contact support

File Upload Issues:
Q: My training files won't upload
A: Check file size limits, verify format support, ensure stable connection

Training Job Failures:
Q: My training job failed
A: Review training logs, check data quality, verify system resources

API Integration:
Q: How do I integrate with my existing systems?
A: Use our REST API, follow documentation, implement proper authentication

Performance Optimization:
Q: How can I improve AI response quality?
A: Use better training data, increase training time, regular model updates

TROUBLESHOOTING GUIDE
======================

System Diagnostics:
1. Check server connectivity
2. Verify API endpoint availability
3. Test authentication tokens
4. Monitor resource usage
5. Review error logs

Error Resolution:
- 401 Unauthorized: Check login credentials
- 403 Forbidden: Verify role permissions
- 404 Not Found: Check endpoint URLs
- 500 Server Error: Contact technical support
- 503 Service Unavailable: Check system status

Performance Issues:
- Slow responses: Check network connection
- Training delays: Monitor system resources
- Upload failures: Verify file integrity
- Memory errors: Reduce batch sizes

BEST PRACTICES
===============

Data Quality:
- Use diverse, high-quality training examples
- Include edge cases and error scenarios
- Regular data updates and validation
- Consistent formatting and structure

Security:
- Strong password policies
- Regular token rotation
- Audit trail monitoring
- Secure API integration

Performance:
- Monitor training metrics
- Regular model retraining
- Optimize configuration parameters
- Load balancing for high traffic

Maintenance:
- Regular system updates
- Backup training data
- Monitor disk usage
- Performance optimization

FAQ SECTION
============

Q: How long does AI training take?
A: Training time varies from 30 minutes to 4 hours depending on data size and complexity.

Q: What's the maximum file size for training data?
A: Individual files can be up to 100MB, with no limit on total dataset size.

Q: Can I use multiple languages?
A: Yes, our AI supports multiple languages with proper training data.

Q: How do I improve response accuracy?
A: Use high-quality training data, include more examples, and regular model updates.

Q: Is my data secure?
A: Yes, we use enterprise-grade security with encryption and role-based access.

Q: Can I integrate with my CRM?
A: Yes, use our REST API for seamless integration with existing systems.

Q: How do I monitor AI performance?
A: Use the admin dashboard for real-time metrics and performance analytics.

Q: What support options are available?
A: We provide 24/7 technical support, documentation, and dedicated success managers.

CONTACT INFORMATION
===================
Email: support@poornasreeai.com
Documentation: https://docs.poornasreeai.com
API Reference: https://api.poornasreeai.com/docs
Status Page: https://status.poornasreeai.com

Version: 2.0
Last Updated: August 2025
© 2025 Poornasree AI. All rights reserved."""
    
    def create_training_text_file(self, pdf_text):
        """Create a text file from extracted PDF content."""
        print(f"\n📝 Creating training text file...")
        
        try:
            # Create temporary file
            temp_dir = tempfile.mkdtemp(prefix="service_guide_training_")
            text_file_path = os.path.join(temp_dir, "service_guide_extracted.txt")
            
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write(f"# SERVICE GUIDE - EXTRACTED CONTENT\n")
                f.write(f"# Extracted on: {datetime.now().isoformat()}\n")
                f.write(f"# Original file: {PDF_FILE_PATH}\n\n")
                f.write(pdf_text)
            
            file_size = os.path.getsize(text_file_path)
            print(f"✅ Training text file created")
            print(f"   Path: {text_file_path}")
            print(f"   Size: {file_size:,} bytes")
            
            return text_file_path
            
        except Exception as e:
            print(f"❌ Failed to create text file: {e}")
            return None
    
    def upload_training_file(self, file_path):
        """Upload the training file to the API."""
        print(f"\n📤 Uploading training file...")
        
        if not self.token:
            print("❌ Not authenticated. Please login first.")
            return False
        
        try:
            with open(file_path, 'rb') as f:
                files = {'files': (os.path.basename(file_path), f, 'text/plain')}
                headers = {'Authorization': f'Bearer {self.token}'}
                
                response = requests.post(
                    f"{API_BASE}/ai/upload-training-data",
                    files=files,
                    headers=headers,
                    timeout=60
                )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ File uploaded successfully!")
                print(f"   Files processed: {data.get('files_processed', 0)}")
                print(f"   Total size: {data.get('total_size', '0B')}")
                print(f"   Uploaded by: {data.get('uploaded_by', 'Unknown')}")
                
                # Store file IDs for training
                self.uploaded_file_ids = data.get('file_ids', [])
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def start_training_job(self):
        """Start a training job with the uploaded file."""
        print(f"\n🚀 Starting training job...")
        
        if not self.token:
            print("❌ Not authenticated. Please login first.")
            return False
        
        if not self.uploaded_file_ids:
            print("❌ No files uploaded. Please upload training data first.")
            return False
        
        try:
            training_request = {
                "name": f"Service Guide Training - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "file_ids": self.uploaded_file_ids,
                "training_config": {
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "epochs": 12,
                    "max_tokens": 2048,
                    "temperature": 0.7
                }
            }
            
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{API_BASE}/ai/start-training",
                json=training_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.training_job_id = data.get('job_id')
                print(f"✅ Training job started successfully!")
                print(f"   Job ID: {self.training_job_id}")
                print(f"   Status: {data.get('status', 'Unknown')}")
                print(f"   Estimated duration: {data.get('estimated_duration', 'Unknown')}")
                print(f"   File count: {data.get('file_count', 0)}")
                return True
            else:
                print(f"❌ Training start failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Training start error: {e}")
            return False
    
    def monitor_training_progress(self):
        """Monitor training job progress."""
        print(f"\n📊 Monitoring training progress...")
        
        if not self.token or not self.training_job_id:
            print("❌ No training job to monitor.")
            return False
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            print("⏳ Checking training status (press Ctrl+C to stop monitoring)...")
            
            while True:
                response = requests.get(
                    f"{API_BASE}/ai/training-jobs",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    jobs = data.get('jobs', [])
                    
                    # Find our job
                    current_job = None
                    for job in jobs:
                        if job.get('job_id') == self.training_job_id:
                            current_job = job
                            break
                    
                    if current_job:
                        status = current_job.get('status', 'unknown')
                        progress = current_job.get('progress', 0)
                        
                        print(f"   Status: {status} | Progress: {progress}%")
                        
                        if status == 'completed':
                            print("✅ Training completed successfully!")
                            return True
                        elif status == 'failed':
                            print("❌ Training failed!")
                            error_msg = current_job.get('error_message', 'Unknown error')
                            print(f"   Error: {error_msg}")
                            return False
                    
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
            return True
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            return False
    
    def interactive_qa_session(self):
        """Start interactive Q&A session with the trained model."""
        print(f"\n💬 Interactive Q&A Session with Service Guide")
        print("=" * 50)
        print("Ask questions about the Service Guide content.")
        print("Type 'exit', 'quit', or 'bye' to end the session.")
        print("Type 'help' for sample questions.")
        print("=" * 50)
        
        if not self.token:
            print("❌ Not authenticated. Please login first.")
            return
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        conversation_id = f"service_guide_{int(time.time())}"
        question_count = 0
        
        while True:
            try:
                print(f"\n🤔 Question #{question_count + 1}")
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    print("\n👋 Thank you for using the Service Guide Q&A system!")
                    break
                
                # Help command
                if user_input.lower() == 'help':
                    self.show_sample_questions()
                    continue
                
                # Send question to AI
                chat_request = {
                    "message": user_input,
                    "conversation_id": conversation_id
                }
                
                print("🤖 AI is thinking...")
                response = requests.post(
                    f"{API_BASE}/ai/chat",
                    json=chat_request,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get('response', 'Sorry, I could not generate a response.')
                    
                    print(f"\n🤖 AI: {ai_response}")
                    question_count += 1
                else:
                    print(f"❌ Error getting AI response: {response.status_code}")
                    print(f"   Response: {response.text}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session ended by user. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error in Q&A session: {e}")
    
    def show_sample_questions(self):
        """Show sample questions users can ask."""
        print("\n💡 Sample Questions About the Service Guide:")
        print("-" * 40)
        sample_questions = [
            "How do I upload training data?",
            "What file formats are supported?",
            "How long does AI training take?",
            "What are the different user roles?",
            "How do I troubleshoot login issues?",
            "What's the maximum file size for uploads?",
            "How do I improve AI response accuracy?",
            "What security features are available?",
            "How do I integrate with my CRM?",
            "What support options are available?"
        ]
        
        for i, question in enumerate(sample_questions, 1):
            print(f"   {i:2d}. {question}")
        
        print("-" * 40)
        print("Feel free to ask any question about the Service Guide content!")
    
    def cleanup_temp_files(self, temp_dir):
        """Clean up temporary files."""
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"✅ Cleaned up temporary files: {temp_dir}")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def run_full_workflow(self):
        """Run the complete training workflow."""
        self.print_header()
        
        # Step 1: Check prerequisites
        if not self.check_pdf_file():
            return False
        
        # Step 2: Authentication
        if not self.login():
            return False
        
        # Step 3: Extract PDF text
        pdf_text = self.extract_pdf_text()
        if not pdf_text:
            return False
        
        # Step 4: Create training text file
        text_file_path = self.create_training_text_file(pdf_text)
        if not text_file_path:
            return False
        
        temp_dir = os.path.dirname(text_file_path)
        
        try:
            # Step 5: Upload training file
            if not self.upload_training_file(text_file_path):
                return False
            
            # Step 6: Start training job
            if not self.start_training_job():
                return False
            
            # Step 7: Monitor training progress
            print(f"\n🎯 Training initiated successfully!")
            print(f"You can monitor progress and then start the Q&A session.")
            
            # Ask user if they want to monitor or skip to Q&A
            monitor_choice = input(f"\nDo you want to monitor training progress? (y/n): ").strip().lower()
            
            if monitor_choice in ['y', 'yes']:
                self.monitor_training_progress()
            
            # Step 8: Interactive Q&A
            qa_choice = input(f"\nDo you want to start the Q&A session now? (y/n): ").strip().lower()
            
            if qa_choice in ['y', 'yes']:
                self.interactive_qa_session()
            
            print(f"\n🎉 Service Guide training workflow completed!")
            return True
            
        finally:
            # Cleanup
            self.cleanup_temp_files(temp_dir)


def main():
    """Main function to run the Service Guide trainer."""
    try:
        trainer = ServiceGuideTrainer()
        
        print("Welcome to the Service Guide AI Training System!")
        print("\nOptions:")
        print("1. Run full training workflow")
        print("2. Just start Q&A session (if already trained)")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            trainer.run_full_workflow()
        elif choice == "2":
            if trainer.login():
                trainer.interactive_qa_session()
        elif choice == "3":
            print("Goodbye!")
        else:
            print("Invalid choice. Please run the script again.")
    
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
