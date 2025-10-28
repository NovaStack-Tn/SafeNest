import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card } from './Card';
import { TrendingUp } from 'lucide-react';

interface LoginChartProps {
  data?: Array<{
    date: string;
    successful: number;
    failed: number;
    anomalies: number;
  }>;
}

export const LoginChart = ({ data }: LoginChartProps) => {
  // Sample data if none provided
  const chartData = data || [
    { date: 'Mon', successful: 45, failed: 3, anomalies: 1 },
    { date: 'Tue', successful: 52, failed: 5, anomalies: 2 },
    { date: 'Wed', successful: 48, failed: 2, anomalies: 0 },
    { date: 'Thu', successful: 61, failed: 4, anomalies: 1 },
    { date: 'Fri', successful: 55, failed: 6, anomalies: 3 },
    { date: 'Sat', successful: 32, failed: 2, anomalies: 0 },
    { date: 'Sun', successful: 28, failed: 1, anomalies: 0 },
  ];

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <TrendingUp className="w-5 h-5 text-primary-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Login Trends (7 Days)
          </h3>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorSuccessful" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorFailed" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorAnomalies" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#f3f4f6'
              }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '12px' }}
            />
            <Area
              type="monotone"
              dataKey="successful"
              stroke="#10b981"
              fillOpacity={1}
              fill="url(#colorSuccessful)"
              name="Successful"
            />
            <Area
              type="monotone"
              dataKey="failed"
              stroke="#ef4444"
              fillOpacity={1}
              fill="url(#colorFailed)"
              name="Failed"
            />
            <Area
              type="monotone"
              dataKey="anomalies"
              stroke="#f59e0b"
              fillOpacity={1}
              fill="url(#colorAnomalies)"
              name="Anomalies"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
