import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus, Target, AlertTriangle, TrendingUp, Shield, Search, Filter } from 'lucide-react';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Loader } from '@/components/Loader';
import api from '@/lib/api';

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
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const { data: threats, isLoading } = useQuery<Threat[]>({
    queryKey: ['threats'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/threats/');
      return response.data.results || response.data;
    },
    refetchInterval: 30000,
  });

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
        <Button>
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
    </div>
  );
};
