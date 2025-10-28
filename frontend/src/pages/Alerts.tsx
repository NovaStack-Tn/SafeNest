import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, TrendingUp, CheckCircle } from 'lucide-react';
import { AlertCard } from '@/components/AlertCard';
import { AlertFilters } from '@/components/AlertFilters';
import { Card } from '@/components/Card';
import { Loader } from '@/components/Loader';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import type { Alert } from '@/lib/types';

export const Alerts = () => {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [severity, setSeverity] = useState('all');
  const [status, setStatus] = useState('all');
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Fetch alerts
  const { data: alerts, isLoading, error } = useQuery<Alert[]>({
    queryKey: ['alerts', severity, status],
    queryFn: async () => {
      let url = '/security/alerts/?';
      const params = new URLSearchParams();
      
      if (severity !== 'all') params.append('severity', severity);
      if (status !== 'all') params.append('status', status);
      
      const response = await api.get(url + params.toString());
      return response.data.results || response.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // WebSocket temporarily disabled - using polling instead
  // TODO: Implement JWT WebSocket authentication
  useEffect(() => {
    // Placeholder for future WebSocket implementation
    setWs(null);
  }, [queryClient]);

  // Acknowledge alert mutation
  const acknowledgeMutation = useMutation({
    mutationFn: async (alertId: number) => {
      await api.patch(`/security/alerts/${alertId}/`, {
        status: 'acknowledged',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alert acknowledged');
    },
    onError: () => {
      toast.error('Failed to acknowledge alert');
    },
  });

  // Resolve alert mutation
  const resolveMutation = useMutation({
    mutationFn: async (alertId: number) => {
      await api.patch(`/security/alerts/${alertId}/`, {
        status: 'resolved',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alert resolved');
    },
    onError: () => {
      toast.error('Failed to resolve alert');
    },
  });

  // Filter alerts by search
  const filteredAlerts = alerts?.filter((alert) => {
    if (search) {
      const searchLower = search.toLowerCase();
      return (
        alert.title.toLowerCase().includes(searchLower) ||
        alert.message.toLowerCase().includes(searchLower) ||
        alert.alert_type?.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });

  const handleReset = () => {
    setSearch('');
    setSeverity('all');
    setStatus('all');
  };

  // Calculate stats
  const stats = {
    total: alerts?.length || 0,
    open: alerts?.filter((a) => a.status === 'open').length || 0,
    critical: alerts?.filter((a) => a.severity === 'critical').length || 0,
    resolved: alerts?.filter((a) => a.status === 'resolved').length || 0,
  };

  if (isLoading) {
    return <Loader text="Loading alerts..." />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <Card className="max-w-md p-8 text-center">
          <AlertTriangle className="w-16 h-16 mx-auto mb-4 text-red-500" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            Failed to Load Alerts
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Unable to fetch alerts from the server.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Security Alerts</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Monitor and respond to security events in real-time
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Auto-refresh (30s)
          </span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Alerts</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                  {stats.total}
                </p>
              </div>
              <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Open</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                  {stats.open}
                </p>
              </div>
              <div className="p-3 rounded-full bg-orange-100 dark:bg-orange-900">
                <AlertTriangle className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Critical</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                  {stats.critical}
                </p>
              </div>
              <div className="p-3 rounded-full bg-red-100 dark:bg-red-900">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card className="hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Resolved</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                  {stats.resolved}
                </p>
              </div>
              <div className="p-3 rounded-full bg-green-100 dark:bg-green-900">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Filters & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <AlertFilters
            search={search}
            onSearchChange={setSearch}
            severity={severity}
            onSeverityChange={setSeverity}
            status={status}
            onStatusChange={setStatus}
            onReset={handleReset}
          />
        </div>

        {/* Alerts List */}
        <div className="lg:col-span-3 space-y-4">
          {filteredAlerts && filteredAlerts.length > 0 ? (
            <AnimatePresence>
              {filteredAlerts.map((alert) => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onAcknowledge={(id) => acknowledgeMutation.mutate(id)}
                  onResolve={(id) => resolveMutation.mutate(id)}
                />
              ))}
            </AnimatePresence>
          ) : (
            <Card className="p-12 text-center">
              <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-500 opacity-50" />
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                No Alerts Found
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {search || severity !== 'all' || status !== 'all'
                  ? 'Try adjusting your filters'
                  : 'All clear! No security alerts at the moment.'}
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
