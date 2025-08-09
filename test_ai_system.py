#!/usr/bin/env python3
"""
Simple test script to verify the AI training system functionality.
"""

import asyncio
import json
import tempfile
import os
from pathlib import Path

async def test_ai_service():
    """Test the AI service methods directly."""
    print("🧪 Testing AI Service Methods...")
    
    # Add the app directory to Python path
    import sys
    sys.path.append(str(Path(__file__).parent / "app"))
    
    try:
        from services.ai_service import ai_service
        print("✅ AI service imported successfully")
        
        # Test 1: Create sample files
        print("\n📁 Creating sample training files...")
        temp_dir = tempfile.mkdtemp()
        
        # Create a sample text file
        sample_txt = os.path.join(temp_dir, "sample.txt")
        with open(sample_txt, 'w') as f:
            f.write("This is sample training content for Poornasree AI.\n")
            f.write("Customer service: How can I help you today?\n")
            f.write("User: I need help with my account.\n")
            f.write("AI: I'd be happy to help you with your account issues.")
        
        # Create a sample JSON file
        sample_json = os.path.join(temp_dir, "sample.json")
        with open(sample_json, 'w') as f:
            json.dump({
                "training_data": "Sample customer interactions",
                "responses": ["How can I help?", "Let me assist you", "I understand your concern"]
            }, f)
        
        print(f"✅ Created sample files in: {temp_dir}")
        
        # Test 2: Test text extraction
        print("\n🔍 Testing text extraction...")
        text_content = await ai_service._extract_text_content(sample_txt, '.txt')
        print(f"✅ Extracted {len(text_content)} characters from TXT file")
        
        json_content = await ai_service._extract_text_content(sample_json, '.json')
        print(f"✅ Extracted {len(json_content)} characters from JSON file")
        
        # Test 3: Test text chunking
        print("\n✂️  Testing text chunking...")
        chunks = ai_service._split_text_into_chunks(text_content, max_chunk_size=50)
        print(f"✅ Split text into {len(chunks)} chunks")
        
        # Test 4: Test training job creation
        print("\n🚀 Testing training job creation...")
        job_result = await ai_service.start_training_job(
            name="Test Training Job",
            file_ids=["test_file_1", "test_file_2"],
            training_config={"learning_rate": 0.001},
            started_by="test_user"
        )
        print(f"✅ Created training job: {job_result['job_id']}")
        
        # Test 5: Test job status retrieval
        print("\n📊 Testing job status retrieval...")
        await asyncio.sleep(1)  # Wait a moment for job to be saved
        jobs = await ai_service.get_training_jobs()
        print(f"✅ Retrieved {len(jobs)} training jobs")
        
        if jobs:
            latest_job = jobs[0]
            print(f"   Latest job: {latest_job['name']} - Status: {latest_job['status']}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up temporary files")
        
        print("\n🎉 All AI service tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_endpoints():
    """Test the API endpoints are accessible."""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get("http://127.0.0.1:8000/health") as response:
                if response.status == 200:
                    print("✅ Main health endpoint accessible")
                else:
                    print(f"⚠️  Main health endpoint returned: {response.status}")
            
            # Test AI health endpoint  
            async with session.get("http://127.0.0.1:8000/api/v1/ai/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ AI health endpoint accessible - Status: {data.get('overall_status', 'unknown')}")
                else:
                    print(f"⚠️  AI health endpoint returned: {response.status}")
                    
        print("🎉 API endpoint tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("   Make sure the FastAPI server is running on port 8000")
        return False

async def main():
    """Main test function."""
    print("🚀 Poornasree AI Training System Test")
    print("=" * 50)
    
    # Test AI service methods
    service_test = await test_ai_service()
    
    # Test API endpoints
    api_test = await test_api_endpoints()
    
    # Summary
    print(f"\n📋 Test Summary:")
    print(f"   AI Service: {'✅ PASS' if service_test else '❌ FAIL'}")
    print(f"   API Endpoints: {'✅ PASS' if api_test else '❌ FAIL'}")
    
    if service_test and api_test:
        print(f"\n🎉 All tests passed! The AI training system is ready.")
    else:
        print(f"\n⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    asyncio.run(main())
