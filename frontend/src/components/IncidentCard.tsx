import { motion } from 'framer-motion';
import { Shield, Clock, Paperclip, User } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import type { Incident } from '@/lib/types';

interface IncidentCardProps {
  incident: Incident;
  onClick: () => void;
}

export const IncidentCard = ({ incident, onClick }: IncidentCardProps) => {
  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'critical':
        return {
          bg: 'bg-red-50 dark:bg-red-900/20',
          border: 'border-l-4 border-red-500',
          badge: 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300',
        };
      case 'high':
        return {
          bg: 'bg-orange-50 dark:bg-orange-900/20',
          border: 'border-l-4 border-orange-500',
          badge: 'bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-300',
        };
      case 'medium':
        return {
          bg: 'bg-yellow-50 dark:bg-yellow-900/20',
          border: 'border-l-4 border-yellow-500',
          badge: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300',
        };
      default:
        return {
          bg: 'bg-blue-50 dark:bg-blue-900/20',
          border: 'border-l-4 border-blue-500',
          badge: 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300',
        };
    }
  };

  const config = getSeverityConfig(incident.severity);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      whileHover={{ scale: 1.02 }}
      onClick={onClick}
      className={`${config.bg} ${config.border} rounded-lg p-4 cursor-pointer hover:shadow-lg transition-all duration-200`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
            #{incident.id}
          </span>
        </div>
        <span className={`px-2 py-0.5 text-xs font-medium rounded ${config.badge} uppercase`}>
          {incident.severity}
        </span>
      </div>

      {/* Title */}
      <h4 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
        {incident.title}
      </h4>

      {/* Description */}
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
        {incident.description}
      </p>

      {/* Metadata */}
      <div className="space-y-2">
        {/* Type Badge */}
        {incident.incident_type && (
          <div className="inline-flex items-center px-2 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded">
            {incident.incident_type}
          </div>
        )}

        {/* Footer Info */}
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-3">
            {incident.assignee_name && (
              <div className="flex items-center gap-1">
                <User className="w-3 h-3" />
                <span className="truncate max-w-[80px]">{incident.assignee_name}</span>
              </div>
            )}
            {incident.evidence_count > 0 && (
              <div className="flex items-center gap-1">
                <Paperclip className="w-3 h-3" />
                <span>{incident.evidence_count}</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>{formatDistanceToNow(new Date(incident.opened_at), { addSuffix: true })}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
