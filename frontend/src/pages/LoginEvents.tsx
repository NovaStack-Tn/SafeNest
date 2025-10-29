import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import {
  Activity, TrendingUp, AlertCircle, CheckCircle, Clock, Filter,
  Calendar, Download, RefreshCw, DoorOpen, ArrowRight, Zap, Brain
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';

interface AccessLog {
  id: number;
  timestamp: string;
  user_name: string;
  access_point_name: string;
  event_type: string;
  is_granted: boolean;
  denial_reason?: string;
  is_anomaly: boolean;
  anomaly_score?: number;
  direction?: string;
  confidence?: number;
}

interface Stats {
  today_logs: number;
  today_granted: number;
  today_denied: number;
  today_anomalies: number;
  top_access_points: Array<{
    access_point__name: string;
    count: number;
  }>;
}

interface BusyHour {
  hour: number;
  time_range: string;
  access_count: number;
  percentage: number;
  load_level: string;
}

interface Suggestion {
  type: string;
  priority: string;
  access_point?: string;
  access_count?: number;
  suggestion: string;
}

interface AIAlert {
  title: string;
  message: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  action: string;
  affected_count: number;
}

export const LoginEvents = () => {
  const [logs, setLogs] = useState<AccessLog[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [busyHours, setBusyHours] = useState<BusyHour[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [aiAlerts, setAiAlerts] = useState<AIAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingAI, setLoadingAI] = useState(false);
  const [filter, setFilter] = useState<'all' | 'granted' | 'denied' | 'anomaly'>('all');
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('24h');
  const [nameFilter, setNameFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  
  useEffect(() => {
    fetchData();
    fetchAIAlerts();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }

      const headers = { Authorization: `Bearer ${token}` };
      
      const hoursMap = { '24h': 24, '7d': 168, '30d': 720 };
      
      const [logsRes, statsRes, analyticsRes] = await Promise.all([
        axios.get(
          `http://localhost:8000/api/access-control/access-logs/recent/?hours=${hoursMap[timeRange]}`,
          { headers }
        ),
        axios.get('http://localhost:8000/api/access-control/stats/summary/', { headers }),
        axios.get('http://localhost:8000/api/access-control/stats/analytics/', { headers })
      ]);

      // Handle paginated response (DRF returns {results: [...]} for lists)
      const logsData = logsRes.data.results || logsRes.data;
      setLogs(Array.isArray(logsData) ? logsData : []);
      setStats(statsRes.data);
      setBusyHours(analyticsRes.data.busy_hours_prediction || []);
      setSuggestions(analyticsRes.data.optimization_suggestions || []);
    } catch (error) {
      console.error('Error fetching data:', error);
      // Ensure arrays are always set even on error
      setLogs([]);
      setBusyHours([]);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAIAlerts = async () => {
    try {
      setLoadingAI(true);
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const headers = { Authorization: `Bearer ${token}` };
      const hoursMap = { '24h': 24, '7d': 168, '30d': 720 };
      
      const response = await axios.get(
        `http://localhost:8000/api/access-control/stats/gemini_alerts/?hours=${hoursMap[timeRange]}`,
        { headers }
      );

      setAiAlerts(response.data.alerts || []);
    } catch (error) {
      console.error('Error fetching AI alerts:', error);
      setAiAlerts([]);
    } finally {
      setLoadingAI(false);
    }
  };

  const filteredLogs = logs.filter(log => {
    // Event type filter
    if (filter === 'granted' && !log.is_granted) return false;
    if (filter === 'denied' && log.is_granted) return false;
    if (filter === 'anomaly' && !log.is_anomaly) return false;
    
    // Name filter
    if (nameFilter) {
      const searchLower = nameFilter.toLowerCase();
      const matchesUser = log.user_name?.toLowerCase().includes(searchLower);
      const matchesPoint = log.access_point_name?.toLowerCase().includes(searchLower);
      if (!matchesUser && !matchesPoint) return false;
    }
    
    // Date filter
    if (dateFilter) {
      const logDate = new Date(log.timestamp).toISOString().split('T')[0];
      if (logDate !== dateFilter) return false;
    }
    
    return true;
  });

  const getEventColor = (log: AccessLog) => {
    if (log.is_anomaly) return 'text-purple-600 bg-purple-100 dark:bg-purple-900/20 border-purple-300';
    if (log.is_granted) return 'text-green-600 bg-green-100 dark:bg-green-900/20 border-green-300';
    return 'text-red-600 bg-red-100 dark:bg-red-900/20 border-red-300';
  };

  const getEventIcon = (log: AccessLog) => {
    if (log.is_anomaly) return <Zap className="w-5 h-5" />;
    if (log.is_granted) return <CheckCircle className="w-5 h-5" />;
    return <AlertCircle className="w-5 h-5" />;
  };

  const getLoadLevelColor = (level: string) => {
    switch (level) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      default: return 'bg-green-500';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const exportData = () => {
    const csv = [
      ['Time', 'User', 'Access Point', 'Status', 'Event', 'Direction', 'Anomaly'].join(','),
      ...filteredLogs.map(log => [
        new Date(log.timestamp).toLocaleString(),
        log.user_name || 'Unknown',
        log.access_point_name,
        log.is_granted ? 'Granted' : 'Denied',
        log.event_type,
        log.direction || '-',
        log.is_anomaly ? 'Yes' : 'No'
      ].join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `access-logs-${new Date().toISOString()}.csv`;
    a.click();
    toast.success('Logs exported successfully!');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Access Logs & Events
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Real-time access monitoring with AI-powered analytics
          </p>
        </div>
        <div className="flex space-x-3">
          <Button variant="secondary" onClick={fetchData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="secondary" onClick={exportData}>
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* AI Security Alerts - Gemini Powered */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`rounded-2xl p-6 text-white shadow-lg ${
          aiAlerts.length > 0 && aiAlerts[0].severity !== 'low' 
            ? 'bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500'
            : 'bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500'
        }`}
      >
        <div className="flex items-start gap-4">
          <div className="bg-white/20 p-3 rounded-full backdrop-blur-sm">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
              🚨 AI Security Alerts
              <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
                Powered by Gemini
              </span>
            </h3>
            {aiAlerts.length > 0 ? (
              <div className="space-y-3">
                {aiAlerts.slice(0, 3).map((alert, index) => (
                  <div key={index} className="bg-white/10 backdrop-blur-sm rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <span className="text-2xl">
                        {alert.severity === 'critical' ? '🔴' :
                         alert.severity === 'high' ? '🟠' :
                         alert.severity === 'medium' ? '🟡' : '🟢'}
                      </span>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold">{alert.title}</h4>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            alert.severity === 'critical' ? 'bg-red-700/50' :
                            alert.severity === 'high' ? 'bg-orange-600/50' :
                            alert.severity === 'medium' ? 'bg-yellow-600/50' :
                            'bg-green-600/50'
                          }`}>
                            {alert.severity}
                          </span>
                        </div>
                        <p className="text-sm text-white/90 mb-1">{alert.message}</p>
                        <p className="text-xs text-white/70">→ {alert.action}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3">
                <p className="text-sm text-white/90">
                  {loadingAI ? 'Analyzing security patterns...' : 'Loading security insights...'}
                </p>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Events</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                {stats?.today_logs || 0}
              </p>
            </div>
            <Activity className="w-12 h-12 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Granted</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {stats?.today_granted || 0}
              </p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Denied</p>
              <p className="text-3xl font-bold text-red-600 mt-2">
                {stats?.today_denied || 0}
              </p>
            </div>
            <AlertCircle className="w-12 h-12 text-red-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">AI Anomalies</p>
              <p className="text-3xl font-bold text-purple-600 mt-2">
                {stats?.today_anomalies || 0}
              </p>
            </div>
            <Zap className="w-12 h-12 text-purple-600" />
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Access Points */}
        <Card className="p-6">
          <div className="flex items-center mb-4">
            <DoorOpen className="w-5 h-5 text-primary-600 mr-2" />
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              Top Access Points
            </h2>
          </div>
          <div className="space-y-3">
            {stats?.top_access_points.slice(0, 5).map((point, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <div className="flex items-center flex-1">
                  <span className="text-2xl mr-3">{idx + 1}.</span>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {point.access_point__name}
                    </p>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-1">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ 
                          width: `${(point.count / stats.top_access_points[0].count) * 100}%` 
                        }}
                      />
                    </div>
                  </div>
                </div>
                <span className="ml-3 text-sm font-bold text-gray-900 dark:text-white">
                  {point.count}
                </span>
              </div>
            ))}
            {(!stats?.top_access_points || stats.top_access_points.length === 0) && (
              <p className="text-center text-gray-500 py-4">No data available</p>
            )}
          </div>
        </Card>

        {/* AI Busy Hours Prediction */}
        <Card className="p-6">
          <div className="flex items-center mb-4">
            <Brain className="w-5 h-5 text-purple-600 mr-2" />
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              AI Busy Hours
            </h2>
          </div>
          <div className="space-y-3">
            {busyHours.slice(0, 5).map((hour, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <div className="flex items-center flex-1">
                  <Clock className="w-4 h-4 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {hour.time_range}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${getLoadLevelColor(hour.load_level)}`} />
                  <span className="text-sm font-medium">{hour.percentage}%</span>
                </div>
              </div>
            ))}
            {busyHours.length === 0 && (
              <p className="text-center text-gray-500 py-4">Analyzing patterns...</p>
            )}
          </div>
        </Card>

      </div>

      {/* Filters */}
      <Card className="p-6">
        <div className="space-y-4">
          {/* Event Type Filters */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Filter className="w-5 h-5 text-gray-400" />
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  variant={filter === 'all' ? 'primary' : 'secondary'}
                  onClick={() => setFilter('all')}
                >
                  All ({logs.length})
                </Button>
                <Button
                  size="sm"
                  variant={filter === 'granted' ? 'primary' : 'secondary'}
                  onClick={() => setFilter('granted')}
                >
                  ✓ Granted ({logs.filter(l => l.is_granted).length})
                </Button>
                <Button
                  size="sm"
                  variant={filter === 'denied' ? 'primary' : 'secondary'}
                  onClick={() => setFilter('denied')}
                >
                  ✗ Denied ({logs.filter(l => !l.is_granted).length})
                </Button>
                <Button
                  size="sm"
                  variant={filter === 'anomaly' ? 'primary' : 'secondary'}
                  onClick={() => setFilter('anomaly')}
                >
                  ⚡ Anomalies ({logs.filter(l => l.is_anomaly).length})
                </Button>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Calendar className="w-5 h-5 text-gray-400" />
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value as any)}
                className="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-sm"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
              </select>
            </div>
          </div>

          {/* Search Filters */}
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search by user name or access point..."
                value={nameFilter}
                onChange={(e) => setNameFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div className="w-48">
              <input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            {(nameFilter || dateFilter) && (
              <Button
                size="sm"
                variant="secondary"
                onClick={() => {
                  setNameFilter('');
                  setDateFilter('');
                }}
              >
                Clear
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Access Logs */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Access Events ({filteredLogs.length})
        </h2>

        {loading ? (
          <div className="text-center py-12">
            <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-gray-600 dark:text-gray-400 mt-4">Loading events...</p>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="text-center py-12">
            <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">No events found</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {filteredLogs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className={`p-4 rounded-lg border-2 ${getEventColor(log)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    {/* Event Icon */}
                    <div className={`p-2 rounded-lg ${getEventColor(log)}`}>
                      {getEventIcon(log)}
                    </div>

                    {/* Event Details */}
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <span className="font-bold text-gray-900 dark:text-white">
                          {log.user_name || 'Unknown User'}
                        </span>
                        <ArrowRight className="w-4 h-4 text-gray-400" />
                        <span className="font-medium text-gray-700 dark:text-gray-300">
                          {log.access_point_name}
                        </span>
                        {log.is_anomaly && (
                          <span className="px-2 py-0.5 bg-purple-600 text-white text-xs font-bold rounded">
                            AI ANOMALY
                          </span>
                        )}
                      </div>

                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600 dark:text-gray-400">
                        <span className="flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          {formatTime(log.timestamp)}
                        </span>
                        <span className="capitalize">{log.event_type.replace('_', ' ')}</span>
                        {log.direction && (
                          <span className="flex items-center">
                            <ArrowRight className="w-4 h-4 mr-1" />
                            {log.direction === 'in' ? 'Entry' : 'Exit'}
                          </span>
                        )}
                        {!log.is_granted && log.denial_reason && (
                          <span className="text-red-600 font-medium">
                            Reason: {log.denial_reason.replace('_', ' ')}
                          </span>
                        )}
                      </div>

                      {log.is_anomaly && log.anomaly_score && (
                        <div className="mt-2 flex items-center">
                          <span className="text-xs text-purple-600 dark:text-purple-400 mr-2">
                            Anomaly Score:
                          </span>
                          <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2 max-w-xs">
                            <div
                              className="bg-purple-600 h-2 rounded-full"
                              style={{ width: `${log.anomaly_score * 100}%` }}
                            />
                          </div>
                          <span className="ml-2 text-xs font-bold text-purple-600">
                            {(log.anomaly_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Timestamp */}
                  <div className="text-right text-xs text-gray-500">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
