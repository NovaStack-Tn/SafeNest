import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, AlertTriangle, TrendingUp, Clock, CheckCircle } from 'lucide-react';
import { IncidentCard } from '@/components/IncidentCard';
import { CreateIncidentModal } from '@/components/CreateIncidentModal';
import { Card } from '@/components/Card';
import { Loader } from '@/components/Loader';
import { Button } from '@/components/Button';
import { useAuthStore } from '@/store/authStore';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import type { Incident } from '@/lib/types';

const STATUS_COLUMNS = [
  { id: 'open', title: 'Open', color: 'bg-red-500', icon: AlertTriangle },
  { id: 'investigating', title: 'Investigating', color: 'bg-orange-500', icon: Clock },
  { id: 'contained', title: 'Contained', color: 'bg-yellow-500', icon: TrendingUp },
  { id: 'resolved', title: 'Resolved', color: 'bg-green-500', icon: CheckCircle },
  { id: 'closed', title: 'Closed', color: 'bg-gray-500', icon: CheckCircle },
];

export const Incidents = () => {
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  // const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null); // TODO: For detail modal

  // Fetch incidents
  const { data: incidents, isLoading, error } = useQuery<Incident[]>({
    queryKey: ['incidents'],
    queryFn: async () => {
      const response = await api.get('/incidents/incidents/');
      return response.data.results || response.data;
    },
    refetchInterval: 60000, // Refresh every minute
  });

  // Create incident mutation
  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      // Add organization from logged-in user
      const payload = {
        ...data,
        organization: user?.organization,
      };
      const response = await api.post('/incidents/incidents/', payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      setIsCreateModalOpen(false);
      toast.success('Incident created successfully');
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail 
        || error.response?.data?.message 
        || JSON.stringify(error.response?.data)
        || 'Failed to create incident';
      console.error('Incident creation error:', error.response?.data);
      toast.error(errorMessage);
    },
  });

  // Group incidents by status
  const groupedIncidents = STATUS_COLUMNS.reduce((acc, column) => {
    acc[column.id] = incidents?.filter((inc) => inc.status === column.id) || [];
    return acc;
  }, {} as Record<string, Incident[]>);

  // Calculate stats
  const stats = {
    total: incidents?.length || 0,
    open: incidents?.filter((i) => i.status === 'open').length || 0,
    critical: incidents?.filter((i) => i.severity === 'critical').length || 0,
    resolved: incidents?.filter((i) => i.status === 'resolved' || i.status === 'closed').length || 0,
  };

  if (isLoading) {
    return <Loader text="Loading incidents..." />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <Card className="max-w-md p-8 text-center">
          <AlertTriangle className="w-16 h-16 mx-auto mb-4 text-red-500" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            Failed to Load Incidents
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Unable to fetch incidents from the server.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Incidents</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage security incidents through their lifecycle
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)} className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          New Incident
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
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
              <div className="p-3 rounded-full bg-red-100 dark:bg-red-900">
                <AlertTriangle className="w-6 h-6 text-red-600" />
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
              <div className="p-3 rounded-full bg-orange-100 dark:bg-orange-900">
                <AlertTriangle className="w-6 h-6 text-orange-600" />
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

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto">
        <div className="flex gap-4 min-w-max pb-4" style={{ minHeight: '500px' }}>
          {STATUS_COLUMNS.map((column) => {
            const Icon = column.icon;
            const columnIncidents = groupedIncidents[column.id] || [];

            return (
              <motion.div
                key={column.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex-shrink-0 w-80"
              >
                <Card className="h-full flex flex-col">
                  {/* Column Header */}
                  <div className="flex items-center gap-2 p-4 border-b border-gray-200 dark:border-gray-700">
                    <div className={`p-1.5 rounded ${column.color} bg-opacity-20`}>
                      <Icon className={`w-4 h-4 ${column.color.replace('bg-', 'text-')}`} />
                    </div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {column.title}
                    </h3>
                    <span className="ml-auto text-sm text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                      {columnIncidents.length}
                    </span>
                  </div>

                  {/* Column Content */}
                  <div className="flex-1 p-4 space-y-3 overflow-y-auto">
                    <AnimatePresence>
                      {columnIncidents.length > 0 ? (
                        columnIncidents.map((incident) => (
                          <IncidentCard
                            key={incident.id}
                            incident={incident}
                            onClick={() => {
                              // TODO: Open incident detail modal
                              toast(`Incident #${incident.id}: ${incident.title}`, { icon: '📋' });
                            }}
                          />
                        ))
                      ) : (
                        <div className="text-center py-8 text-gray-400 dark:text-gray-500 text-sm">
                          No incidents
                        </div>
                      )}
                    </AnimatePresence>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Create Incident Modal */}
      <CreateIncidentModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={(data) => createMutation.mutate(data)}
        loading={createMutation.isPending}
      />
    </div>
  );
};
