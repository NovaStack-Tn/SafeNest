"""
Interactive demo of the SafeNest Chatbot with Gemini 2.5 Flash.
Shows real-world usage with function calling.
"""
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from llm.services import AssistantBotService
from core.models import User

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_response(response):
    """Print formatted chatbot response."""
    print("\n🤖 Assistant:")
    print("-" * 70)
    print(response['content'])
    
    if response.get('tool_results'):
        print("\n🔧 Tools Used:")
        for tool_result in response['tool_results']:
            print(f"\n  📌 {tool_result['tool']}:")
            result = tool_result['result']
            if isinstance(result, dict):
                for key, value in result.items():
                    if isinstance(value, list) and len(value) > 0:
                        print(f"     {key}: {len(value)} items")
                        for item in value[:3]:  # Show first 3 items
                            if isinstance(item, dict):
                                print(f"       - {item}")
                    else:
                        print(f"     {key}: {value}")
            else:
                print(f"     {result}")
    print("-" * 70)

def run_demo():
    """Run interactive chatbot demo."""
    print("\n" + "🚀" * 35)
    print("SAFENEST AI CHATBOT - LIVE DEMO")
    print("Powered by Google Gemini 2.5 Flash")
    print("🚀" * 35)
    
    # Get a user for testing
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
    
    if not user or not user.organization:
        print("\n❌ No user/organization found. Please create a user first.")
        return
    
    print(f"\n👤 Testing as: {user.username} ({user.organization.name})")
    
    # Initialize the bot
    bot = AssistantBotService(user.organization.id, user.id)
    conversation_history = []
    
    # Demo queries
    demo_queries = [
        "Hello! What can you help me with?",
        "Search for incidents in the last 7 days",
        "Tell me about security alerts",
    ]
    
    print("\n📝 Running automated demo queries...")
    print("   (You can also run this interactively by modifying the script)")
    
    for i, query in enumerate(demo_queries, 1):
        print_header(f"QUERY {i}")
        print(f"\n💬 User: {query}")
        
        try:
            response = bot.chat(query, conversation_history)
            print_response(response)
            
            # Add to conversation history
            conversation_history.append({'role': 'user', 'content': query})
            conversation_history.append({'role': 'assistant', 'content': response['content']})
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE!")
    print("=" * 70)
    print("\n📊 Summary:")
    print(f"   - Total queries: {len(demo_queries)}")
    print(f"   - Conversation turns: {len(conversation_history)}")
    print(f"   - Bot type: Security Assistant")
    print(f"   - Model: Google Gemini 2.5 Flash")
    print(f"   - Function calling: Enabled (5 tools available)")
    
    print("\n💡 Tips:")
    print("   - Try asking: 'Who is [person name]?' to test face identity lookup")
    print("   - Try asking: 'Show me camera 1' to get camera detections")
    print("   - Try asking: 'Create a high severity incident for unauthorized access'")
    print("   - Try asking: 'Search for failed login attempts in the last 24 hours'")
    
    print("\n🌐 To test in the web UI:")
    print("   1. Make sure frontend is running (npm run dev)")
    print("   2. Navigate to 'AI & Tools' page")
    print("   3. Click 'Security Assistant'")
    print("   4. Start chatting!")
    
    print("\n" + "🎉" * 35 + "\n")

if __name__ == '__main__':
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
