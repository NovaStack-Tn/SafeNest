import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, X, CheckCircle } from 'lucide-react';
import { Card } from './Card';
import type { Alert } from '@/lib/types';

export const RealtimeAlerts = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  // WebSocket is temporarily disabled due to JWT authentication issues
  // TODO: Implement JWT WebSocket authentication middleware
  // For now, the Alerts page uses polling instead
  
  /* Disabled WebSocket code:
  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    const token = localStorage.getItem('access_token');
    
    if (!token) return;

    const websocket = new WebSocket(`${wsUrl}/alerts/?token=${token}`);

    websocket.onopen = () => {
      console.log('WebSocket connected');
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'alert') {
        setAlerts((prev) => [data.alert, ...prev].slice(0, 5));
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return () => {
      websocket.close();
    };
  }, []);
  */

  const removeAlert = (id: number) => {
    setAlerts((prev) => prev.filter((alert) => alert.id !== id));
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 border-red-500';
      case 'high':
        return 'bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-300 border-orange-500';
      case 'medium':
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300 border-yellow-500';
      default:
        return 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 border-blue-500';
    }
  };

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <AlertTriangle className="w-5 h-5 text-orange-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Live Alerts
          </h3>
        </div>
        <div className="flex items-center">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse mr-2" />
          <span className="text-xs text-gray-600 dark:text-gray-400">
            Polling Mode
          </span>
        </div>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        <AnimatePresence>
          {alerts.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <CheckCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No recent alerts</p>
            </div>
          ) : (
            alerts.map((alert) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className={`p-3 rounded-lg border-l-4 ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-1">
                      <span className="font-semibold text-sm">{alert.title}</span>
                      <span className="ml-2 px-2 py-0.5 text-xs font-medium rounded-full bg-white dark:bg-gray-800">
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-sm opacity-90">{alert.message}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {new Date(alert.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                  <button
                    onClick={() => removeAlert(alert.id)}
                    className="ml-2 p-1 hover:bg-white dark:hover:bg-gray-700 rounded transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </Card>
  );
};
