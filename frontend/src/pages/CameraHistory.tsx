import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { History, Eye, AlertCircle, CheckCircle, Camera, ArrowLeft, X, Calendar, Filter, Download } from 'lucide-react';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface Detection {
  id: number;
  timestamp: string;
  identity_label?: string;
  identity_photo?: string;
  identity?: {
    id: number;
    person_label: string;
    photo?: string;
  };
  similarity?: number;
  is_match: boolean;
  age?: number;
  gender?: string;
  confidence: number;
  frame_image?: string;
  frame_url?: string;
}

export const CameraHistory = () => {
  const navigate = useNavigate();
  const [detections, setDetections] = useState<Detection[]>([]);
  const [alerts, setAlerts] = useState<Detection[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'matched' | 'unknown'>('all');
  const [dateFilter, setDateFilter] = useState<'all' | 'today' | 'week' | 'month' | 'custom'>('all');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedDetection, setSelectedDetection] = useState<Detection | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchHistory();
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchHistory, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('No token found, cannot fetch history');
        setLoading(false);
        return;
      }
      
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch recent detections
      const detectionsRes = await axios.get(
        'http://localhost:8000/api/faces/detections/recent/?limit=50',
        { headers }
      );

      // Fetch alerts (unknown faces)
      const alertsRes = await axios.get(
        'http://localhost:8000/api/faces/detections/alerts/?limit=20',
        { headers }
      );

      setDetections(detectionsRes.data);
      setAlerts(alertsRes.data);
    } catch (error: any) {
      if (error.response?.status === 401) {
        console.log('Unauthorized - please login');
      } else {
        console.error('Failed to fetch history:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const filteredDetections = detections.filter(det => {
    // Filter by match status
    if (filter === 'matched' && !det.is_match) return false;
    if (filter === 'unknown' && det.is_match) return false;
    
    // Filter by date
    const detDate = new Date(det.timestamp);
    const now = new Date();
    
    if (dateFilter === 'today') {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (detDate < today) return false;
    } else if (dateFilter === 'week') {
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      if (detDate < weekAgo) return false;
    } else if (dateFilter === 'month') {
      const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      if (detDate < monthAgo) return false;
    } else if (dateFilter === 'custom' && startDate && endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);
      end.setHours(23, 59, 59, 999);
      if (detDate < start || detDate > end) return false;
    }
    
    return true;
  });

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <Button 
            onClick={() => navigate('/cameras')} 
            variant="secondary" 
            className="mb-3"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Cameras
          </Button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Detection History
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Real-time surveillance detections and alerts
          </p>
        </div>
        <Button onClick={fetchHistory}>
          <History className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Detections</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                {detections.length}
              </p>
            </div>
            <Camera className="w-12 h-12 text-primary-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Matched</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {detections.filter(d => d.is_match).length}
              </p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Unknown</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">
                {detections.filter(d => !d.is_match).length}
              </p>
            </div>
            <AlertCircle className="w-12 h-12 text-yellow-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Alerts</p>
              <p className="text-3xl font-bold text-red-600 mt-2">{alerts.length}</p>
            </div>
            <AlertCircle className="w-12 h-12 text-red-600" />
          </div>
        </Card>
      </div>

      {/* Filter Panel */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center">
            <Filter className="w-5 h-5 mr-2" />
            Filters
          </h2>
          <Button 
            variant="secondary" 
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            {showFilters ? 'Hide' : 'Show'} Filters
          </Button>
        </div>

        {/* Status Filters */}
        <div className="mb-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
            Detection Status
          </label>
          <div className="flex space-x-3">
            <Button
              onClick={() => setFilter('all')}
              variant={filter === 'all' ? 'primary' : 'secondary'}
              size="sm"
            >
              All ({detections.length})
            </Button>
            <Button
              onClick={() => setFilter('matched')}
              variant={filter === 'matched' ? 'primary' : 'secondary'}
              size="sm"
            >
              ✅ Matched ({detections.filter(d => d.is_match).length})
            </Button>
            <Button
              onClick={() => setFilter('unknown')}
              variant={filter === 'unknown' ? 'primary' : 'secondary'}
              size="sm"
            >
              ⚠️ Unknown ({detections.filter(d => !d.is_match).length})
            </Button>
          </div>
        </div>

        {/* Date Filters */}
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              <Calendar className="w-4 h-4 inline mr-1" />
              Time Period
            </label>
            <div className="flex flex-wrap gap-3 mb-4">
              <Button
                onClick={() => setDateFilter('all')}
                variant={dateFilter === 'all' ? 'primary' : 'secondary'}
                size="sm"
              >
                All Time
              </Button>
              <Button
                onClick={() => setDateFilter('today')}
                variant={dateFilter === 'today' ? 'primary' : 'secondary'}
                size="sm"
              >
                Today
              </Button>
              <Button
                onClick={() => setDateFilter('week')}
                variant={dateFilter === 'week' ? 'primary' : 'secondary'}
                size="sm"
              >
                Last 7 Days
              </Button>
              <Button
                onClick={() => setDateFilter('month')}
                variant={dateFilter === 'month' ? 'primary' : 'secondary'}
                size="sm"
              >
                Last 30 Days
              </Button>
              <Button
                onClick={() => setDateFilter('custom')}
                variant={dateFilter === 'custom' ? 'primary' : 'secondary'}
                size="sm"
              >
                Custom Range
              </Button>
            </div>

            {/* Custom Date Range */}
            {dateFilter === 'custom' && (
              <div className="grid grid-cols-2 gap-4 mt-3">
                <div>
                  <label className="text-sm text-gray-600 dark:text-gray-400 block mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-600 dark:text-gray-400 block mb-1">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  />
                </div>
              </div>
            )}

            <div className="mt-4 flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">
                Showing {filteredDetections.length} of {detections.length} detections
              </span>
              {(filter !== 'all' || dateFilter !== 'all') && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    setFilter('all');
                    setDateFilter('all');
                    setStartDate('');
                    setEndDate('');
                  }}
                >
                  Clear Filters
                </Button>
              )}
            </div>
          </motion.div>
        )}
      </Card>

      {/* Active Alerts */}
      {alerts.length > 0 && (
        <Card className="p-6">
          <h2 className="text-xl font-bold text-red-600 dark:text-red-400 mb-4 flex items-center">
            <AlertCircle className="w-6 h-6 mr-2" />
            Active Alerts - Unknown Persons
          </h2>
          <div className="space-y-3">
            {alerts.map((det) => (
              <motion.div
                key={det.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="p-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-300 dark:border-red-700 rounded-lg"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <AlertCircle className="w-8 h-8 text-red-600" />
                    <div>
                      <p className="font-bold text-red-900 dark:text-red-300">
                        ⚠️ Unknown Person Detected
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Detection Confidence: {(det.confidence * 100).toFixed(1)}%
                        {det.age && ` • Age: ~${det.age}`}
                        {det.gender && ` • Gender: ${det.gender === 'M' ? 'Male' : 'Female'}`}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-red-700 dark:text-red-400">
                      {formatTime(det.timestamp)}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* Detection History */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Detection History
        </h2>

        {loading ? (
          <div className="text-center py-12">
            <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-gray-600 dark:text-gray-400 mt-4">Loading history...</p>
          </div>
        ) : filteredDetections.length === 0 ? (
          <div className="text-center py-12">
            <History className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">No detections found</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {filteredDetections.map((det) => (
              <motion.div
                key={det.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                onClick={() => setSelectedDetection(det)}
                className={`p-4 rounded-lg border-2 cursor-pointer hover:shadow-lg transition-shadow ${
                  det.is_match
                    ? 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700 hover:border-green-500'
                    : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-700 hover:border-yellow-500'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    {/* Show face screenshot if available, otherwise identity photo */}
                    {det.frame_url ? (
                      <img
                        src={det.frame_url}
                        alt={det.identity_label || 'Unknown'}
                        className={`w-16 h-16 rounded-lg object-cover border-2 ${
                          det.is_match ? 'border-green-500' : 'border-red-500'
                        }`}
                        onError={() => {
                          console.log('Image failed to load:', det.frame_url);
                        }}
                      />
                    ) : det.identity_photo ? (
                      <img
                        src={det.identity_photo}
                        alt={det.identity_label || 'Unknown'}
                        className="w-16 h-16 rounded-lg object-cover border-2 border-green-500"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-lg bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                        {det.is_match ? (
                          <Eye className="w-6 h-6 text-green-600" />
                        ) : (
                          <AlertCircle className="w-6 h-6 text-yellow-600" />
                        )}
                      </div>
                    )}
                    <div>
                      <p className="font-bold text-gray-900 dark:text-white">
                        {det.identity_label || 'Unknown Person'}
                      </p>
                      <div className="flex items-center space-x-4 mt-1">
                        {det.similarity && (
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            Match: {(det.similarity * 100).toFixed(1)}%
                          </span>
                        )}
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          Confidence: {(det.confidence * 100).toFixed(1)}%
                        </span>
                        {det.age && (
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            Age: ~{det.age}
                          </span>
                        )}
                        {det.gender && (
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            {det.gender === 'M' ? 'Male' : 'Female'}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {formatTime(det.timestamp)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(det.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </Card>

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedDetection && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedDetection(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            >
              {/* Modal Header */}
              <div className={`p-6 border-b border-gray-200 dark:border-gray-700 ${
                selectedDetection.is_match
                  ? 'bg-green-50 dark:bg-green-900/20'
                  : 'bg-red-50 dark:bg-red-900/20'
              }`}>
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
                    {selectedDetection.is_match ? (
                      <>
                        <CheckCircle className="w-8 h-8 text-green-600 mr-3" />
                        Matched Detection
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-8 h-8 text-red-600 mr-3" />
                        Unknown Person Alert
                      </>
                    )}
                  </h2>
                  <button
                    onClick={() => setSelectedDetection(null)}
                    className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
                  >
                    <X className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>
              </div>

              {/* Modal Body */}
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left: Image */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                      Captured Face
                    </label>
                    <div className="relative">
                      {selectedDetection.frame_url ? (
                        <img
                          src={selectedDetection.frame_url}
                          alt={selectedDetection.identity_label || 'Unknown'}
                          className={`w-full h-auto rounded-lg border-4 ${
                            selectedDetection.is_match ? 'border-green-500' : 'border-red-500'
                          } shadow-lg`}
                        />
                      ) : selectedDetection.identity_photo ? (
                        <img
                          src={selectedDetection.identity_photo}
                          alt={selectedDetection.identity_label || 'Unknown'}
                          className="w-full h-auto rounded-lg border-4 border-green-500 shadow-lg"
                        />
                      ) : (
                        <div className="w-full h-64 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                          <Camera className="w-16 h-16 text-gray-400" />
                        </div>
                      )}
                      
                      {/* Download Button */}
                      {selectedDetection.frame_url && (
                        <a
                          href={selectedDetection.frame_url}
                          download={`detection_${selectedDetection.id}.jpg`}
                          className="absolute top-3 right-3 p-2 bg-black/60 hover:bg-black/80 rounded-full transition-colors"
                        >
                          <Download className="w-5 h-5 text-white" />
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Right: Details */}
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Identity
                      </label>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                        {selectedDetection.identity_label || 'Unknown Person'}
                      </p>
                    </div>

                    {selectedDetection.similarity && (
                      <div>
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Match Confidence
                        </label>
                        <div className="mt-2">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-2xl font-bold text-green-600">
                              {(selectedDetection.similarity * 100).toFixed(1)}%
                            </span>
                            <span className="text-sm text-gray-500">
                              {selectedDetection.similarity >= 0.8 ? 'High' : 
                               selectedDetection.similarity >= 0.6 ? 'Medium' : 'Low'}
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                            <div
                              className="bg-green-500 h-3 rounded-full transition-all"
                              style={{ width: `${selectedDetection.similarity * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Detection Confidence
                      </label>
                      <div className="mt-2">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xl font-bold text-blue-600">
                            {(selectedDetection.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full transition-all"
                            style={{ width: `${selectedDetection.confidence * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Demographics */}
                    <div className="grid grid-cols-2 gap-4">
                      {selectedDetection.age && (
                        <div className="bg-gray-50 dark:bg-gray-900/50 p-4 rounded-lg">
                          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Age
                          </label>
                          <p className="text-xl font-bold text-gray-900 dark:text-white mt-1">
                            ~{selectedDetection.age}
                          </p>
                        </div>
                      )}
                      {selectedDetection.gender && (
                        <div className="bg-gray-50 dark:bg-gray-900/50 p-4 rounded-lg">
                          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Gender
                          </label>
                          <p className="text-xl font-bold text-gray-900 dark:text-white mt-1">
                            {selectedDetection.gender === 'M' ? 'Male' : 'Female'}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Timestamp */}
                    <div className="bg-gray-50 dark:bg-gray-900/50 p-4 rounded-lg">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Detection Time
                      </label>
                      <p className="text-lg font-semibold text-gray-900 dark:text-white mt-1">
                        {new Date(selectedDetection.timestamp).toLocaleString()}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        {formatTime(selectedDetection.timestamp)}
                      </p>
                    </div>

                    {/* Status Badge */}
                    <div className={`p-4 rounded-lg border-2 ${
                      selectedDetection.is_match
                        ? 'bg-green-50 dark:bg-green-900/20 border-green-500'
                        : 'bg-red-50 dark:bg-red-900/20 border-red-500'
                    }`}>
                      <div className="flex items-center">
                        {selectedDetection.is_match ? (
                          <>
                            <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
                            <div>
                              <p className="font-bold text-green-900 dark:text-green-300">
                                Authorized Person
                              </p>
                              <p className="text-sm text-green-700 dark:text-green-400">
                                Identity verified and recognized
                              </p>
                            </div>
                          </>
                        ) : (
                          <>
                            <AlertCircle className="w-6 h-6 text-red-600 mr-2" />
                            <div>
                              <p className="font-bold text-red-900 dark:text-red-300">
                                Unknown Person
                              </p>
                              <p className="text-sm text-red-700 dark:text-red-400">
                                No match found in database
                              </p>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Modal Footer */}
              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
                <Button variant="secondary" onClick={() => setSelectedDetection(null)}>
                  Close
                </Button>
                {selectedDetection.frame_url && (
                  <a href={selectedDetection.frame_url} download={`detection_${selectedDetection.id}.jpg`}>
                    <Button variant="primary">
                      <Download className="w-4 h-4 mr-2" />
                      Download Image
                    </Button>
                  </a>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
