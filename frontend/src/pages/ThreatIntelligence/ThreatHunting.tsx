import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Search, Sparkles, FileText } from 'lucide-react';
import api from '@/lib/api';
import toast from 'react-hot-toast';

export const ThreatHunting = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any>(null);

  const huntMutation = useMutation({
    mutationFn: async (queryText: string) => {
      const response = await api.post('/threat-intelligence/ai/threat-hunting/query/', {
        query: queryText,
      });
      return response.data;
    },
    onSuccess: (data) => {
      setResults(data);
      toast.success('Query executed successfully');
    },
    onError: () => {
      toast.error('Failed to execute query');
    },
  });

  const handleSearch = () => {
    if (query.trim()) {
      huntMutation.mutate(query);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Threat Hunting
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          AI-powered natural language threat queries
        </p>
      </div>

      <Card className="p-6">
        <div className="flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Ask me anything... e.g. 'Show me all failed logins from China in the last 7 days'"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <Button onClick={handleSearch} disabled={huntMutation.isPending}>
            <Sparkles className="w-4 h-4 mr-2" />
            {huntMutation.isPending ? 'Hunting...' : 'Hunt'}
          </Button>
        </div>
      </Card>

      {results && (
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Query Results
            </h3>
          </div>
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Intent: <span className="font-semibold">{results.intent}</span>
            </p>
            <pre className="text-xs text-gray-800 dark:text-gray-200 overflow-auto">
              {JSON.stringify(results.results, null, 2)}
            </pre>
          </div>
        </Card>
      )}

      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Example Queries
        </h3>
        <div className="space-y-2">
          {[
            'Show me all failed logins from the last 7 days',
            'Find unusual access patterns',
            'Show threats by location',
            'List suspicious users with multiple alerts',
            'Show me recent incidents',
          ].map((example, i) => (
            <button
              key={i}
              onClick={() => setQuery(example)}
              className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </Card>
    </div>
  );
};
