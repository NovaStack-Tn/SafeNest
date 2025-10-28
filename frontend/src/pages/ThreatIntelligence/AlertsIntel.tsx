import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Bell, CheckCircle, Clock, XCircle, Search } from 'lucide-react';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Loader } from '@/components/Loader';
import api from '@/lib/api';

interface Alert {
  id: number;
  title: string;
  description: string;
  alert_type: string;
  severity: string;
  status: string;
  confidence_score: number;
  triggered_at: string;
  user_name?: string;
}

const SEVERITY_COLORS = {
  critical: 'bg-red-600',
  high: 'bg-orange-600',
  medium: 'bg-yellow-600',
  low: 'bg-blue-600',
  info: 'bg-gray-600',
};

export const AlertsIntel = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const { data: alerts, isLoading } = useQuery<Alert[]>({
    queryKey: ['alerts-intel'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/alerts/');
      return response.data.results || response.data;
    },
    refetchInterval: 15000,
  });

  const filteredAlerts = alerts?.filter((alert) => {
    const matchesSearch = alert.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || alert.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const stats = {
    total: alerts?.length || 0,
    new: alerts?.filter((a) => a.status === 'new').length || 0,
    critical: alerts?.filter((a) => a.severity === 'critical').length || 0,
    resolved: alerts?.filter((a) => a.status === 'resolved').length || 0,
  };

  if (isLoading) {
    return <Loader text="Loading alerts..." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Threat Intelligence Alerts
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            System-generated threat alerts and notifications
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Alerts</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{stats.total}</p>
            </div>
            <Bell className="w-12 h-12 text-blue-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">New</p>
              <p className="text-3xl font-bold text-red-600 mt-2">{stats.new}</p>
            </div>
            <Clock className="w-12 h-12 text-red-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Critical</p>
              <p className="text-3xl font-bold text-orange-600 mt-2">{stats.critical}</p>
            </div>
            <XCircle className="w-12 h-12 text-orange-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Resolved</p>
              <p className="text-3xl font-bold text-green-600 mt-2">{stats.resolved}</p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search alerts..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Statuses</option>
            <option value="new">New</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="investigating">Investigating</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </Card>

      {/* Alerts List */}
      <div className="space-y-3">
        {filteredAlerts?.map((alert) => (
          <Card key={alert.id} className="p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className={`w-2 h-2 rounded-full ${SEVERITY_COLORS[alert.severity as keyof typeof SEVERITY_COLORS]}`} />
                  <span className="text-xs font-semibold text-gray-500 uppercase">
                    {alert.severity}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(alert.triggered_at).toLocaleString()}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                  {alert.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {alert.description}
                </p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Type: {alert.alert_type.replace('_', ' ')}</span>
                  {alert.user_name && <span>User: {alert.user_name}</span>}
                  <span>Confidence: {(alert.confidence_score * 100).toFixed(0)}%</span>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="secondary" size="sm">
                  Acknowledge
                </Button>
                <Button variant="primary" size="sm">
                  View
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
