import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Shield, Plus, AlertTriangle, TrendingUp, Target } from 'lucide-react';

export const ThreatIntel = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Threat Intelligence
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Monitor threats, analyze risks, and detect anomalies
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add Threat
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Threats</p>
              <p className="text-3xl font-bold text-red-600 mt-2">7</p>
            </div>
            <AlertTriangle className="w-12 h-12 text-red-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Critical</p>
              <p className="text-3xl font-bold text-red-600 mt-2">2</p>
            </div>
            <Target className="w-12 h-12 text-red-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Anomalies Detected</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">15</p>
            </div>
            <TrendingUp className="w-12 h-12 text-yellow-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Risk Score</p>
              <p className="text-3xl font-bold text-orange-600 mt-2">65</p>
            </div>
            <Shield className="w-12 h-12 text-orange-600" />
          </div>
        </Card>
      </div>

      <Card className="p-12">
        <div className="text-center">
          <Shield className="w-20 h-20 text-gray-400 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            Threat Intelligence & Risk Assessment
          </h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-6">
            AI-powered threat detection, anomaly monitoring, and predictive risk analytics coming soon.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto text-left">
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-red-600 mb-2" />
              <h3 className="font-semibold mb-1">Anomaly Detection</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">ML-based behavioral analysis</p>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Target className="w-5 h-5 text-orange-600 mb-2" />
              <h3 className="font-semibold mb-1">Threat Scoring</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Real-time risk assessment</p>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <TrendingUp className="w-5 h-5 text-blue-600 mb-2" />
              <h3 className="font-semibold mb-1">Predictive Analytics</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Forecast threat trends</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
