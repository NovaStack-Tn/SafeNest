import { useState } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { X, AlertTriangle, Sparkles, Target, Search, Bell } from 'lucide-react';
import { Button } from './Button';
import { Card } from './Card';
import api from '@/lib/api';
import toast from 'react-hot-toast';

interface ThreatDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  threat: any;
}

type TabType = 'details' | 'alerts' | 'ai-analysis' | 'indicators' | 'assessments';

export const ThreatDetailModal = ({ isOpen, onClose, threat }: ThreatDetailModalProps) => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>('details');
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [extractedIndicators, setExtractedIndicators] = useState<any>(null);

  const analyzeMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post(`/threat-intelligence/threats/${threat.id}/ai_analyze/`);
      return response.data;
    },
    onSuccess: (data) => {
      setAiAnalysis(data);
      queryClient.invalidateQueries({ queryKey: ['threats'] });
      toast.success('AI analysis complete!');
    },
    onError: () => {
      toast.error('AI analysis failed');
    },
  });

  const generateRiskMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post(`/threat-intelligence/threats/${threat.id}/generate_risk_assessment/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risk-assessments'] });
      toast.success('Risk assessment generated!');
      setActiveTab('assessments');
    },
    onError: () => {
      toast.error('Failed to generate risk assessment');
    },
  });

  const extractIndicatorsMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post(`/threat-intelligence/threats/${threat.id}/extract_indicators/`);
      return response.data;
    },
    onSuccess: (data) => {
      setExtractedIndicators(data);
      queryClient.invalidateQueries({ queryKey: ['threat-indicators'] });
      toast.success(`Extracted ${data.indicators?.length || 0} indicators!`);
      setActiveTab('indicators');
    },
    onError: () => {
      toast.error('Failed to extract indicators');
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: async (status: string) => {
      const response = await api.post(`/threat-intelligence/threats/${threat.id}/update_status/`, { status });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['threats'] });
      toast.success('Status updated!');
    },
    onError: () => {
      toast.error('Failed to update status');
    },
  });

  // Fetch related alerts - MUST be before conditional return (React Hooks rules)
  const { data: relatedAlerts } = useQuery({
    queryKey: ['threat-alerts', threat?.id],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/alerts/', {
        params: { threat: threat.id }
      });
      return response.data.results || response.data;
    },
    enabled: isOpen && !!threat?.id,
  });

  if (!isOpen || !threat) return null;

  const tabs = [
    { id: 'details' as TabType, label: 'Details', icon: AlertTriangle },
    { id: 'alerts' as TabType, label: 'Related Alerts', icon: Bell, count: relatedAlerts?.length || 0 },
    { id: 'ai-analysis' as TabType, label: 'AI Analysis', icon: Sparkles },
    { id: 'indicators' as TabType, label: 'Indicators', icon: Search },
    { id: 'assessments' as TabType, label: 'Risk Assessment', icon: Target },
  ];

  const STATUS_OPTIONS = [
    { value: 'new', label: 'New', color: 'bg-blue-100 text-blue-800' },
    { value: 'investigating', label: 'Investigating', color: 'bg-purple-100 text-purple-800' },
    { value: 'confirmed', label: 'Confirmed', color: 'bg-red-100 text-red-800' },
    { value: 'mitigated', label: 'Mitigated', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'resolved', label: 'Resolved', color: 'bg-green-100 text-green-800' },
    { value: 'false_positive', label: 'False Positive', color: 'bg-gray-100 text-gray-800' },
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="inline-block w-full max-w-4xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-gray-800 shadow-xl rounded-lg">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {threat.title}
                </h3>
                <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                  threat.severity === 'critical' ? 'bg-red-100 text-red-800' :
                  threat.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                  threat.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {threat.severity}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Type: {threat.threat_type} • Created {new Date(threat.created_at).toLocaleDateString()}
              </p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex -mb-px px-6">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      py-4 px-4 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors
                      ${activeTab === tab.id
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                    {tab.count !== undefined && tab.count > 0 && (
                      <span className="ml-1 px-2 py-0.5 text-xs bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded-full">
                        {tab.count}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="p-6 max-h-[60vh] overflow-y-auto">
            {activeTab === 'details' && (
              <div className="space-y-6">
                {/* Status Update */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Status
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {STATUS_OPTIONS.map(status => (
                      <button
                        key={status.value}
                        onClick={() => updateStatusMutation.mutate(status.value)}
                        disabled={threat.status === status.value}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                          threat.status === status.value
                            ? status.color + ' ring-2 ring-blue-500'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }`}
                      >
                        {status.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Description */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</h4>
                  <p className="text-gray-900 dark:text-white">{threat.description}</p>
                </div>

                {/* Source */}
                {threat.source && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Source</h4>
                    <p className="text-gray-900 dark:text-white">{threat.source}</p>
                  </div>
                )}

                {/* Tags */}
                {threat.tags && threat.tags.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      {threat.tags.map((tag: string) => (
                        <span key={tag} className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Quick Actions */}
                <div className="grid grid-cols-3 gap-3 pt-4">
                  <Button
                    onClick={() => analyzeMutation.mutate()}
                    disabled={analyzeMutation.isPending}
                    variant="secondary"
                    className="flex items-center gap-2"
                  >
                    <Sparkles className="w-4 h-4" />
                    {analyzeMutation.isPending ? 'Analyzing...' : 'AI Analyze'}
                  </Button>
                  <Button
                    onClick={() => generateRiskMutation.mutate()}
                    disabled={generateRiskMutation.isPending}
                    variant="secondary"
                    className="flex items-center gap-2"
                  >
                    <Target className="w-4 h-4" />
                    {generateRiskMutation.isPending ? 'Generating...' : 'Risk Assessment'}
                  </Button>
                  <Button
                    onClick={() => extractIndicatorsMutation.mutate()}
                    disabled={extractIndicatorsMutation.isPending}
                    variant="secondary"
                    className="flex items-center gap-2"
                  >
                    <Search className="w-4 h-4" />
                    {extractIndicatorsMutation.isPending ? 'Extracting...' : 'Extract IOCs'}
                  </Button>
                </div>
              </div>
            )}

            {activeTab === 'alerts' && (
              <div className="space-y-4">
                {!relatedAlerts || relatedAlerts.length === 0 ? (
                  <div className="text-center py-12">
                    <Bell className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h4 className="text-lg font-semibold mb-2">No Related Alerts</h4>
                    <p className="text-gray-600 dark:text-gray-400">
                      No alerts have been linked to this threat yet
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {relatedAlerts.map((alert: any) => (
                      <Card key={alert.id} className="p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <Bell className="w-4 h-4 text-orange-500" />
                              <h5 className="font-semibold text-gray-900 dark:text-white">
                                {alert.title}
                              </h5>
                              <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                                alert.severity === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                                alert.severity === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                                alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                                'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                              }`}>
                                {alert.severity}
                              </span>
                              <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                                alert.status === 'new' ? 'bg-blue-100 text-blue-800' :
                                alert.status === 'acknowledged' ? 'bg-purple-100 text-purple-800' :
                                'bg-green-100 text-green-800'
                              }`}>
                                {alert.status}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                              {alert.description}
                            </p>
                            <div className="flex items-center gap-4 text-xs text-gray-500">
                              <span>Type: {alert.alert_type}</span>
                              {alert.source && <span>Source: {alert.source}</span>}
                              <span>{new Date(alert.created_at).toLocaleString()}</span>
                            </div>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'ai-analysis' && (
              <div className="space-y-4">
                {!aiAnalysis && !threat.ai_analyzed && (
                  <div className="text-center py-12">
                    <Sparkles className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h4 className="text-lg font-semibold mb-2">AI Analysis Not Run Yet</h4>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      Run AI analysis to get severity assessment, attack vectors, and recommendations
                    </p>
                    <Button onClick={() => analyzeMutation.mutate()} disabled={analyzeMutation.isPending}>
                      <Sparkles className="w-4 h-4 mr-2" />
                      {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze Now'}
                    </Button>
                  </div>
                )}

                {(aiAnalysis?.analysis || threat.ai_analysis) && (
                  <div className="space-y-4">
                    {/* AI Confidence */}
                    {(aiAnalysis?.analysis?.confidence || threat.ai_confidence) && (
                      <Card className="p-4">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">AI Confidence</span>
                          <span className="text-lg font-bold text-blue-600">
                            {Math.round((aiAnalysis?.analysis?.confidence || threat.ai_confidence) * 100)}%
                          </span>
                        </div>
                      </Card>
                    )}

                    {/* Analysis Details */}
                    {Object.entries(aiAnalysis?.analysis || threat.ai_analysis || {}).map(([key, value]) => {
                      if (key === 'confidence' || !value) return null;
                      return (
                        <Card key={key} className="p-4">
                          <h5 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 capitalize">
                            {key.replace(/_/g, ' ')}
                          </h5>
                          {Array.isArray(value) ? (
                            <ul className="list-disc list-inside space-y-1">
                              {value.map((item, i) => (
                                <li key={i} className="text-sm text-gray-900 dark:text-white">{item}</li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-sm text-gray-900 dark:text-white">{String(value)}</p>
                          )}
                        </Card>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'indicators' && (
              <div className="space-y-4">
                {!extractedIndicators && (
                  <div className="text-center py-12">
                    <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h4 className="text-lg font-semibold mb-2">No Indicators Extracted</h4>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      Extract indicators of compromise from the threat description
                    </p>
                    <Button onClick={() => extractIndicatorsMutation.mutate()} disabled={extractIndicatorsMutation.isPending}>
                      <Search className="w-4 h-4 mr-2" />
                      {extractIndicatorsMutation.isPending ? 'Extracting...' : 'Extract Now'}
                    </Button>
                  </div>
                )}

                {extractedIndicators && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      {extractedIndicators.summary}
                    </p>
                    <div className="space-y-3">
                      {extractedIndicators.indicators?.map((indicator: any, index: number) => (
                        <Card key={index} className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                                  {indicator.type}
                                </span>
                                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                  {indicator.confidence} confidence
                                </span>
                              </div>
                              <p className="font-mono text-sm font-semibold mb-1">{indicator.value}</p>
                              <p className="text-xs text-gray-600 dark:text-gray-400">{indicator.description}</p>
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'assessments' && (
              <div className="text-center py-12">
                <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold mb-2">Generate Risk Assessment</h4>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Create a comprehensive risk assessment for this threat
                </p>
                <Button onClick={() => generateRiskMutation.mutate()} disabled={generateRiskMutation.isPending}>
                  <Target className="w-4 h-4 mr-2" />
                  {generateRiskMutation.isPending ? 'Generating...' : 'Generate Now'}
                </Button>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
            <Button variant="secondary" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
