#!/usr/bin/env python3
"""
Test Trained AI Model - Poornasree AI
=====================================
Test the trained AI model by asking questions and evaluating responses.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "official4tishnu@gmail.com"
ADMIN_PASSWORD = "Access@404"

def login():
    """Login as admin to get access token."""
    print("🔐 Logging in as admin...")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful! User: {data['user']['first_name']} {data['user']['last_name']}")
        return data["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_ai_chat(token, question):
    """Test AI chat with a specific question."""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/v1/ai/chat",
        headers=headers,
        json={
            "message": question,
            "conversation_id": f"test_{int(time.time())}"
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("response", "No response received")
    else:
        return f"Error: {response.status_code} - {response.text}"

def test_ai_generate(token, prompt):
    """Test AI text generation with a specific prompt."""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/v1/ai/google-ai/generate",
        headers=headers,
        json={
            "prompt": prompt,
            "max_tokens": 200,
            "temperature": 0.7
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("generated_text", "No text generated")
    else:
        return f"Error: {response.status_code} - {response.text}"

def search_weaviate(token, query):
    """Search the Weaviate vector database."""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/v1/ai/search",
        headers=headers,
        json={
            "query": query,
            "limit": 3
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        return f"Error: {response.status_code} - {response.text}"

def main():
    """Main testing function."""
    print("🧪 Poornasree AI Model Testing")
    print("=" * 50)
    print(f"🌐 API Base URL: {BASE_URL}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    print()
    
    # Test questions based on our training data
    test_questions = [
        # Customer service questions
        {
            "category": "Customer Service",
            "question": "How can I upload training data?",
            "expected_topics": ["upload", "files", "training", "formats"]
        },
        {
            "category": "Customer Service", 
            "question": "What file formats do you support?",
            "expected_topics": ["PDF", "DOC", "TXT", "JSON", "CSV"]
        },
        {
            "category": "Technical Support",
            "question": "How do I start training my AI model?",
            "expected_topics": ["training", "model", "process", "steps"]
        },
        {
            "category": "General Information",
            "question": "What is Poornasree AI?",
            "expected_topics": ["AI", "platform", "intelligent", "solutions"]
        },
        {
            "category": "Troubleshooting",
            "question": "I'm having issues with file upload, what should I do?",
            "expected_topics": ["file", "upload", "troubleshooting", "support"]
        }
    ]
    
    print("🎯 Testing AI Chat Responses")
    print("=" * 30)
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {test['category']}")
        print(f"❓ Question: {test['question']}")
        print("🤖 AI Response:")
        
        # Test chat endpoint
        response = test_ai_chat(token, test['question'])
        print(f"   {response}")
        
        # Check if expected topics are mentioned
        response_lower = response.lower()
        found_topics = [topic for topic in test['expected_topics'] if topic.lower() in response_lower]
        
        if found_topics:
            print(f"✅ Found relevant topics: {', '.join(found_topics)}")
        else:
            print("⚠️  No expected topics found in response")
        
        print("-" * 50)
        time.sleep(1)  # Rate limiting
    
    print("\n🔍 Testing Semantic Search")
    print("=" * 30)
    
    search_queries = [
        "file upload process",
        "supported file formats", 
        "training documentation",
        "customer support"
    ]
    
    for query in search_queries:
        print(f"\n🔎 Search Query: {query}")
        results = search_weaviate(token, query)
        
        if isinstance(results, list) and results:
            print(f"✅ Found {len(results)} results:")
            for j, result in enumerate(results, 1):
                print(f"   {j}. {result.get('content', 'No content')[:100]}...")
        else:
            print(f"❌ Search failed or no results: {results}")
        
        time.sleep(1)  # Rate limiting
    
    print("\n🎨 Testing Text Generation")
    print("=" * 30)
    
    generation_prompts = [
        "Explain the benefits of using Poornasree AI for business",
        "Write a brief guide on how to get started with AI training",
        "Describe the customer support process"
    ]
    
    for prompt in generation_prompts:
        print(f"\n💭 Prompt: {prompt}")
        generated = test_ai_generate(token, prompt)
        print(f"🤖 Generated: {generated}")
        time.sleep(1)  # Rate limiting
    
    print("\n" + "=" * 50)
    print("🎉 AI MODEL TESTING COMPLETED!")
    print("=" * 50)
    print("📊 Test Summary:")
    print(f"   ✅ Chat Tests: {len(test_questions)} questions asked")
    print(f"   ✅ Search Tests: {len(search_queries)} queries executed")
    print(f"   ✅ Generation Tests: {len(generation_prompts)} prompts tested")
    print("\n📋 Evaluation:")
    print("   - Check if responses are relevant to training data")
    print("   - Verify search results contain uploaded content")
    print("   - Assess generation quality and coherence")
    print("   - Monitor for hallucinations or off-topic responses")

if __name__ == "__main__":
    main()
