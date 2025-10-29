import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import {
  DoorOpen, Plus, Edit2, Trash2, Lock, Unlock, Search,
  Activity, CheckCircle, Sparkles, MapPin, X
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';

interface AccessPoint {
  id: number;
  name: string;
  point_type: string;
  location: string;
  description: string;
  hardware_id: string;
  ip_address?: string;
  status: string;
  is_secure: boolean;
  requires_escort: boolean;
  lockdown_enabled: boolean;
  created_at: string;
  last_activity_at?: string;
}

interface Stats {
  total_access_points: number;
  active_points: number;
  today_logs: number;
  today_granted: number;
}

interface AISuggestion {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  category: string;
  icon: string;
}

export const AccessPoints = () => {
  const [accessPoints, setAccessPoints] = useState<AccessPoint[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showModal, setShowModal] = useState(false);
  const [editingPoint, setEditingPoint] = useState<AccessPoint | null>(null);
  const [aiSuggestions, setAiSuggestions] = useState<AISuggestion[]>([]);
  const [loadingAI, setLoadingAI] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    point_type: 'door',
    location: '',
    description: '',
    hardware_id: '',
    ip_address: '',
    status: 'active'
  });

  useEffect(() => {
    fetchData();
    fetchAISuggestions();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }

      const headers = { Authorization: `Bearer ${token}` };
      
      const [pointsRes, statsRes] = await Promise.all([
        axios.get('http://localhost:8000/api/access-control/access-points/', { headers }),
        axios.get('http://localhost:8000/api/access-control/stats/summary/', { headers })
      ]);

      // Handle paginated response (DRF returns {results: [...]} for lists)
      const pointsData = pointsRes.data.results || pointsRes.data;
      setAccessPoints(Array.isArray(pointsData) ? pointsData : []);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      // Ensure accessPoints is always an array even on error
      setAccessPoints([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAISuggestions = async () => {
    try {
      setLoadingAI(true);
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(
        'http://localhost:8000/api/access-control/stats/gemini_suggestions/',
        { headers }
      );

      setAiSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Error fetching AI suggestions:', error);
      setAiSuggestions([]);
    } finally {
      setLoadingAI(false);
    }
  };

  const handleCreate = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        'http://localhost:8000/api/access-control/access-points/',
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Access point created successfully!');
      setShowModal(false);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error('Failed to create access point');
    }
  };

  const handleUpdate = async () => {
    if (!editingPoint) return;
    try {
      const token = localStorage.getItem('access_token');
      await axios.put(
        `http://localhost:8000/api/access-control/access-points/${editingPoint.id}/`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Access point updated successfully!');
      setShowModal(false);
      setEditingPoint(null);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error('Failed to update access point');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this access point?')) return;
    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(
        `http://localhost:8000/api/access-control/access-points/${id}/`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Access point deleted successfully!');
      fetchData();
    } catch (error) {
      toast.error('Failed to delete access point');
    }
  };

  const handleLockdown = async (id: number, enable: boolean) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `http://localhost:8000/api/access-control/access-points/${id}/${enable ? 'lockdown' : 'unlock'}/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success(`Lockdown ${enable ? 'activated' : 'deactivated'}!`);
      fetchData();
    } catch (error) {
      toast.error('Failed to toggle lockdown');
    }
  };

  const openCreateModal = () => {
    resetForm();
    setEditingPoint(null);
    setShowModal(true);
  };

  const openEditModal = (point: AccessPoint) => {
    setEditingPoint(point);
    setFormData({
      name: point.name,
      point_type: point.point_type,
      location: point.location,
      description: point.description,
      hardware_id: point.hardware_id,
      ip_address: point.ip_address || '',
      status: point.status
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      point_type: 'door',
      location: '',
      description: '',
      hardware_id: '',
      ip_address: '',
      status: 'active'
    });
  };

  const filteredPoints = accessPoints.filter(point => {
    const matchesSearch = point.name.toLowerCase().includes(search.toLowerCase()) ||
                         point.location.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'all' || point.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      case 'inactive': return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20';
      case 'maintenance': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
      case 'error': return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'door': return '🚪';
      case 'gate': return '🛑';
      case 'turnstile': return '↻';
      case 'elevator': return '🛗';
      case 'parking': return '🅿️';
      default: return '🚪';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Access Points
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage doors, gates, turnstiles, and entry points
          </p>
        </div>
        <Button onClick={openCreateModal}>
          <Plus className="w-4 h-4 mr-2" />
          Add Access Point
        </Button>
      </div>

      {/* AI Suggestions Bubble */}
      {aiSuggestions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl p-6 text-white shadow-lg"
        >
          <div className="flex items-start gap-4">
            <div className="bg-white/20 p-3 rounded-full backdrop-blur-sm">
              <Sparkles className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                🤖 AI Recommendations
                <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
                  Powered by Gemini
                </span>
              </h3>
              <div className="space-y-3">
                {aiSuggestions.slice(0, 3).map((suggestion, index) => (
                  <div key={index} className="bg-white/10 backdrop-blur-sm rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <span className="text-2xl">{
                        suggestion.icon === 'shield' ? '🛡️' :
                        suggestion.icon === 'clock' ? '⏰' :
                        suggestion.icon === 'users' ? '👥' :
                        suggestion.icon === 'zap' ? '⚡' : '💡'
                      }</span>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold">{suggestion.title}</h4>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            suggestion.priority === 'high' ? 'bg-red-500/30' :
                            suggestion.priority === 'medium' ? 'bg-yellow-500/30' :
                            'bg-green-500/30'
                          }`}>
                            {suggestion.priority}
                          </span>
                        </div>
                        <p className="text-sm text-white/90">{suggestion.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              {loadingAI && (
                <p className="text-sm text-white/70 mt-2">Loading more suggestions...</p>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Points</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                {stats?.total_access_points || 0}
              </p>
            </div>
            <DoorOpen className="w-12 h-12 text-primary-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active</p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
                {stats?.active_points || 0}
              </p>
            </div>
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Today's Access</p>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">
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
              <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
                {stats?.today_granted || 0}
              </p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by name or location..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            </div>
          </div>
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="maintenance">Maintenance</option>
              <option value="error">Error</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Access Points Table */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Access Points ({filteredPoints.length})
        </h2>
        
        {loading ? (
          <div className="text-center py-12">
            <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-gray-600 dark:text-gray-400 mt-4">Loading...</p>
          </div>
        ) : filteredPoints.length === 0 ? (
          <div className="text-center py-12">
            <DoorOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">No access points found</p>
            <Button onClick={openCreateModal} className="mt-4">
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Access Point
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">Name</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">Location</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">Hardware ID</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredPoints.map((point) => (
                  <motion.tr
                    key={point.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                  >
                    <td className="py-4 px-4">
                      <div className="flex items-center">
                        <span className="text-2xl mr-3">{getTypeIcon(point.point_type)}</span>
                        <div>
                          <p className="font-semibold text-gray-900 dark:text-white">{point.name}</p>
                          <p className="text-xs text-gray-500 capitalize">{point.point_type.replace('_', ' ')}</p>
                          {point.lockdown_enabled && (
                            <span className="text-xs text-red-600 flex items-center mt-1">
                              <Lock className="w-3 h-3 mr-1" /> Lockdown
                            </span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                        <MapPin className="w-4 h-4 mr-1" />
                        {point.location}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(point.status)}`}>
                        {point.status}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-sm text-gray-600 dark:text-gray-400 font-mono">
                        {point.hardware_id}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleLockdown(point.id, !point.lockdown_enabled)}
                          className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                          title={point.lockdown_enabled ? 'Unlock' : 'Lockdown'}
                        >
                          {point.lockdown_enabled ? (
                            <Unlock className="w-4 h-4 text-green-600" />
                          ) : (
                            <Lock className="w-4 h-4 text-yellow-600" />
                          )}
                        </button>
                        <button
                          onClick={() => openEditModal(point)}
                          className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                          title="Edit"
                        >
                          <Edit2 className="w-4 h-4 text-blue-600" />
                        </button>
                        <button
                          onClick={() => handleDelete(point.id)}
                          className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Create/Edit Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
            onClick={() => setShowModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              {/* Modal Header */}
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {editingPoint ? 'Edit Access Point' : 'Create Access Point'}
                  </h2>
                  <button
                    onClick={() => setShowModal(false)}
                    className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
                  >
                    <X className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>
              </div>

              {/* Modal Body */}
              <div className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Name *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                      placeholder="e.g., Main Entrance Door"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Type *
                    </label>
                    <select
                      value={formData.point_type}
                      onChange={(e) => setFormData({...formData, point_type: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                    >
                      <option value="door">🚪 Door</option>
                      <option value="gate">🛑 Gate</option>
                      <option value="turnstile">↻ Turnstile</option>
                      <option value="elevator">🛗 Elevator</option>
                      <option value="zone">🔒 Security Zone</option>
                      <option value="parking">🅿️ Parking Barrier</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Status *
                    </label>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData({...formData, status: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                      <option value="maintenance">Maintenance</option>
                    </select>
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Location *
                    </label>
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) => setFormData({...formData, location: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                      placeholder="e.g., Building A, Floor 1"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Hardware ID *
                    </label>
                    <input
                      type="text"
                      value={formData.hardware_id}
                      onChange={(e) => setFormData({...formData, hardware_id: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                      placeholder="e.g., AP-001"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      IP Address
                    </label>
                    <input
                      type="text"
                      value={formData.ip_address}
                      onChange={(e) => setFormData({...formData, ip_address: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                      placeholder="e.g., 192.168.1.100"
                    />
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                      placeholder="Additional details about this access point..."
                    />
                  </div>
                </div>
              </div>

              {/* Modal Footer */}
              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
                <Button variant="secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </Button>
                <Button onClick={editingPoint ? handleUpdate : handleCreate}>
                  {editingPoint ? 'Update' : 'Create'}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
