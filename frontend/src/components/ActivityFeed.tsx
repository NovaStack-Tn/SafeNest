import { useQuery } from '@tanstack/react-query';
import { Activity, User, Shield, Camera, AlertCircle } from 'lucide-react';
import { Card } from './Card';
import { Loader } from './Loader';
import api from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';

interface ActivityItem {
  id: number;
  type: 'login' | 'incident' | 'alert' | 'face_detection';
  description: string;
  user?: string;
  timestamp: string;
  severity?: string;
}

export const ActivityFeed = () => {
  const { data: activities, isLoading } = useQuery<ActivityItem[]>({
    queryKey: ['activity-feed'],
    queryFn: async () => {
      const response = await api.get('/dashboard/activity/?limit=10');
      return response.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'login':
        return <User className="w-4 h-4" />;
      case 'incident':
        return <Shield className="w-4 h-4" />;
      case 'alert':
        return <AlertCircle className="w-4 h-4" />;
      case 'face_detection':
        return <Camera className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getActivityColor = (type: string, severity?: string) => {
    if (severity === 'critical' || severity === 'high') {
      return 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300';
    }
    switch (type) {
      case 'login':
        return 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300';
      case 'incident':
        return 'bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-300';
      case 'alert':
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-600 dark:text-yellow-300';
      case 'face_detection':
        return 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-300';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300';
    }
  };

  if (isLoading) {
    return <Loader text="Loading activity..." />;
  }

  return (
    <Card>
      <div className="flex items-center mb-4">
        <Activity className="w-5 h-5 text-primary-600 mr-2" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Recent Activity
        </h3>
      </div>

      <div className="space-y-3">
        {activities && activities.length > 0 ? (
          activities.map((activity) => (
            <div
              key={activity.id}
              className="flex items-start space-x-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <div className={`p-2 rounded-full ${getActivityColor(activity.type, activity.severity)}`}>
                {getActivityIcon(activity.type)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900 dark:text-white">
                  {activity.description}
                </p>
                <div className="flex items-center mt-1 text-xs text-gray-500 dark:text-gray-400">
                  {activity.user && (
                    <>
                      <span>{activity.user}</span>
                      <span className="mx-1">•</span>
                    </>
                  )}
                  <span>
                    {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                  </span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No recent activity</p>
          </div>
        )}
      </div>
    </Card>
  );
};
