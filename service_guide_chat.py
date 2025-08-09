#!/usr/bin/env python3
"""
Service Guide Q&A Chat - Poornasree AI
======================================
Interactive chat interface for asking questions about the Service Guide.
Connects to trained AI model for Service Guide knowledge.
"""

import requests
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"
ADMIN_EMAIL = "official4tishnu@gmail.com"
ADMIN_PASSWORD = "Access@404"

class ServiceGuideChat:
    """Interactive chat interface for Service Guide questions."""
    
    def __init__(self):
        self.token = None
        self.conversation_id = f"service_guide_chat_{int(time.time())}"
        self.question_count = 0
    
    def login(self):
        """Authenticate with the API."""
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                user_info = data["user"]
                print(f"✅ Connected as {user_info['first_name']} {user_info['last_name']} ({user_info['role']})")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def print_welcome(self):
        """Print welcome message and instructions."""
        print("\n" + "="*60)
        print("🚀 SERVICE GUIDE AI ASSISTANT")
        print("="*60)
        print("💬 Ask me anything about the Poornasree AI Service Guide!")
        print("📖 I'm trained on the complete Service Guide documentation.")
        print("\n🎯 Sample Questions:")
        print("   • How do I upload training data?")
        print("   • What file formats are supported?")
        print("   • How long does AI training take?")
        print("   • What are the different user roles?")
        print("   • How do I troubleshoot login issues?")
        print("   • What's the maximum file size for uploads?")
        print("   • How do I improve AI response accuracy?")
        print("\n⌨️  Commands:")
        print("   • Type 'help' for more sample questions")
        print("   • Type 'exit', 'quit', or 'bye' to end session")
        print("="*60)
    
    def show_sample_questions(self):
        """Show comprehensive list of sample questions."""
        print("\n💡 COMPREHENSIVE SERVICE GUIDE QUESTIONS:")
        print("-" * 50)
        
        categories = {
            "📤 Data Upload & Training": [
                "How do I upload training data to the system?",
                "What file formats are supported for training?",
                "What's the maximum file size I can upload?",
                "How do I start a training job?",
                "How long does training typically take?"
            ],
            "👤 User Management": [
                "What are the different user roles in the system?",
                "How do I create new admin users?",
                "What permissions does each role have?",
                "How do I manage user accounts?",
                "How do user applications work?"
            ],
            "🔧 Technical Support": [
                "How do I troubleshoot login issues?",
                "What should I do if file upload fails?",
                "How do I resolve training job failures?",
                "How do I check system status?",
                "What are common error codes?"
            ],
            "⚡ Performance & Optimization": [
                "How do I improve AI response accuracy?",
                "What are the best practices for training data?",
                "How do I optimize system performance?",
                "How do I monitor training progress?",
                "What security features are available?"
            ],
            "🔗 Integration & API": [
                "How do I integrate with existing systems?",
                "What API endpoints are available?",
                "How do I use the REST API?",
                "How do I implement authentication?",
                "What are the rate limits?"
            ]
        }
        
        for category, questions in categories.items():
            print(f"\n{category}")
            for i, question in enumerate(questions, 1):
                print(f"   {i}. {question}")
        
        print("-" * 50)
        print("Choose any question or ask your own!")
    
    def ask_question(self, question):
        """Send question to AI and get response."""
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            chat_request = {
                "message": question,
                "conversation_id": self.conversation_id
            }
            
            print("🤖 AI is analyzing the Service Guide...")
            
            response = requests.post(
                f"{API_BASE}/ai/chat",
                json=chat_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', 'Sorry, I could not generate a response.')
                return ai_response
            else:
                error_msg = f"API Error {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', error_msg)
                except:
                    pass
                return f"❌ Error: {error_msg}"
                
        except Exception as e:
            return f"❌ Connection error: {e}"
    
    def start_chat_session(self):
        """Main chat loop."""
        self.print_welcome()
        
        while True:
            try:
                self.question_count += 1
                print(f"\n🤔 Question #{self.question_count}")
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    print("\n👋 Thank you for using the Service Guide AI Assistant!")
                    print("🎯 Visit again anytime for more Service Guide help!")
                    break
                
                # Help command
                if user_input.lower() == 'help':
                    self.show_sample_questions()
                    continue
                
                # Get AI response
                ai_response = self.ask_question(user_input)
                
                # Display response with formatting
                print(f"\n🤖 Service Guide AI:")
                print("─" * 40)
                print(ai_response)
                print("─" * 40)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session ended. Thank you for using Service Guide AI!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
    
    def run(self):
        """Main execution method."""
        print("🔗 Connecting to Service Guide AI...")
        
        if not self.login():
            print("❌ Cannot start chat session without authentication.")
            print("🔧 Please ensure the backend is running and credentials are correct.")
            return False
        
        self.start_chat_session()
        return True

def main():
    """Main function."""
    try:
        chat = ServiceGuideChat()
        chat.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
