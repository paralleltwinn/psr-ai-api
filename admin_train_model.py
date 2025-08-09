#!/usr/bin/env python3
"""
Admin Training Script for Poornasree AI
Authenticates as admin and trains the AI model with sample data.
"""

import requests
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime
import time

# Admin credentials
ADMIN_EMAIL = "official4tishnu@gmail.com"
ADMIN_PASSWORD = "Access@404"
BASE_URL = "http://127.0.0.1:8000"

print("🚀 Poornasree AI - Admin Model Training")
print("=" * 50)
print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"👤 Admin: {ADMIN_EMAIL}")
print(f"🌐 API URL: {BASE_URL}")
print("=" * 50)

def authenticate_admin():
    """Authenticate as admin and get access token."""
    print("\n🔐 Authenticating as Admin...")
    
    try:
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user", {})
            
            print(f"✅ Authentication successful!")
            print(f"   User: {user.get('first_name')} {user.get('last_name')}")
            print(f"   Role: {user.get('role')}")
            print(f"   Status: {user.get('status')}")
            
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def create_comprehensive_training_data():
    """Create comprehensive training data files."""
    print("\n📄 Creating Comprehensive Training Data...")
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="poornasree_admin_training_")
        print(f"📁 Created temp directory: {temp_dir}")
        
        files_created = []
        
        # 1. Customer Service Manual (TXT)
        service_manual = os.path.join(temp_dir, "customer_service_manual.txt")
        with open(service_manual, 'w', encoding='utf-8') as f:
            f.write("""POORNASREE AI - CUSTOMER SERVICE TRAINING MANUAL

SECTION 1: GREETING PROTOCOLS
=============================
- Always start with: "Hello! Welcome to Poornasree AI. How can I assist you today?"
- Maintain a professional and friendly tone
- Use active listening techniques
- Acknowledge customer concerns immediately

SECTION 2: COMMON CUSTOMER ISSUES
=================================

Account Management:
Q: I can't access my account
A: I understand your frustration. Let me help you regain access to your account. Can you please provide your registered email address?

Q: How do I reset my password?
A: I'll guide you through the password reset process. Please check your email for a reset link, or I can send you a new one.

Q: My account was suspended
A: I apologize for the inconvenience. Let me review your account status and help resolve this issue immediately.

AI Training Issues:
Q: My training job failed
A: I'm sorry to hear about the training issue. Let me check your job status and identify what went wrong. Can you provide your job ID?

Q: How long does training usually take?
A: Training time varies based on data size, typically 30 minutes to 2 hours. I can check your specific job's progress.

Q: Can I cancel a training job?
A: Yes, you can cancel active training jobs. Let me help you stop the current job and preserve your data.

Technical Support:
Q: The AI responses are not accurate
A: I understand your concern about response quality. This usually improves with more training data. Would you like me to help optimize your training dataset?

Q: How do I improve model performance?
A: Great question! Model performance improves with diverse, high-quality training data. I can provide specific recommendations for your use case.

SECTION 3: BILLING AND PAYMENTS
===============================
Q: I was charged incorrectly
A: I sincerely apologize for any billing confusion. Let me review your account charges and ensure everything is correct.

Q: How do I upgrade my plan?
A: I'd be happy to help you upgrade! Let me show you our available plans and find the best fit for your needs.

Q: Can I get a refund?
A: I understand your concern. Let me review your usage and see what options are available for your situation.

SECTION 4: ESCALATION PROCEDURES
================================
- If issue cannot be resolved in 15 minutes, escalate to Level 2 support
- Always provide ticket number for follow-up
- Inform customer of escalation timeline
- Summarize issue details for next agent

SECTION 5: CLOSING PROTOCOLS
============================
- Summarize the solution provided
- Ask: "Is there anything else I can help you with today?"
- Provide relevant resources or documentation
- Thank customer: "Thank you for choosing Poornasree AI!"
""")
        
        files_created.append(service_manual)
        print(f"✅ Created: customer_service_manual.txt ({os.path.getsize(service_manual):,} bytes)")
        
        # 2. FAQ Database (JSON)
        faq_db = os.path.join(temp_dir, "faq_database.json")
        faq_data = {
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "categories": {
                "general": [
                    {
                        "question": "What is Poornasree AI?",
                        "answer": "Poornasree AI is an advanced artificial intelligence platform that helps businesses automate customer support, train custom AI models, and improve service quality through intelligent automation.",
                        "keywords": ["about", "platform", "ai", "service"]
                    },
                    {
                        "question": "How does the AI training work?",
                        "answer": "Our AI training uses Weaviate vector database and Google's Gemini 2.5 Flash model. You upload your data, we process it into embeddings, and train a custom model for your specific needs.",
                        "keywords": ["training", "weaviate", "gemini", "custom model"]
                    },
                    {
                        "question": "What file formats are supported?",
                        "answer": "We support PDF, DOC, DOCX, TXT, JSON, and CSV file formats. Our system automatically extracts and processes content from these files for training.",
                        "keywords": ["file types", "upload", "formats", "pdf", "doc", "txt"]
                    }
                ],
                "technical": [
                    {
                        "question": "How long does model training take?",
                        "answer": "Training time depends on data volume and complexity. Typically, small datasets (under 10MB) take 30-60 minutes, while larger datasets may take 2-4 hours.",
                        "keywords": ["training time", "duration", "performance"]
                    },
                    {
                        "question": "Can I integrate with my existing systems?",
                        "answer": "Yes! Our REST API allows seamless integration with most customer service platforms, CRM systems, and business applications. We provide comprehensive documentation and SDKs.",
                        "keywords": ["integration", "api", "crm", "systems"]
                    },
                    {
                        "question": "How accurate are the AI responses?",
                        "answer": "Our AI achieves 95%+ accuracy with properly trained models. Accuracy improves with quality training data and regular model updates.",
                        "keywords": ["accuracy", "performance", "quality"]
                    }
                ],
                "billing": [
                    {
                        "question": "What are the pricing plans?",
                        "answer": "We offer flexible pricing: Starter ($49/month), Professional ($149/month), and Enterprise (custom pricing). Each plan includes different training limits and features.",
                        "keywords": ["pricing", "plans", "cost", "billing"]
                    },
                    {
                        "question": "Is there a free trial?",
                        "answer": "Yes! We offer a 14-day free trial with full access to all features. No credit card required to start.",
                        "keywords": ["free trial", "trial", "demo"]
                    }
                ]
            },
            "metadata": {
                "total_questions": 8,
                "last_updated": datetime.now().isoformat(),
                "languages": ["en"],
                "confidence_threshold": 0.85
            }
        }
        
        with open(faq_db, 'w', encoding='utf-8') as f:
            json.dump(faq_data, f, indent=2)
        
        files_created.append(faq_db)
        print(f"✅ Created: faq_database.json ({os.path.getsize(faq_db):,} bytes)")
        
        # 3. Training Conversations (CSV)
        conversations_csv = os.path.join(temp_dir, "training_conversations.csv")
        with open(conversations_csv, 'w', encoding='utf-8') as f:
            f.write("""customer_input,ai_response,category,intent,confidence
"Hello, I need help with my account","Hello! I'd be happy to help you with your account. What specific issue are you experiencing?",account_support,account_help,0.98
"I forgot my password","No problem! I can help you reset your password. Please provide your registered email address and I'll send you a reset link.",account_support,password_reset,0.97
"My training job is stuck","I understand your concern about the training job. Let me check the status for you. Can you please provide your job ID?",technical_support,training_issue,0.95
"How much does this cost?","Our pricing is very competitive! We have three plans: Starter at $49/month, Professional at $149/month, and Enterprise with custom pricing. Which plan interests you?",billing,pricing_inquiry,0.96
"The AI isn't working properly","I'm sorry to hear you're experiencing issues. Let me help troubleshoot this. Can you describe what specific problem you're encountering?",technical_support,troubleshooting,0.94
"I want to cancel my subscription","I understand you'd like to cancel. Before we proceed, may I ask if there's anything specific that's not meeting your expectations? I'd like to help if possible.",billing,cancellation,0.93
"How do I upload training data?","Great question! You can upload training data through our dashboard. Go to AI > Training, click 'Upload Files', and select your documents. We support PDF, DOC, TXT, JSON, and CSV formats.",technical_support,how_to,0.97
"Is my data secure?","Absolutely! We use enterprise-grade security with end-to-end encryption, secure cloud storage, and strict access controls. Your data privacy is our top priority.",security,data_privacy,0.98
"Can I get a refund?","I understand your concern. Let me review your account and usage to see what options are available. We want to ensure you're satisfied with our service.",billing,refund_request,0.92
"Thank you for your help","You're very welcome! I'm glad I could assist you today. Is there anything else I can help you with?",closing,gratitude,0.99
""")
        
        files_created.append(conversations_csv)
        print(f"✅ Created: training_conversations.csv ({os.path.getsize(conversations_csv):,} bytes)")
        
        # 4. Product Knowledge Base (TXT)
        knowledge_base = os.path.join(temp_dir, "product_knowledge.txt")
        with open(knowledge_base, 'w', encoding='utf-8') as f:
            f.write("""POORNASREE AI - PRODUCT KNOWLEDGE BASE

PLATFORM OVERVIEW
==================
Poornasree AI is a comprehensive artificial intelligence platform designed for businesses seeking to automate customer support and enhance service quality. Our platform combines cutting-edge AI technology with user-friendly interfaces to deliver exceptional results.

CORE FEATURES
=============

1. AI Model Training
   - Custom model training using your business data
   - Support for multiple file formats (PDF, DOC, DOCX, TXT, JSON, CSV)
   - Weaviate vector database integration for semantic search
   - Google Gemini 2.5 Flash for advanced language processing

2. Real-time Customer Support
   - Instant AI-powered responses
   - 24/7 availability
   - Multi-language support
   - Seamless human handoff when needed

3. Analytics and Insights
   - Performance monitoring dashboards
   - Training progress tracking
   - Response accuracy metrics
   - Customer satisfaction analytics

4. Integration Capabilities
   - REST API for easy integration
   - Webhook support for real-time updates
   - CRM system connectors
   - Third-party platform compatibility

TECHNICAL SPECIFICATIONS
========================

Infrastructure:
- Cloud-based architecture for scalability
- 99.9% uptime guarantee
- Global CDN for fast response times
- Enterprise-grade security protocols

AI Technology:
- Transformer-based neural networks
- Vector similarity search
- Contextual understanding
- Continuous learning capabilities

Data Processing:
- Automatic content extraction
- Text preprocessing and cleaning
- Intelligent chunking for optimal training
- Metadata preservation and organization

PRICING STRUCTURE
=================

Starter Plan ($49/month):
- Up to 1,000 monthly queries
- 5 training documents
- Basic analytics
- Email support

Professional Plan ($149/month):
- Up to 10,000 monthly queries
- 50 training documents
- Advanced analytics
- Priority support
- API access

Enterprise Plan (Custom):
- Unlimited queries
- Unlimited training documents
- Custom integrations
- Dedicated support
- SLA guarantees

SUPPORT SERVICES
================

Training and Onboarding:
- Comprehensive setup assistance
- Best practices guidance
- Data optimization recommendations
- Performance tuning support

Ongoing Support:
- 24/7 technical assistance
- Regular system updates
- Security monitoring
- Performance optimization

SECURITY MEASURES
=================

Data Protection:
- End-to-end encryption
- Secure data storage
- Regular security audits
- GDPR compliance

Access Control:
- Role-based permissions
- Multi-factor authentication
- Audit logs
- Session management

Privacy Compliance:
- Data anonymization options
- Retention policy controls
- Right to deletion
- Transparent data usage
""")
        
        files_created.append(knowledge_base)
        print(f"✅ Created: product_knowledge.txt ({os.path.getsize(knowledge_base):,} bytes)")
        
        # Calculate total size
        total_size = sum(os.path.getsize(f) for f in files_created)
        print(f"\n📊 Training Data Summary:")
        print(f"   Files created: {len(files_created)}")
        print(f"   Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        
        return temp_dir, files_created
        
    except Exception as e:
        print(f"❌ Failed to create training data: {e}")
        return None, []

def upload_training_files(token, files_list):
    """Upload training files to the server."""
    print(f"\n📤 Uploading {len(files_list)} Training Files...")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Prepare files for upload
        files_to_upload = []
        for file_path in files_list:
            files_to_upload.append(
                ('files', (os.path.basename(file_path), open(file_path, 'rb'), 'text/plain'))
            )
        
        response = requests.post(
            f"{BASE_URL}/ai/upload-training-data",
            headers=headers,
            files=files_to_upload,
            timeout=60
        )
        
        # Close file handles
        for _, (_, file_handle, _) in files_to_upload:
            file_handle.close()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   Files processed: {data.get('files_processed', 0)}")
            print(f"   Total size: {data.get('total_size', 'unknown')}")
            print(f"   File IDs: {data.get('file_ids', [])}")
            
            return data.get('file_ids', [])
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return []

def start_training_job(token, file_ids):
    """Start the AI training job."""
    print(f"\n🚀 Starting AI Training Job...")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        training_request = {
            "name": f"Admin Training Job - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "file_ids": file_ids,
            "training_config": {
                "learning_rate": 0.001,
                "batch_size": 32,
                "epochs": 15,
                "max_tokens": 2048,
                "temperature": 0.7
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/ai/start-training",
            headers=headers,
            json=training_request,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Training job started!")
            print(f"   Job ID: {data.get('job_id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Estimated duration: {data.get('estimated_duration')}")
            print(f"   File count: {data.get('file_count')}")
            
            return data.get('job_id')
        else:
            print(f"❌ Training start failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Training start error: {e}")
        return None

def monitor_training_job(token, job_id):
    """Monitor the training job progress."""
    print(f"\n📊 Monitoring Training Job: {job_id}")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        max_checks = 20  # Maximum monitoring attempts
        check_count = 0
        
        while check_count < max_checks:
            response = requests.get(
                f"{BASE_URL}/ai/training-jobs",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])
                
                # Find our job
                current_job = None
                for job in jobs:
                    if job.get('job_id') == job_id:
                        current_job = job
                        break
                
                if current_job:
                    status = current_job.get('status', 'unknown')
                    progress = current_job.get('progress', 0)
                    
                    print(f"   Status: {status} | Progress: {progress}% | Check {check_count + 1}/{max_checks}")
                    
                    if status in ['completed', 'failed']:
                        print(f"\n✅ Training job {status}!")
                        if status == 'completed':
                            print(f"   Completed at: {current_job.get('completed_at', 'unknown')}")
                        elif status == 'failed':
                            print(f"   Error: {current_job.get('error_message', 'unknown error')}")
                        return status
                    
                    elif status == 'running':
                        print(f"   Training in progress... {progress}% complete")
                    
                else:
                    print(f"   Job not found in current jobs list")
                
            else:
                print(f"   Failed to get job status: {response.status_code}")
            
            check_count += 1
            time.sleep(10)  # Wait 10 seconds before next check
        
        print(f"\n⚠️  Monitoring timeout after {max_checks} checks")
        return "timeout"
        
    except Exception as e:
        print(f"❌ Monitoring error: {e}")
        return "error"

def check_ai_health(token):
    """Check AI service health."""
    print(f"\n🔍 Checking AI Service Health...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/ai/health",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI services health check:")
            print(f"   Overall status: {data.get('overall_status', 'unknown')}")
            
            services = data.get('services', {})
            for service_name, service_info in services.items():
                status = service_info.get('status', service_info.get('connected', 'unknown'))
                print(f"   {service_name}: {status}")
            
            return True
        else:
            print(f"⚠️  Health check returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def cleanup_temp_files(temp_dir):
    """Clean up temporary files."""
    print(f"\n🧹 Cleaning up temporary files...")
    
    try:
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            print(f"✅ Cleaned up: {temp_dir}")
    except Exception as e:
        print(f"⚠️  Cleanup failed: {e}")

def main():
    """Main training function."""
    print("\n🎯 Starting Admin Model Training Process...")
    
    results = {
        "authentication": False,
        "file_creation": False,
        "file_upload": False,
        "training_start": False,
        "training_complete": False
    }
    
    temp_dir = None
    
    try:
        # Step 1: Authenticate as admin
        token = authenticate_admin()
        results["authentication"] = bool(token)
        
        if not token:
            print("❌ Cannot proceed without authentication")
            return
        
        # Step 2: Check AI health
        check_ai_health(token)
        
        # Step 3: Create training data
        temp_dir, files_list = create_comprehensive_training_data()
        results["file_creation"] = bool(temp_dir and files_list)
        
        if not files_list:
            print("❌ Cannot proceed without training files")
            return
        
        # Step 4: Upload files
        file_ids = upload_training_files(token, files_list)
        results["file_upload"] = bool(file_ids)
        
        if not file_ids:
            print("❌ Cannot proceed without uploaded files")
            return
        
        # Step 5: Start training
        job_id = start_training_job(token, file_ids)
        results["training_start"] = bool(job_id)
        
        if not job_id:
            print("❌ Cannot proceed without training job")
            return
        
        # Step 6: Monitor training
        final_status = monitor_training_job(token, job_id)
        results["training_complete"] = final_status == "completed"
        
    finally:
        # Cleanup
        if temp_dir:
            cleanup_temp_files(temp_dir)
    
    # Results summary
    print("\n" + "=" * 50)
    print("📊 TRAINING RESULTS SUMMARY")
    print("=" * 50)
    
    for step_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {step_name.replace('_', ' ').title()}: {status}")
    
    successful_steps = sum(results.values())
    total_steps = len(results)
    
    print(f"\n🎯 Overall Result: {successful_steps}/{total_steps} steps completed")
    
    if results["training_complete"]:
        print("🎉 MODEL TRAINING COMPLETED SUCCESSFULLY!")
        print("\n📝 Your AI model is now trained and ready to use!")
        print("   • Access the web interface at http://localhost:3000")
        print("   • Test the trained model through the chat interface")
        print("   • Monitor performance in the admin dashboard")
    elif results["training_start"]:
        print("⏳ Training job started but may still be in progress")
        print("   • Check the admin dashboard for status updates")
        print("   • Training typically completes within 1-2 hours")
    else:
        print("⚠️  Training process incomplete. Please check the errors above.")
    
    print(f"\n⏰ Training process completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

if __name__ == "__main__":
    main()
