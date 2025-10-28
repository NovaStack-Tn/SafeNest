import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Shield,
  AlertTriangle,
  Users,
  Camera,
  Activity,
  TrendingUp,
  FileText,
  MessageSquare,
} from 'lucide-react';
import { Card } from '@/components/Card';
import { Loader } from '@/components/Loader';
import { RealtimeAlerts } from '@/components/RealtimeAlerts';
import { ActivityFeed } from '@/components/ActivityFeed';
import { LoginChart } from '@/components/LoginChart';
import api from '@/lib/api';
import type { DashboardStats } from '@/lib/types';

export const Dashboard = () => {
  const navigate = useNavigate();
  
  const { data: stats, isLoading, error } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await api.get('/dashboard/stats/?range=7d');
      return response.data;
    },
    refetchInterval: 60000, // Refresh every minute
  });

  if (isLoading) {
    return <Loader text="Loading dashboard..." />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <Card className="max-w-md p-8 text-center">
          <AlertTriangle className="w-16 h-16 mx-auto mb-4 text-red-500" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            Failed to Load Dashboard
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Unable to connect to the backend API. Please make sure the backend server is running.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Retry
          </button>
        </Card>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Logins',
      value: stats?.logins.total || 0,
      change: '+12%',
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900',
    },
    {
      title: 'Active Alerts',
      value: stats?.alerts.open || 0,
      change: '-5%',
      icon: AlertTriangle,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900',
    },
    {
      title: 'Open Incidents',
      value: stats?.incidents.open || 0,
      change: '+3%',
      icon: Shield,
      color: 'text-red-600',
      bgColor: 'bg-red-100 dark:bg-red-900',
    },
    {
      title: 'Face Detections',
      value: stats?.faces.detections || 0,
      change: '+18%',
      icon: Camera,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Welcome back! Here's your security overview for the last 7 days.
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="hover:shadow-lg transition-shadow duration-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                    {stat.value.toLocaleString()}
                  </p>
                  <div className="flex items-center mt-2">
                    <TrendingUp className="w-4 h-4 text-green-600 mr-1" />
                    <span className="text-sm text-green-600">{stat.change}</span>
                  </div>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Login Chart */}
      <LoginChart />

      {/* Real-time Activity & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityFeed />
        <RealtimeAlerts />
      </div>

      {/* Security Status */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Security Status Overview
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="flex items-center">
              <Activity className="w-5 h-5 text-green-600 mr-2" />
              <span className="text-sm text-gray-700 dark:text-gray-300">System</span>
            </div>
            <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 text-xs font-medium rounded-full">
              Healthy
            </span>
          </div>
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-orange-600 mr-2" />
              <span className="text-sm text-gray-700 dark:text-gray-300">Critical</span>
            </div>
            <span className="px-2 py-1 bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-300 text-xs font-medium rounded-full">
              {stats?.alerts.critical || 0}
            </span>
          </div>
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="flex items-center">
              <Camera className="w-5 h-5 text-blue-600 mr-2" />
              <span className="text-sm text-gray-700 dark:text-gray-300">Matches</span>
            </div>
            <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs font-medium rounded-full">
              {stats?.faces.matches || 0}
            </span>
          </div>
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="flex items-center">
              <Users className="w-5 h-5 text-purple-600 mr-2" />
              <span className="text-sm text-gray-700 dark:text-gray-300">Logins</span>
            </div>
            <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 text-xs font-medium rounded-full">
              {stats?.logins.total || 0}
            </span>
          </div>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <button
            onClick={() => navigate('/alerts')}
            className="p-4 text-center hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors group"
          >
            <Shield className="w-8 h-8 mx-auto mb-2 text-primary-600 group-hover:scale-110 transition-transform" />
            <span className="text-sm text-gray-700 dark:text-gray-300">Alerts</span>
          </button>
          <button
            onClick={() => navigate('/incidents')}
            className="p-4 text-center hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors group"
          >
            <FileText className="w-8 h-8 mx-auto mb-2 text-primary-600 group-hover:scale-110 transition-transform" />
            <span className="text-sm text-gray-700 dark:text-gray-300">Incidents</span>
          </button>
          <button
            onClick={() => navigate('/faces')}
            className="p-4 text-center hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors group"
          >
            <Camera className="w-8 h-8 mx-auto mb-2 text-primary-600 group-hover:scale-110 transition-transform" />
            <span className="text-sm text-gray-700 dark:text-gray-300">Faces</span>
          </button>
          <button
            onClick={() => navigate('/login-events')}
            className="p-4 text-center hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors group"
          >
            <Users className="w-8 h-8 mx-auto mb-2 text-primary-600 group-hover:scale-110 transition-transform" />
            <span className="text-sm text-gray-700 dark:text-gray-300">Logins</span>
          </button>
          <button
            onClick={() => navigate('/activity')}
            className="p-4 text-center hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors group"
          >
            <Activity className="w-8 h-8 mx-auto mb-2 text-primary-600 group-hover:scale-110 transition-transform" />
            <span className="text-sm text-gray-700 dark:text-gray-300">Activity</span>
          </button>
          <button
            onClick={() => navigate('/chat')}
            className="p-4 text-center hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors group"
          >
            <MessageSquare className="w-8 h-8 mx-auto mb-2 text-primary-600 group-hover:scale-110 transition-transform" />
            <span className="text-sm text-gray-700 dark:text-gray-300">AI Chat</span>
          </button>
        </div>
      </Card>
    </div>
  );
};
