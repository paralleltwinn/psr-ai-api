#!/usr/bin/env python3
"""
=============================================================================
POORNASREE AI - TRAINING SCRIPT
=============================================================================

Comprehensive script to upload sample PDFs and train AI models using 
Weaviate vector database and Gemini AI.

Features:
- Sample PDF creation and upload
- Weaviate vector database integration  
- Gemini 2.5 Flash model training
- Progress monitoring and job management
- Error handling and logging

Usage:
    python training_script.py
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from datetime import datetime
from typing import List, Dict, Any

import aiofiles
import aiohttp
from fpdf import FPDF

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

class TrainingScript:
    """Main training script class for AI model training."""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.session = None
        self.auth_token = None
        self.admin_credentials = {
            "email": "official.tishnu@gmail.com",
            "password": "Access@404"
        }
    
    async def run(self):
        """Main entry point for the training script."""
        print("🚀 Starting Poornasree AI Training Script")
        print("=" * 60)
        
        try:
            # Initialize HTTP session
            self.session = aiohttp.ClientSession()
            
            # Step 1: Authenticate as admin
            await self.authenticate()
            
            # Step 2: Check AI services health
            await self.check_ai_health()
            
            # Step 3: Create sample training data
            sample_files = await self.create_sample_training_data()
            
            # Step 4: Upload training files
            file_ids = await self.upload_training_files(sample_files)
            
            # Step 5: Start training job
            job_id = await self.start_training_job(file_ids)
            
            # Step 6: Monitor training progress
            await self.monitor_training_job(job_id)
            
            # Step 7: Verify training completion
            await self.verify_training_results()
            
            print("\n✅ Training script completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Training script failed: {e}")
            raise
        finally:
            if self.session:
                await self.session.close()
    
    async def authenticate(self):
        """Authenticate with the API to get admin token."""
        print("\n🔐 Authenticating as admin...")
        
        url = f"{self.base_url}/api/v1/auth/login"
        
        async with self.session.post(url, json=self.admin_credentials) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data["access_token"]
                user_info = data["user"]
                print(f"✅ Authenticated as: {user_info['first_name']} {user_info['last_name']} ({user_info['role']})")
            else:
                error_data = await response.json()
                raise Exception(f"Authentication failed: {error_data.get('detail', 'Unknown error')}")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def check_ai_health(self):
        """Check the health of AI services."""
        print("\n🔍 Checking AI services health...")
        
        url = f"{self.base_url}/api/v1/ai/health"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                health_data = await response.json()
                print(f"✅ AI Services Status: {health_data.get('overall_status', 'unknown')}")
                
                # Print service details
                services = health_data.get('services', {})
                for service_name, service_info in services.items():
                    status = service_info.get('status', service_info.get('connected', 'unknown'))
                    print(f"   📊 {service_name.title()}: {status}")
            else:
                print("⚠️  AI health check failed, but continuing...")
    
    async def create_sample_training_data(self) -> List[str]:
        """Create sample training data files (PDF, TXT, JSON)."""
        print("\n📝 Creating sample training data...")
        
        # Create temporary directory for sample files
        temp_dir = tempfile.mkdtemp(prefix="ai_training_")
        sample_files = []
        
        # 1. Create sample PDF
        pdf_path = os.path.join(temp_dir, "customer_support_guide.pdf")
        await self.create_sample_pdf(pdf_path)
        sample_files.append(pdf_path)
        
        # 2. Create sample TXT file
        txt_path = os.path.join(temp_dir, "ai_training_instructions.txt")
        await self.create_sample_txt(txt_path)
        sample_files.append(txt_path)
        
        # 3. Create sample JSON file
        json_path = os.path.join(temp_dir, "training_config.json")
        await self.create_sample_json(json_path)
        sample_files.append(json_path)
        
        print(f"✅ Created {len(sample_files)} sample training files")
        for file_path in sample_files:
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"   📄 {os.path.basename(file_path)} ({file_size:.1f} KB)")
        
        return sample_files
    
    async def create_sample_pdf(self, file_path: str):
        """Create a sample PDF with customer support content."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Poornasree AI - Customer Support Guide", ln=True, align='C')
        
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        
        content = [
            "Welcome to Poornasree AI Customer Support",
            "",
            "This guide provides comprehensive information for customer service representatives",
            "on how to handle customer inquiries and provide excellent support.",
            "",
            "Common Customer Issues:",
            "1. Login Problems - Help customers reset passwords and recover accounts",
            "2. Product Information - Provide detailed information about our AI services",
            "3. Technical Support - Guide customers through troubleshooting steps",
            "4. Billing Questions - Assist with payment and subscription issues",
            "",
            "Best Practices:",
            "- Always greet customers warmly and professionally",
            "- Listen actively to understand their concerns",
            "- Provide clear, step-by-step solutions",
            "- Follow up to ensure issues are resolved",
            "- Escalate complex issues to technical team when needed",
            "",
            "AI Training Data:",
            "This document contains sample customer support scenarios and responses",
            "that can be used to train our AI models for better customer service.",
        ]
        
        for line in content:
            pdf.cell(0, 6, line, ln=True)
        
        pdf.output(file_path)
    
    async def create_sample_txt(self, file_path: str):
        """Create a sample text file with AI training instructions."""
        content = """AI Training Instructions for Poornasree AI

This document contains training instructions and sample data for the Poornasree AI system.

Training Objectives:
- Improve customer service response quality
- Enhance technical support capabilities  
- Develop better understanding of user intent
- Provide more accurate and helpful responses

Sample Customer Interactions:

Customer: "I'm having trouble logging into my account"
AI Response: "I'd be happy to help you with your login issue. Let me guide you through some troubleshooting steps. First, please verify that you're using the correct email address and check if Caps Lock is enabled."

Customer: "What AI services do you offer?"
AI Response: "Poornasree AI offers a comprehensive suite of AI services including natural language processing, machine learning model training, automated customer support, and intelligent data analysis. Would you like detailed information about any specific service?"

Customer: "How do I cancel my subscription?"
AI Response: "I can help you with your subscription. To cancel, you can either log into your account and go to the billing section, or I can process the cancellation for you right now. May I ask if there's a specific reason for canceling? We might be able to address any concerns."

Training Guidelines:
- Always be helpful and professional
- Provide clear, actionable solutions
- Ask clarifying questions when needed
- Offer alternatives when possible
- Escalate complex technical issues appropriately

This training data helps the AI understand context, tone, and appropriate responses for various customer service scenarios.
"""
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    async def create_sample_json(self, file_path: str):
        """Create a sample JSON file with training configuration."""
        config_data = {
            "training_metadata": {
                "created_by": "training_script",
                "created_at": datetime.utcnow().isoformat(),
                "purpose": "AI model training for customer support",
                "version": "1.0"
            },
            "training_parameters": {
                "learning_rate": 0.001,
                "batch_size": 32,
                "epochs": 10,
                "max_tokens": 2048,
                "temperature": 0.7
            },
            "data_sources": [
                {
                    "type": "customer_support_guide",
                    "format": "pdf",
                    "description": "Comprehensive customer support procedures and best practices"
                },
                {
                    "type": "training_instructions",
                    "format": "txt", 
                    "description": "AI training guidelines and sample interactions"
                },
                {
                    "type": "configuration",
                    "format": "json",
                    "description": "Training parameters and metadata"
                }
            ],
            "expected_outcomes": [
                "Improved customer service response quality",
                "Better understanding of user intent and context",
                "More accurate technical support guidance",
                "Enhanced conversational AI capabilities"
            ],
            "evaluation_metrics": {
                "response_accuracy": ">=90%",
                "response_time": "<=2 seconds",
                "customer_satisfaction": ">=4.5/5",
                "issue_resolution_rate": ">=85%"
            }
        }
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(config_data, indent=2))
    
    async def upload_training_files(self, file_paths: List[str]) -> List[str]:
        """Upload training files to the API."""
        print(f"\n📤 Uploading {len(file_paths)} training files...")
        
        url = f"{self.base_url}/api/v1/ai/upload-training-data"
        
        # Upload files one by one to avoid file handle issues
        uploaded_file_ids = []
        
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            
            # Prepare multipart form data for single file
            data = aiohttp.FormData()
            
            # Read file content into memory first
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            data.add_field('files', file_content, filename=filename)
            
            try:
                async with self.session.post(url, data=data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        file_ids = result.get("file_ids", [])
                        uploaded_file_ids.extend(file_ids)
                        print(f"✅ Uploaded {filename} ({len(file_content)/1024:.1f} KB)")
                    else:
                        error_data = await response.json()
                        print(f"❌ Failed to upload {filename}: {error_data.get('detail', 'Unknown error')}")
                        
            except Exception as e:
                print(f"❌ Error uploading {filename}: {e}")
        
        if uploaded_file_ids:
            print(f"✅ Successfully uploaded {len(uploaded_file_ids)} files")
            print(f"   🔗 File IDs: {', '.join(uploaded_file_ids[:3])}{'...' if len(uploaded_file_ids) > 3 else ''}")
            return uploaded_file_ids
        else:
            raise Exception("No files were uploaded successfully")
    
    async def start_training_job(self, file_ids: List[str]) -> str:
        """Start a new training job."""
        print(f"\n🚀 Starting training job with {len(file_ids)} files...")
        
        url = f"{self.base_url}/api/v1/ai/start-training"
        
        training_request = {
            "name": f"AI Training Job - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "file_ids": file_ids,
            "training_config": {
                "learning_rate": 0.001,
                "batch_size": 32,
                "epochs": 10,
                "max_tokens": 2048,
                "temperature": 0.7
            }
        }
        
        async with self.session.post(url, json=training_request, headers=self.get_auth_headers()) as response:
            if response.status == 200:
                result = await response.json()
                job_id = result["job_id"]
                print(f"✅ Training job started successfully")
                print(f"   🆔 Job ID: {job_id}")
                print(f"   ⏱️  Estimated duration: {result.get('estimated_duration', 'unknown')}")
                return job_id
            else:
                error_data = await response.json()
                raise Exception(f"Training job failed to start: {error_data.get('detail', 'Unknown error')}")
    
    async def monitor_training_job(self, job_id: str):
        """Monitor training job progress until completion."""
        print(f"\n📊 Monitoring training job: {job_id}")
        
        url = f"{self.base_url}/api/v1/ai/training-jobs"
        
        last_progress = -1
        
        while True:
            async with self.session.get(url, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    result = await response.json()
                    jobs = result.get("jobs", [])
                    
                    # Find our job
                    current_job = None
                    for job in jobs:
                        if job["job_id"] == job_id:
                            current_job = job
                            break
                    
                    if current_job:
                        status = current_job["status"]
                        progress = current_job.get("progress", 0)
                        
                        # Only print progress updates when it changes
                        if progress != last_progress:
                            print(f"   📈 Progress: {progress}% - Status: {status}")
                            last_progress = progress
                        
                        if status == "completed":
                            print("✅ Training job completed successfully!")
                            break
                        elif status == "failed":
                            error_msg = current_job.get("error_message", "Unknown error")
                            raise Exception(f"Training job failed: {error_msg}")
                    else:
                        raise Exception(f"Training job {job_id} not found")
                else:
                    print("⚠️  Failed to get job status, retrying...")
            
            # Wait before next check
            await asyncio.sleep(5)
    
    async def verify_training_results(self):
        """Verify that training completed successfully."""
        print("\n🔍 Verifying training results...")
        
        # Get all training jobs to verify completion
        url = f"{self.base_url}/api/v1/ai/training-jobs"
        
        async with self.session.get(url, headers=self.get_auth_headers()) as response:
            if response.status == 200:
                result = await response.json()
                jobs = result.get("jobs", [])
                
                completed_jobs = [job for job in jobs if job["status"] == "completed"]
                total_jobs = len(jobs)
                
                print(f"✅ Training verification complete")
                print(f"   📊 Total jobs: {total_jobs}")
                print(f"   ✅ Completed jobs: {len(completed_jobs)}")
                
                if completed_jobs:
                    latest_job = completed_jobs[0]  # Jobs are sorted by creation time
                    print(f"   🆔 Latest job: {latest_job['name']}")
                    print(f"   ⏱️  Completed at: {latest_job.get('completed_at', 'unknown')}")
                
            else:
                print("⚠️  Could not verify training results")


async def main():
    """Main function to run the training script."""
    script = TrainingScript()
    await script.run()


if __name__ == "__main__":
    # Install required dependencies
    try:
        import aiohttp
        import aiofiles
        from fpdf import FPDF
    except ImportError as e:
        print(f"❌ Missing required dependency: {e}")
        print("\n📦 Please install required packages:")
        print("pip install aiohttp aiofiles fpdf2")
        sys.exit(1)
    
    # Run the training script
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Training script interrupted by user")
    except Exception as e:
        print(f"\n💥 Training script failed with error: {e}")
        sys.exit(1)
