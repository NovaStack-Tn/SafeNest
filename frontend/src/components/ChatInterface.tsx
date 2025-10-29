import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Wrench, AlertCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { Button } from './Button';
import axios from 'axios';

interface Message {
  role: 'user' | 'assistant' | 'tool';
  content: string;
  tool_name?: string;
  tool_result?: any;
  tool_results?: Array<{tool: string; result: any}>;
}

interface ChatInterfaceProps {
  botType: 'assistant' | 'recommendation' | 'analysis';
  sessionId?: number;
  onSessionCreated?: (sessionId: number) => void;
}

export const ChatInterface = ({ botType, sessionId, onSessionCreated }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedTools, setExpandedTools] = useState<Set<number>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getBotTitle = () => {
    switch (botType) {
      case 'assistant':
        return 'Security Assistant';
      case 'recommendation':
        return 'Recommendation Bot';
      case 'analysis':
        return 'Analysis Bot';
      default:
        return 'AI Assistant';
    }
  };

  const getBotDescription = () => {
    switch (botType) {
      case 'assistant':
        return 'Ask questions about security events, incidents, and access control';
      case 'recommendation':
        return 'Get security policy and rule recommendations';
      case 'analysis':
        return 'Generate security reports and analytics';
      default:
        return 'Chat with AI';
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setError('Please login to use the chat feature');
        setLoading(false);
        return;
      }
      
      const response = await axios.post(
        'http://localhost:8000/api/llm/api/chat/',
        {
          message: userMessage,
          bot_type: botType,
          session_id: sessionId,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      // Update session ID if new session was created
      if (response.data.session_id && !sessionId && onSessionCreated) {
        onSessionCreated(response.data.session_id);
      }

      // Add assistant response with tool results embedded
      setMessages(prev => [
        ...prev,
        { 
          role: 'assistant', 
          content: response.data.message,
          tool_results: response.data.tool_results || []
        },
      ]);
    } catch (err: any) {
      console.error('Chat error:', err);
      setError(err.response?.data?.error || 'Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleToolExpansion = (messageIndex: number) => {
    setExpandedTools(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageIndex)) {
        newSet.delete(messageIndex);
      } else {
        newSet.add(messageIndex);
      }
      return newSet;
    });
  };

  const renderToolResults = (toolResults: Array<{tool: string; result: any}>, messageIndex: number) => {
    const isExpanded = expandedTools.has(messageIndex);
    
    return (
      <div className="mt-2">
        <button
          onClick={() => toggleToolExpansion(messageIndex)}
          className="flex items-center gap-2 px-3 py-2 text-sm text-blue-600 dark:text-blue-400 
                   hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
        >
          {isExpanded ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
          <Wrench className="w-4 h-4" />
          <span className="font-medium">
            {toolResults.length} tool{toolResults.length > 1 ? 's' : ''} used
          </span>
        </button>
        
        {isExpanded && (
          <div className="mt-2 space-y-2">
            {toolResults.map((toolResult, idx) => (
              <div 
                key={idx}
                className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {toolResult.tool}
                  </span>
                </div>
                <pre className="text-xs text-gray-600 dark:text-gray-400 overflow-x-auto max-h-60 overflow-y-auto">
                  {JSON.stringify(toolResult.result, null, 2)}
                </pre>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
            <Bot className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {getBotTitle()}
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {getBotDescription()}
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Start a conversation
            </h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
              {getBotDescription()}
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index}>
            {message.role === 'user' && (
              <div className="flex justify-end">
                <div className="flex items-start gap-2 max-w-[80%]">
                  <div className="bg-primary-600 text-white rounded-lg px-4 py-2 shadow-sm">
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
                      <User className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {message.role === 'assistant' && (
              <div className="flex justify-start">
                <div className="flex items-start gap-2 max-w-[80%]">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="bg-white dark:bg-gray-800 rounded-lg px-4 py-2 shadow-sm border border-gray-200 dark:border-gray-700">
                      <p className="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">
                        {message.content || 'Processing...'}
                      </p>
                    </div>
                    {message.tool_results && message.tool_results.length > 0 && (
                      renderToolResults(message.tool_results, index)
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-start gap-2">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg px-4 py-2 shadow-sm border border-gray-200 dark:border-gray-700">
                <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="flex justify-center">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg px-4 py-3 flex items-start gap-2 max-w-[80%]">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-900 dark:text-red-200">{error}</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={loading}
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                     bg-white dark:bg-gray-900 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-primary-500 focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <Button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-4 py-2"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};
