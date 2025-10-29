import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  X, Shield, Clock, User, FileText, Paperclip, Activity,
  CheckCircle, Sparkles, Upload, Download
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';
import { Card } from './Card';
import { Button } from './Button';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import type { Incident, IncidentEvent, Evidence } from '@/lib/types';

interface IncidentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  incidentId: number;
}

export const IncidentDetailModal = ({
  isOpen,
  onClose,
  incidentId,
}: IncidentDetailModalProps) => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'timeline' | 'evidence' | 'resolution'>('timeline');
  const [comment, setComment] = useState('');
  const [showResolutionForm, setShowResolutionForm] = useState(false);
  const [uploadingEvidence, setUploadingEvidence] = useState(false);
  const [aiSummary, setAiSummary] = useState<string | null>(null);
  const [aiActions, setAiActions] = useState<Array<{action: string, priority: string, description: string}> | null>(null);
  const [resolutionData, setResolutionData] = useState({
    resolution_type: 'resolved',
    summary: '',
    actions_taken: '',
    root_cause: '',
    preventive_measures: '',
  });

  // Fetch incident details
  const { data: incident, isLoading } = useQuery<Incident>({
    queryKey: ['incident', incidentId],
    queryFn: async () => {
      const response = await api.get(`/incidents/incidents/${incidentId}/`);
      return response.data;
    },
    enabled: isOpen && !!incidentId,
  });

  // Add comment mutation
  const addCommentMutation = useMutation({
    mutationFn: async (commentText: string) => {
      const response = await api.post(`/incidents/incidents/${incidentId}/add_comment/`, {
        comment: commentText,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incident', incidentId] });
      setComment('');
      toast.success('Comment added');
    },
    onError: () => {
      toast.error('Failed to add comment');
    },
  });

  // AI Classify mutation
  const aiClassifyMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post(`/incidents/incidents/${incidentId}/ai_classify/`);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['incident', incidentId] });
      toast.success(`AI classified as ${data.severity} (${Math.round(data.confidence * 100)}% confidence)`);
    },
    onError: () => {
      toast.error('AI classification failed');
    },
  });

  // AI Summary mutation
  const aiSummaryMutation = useMutation({
    mutationFn: async () => {
      const response = await api.get(`/incidents/incidents/${incidentId}/ai_summary/`);
      return response.data;
    },
    onSuccess: (data) => {
      setAiSummary(data.summary);
      toast.success('AI summary generated');
    },
    onError: () => {
      toast.error('Failed to generate AI summary');
    },
  });

  // AI Actions mutation
  const aiActionsMutation = useMutation({
    mutationFn: async () => {
      const response = await api.get(`/incidents/incidents/${incidentId}/ai_actions/`);
      return response.data;
    },
    onSuccess: (data) => {
      setAiActions(data.actions);
      toast.success('AI actions suggested');
    },
    onError: () => {
      toast.error('Failed to get AI recommendations');
    },
  });

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async (status: string) => {
      const response = await api.patch(`/incidents/incidents/${incidentId}/`, { status });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incident', incidentId] });
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      toast.success('Status updated');
    },
    onError: () => {
      toast.error('Failed to update status');
    },
  });

  // Add resolution mutation
  const addResolutionMutation = useMutation({
    mutationFn: async (data: typeof resolutionData) => {
      const response = await api.post('/incidents/resolutions/', {
        ...data,
        incident: incidentId,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incident', incidentId] });
      setShowResolutionForm(false);
      setResolutionData({
        resolution_type: 'resolved',
        summary: '',
        actions_taken: '',
        root_cause: '',
        preventive_measures: '',
      });
      toast.success('Resolution added successfully');
    },
    onError: () => {
      toast.error('Failed to add resolution');
    },
  });

  // Handle evidence upload
  const handleEvidenceUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploadingEvidence(true);
    const file = files[0];

    try {
      // Auto-detect file kind based on file type
      let kind = 'other';
      if (file.type.startsWith('image/')) {
        kind = 'image';
      } else if (file.type === 'application/pdf') {
        kind = 'document';
      } else if (file.name.endsWith('.log') || file.name.endsWith('.txt')) {
        kind = 'log';
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('incident', incidentId.toString());
      formData.append('kind', kind);
      formData.append('description', `Uploaded: ${file.name}`);

      await api.post('/incidents/evidence/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      queryClient.invalidateQueries({ queryKey: ['incident', incidentId] });
      toast.success('Evidence uploaded successfully');
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMsg = error.response?.data?.detail || error.response?.data?.file?.[0] || 'Failed to upload evidence';
      toast.error(errorMsg);
    } finally {
      setUploadingEvidence(false);
      // Reset file input
      if (event.target) {
        event.target.value = '';
      }
    }
  };

  if (!incident || isLoading) {
    return null;
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-300';
      case 'high': return 'text-orange-600 bg-orange-100 dark:bg-orange-900 dark:text-orange-300';
      case 'medium': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-300';
      default: return 'text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-300';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-300';
      case 'investigating': return 'text-orange-600 bg-orange-100 dark:bg-orange-900 dark:text-orange-300';
      case 'contained': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-300';
      case 'resolved': return 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-300';
      case 'closed': return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-300';
      default: return 'text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-300';
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Modal */}
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-6xl max-h-[90vh] overflow-hidden"
            >
              <Card className="flex flex-col h-full">
                {/* Header */}
                <div className="flex items-start justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Shield className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        Incident #{incident.id}
                      </span>
                      <span className={`px-3 py-1 text-xs font-medium rounded-full uppercase ${getSeverityColor(incident.severity)}`}>
                        {incident.severity}
                      </span>
                      <span className={`px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(incident.status)}`}>
                        {incident.status}
                      </span>
                      {incident.ai_generated && (
                        <span className="px-3 py-1 text-xs font-medium rounded-full bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          AI Generated
                        </span>
                      )}
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                      {incident.title}
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400">
                      {incident.description}
                    </p>
                    
                    {/* Metadata */}
                    <div className="flex flex-wrap gap-4 mt-4 text-sm">
                      {incident.created_by_name && (
                        <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                          <User className="w-4 h-4" />
                          <span>Created by {incident.created_by_name}</span>
                        </div>
                      )}
                      {incident.assignee_name && (
                        <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                          <User className="w-4 h-4" />
                          <span>Assigned to {incident.assignee_name}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                        <Clock className="w-4 h-4" />
                        <span>{formatDistanceToNow(new Date(incident.opened_at), { addSuffix: true })}</span>
                      </div>
                      {incident.category_name && (
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-1 text-xs rounded" style={{ backgroundColor: incident.category_color + '20', color: incident.category_color }}>
                            {incident.category_name}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* AI Entities */}
                    {incident.extracted_entities && Object.keys(incident.extracted_entities).length > 0 && (
                      <div className="mt-4 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                        <p className="text-sm font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                          <Sparkles className="w-4 h-4 text-purple-600" />
                          AI Extracted Entities
                        </p>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          {Object.entries(incident.extracted_entities).map(([key, values]) => (
                            Array.isArray(values) && values.length > 0 && (
                              <div key={key}>
                                <span className="font-medium text-gray-700 dark:text-gray-300 capitalize">{key.replace('_', ' ')}: </span>
                                <span className="text-gray-600 dark:text-gray-400">{values.join(', ')}</span>
                              </div>
                            )
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={onClose}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Actions Bar */}
                <div className="flex items-center gap-2 px-6 py-3 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                  <Button
                    onClick={() => aiClassifyMutation.mutate()}
                    loading={aiClassifyMutation.isPending}
                    className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700"
                  >
                    <Sparkles className="w-4 h-4" />
                    AI Classify
                  </Button>

                  <Button
                    onClick={() => aiSummaryMutation.mutate()}
                    loading={aiSummaryMutation.isPending}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
                  >
                    <Sparkles className="w-4 h-4" />
                    Generate Summary
                  </Button>

                  <Button
                    onClick={() => aiActionsMutation.mutate()}
                    loading={aiActionsMutation.isPending}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
                  >
                    <Sparkles className="w-4 h-4" />
                    Suggest Actions
                  </Button>
                  
                  <select
                    value={incident.status}
                    onChange={(e) => updateStatusMutation.mutate(e.target.value)}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                  >
                    <option value="open">Open</option>
                    <option value="investigating">Investigating</option>
                    <option value="contained">Contained</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>

                  {!incident.has_resolution && (incident.status === 'resolved' || incident.status === 'closed') && (
                    <Button
                      onClick={() => setShowResolutionForm(true)}
                      className="flex items-center gap-2"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Add Resolution
                    </Button>
                  )}
                </div>

                {/* Tabs */}
                <div className="flex border-b border-gray-200 dark:border-gray-700 px-6">
                  <button
                    onClick={() => setActiveTab('timeline')}
                    className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === 'timeline'
                        ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                        : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4" />
                      Timeline ({incident.event_count})
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('evidence')}
                    className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === 'evidence'
                        ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                        : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Paperclip className="w-4 h-4" />
                      Evidence ({incident.evidence_count})
                    </div>
                  </button>
                  {incident.has_resolution && (
                    <button
                      onClick={() => setActiveTab('resolution')}
                      className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                        activeTab === 'resolution'
                          ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                          : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4" />
                        Resolution
                      </div>
                    </button>
                  )}
                </div>

                {/* AI Summary Display */}
                {aiSummary && (
                  <div className="mx-6 mt-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <div className="flex items-start gap-3">
                      <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                          AI-Generated Summary
                        </h3>
                        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                          {aiSummary}
                        </p>
                      </div>
                      <button
                        onClick={() => setAiSummary(null)}
                        className="p-1 hover:bg-blue-100 dark:hover:bg-blue-800 rounded transition-colors"
                        title="Close summary"
                      >
                        <X className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                      </button>
                    </div>
                  </div>
                )}

                {/* AI Actions Display */}
                {aiActions && (
                  <div className="mx-6 mt-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <div className="flex items-start gap-3">
                      <Sparkles className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                            AI-Recommended Actions
                          </h3>
                          <button
                            onClick={() => setAiActions(null)}
                            className="p-1 hover:bg-green-100 dark:hover:bg-green-800 rounded transition-colors"
                            title="Close actions"
                          >
                            <X className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                          </button>
                        </div>
                        <div className="space-y-3">
                          {aiActions.map((action, index) => (
                            <div key={index} className="flex gap-3 items-start">
                              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-200 dark:bg-green-800 flex items-center justify-center text-xs font-bold text-green-700 dark:text-green-300">
                                {index + 1}
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                                    {action.action}
                                  </h4>
                                  <span className={`px-2 py-0.5 text-xs rounded-full ${
                                    action.priority.toLowerCase() === 'high'
                                      ? 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300'
                                      : action.priority.toLowerCase() === 'medium'
                                      ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300'
                                      : 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                                  }`}>
                                    {action.priority}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  {action.description}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Tab Content */}
                <div className="flex-1 overflow-y-auto p-6">
                  {activeTab === 'timeline' && (
                    <div className="space-y-4">
                      {/* Add Comment */}
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={comment}
                          onChange={(e) => setComment(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && comment && addCommentMutation.mutate(comment)}
                          placeholder="Add a comment..."
                          className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        />
                        <Button
                          onClick={() => comment && addCommentMutation.mutate(comment)}
                          loading={addCommentMutation.isPending}
                          disabled={!comment}
                        >
                          Comment
                        </Button>
                      </div>

                      {/* Events Timeline */}
                      {incident.events && incident.events.length > 0 ? (
                        <div className="max-h-[500px] overflow-y-auto pr-2 space-y-3">
                          {incident.events.map((event: IncidentEvent) => (
                            <motion.div
                              key={event.id}
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              className="flex gap-3"
                            >
                              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                                <Activity className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                              </div>
                              <div className="flex-1 pb-4 border-b border-gray-200 dark:border-gray-700">
                                <div className="flex items-start justify-between mb-1">
                                  <p className="font-medium text-gray-900 dark:text-white">
                                    {event.action.replace('_', ' ').toUpperCase()}
                                  </p>
                                  <span className="text-xs text-gray-500 dark:text-gray-400">
                                    {format(new Date(event.timestamp), 'MMM d, yyyy HH:mm')}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                                  {event.description}
                                </p>
                                {event.actor_name && (
                                  <p className="text-xs text-gray-500 dark:text-gray-400">
                                    by {event.actor_name}
                                  </p>
                                )}
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-12 text-gray-400 dark:text-gray-500">
                          <Activity className="w-12 h-12 mx-auto mb-3 opacity-50" />
                          <p>No timeline events yet</p>
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'evidence' && (
                    <div className="space-y-4">
                      {/* Upload Evidence */}
                      <div>
                        <input
                          type="file"
                          onChange={handleEvidenceUpload}
                          className="hidden"
                          id="evidence-upload"
                          accept=".pdf,.jpg,.jpeg,.png,.txt,.log,.csv,.json"
                        />
                        <Button
                          onClick={() => document.getElementById('evidence-upload')?.click()}
                          disabled={uploadingEvidence}
                          loading={uploadingEvidence}
                          className="flex items-center gap-2"
                        >
                          <Upload className="w-4 h-4" />
                          {uploadingEvidence ? 'Uploading...' : 'Upload Evidence'}
                        </Button>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Accepted: PDF, Images, Logs, CSV, JSON (Max 10MB)
                        </p>
                      </div>

                      {/* Evidence List */}
                      {incident.evidence && incident.evidence.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {incident.evidence.map((evidence: Evidence) => (
                            <Card key={evidence.id} className="p-4">
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex items-center gap-2">
                                  <FileText className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                                  <h4 className="font-medium text-gray-900 dark:text-white">
                                    {evidence.file_name}
                                  </h4>
                                </div>
                                <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">
                                  {evidence.kind}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                                {evidence.description}
                              </p>
                              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                                <span>
                                  {evidence.uploaded_by_name} • {formatDistanceToNow(new Date(evidence.uploaded_at), { addSuffix: true })}
                                </span>
                                {evidence.file_url && (
                                  <a href={evidence.file_url} target="_blank" rel="noopener noreferrer">
                                    <Download className="w-4 h-4 hover:text-primary-600" />
                                  </a>
                                )}
                              </div>
                            </Card>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-12 text-gray-400 dark:text-gray-500">
                          <Paperclip className="w-12 h-12 mx-auto mb-3 opacity-50" />
                          <p>No evidence attached</p>
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'resolution' && incident.resolution && (
                    <div className="space-y-4">
                      <Card className="p-6">
                        <div className="flex items-center gap-2 mb-4">
                          <CheckCircle className="w-6 h-6 text-green-600" />
                          <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                            Resolution Details
                          </h3>
                          <span className="ml-auto px-3 py-1 text-sm bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full">
                            {incident.resolution.resolution_type.replace('_', ' ')}
                          </span>
                        </div>
                        
                        <div className="space-y-4">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white mb-2">Summary</h4>
                            <p className="text-gray-600 dark:text-gray-400">{incident.resolution.summary}</p>
                          </div>
                          
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white mb-2">Actions Taken</h4>
                            <p className="text-gray-600 dark:text-gray-400">{incident.resolution.actions_taken}</p>
                          </div>
                          
                          {incident.resolution.root_cause && (
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Root Cause</h4>
                              <p className="text-gray-600 dark:text-gray-400">{incident.resolution.root_cause}</p>
                            </div>
                          )}
                          
                          {incident.resolution.preventive_measures && (
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Preventive Measures</h4>
                              <p className="text-gray-600 dark:text-gray-400">{incident.resolution.preventive_measures}</p>
                            </div>
                          )}
                          
                          <div className="pt-4 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-500 dark:text-gray-400">
                            Resolved by {incident.resolution.resolved_by_name} • {formatDistanceToNow(new Date(incident.resolution.resolved_at), { addSuffix: true })}
                          </div>
                        </div>
                      </Card>
                    </div>
                  )}

                  {/* Resolution Form Modal */}
                  {showResolutionForm && (
                    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
                      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
                        <div className="flex items-center justify-between mb-6">
                          <h3 className="text-xl font-bold text-gray-900 dark:text-white">Add Resolution</h3>
                          <button
                            onClick={() => setShowResolutionForm(false)}
                            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                          >
                            <X className="w-5 h-5" />
                          </button>
                        </div>

                        <form
                          onSubmit={(e) => {
                            e.preventDefault();
                            addResolutionMutation.mutate(resolutionData);
                          }}
                          className="space-y-4"
                        >
                          <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Resolution Type
                            </label>
                            <select
                              value={resolutionData.resolution_type}
                              onChange={(e) => setResolutionData({ ...resolutionData, resolution_type: e.target.value })}
                              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                              required
                            >
                              <option value="resolved">Resolved</option>
                              <option value="false_positive">False Positive</option>
                              <option value="duplicate">Duplicate</option>
                              <option value="mitigated">Mitigated</option>
                              <option value="escalated">Escalated</option>
                              <option value="cannot_fix">Cannot Fix</option>
                            </select>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Summary *
                            </label>
                            <textarea
                              value={resolutionData.summary}
                              onChange={(e) => setResolutionData({ ...resolutionData, summary: e.target.value })}
                              rows={3}
                              required
                              placeholder="Brief summary of what happened..."
                              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Actions Taken *
                            </label>
                            <textarea
                              value={resolutionData.actions_taken}
                              onChange={(e) => setResolutionData({ ...resolutionData, actions_taken: e.target.value })}
                              rows={3}
                              required
                              placeholder="What actions were taken to resolve this incident..."
                              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Root Cause
                            </label>
                            <textarea
                              value={resolutionData.root_cause}
                              onChange={(e) => setResolutionData({ ...resolutionData, root_cause: e.target.value })}
                              rows={2}
                              placeholder="Why did this incident occur..."
                              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Preventive Measures
                            </label>
                            <textarea
                              value={resolutionData.preventive_measures}
                              onChange={(e) => setResolutionData({ ...resolutionData, preventive_measures: e.target.value })}
                              rows={2}
                              placeholder="How to prevent this from happening again..."
                              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none"
                            />
                          </div>

                          <div className="flex gap-3 pt-4">
                            <Button
                              type="button"
                              onClick={() => setShowResolutionForm(false)}
                              className="flex-1 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600"
                            >
                              Cancel
                            </Button>
                            <Button
                              type="submit"
                              loading={addResolutionMutation.isPending}
                              disabled={addResolutionMutation.isPending}
                              className="flex-1"
                            >
                              Add Resolution
                            </Button>
                          </div>
                        </form>
                      </Card>
                    </div>
                  )}
                </div>
              </Card>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};
