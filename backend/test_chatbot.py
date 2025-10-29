"""
Test script to verify chatbot functionality with Gemini.
"""
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from django.conf import settings
from llm.services import LLMService, AssistantBotService
from core.models import User, Organization

def test_gemini_api_key():
    """Test if GEMINI_API_KEY is configured."""
    print("=" * 60)
    print("TEST 1: Checking GEMINI_API_KEY Configuration")
    print("=" * 60)
    
    if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
        print("✅ GEMINI_API_KEY is configured")
        print(f"   Key prefix: {settings.GEMINI_API_KEY[:10]}...")
        return True
    else:
        print("❌ GEMINI_API_KEY is NOT configured")
        print("   Please set GEMINI_API_KEY in your .env file")
        print("   Get your key from: https://aistudio.google.com/app/apikey")
        return False

def test_llm_service():
    """Test basic LLM service."""
    print("\n" + "=" * 60)
    print("TEST 2: Testing LLM Service Basic Chat")
    print("=" * 60)
    
    try:
        llm = LLMService()
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Say "Hello from Gemini!" in one sentence.'}
        ]
        
        print("Sending test message to Gemini...")
        response = llm.chat_completion(messages, temperature=0.5, max_tokens=50)
        
        if response['content']:
            print(f"✅ LLM Service Working!")
            print(f"   Response: {response['content']}")
            return True
        else:
            print("❌ No response content received")
            return False
            
    except Exception as e:
        print(f"❌ LLM Service Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_function_calling():
    """Test function calling with tools."""
    print("\n" + "=" * 60)
    print("TEST 3: Testing Function Calling")
    print("=" * 60)
    
    try:
        # Get a test user and organization
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()
        
        if not user or not user.organization:
            print("⚠️  No user/organization found, skipping function calling test")
            return True
        
        bot = AssistantBotService(user.organization.id, user.id)
        
        print("Testing tool availability...")
        tools = bot._get_tools()
        print(f"✅ Found {len(tools)} tools available:")
        for tool in tools:
            print(f"   - {tool['function']['name']}: {tool['function']['description']}")
        
        print("\nSending test message with potential tool usage...")
        response = bot.chat("Hello, what can you help me with?")
        
        if response['content']:
            print(f"✅ Assistant Response: {response['content'][:200]}...")
            if response.get('tool_results'):
                print(f"   Tools called: {len(response['tool_results'])}")
                for tool_result in response['tool_results']:
                    print(f"   - {tool_result['tool']}")
            return True
        else:
            print("❌ No response from assistant")
            return False
            
    except Exception as e:
        print(f"❌ Function Calling Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_conversion():
    """Test OpenAI to Gemini tool conversion."""
    print("\n" + "=" * 60)
    print("TEST 4: Testing Tool Format Conversion")
    print("=" * 60)
    
    try:
        llm = LLMService()
        
        # Sample OpenAI tool format
        openai_tools = [
            {
                'type': 'function',
                'function': {
                    'name': 'test_tool',
                    'description': 'A test tool',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {'type': 'string'}
                        }
                    }
                }
            }
        ]
        
        gemini_tools = llm._convert_tools_to_gemini_format(openai_tools)
        
        print("✅ Tool conversion successful!")
        print(f"   OpenAI format tools: {len(openai_tools)}")
        print(f"   Gemini format tools: {len(gemini_tools)}")
        print(f"   Converted tool: {gemini_tools[0].name}")
        return True
        
    except Exception as e:
        print(f"❌ Tool Conversion Error: {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print("\n" + "🤖" * 30)
    print("SAFENEST CHATBOT TEST SUITE - GEMINI 2.5 FLASH")
    print("🤖" * 30 + "\n")
    
    results = []
    
    # Test 1: API Key
    results.append(("API Key Configuration", test_gemini_api_key()))
    
    if results[0][1]:  # Only continue if API key is set
        # Test 2: Basic LLM
        results.append(("LLM Service", test_llm_service()))
        
        # Test 3: Function Calling
        results.append(("Function Calling", test_function_calling()))
        
        # Test 4: Tool Conversion
        results.append(("Tool Conversion", test_tool_conversion()))
    else:
        print("\n⚠️  Skipping remaining tests due to missing API key")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Chatbot is ready to use!")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
