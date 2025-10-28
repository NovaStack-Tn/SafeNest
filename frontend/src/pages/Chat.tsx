import { Card } from '@/components/Card';
import { MessageSquare, Bot, Sparkles } from 'lucide-react';

export const Chat = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            AI Security Assistant
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Chat with AI for security insights, queries, and recommendations
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-3">
            <Bot className="w-8 h-8 text-primary-600" />
            <h3 className="font-semibold text-lg">Security Bot</h3>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Ask questions about security policies, incidents, and access control
          </p>
        </Card>
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-3">
            <Sparkles className="w-8 h-8 text-purple-600" />
            <h3 className="font-semibold text-lg">Investigation Assistant</h3>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Get help with incident investigations and evidence analysis
          </p>
        </Card>
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-3">
            <MessageSquare className="w-8 h-8 text-blue-600" />
            <h3 className="font-semibold text-lg">Threat Hunter</h3>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Query threat intelligence and run security analytics
          </p>
        </Card>
      </div>

      <Card className="p-12">
        <div className="text-center">
          <MessageSquare className="w-20 h-20 text-gray-400 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            AI-Powered Security Chat
          </h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-6">
            Intelligent conversational AI for security operations, investigations, and analytics.
          </p>
          <div className="max-w-2xl mx-auto text-left space-y-3">
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <p className="text-sm font-medium text-blue-900 dark:text-blue-300">
                💬 "Show me all incidents in Building A this week"
              </p>
            </div>
            <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
              <p className="text-sm font-medium text-purple-900 dark:text-purple-300">
                💬 "Who has access to the server room after hours?"
              </p>
            </div>
            <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <p className="text-sm font-medium text-green-900 dark:text-green-300">
                💬 "Analyze threat patterns from the last 30 days"
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
