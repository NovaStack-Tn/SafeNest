import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/Card';
import { Loader } from '@/components/Loader';
import { Crosshair, Hash, Globe, Mail } from 'lucide-react';
import api from '@/lib/api';

interface ThreatIndicator {
  id: number;
  indicator_type: string;
  indicator_value: string;
  description: string;
  severity: string;
  status: string;
  confidence_score: number;
  times_detected: number;
  last_seen: string;
}

const INDICATOR_ICONS: any = {
  ip_address: Globe,
  domain: Globe,
  email: Mail,
  file_hash: Hash,
  url: Globe,
};

export const ThreatIndicators = () => {
  const { data: indicators, isLoading } = useQuery<ThreatIndicator[]>({
    queryKey: ['threat-indicators'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/indicators/');
      return response.data.results || response.data;
    },
  });

  if (isLoading) {
    return <Loader text="Loading indicators..." />;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
        Threat Indicators (IOCs)
      </h1>
      <div className="space-y-3">
        {indicators?.map((indicator) => {
          const Icon = INDICATOR_ICONS[indicator.indicator_type] || Crosshair;
          return (
            <Card key={indicator.id} className="p-5">
              <div className="flex items-center gap-4">
                <Icon className="w-6 h-6 text-gray-400" />
                <div className="flex-1">
                  <p className="font-mono text-sm text-gray-900 dark:text-white font-semibold">
                    {indicator.indicator_value}
                  </p>
                  <p className="text-xs text-gray-500">
                    {indicator.indicator_type} • Detected {indicator.times_detected} times
                  </p>
                </div>
                <span className={`px-3 py-1 rounded text-xs font-semibold ${
                  indicator.severity === 'critical' ? 'bg-red-600 text-white' :
                  indicator.severity === 'high' ? 'bg-orange-600 text-white' :
                  'bg-yellow-600 text-white'
                }`}>
                  {indicator.severity}
                </span>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
