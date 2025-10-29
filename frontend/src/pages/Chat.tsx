import { useState } from 'react';
import { Card } from '@/components/Card';
import { ChatInterface } from '@/components/ChatInterface';
import { Bot, Sparkles, BarChart3 } from 'lucide-react';

type BotType = 'assistant' | 'recommendation' | 'analysis';

export const Chat = () => {
  const [selectedBot, setSelectedBot] = useState<BotType | null>(null);
  const [sessionId, setSessionId] = useState<number | undefined>(undefined);

  const handleBotSelect = (botType: BotType) => {
    setSelectedBot(botType);
    setSessionId(undefined); // Reset session when switching bots
  };

  const handleBack = () => {
    setSelectedBot(null);
    setSessionId(undefined);
  };

  if (selectedBot) {
    return (
      <div className="h-[calc(100vh-4rem)] flex flex-col">
        <div className="mb-4">
          <button
            onClick={handleBack}
            className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 
                     font-medium text-sm flex items-center gap-2"
          >
            ← Back to bot selection
          </button>
        </div>
        <Card className="flex-1 flex flex-col overflow-hidden">
          <ChatInterface
            botType={selectedBot}
            sessionId={sessionId}
            onSessionCreated={setSessionId}
          />
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            AI & Tools
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Chat with AI for security insights, queries, and recommendations
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card
          className="p-6 cursor-pointer hover:shadow-lg transition-shadow border-2 border-transparent hover:border-primary-500"
          onClick={() => handleBotSelect('assistant')}
        >
          <div className="flex items-center space-x-3 mb-3">
            <Bot className="w-8 h-8 text-primary-600" />
            <h3 className="font-semibold text-lg">Security Assistant</h3>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Ask questions about security events, incidents, and access control. Uses function calling to search logs and create incidents.
          </p>
          <button className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
            Start Chat
          </button>
        </Card>

        <Card
          className="p-6 cursor-pointer hover:shadow-lg transition-shadow border-2 border-transparent hover:border-purple-500"
          onClick={() => handleBotSelect('recommendation')}
        >
          <div className="flex items-center space-x-3 mb-3">
            <Sparkles className="w-8 h-8 text-purple-600" />
            <h3 className="font-semibold text-lg">Recommendation Bot</h3>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Get AI-powered security policy and rule recommendations based on recent security events and patterns.
          </p>
          <button className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
            Get Recommendations
          </button>
        </Card>

        <Card
          className="p-6 cursor-pointer hover:shadow-lg transition-shadow border-2 border-transparent hover:border-blue-500"
          onClick={() => handleBotSelect('analysis')}
        >
          <div className="flex items-center space-x-3 mb-3">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            <h3 className="font-semibold text-lg">Analysis Bot</h3>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Generate comprehensive security reports and analytics with AI-powered insights and trend analysis.
          </p>
          <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Generate Analysis
          </button>
        </Card>
      </div>

      <Card className="p-12">
        <div className="text-center">
          <Bot className="w-20 h-20 text-gray-400 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            AI-Powered Security Chat
          </h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-6">
            Intelligent conversational AI powered by Google Gemini 2.5 Flash for security operations, investigations, and analytics.
          </p>
          <div className="max-w-2xl mx-auto text-left space-y-3">
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <p className="text-sm font-medium text-blue-900 dark:text-blue-300">
                💬 "Show me all incidents in Building A this week"
              </p>
            </div>
            <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
              <p className="text-sm font-medium text-purple-900 dark:text-purple-300">
                💬 "Who is John Smith in the face recognition system?"
              </p>
            </div>
            <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <p className="text-sm font-medium text-green-900 dark:text-green-300">
                💬 "Search for failed login attempts in the last 24 hours"
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
