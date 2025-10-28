import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/Card';
import { Loader } from '@/components/Loader';
import { Eye, User, Car, Monitor } from 'lucide-react';
import api from '@/lib/api';

interface WatchlistEntry {
  id: number;
  watchlist_type: string;
  name: string;
  description: string;
  threat_level: string;
  subject_identifier: string;
  times_detected: number;
  last_detected_at?: string;
  alert_on_detection: boolean;
}

const TYPE_ICONS: any = {
  person: User,
  vehicle: Car,
  device: Monitor,
};

export const Watchlist = () => {
  const { data: watchlist, isLoading } = useQuery<WatchlistEntry[]>({
    queryKey: ['watchlist'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/watchlist/');
      return response.data.results || response.data;
    },
  });

  if (isLoading) {
    return <Loader text="Loading watchlist..." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Watchlist
        </h1>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {watchlist?.map((entry) => {
          const Icon = TYPE_ICONS[entry.watchlist_type] || Eye;
          return (
            <Card key={entry.id} className="p-6">
              <div className="flex items-start gap-4">
                <Icon className="w-8 h-8 text-gray-400" />
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                    {entry.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {entry.description}
                  </p>
                  <div className="flex items-center gap-3 text-xs">
                    <span className={`px-2 py-1 rounded font-semibold ${
                      entry.threat_level === 'critical' ? 'bg-red-600 text-white' :
                      entry.threat_level === 'high' ? 'bg-orange-600 text-white' :
                      'bg-yellow-600 text-white'
                    }`}>
                      {entry.threat_level}
                    </span>
                    <span className="text-gray-500">
                      {entry.subject_identifier}
                    </span>
                    <span className="text-gray-500">
                      Detected: {entry.times_detected}
                    </span>
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
