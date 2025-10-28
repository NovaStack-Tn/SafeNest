import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { History, Eye, AlertCircle, CheckCircle, Camera, ArrowLeft } from 'lucide-react';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface Detection {
  id: number;
  timestamp: string;
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
}

export const CameraHistory = () => {
  const navigate = useNavigate();
  const [detections, setDetections] = useState<Detection[]>([]);
  const [alerts, setAlerts] = useState<Detection[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'matched' | 'unknown'>('all');

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
    if (filter === 'matched') return det.is_match;
    if (filter === 'unknown') return !det.is_match;
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

      {/* Filter Buttons */}
      <div className="flex space-x-3">
        <Button
          onClick={() => setFilter('all')}
          variant={filter === 'all' ? 'primary' : 'secondary'}
        >
          All ({detections.length})
        </Button>
        <Button
          onClick={() => setFilter('matched')}
          variant={filter === 'matched' ? 'primary' : 'secondary'}
        >
          Matched ({detections.filter(d => d.is_match).length})
        </Button>
        <Button
          onClick={() => setFilter('unknown')}
          variant={filter === 'unknown' ? 'primary' : 'secondary'}
        >
          Unknown ({detections.filter(d => !d.is_match).length})
        </Button>
      </div>

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
                className={`p-4 rounded-lg border-2 ${
                  det.is_match
                    ? 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700'
                    : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-700'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    {det.identity?.photo ? (
                      <img
                        src={`http://localhost:8000${det.identity.photo}`}
                        alt={det.identity.person_label}
                        className="w-12 h-12 rounded-full object-cover border-2 border-green-500"
                      />
                    ) : (
                      <div className="w-12 h-12 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                        {det.is_match ? (
                          <Eye className="w-6 h-6 text-green-600" />
                        ) : (
                          <AlertCircle className="w-6 h-6 text-yellow-600" />
                        )}
                      </div>
                    )}
                    <div>
                      <p className="font-bold text-gray-900 dark:text-white">
                        {det.identity?.person_label || 'Unknown Person'}
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
    </div>
  );
};
