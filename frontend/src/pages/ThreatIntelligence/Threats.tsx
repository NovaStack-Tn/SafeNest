import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Target, AlertTriangle, TrendingUp, Shield, Search, Filter, X } from 'lucide-react';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Loader } from '@/components/Loader';
import { useAuthStore } from '@/store/authStore';
import api from '@/lib/api';
import toast from 'react-hot-toast';

interface Threat {
  id: number;
  title: string;
  description: string;
  threat_type: string;
  severity: string;
  status: string;
  risk_score: number;
  confidence_score: number;
  first_detected_at: string;
  location_name?: string;
}

const SEVERITY_COLORS = {
  critical: 'bg-red-500 text-white',
  high: 'bg-orange-500 text-white',
  medium: 'bg-yellow-500 text-white',
  low: 'bg-green-500 text-white',
};

const STATUS_COLORS = {
  new: 'bg-blue-500',
  investigating: 'bg-purple-500',
  confirmed: 'bg-orange-500',
  mitigated: 'bg-yellow-500',
  resolved: 'bg-green-500',
  false_positive: 'bg-gray-500',
};

export const Threats = () => {
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    threat_type: 'malware',
    severity: 'medium',
    source: 'manual',
  });

  const { data: threats, isLoading } = useQuery<Threat[]>({
    queryKey: ['threats'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/threats/');
      return response.data.results || response.data;
    },
    refetchInterval: 30000,
  });

  // Create threat mutation
  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const payload = {
        ...data,
        organization: user?.organization,
        created_by: user?.id,
      };
      const response = await api.post('/threat-intelligence/threats/', payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['threats'] });
      setIsCreateModalOpen(false);
      setFormData({
        title: '',
        description: '',
        threat_type: 'malware',
        severity: 'medium',
        source: 'manual',
      });
      toast.success('Threat created successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create threat');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const filteredThreats = threats?.filter((threat) => {
    const matchesSearch = threat.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         threat.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = severityFilter === 'all' || threat.severity === severityFilter;
    const matchesStatus = statusFilter === 'all' || threat.status === statusFilter;
    return matchesSearch && matchesSeverity && matchesStatus;
  });

  const stats = {
    total: threats?.length || 0,
    critical: threats?.filter((t) => t.severity === 'critical').length || 0,
    active: threats?.filter((t) => !['resolved', 'false_positive'].includes(t.status)).length || 0,
    avgRisk: threats?.length ? 
      (threats.reduce((sum, t) => sum + t.risk_score, 0) / threats.length).toFixed(1) : 0,
  };

  if (isLoading) {
    return <Loader text="Loading threats..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Threat Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Monitor and manage security threats
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Threat
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Threats</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{stats.total}</p>
            </div>
            <Target className="w-12 h-12 text-blue-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Critical</p>
              <p className="text-3xl font-bold text-red-600 mt-2">{stats.critical}</p>
            </div>
            <AlertTriangle className="w-12 h-12 text-red-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Threats</p>
              <p className="text-3xl font-bold text-orange-600 mt-2">{stats.active}</p>
            </div>
            <TrendingUp className="w-12 h-12 text-orange-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Avg Risk Score</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">{stats.avgRisk}</p>
            </div>
            <Shield className="w-12 h-12 text-yellow-600" />
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search threats..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div>
            <select
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div>
            <select
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="new">New</option>
              <option value="investigating">Investigating</option>
              <option value="confirmed">Confirmed</option>
              <option value="mitigated">Mitigated</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Threats List */}
      <div className="space-y-4">
        {filteredThreats?.length === 0 ? (
          <Card className="p-12">
            <div className="text-center">
              <Filter className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                No threats found
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Try adjusting your filters
              </p>
            </div>
          </Card>
        ) : (
          filteredThreats?.map((threat) => (
            <Card key={threat.id} className="p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${SEVERITY_COLORS[threat.severity as keyof typeof SEVERITY_COLORS]}`}>
                      {threat.severity.toUpperCase()}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold text-white ${STATUS_COLORS[threat.status as keyof typeof STATUS_COLORS]}`}>
                      {threat.status.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="text-sm text-gray-500">
                      Risk: {threat.risk_score.toFixed(1)}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {threat.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-3">
                    {threat.description}
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>Type: {threat.threat_type.replace('_', ' ')}</span>
                    {threat.location_name && <span>📍 {threat.location_name}</span>}
                    <span>Detected: {new Date(threat.first_detected_at).toLocaleDateString()}</span>
                    <span>Confidence: {(threat.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                </div>
                <Button variant="secondary" size="sm">
                  View Details
                </Button>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Create Threat Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Create New Threat
                </h2>
                <button
                  onClick={() => setIsCreateModalOpen(false)}
                  className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Title *
                  </label>
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description *
                  </label>
                  <textarea
                    required
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Threat Type *
                    </label>
                    <select
                      required
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      value={formData.threat_type}
                      onChange={(e) => setFormData({ ...formData, threat_type: e.target.value })}
                    >
                      <option value="malware">Malware</option>
                      <option value="phishing">Phishing</option>
                      <option value="ransomware">Ransomware</option>
                      <option value="ddos">DDoS</option>
                      <option value="data_breach">Data Breach</option>
                      <option value="unauthorized_access">Unauthorized Access</option>
                      <option value="insider_threat">Insider Threat</option>
                      <option value="social_engineering">Social Engineering</option>
                      <option value="zero_day">Zero Day</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Severity *
                    </label>
                    <select
                      required
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      value={formData.severity}
                      onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Source
                  </label>
                  <select
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    value={formData.source}
                    onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                  >
                    <option value="manual">Manual</option>
                    <option value="automated">Automated</option>
                    <option value="external_feed">External Feed</option>
                    <option value="user_report">User Report</option>
                  </select>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    type="submit"
                    disabled={createMutation.isPending}
                    className="flex-1"
                  >
                    {createMutation.isPending ? 'Creating...' : 'Create Threat'}
                  </Button>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => setIsCreateModalOpen(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
