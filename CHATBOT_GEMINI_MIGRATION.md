# SafeNest Chatbot Migration to Google Gemini

## Overview
Successfully migrated the SafeNest AI chatbot system from OpenAI to **Google Gemini 2.5 Flash** with full function calling support and modern chat interface.

## Changes Made

### Backend Migration

#### 1. **LLM Service (`backend/llm/services.py`)**
- ✅ Migrated from OpenAI to Google Gemini 2.5 Flash
- ✅ Model: `models/gemini-2.5-flash`
- ✅ Implemented function calling support (tool calling)
- ✅ Added tool format converter (OpenAI format → Gemini format)
- ✅ System prompt support via `system_instruction` parameter
- ✅ Chat history management with proper role mapping
- ✅ Embedding service using `models/embedding-001` (768-dim)

**Key Features:**
```python
- LLMService.chat_completion() - Main chat API with tool support
- LLMService._convert_tools_to_gemini_format() - Tool format converter
- LLMService.create_embedding() - Text embeddings with Gemini
```

#### 2. **Bot Services Unchanged**
- ✅ **AssistantBotService** - Works with Gemini (function calling preserved)
- ✅ **RecommendationBotService** - Compatible with Gemini
- ✅ **AnalysisBotService** - Compatible with Gemini

#### 3. **Function Calling Tools**
All 5 tools work with Gemini:
- `search_logs` - Search login events, alerts, incidents
- `create_incident` - Create new security incidents
- `get_incident` - Get incident details
- `who_is` - Look up face identities
- `show_camera` - Get camera detections

### Frontend Implementation

#### 1. **ChatInterface Component** (`frontend/src/components/ChatInterface.tsx`)
New fully functional chat interface:
- ✅ Real-time message streaming
- ✅ User and assistant message bubbles
- ✅ **Collapsible tool results** - Clean UI with expand/collapse toggle
- ✅ Natural language responses from Gemini
- ✅ Loading states and error handling
- ✅ Session management
- ✅ Support for all 3 bot types
- ✅ Modern, responsive UI with dark mode

**Features:**
- Message history with auto-scroll
- Tool execution visualization
- Error handling with user feedback
- Keyboard shortcuts (Enter to send)
- Loading indicators
- Session persistence

#### 2. **Updated Chat Page** (`frontend/src/pages/Chat.tsx`)
- ✅ Bot selection interface (3 cards)
- ✅ Dynamic bot switching
- ✅ Session management per bot
- ✅ Back navigation
- ✅ Example queries display

**Three Bot Types:**
1. **Security Assistant** - Main bot with function calling
2. **Recommendation Bot** - Security policy suggestions
3. **Analysis Bot** - Generate reports and analytics

### Configuration

#### Environment Variables
Already configured in `backend/safenest/settings.py`:
```python
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

Add to `.env` file:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Dependencies
Already in `requirements.txt`:
```
google-generativeai>=0.8.0
```

### API Endpoints

**Chat Endpoint:**
```
POST /api/llm/api/chat/
```

**Request:**
```json
{
  "message": "Show me all incidents from last week",
  "bot_type": "assistant",
  "session_id": 123  // Optional, omit for new session
}
```

**Response:**
```json
{
  "session_id": 123,
  "message": "Here are the incidents from last week...",
  "tool_results": [
    {
      "tool": "search_logs",
      "result": {
        "incidents": [...],
        "count": 5
      }
    }
  ]
}
```

**Other Endpoints:**
```
GET /api/llm/api/recommendations/
GET /api/llm/api/weekly_analysis/
```

## Function Calling Implementation

### How It Works

1. **Tool Definition** (OpenAI format maintained for compatibility):
```python
{
  'type': 'function',
  'function': {
    'name': 'search_logs',
    'description': 'Search login events and alerts',
    'parameters': {
      'type': 'object',
      'properties': {...},
      'required': [...]
    }
  }
}
```

2. **Automatic Conversion to Gemini Format**:
```python
def _convert_tools_to_gemini_format(self, openai_tools):
    gemini_tools = []
    for tool in openai_tools:
        func = tool['function']
        gemini_tools.append({
            'name': func['name'],
            'description': func['description'],
            'parameters': func['parameters']
        })
    return gemini_tools
```

3. **Tool Execution**:
- Gemini calls function with parameters
- Backend executes tool via `SafeNestTools`
- Results returned to chat interface
- Displayed in expandable UI component

## UI Features

### Chat Interface
- **Message Bubbles**: User (right, blue) and Assistant (left, white)
- **Natural Language Responses**: Gemini summarizes tool results conversationally
- **Collapsible Tool Results**: Clean toggle button showing "X tools used"
  - Click to expand/collapse technical details
  - Each tool result in its own card
  - JSON formatted and scrollable
  - Independent state per message
- **Loading States**: Spinner animation during API calls
- **Error Handling**: Red alert boxes for errors
- **Auto-scroll**: Keeps latest messages visible
- **Dark Mode**: Full theme support

### Bot Selection
- **Card-based UI**: 3 interactive cards
- **Hover Effects**: Border color changes on hover
- **Click to Start**: Direct navigation to chat
- **Example Queries**: Shows what each bot can do

## Testing the Chatbot

### 1. Start Backend
```bash
cd backend
python manage.py runserver
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Set API Key
Add to `backend/.env`:
```bash
GEMINI_API_KEY=your_api_key_here
```

Get your API key from: https://aistudio.google.com/app/apikey

### 4. Test Queries

**Security Assistant (with function calling):**
- "Search for failed login attempts in the last 24 hours"
- "Who is John Smith?" (face identity lookup)
- "Create a high severity incident for unauthorized access"
- "Show me incident #5"
- "Get detections from camera 1"

**Recommendation Bot:**
- "What security improvements should we make?"
- "Analyze recent security patterns"

**Analysis Bot:**
- "Generate a weekly security report"
- "What are the key security trends?"

## Architecture

```
Frontend (React + TypeScript)
    ↓
ChatInterface Component
    ↓
POST /api/llm/api/chat/
    ↓
LLMAPIViewSet.chat()
    ↓
AssistantBotService.chat()
    ↓
LLMService.chat_completion()
    ↓
Google Gemini 2.5 Flash API
    ↓ (if function call needed)
SafeNestTools.execute_tool()
    ↓
Database Queries
    ↓
Return Results to User
```

## Key Improvements

### Over OpenAI Implementation:
1. **Lower Cost**: Gemini 2.5 Flash is more cost-effective
2. **Higher Rate Limits**: 15 RPM free tier vs OpenAI's limits
3. **Latest Model**: Using the newest Gemini 2.5 Flash
4. **Native System Instructions**: Better prompt handling
5. **Function Calling**: Fully compatible format

### Frontend Enhancements:
1. **Modern UI**: Clean, professional chat interface
2. **Tool Visualization**: See what tools the AI is using
3. **Error Handling**: Clear user feedback
4. **Session Management**: Persistent conversations
5. **Multi-bot Support**: Easy switching between bots

## Gemini API Limits (Free Tier)

- **Rate Limit**: 15 requests per minute (RPM)
- **Daily Requests**: 1,500 requests per day (RPD)
- **Token Limit**: 1,000,000 tokens per minute (TPM)
- **Context Window**: 1M tokens input, 8K output

## Migration Checklist

- [x] Migrate LLMService to Gemini
- [x] Implement function calling converter
- [x] Update embedding service
- [x] Test all 5 tool functions
- [x] Build ChatInterface component
- [x] Update Chat page with bot selection
- [x] Fix API endpoint URLs
- [x] Add error handling
- [x] Add loading states
- [x] Support session management
- [x] Add tool result display
- [x] Test dark mode support
- [x] Document changes

## Files Modified

### Backend:
- `backend/llm/services.py` - Complete Gemini migration
- `backend/safenest/settings.py` - Already had GEMINI_API_KEY

### Frontend:
- `frontend/src/components/ChatInterface.tsx` - **NEW** functional chat UI
- `frontend/src/pages/Chat.tsx` - Updated with bot selection

### Documentation:
- `CHATBOT_GEMINI_MIGRATION.md` - **NEW** this file

## Notes

- ✅ Backward compatible with existing tool definitions
- ✅ No database schema changes needed
- ✅ All existing bot services work unchanged
- ✅ Function calling fully implemented
- ✅ Ready for production use

## Next Steps

1. Test with real security data
2. Add chat session history view
3. Implement chat export functionality
4. Add voice input support (future)
5. Implement RAG for document search (future)

## Support

For issues or questions:
- Check Gemini API status: https://status.google.com/
- Verify API key is set correctly
- Check browser console for frontend errors
- Check Django logs for backend errors
- Ensure database is running (PostgreSQL)

---

**Status**: ✅ **Complete and Ready to Use**

**Powered by**: Google Gemini 2.5 Flash
