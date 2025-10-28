import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, Clock, X } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import type { Alert } from '@/lib/types';
import { Card } from './Card';

interface AlertCardProps {
  alert: Alert;
  onAcknowledge?: (id: number) => void;
  onResolve?: (id: number) => void;
  onDismiss?: (id: number) => void;
}

export const AlertCard = ({ alert, onAcknowledge, onResolve, onDismiss }: AlertCardProps) => {
  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'critical':
        return {
          bg: 'bg-red-50 dark:bg-red-900/20',
          border: 'border-l-4 border-red-500',
          badge: 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300',
          icon: 'text-red-600',
        };
      case 'high':
        return {
          bg: 'bg-orange-50 dark:bg-orange-900/20',
          border: 'border-l-4 border-orange-500',
          badge: 'bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-300',
          icon: 'text-orange-600',
        };
      case 'medium':
        return {
          bg: 'bg-yellow-50 dark:bg-yellow-900/20',
          border: 'border-l-4 border-yellow-500',
          badge: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300',
          icon: 'text-yellow-600',
        };
      default:
        return {
          bg: 'bg-blue-50 dark:bg-blue-900/20',
          border: 'border-l-4 border-blue-500',
          badge: 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300',
          icon: 'text-blue-600',
        };
    }
  };

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'resolved':
        return {
          badge: 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300',
          icon: CheckCircle,
          text: 'Resolved',
        };
      case 'acknowledged':
        return {
          badge: 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300',
          icon: Clock,
          text: 'Acknowledged',
        };
      default:
        return {
          badge: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
          icon: AlertTriangle,
          text: 'Open',
        };
    }
  };

  const severityConfig = getSeverityConfig(alert.severity);
  const statusConfig = getStatusConfig(alert.status);
  const StatusIcon = statusConfig.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="group"
    >
      <Card className={`${severityConfig.bg} ${severityConfig.border} hover:shadow-lg transition-all duration-200`}>
        <div className="flex items-start justify-between gap-4">
          {/* Alert Icon & Content */}
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className={`p-2 rounded-full ${severityConfig.badge} flex-shrink-0`}>
              <AlertTriangle className={`w-5 h-5 ${severityConfig.icon}`} />
            </div>
            
            <div className="flex-1 min-w-0">
              {/* Header */}
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                  {alert.title}
                </h3>
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${severityConfig.badge} uppercase`}>
                  {alert.severity}
                </span>
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${statusConfig.badge} flex items-center gap-1`}>
                  <StatusIcon className="w-3 h-3" />
                  {statusConfig.text}
                </span>
              </div>

              {/* Message */}
              <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                {alert.message}
              </p>

              {/* Metadata */}
              <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                </span>
                {alert.alert_type && (
                  <span className="px-2 py-0.5 bg-gray-200 dark:bg-gray-700 rounded">
                    {alert.alert_type}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 flex-shrink-0">
            {alert.status === 'open' && onAcknowledge && (
              <button
                onClick={() => onAcknowledge(alert.id)}
                className="px-3 py-1.5 text-xs font-medium text-blue-700 dark:text-blue-300 bg-blue-100 dark:bg-blue-900 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
                title="Acknowledge"
              >
                Acknowledge
              </button>
            )}
            {(alert.status === 'open' || alert.status === 'acknowledged') && onResolve && (
              <button
                onClick={() => onResolve(alert.id)}
                className="px-3 py-1.5 text-xs font-medium text-green-700 dark:text-green-300 bg-green-100 dark:bg-green-900 rounded hover:bg-green-200 dark:hover:bg-green-800 transition-colors"
                title="Resolve"
              >
                Resolve
              </button>
            )}
            {onDismiss && (
              <button
                onClick={() => onDismiss(alert.id)}
                className="p-1.5 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
                title="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </Card>
    </motion.div>
  );
};
