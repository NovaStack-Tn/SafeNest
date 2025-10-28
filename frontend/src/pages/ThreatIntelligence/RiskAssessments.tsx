import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/Card';
import { Loader } from '@/components/Loader';
import { TrendingUp, TrendingDown, AlertCircle, Users, MapPin } from 'lucide-react';
import api from '@/lib/api';

interface RiskAssessment {
  id: number;
  title: string;
  description: string;
  assessment_type: string;
  risk_level: string;
  risk_score: number;
  likelihood: number;
  impact: number;
  assessed_at: string;
  subject_user_name?: string;
}

const RISK_COLORS = {
  critical: 'bg-red-600 text-white',
  severe: 'bg-orange-600 text-white',
  high: 'bg-yellow-600 text-white',
  moderate: 'bg-blue-600 text-white',
  low: 'bg-green-600 text-white',
  minimal: 'bg-gray-600 text-white',
};

export const RiskAssessments = () => {
  const { data: assessments, isLoading } = useQuery<RiskAssessment[]>({
    queryKey: ['risk-assessments'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/risk-assessments/');
      return response.data.results || response.data;
    },
  });

  const stats = {
    total: assessments?.length || 0,
    critical: assessments?.filter((a) => a.risk_level === 'critical' || a.risk_level === 'severe').length || 0,
    avgScore: assessments?.length ? 
      (assessments.reduce((sum, a) => sum + a.risk_score, 0) / assessments.length).toFixed(1) : 0,
  };

  if (isLoading) {
    return <Loader text="Loading risk assessments..." />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Risk Assessments
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          AI-powered risk analysis and impact assessments
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Assessments</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{stats.total}</p>
            </div>
            <TrendingUp className="w-12 h-12 text-blue-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">High/Critical Risk</p>
              <p className="text-3xl font-bold text-red-600 mt-2">{stats.critical}</p>
            </div>
            <AlertCircle className="w-12 h-12 text-red-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Average Risk Score</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">{stats.avgScore}</p>
            </div>
            <TrendingDown className="w-12 h-12 text-yellow-600" />
          </div>
        </Card>
      </div>

      {/* Assessments Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {assessments?.map((assessment) => (
          <Card key={assessment.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${RISK_COLORS[assessment.risk_level as keyof typeof RISK_COLORS]}`}>
                  {assessment.risk_level.toUpperCase()}
                </span>
              </div>
              <span className="text-2xl font-bold text-gray-900 dark:text-white">
                {assessment.risk_score.toFixed(1)}
              </span>
            </div>
            
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {assessment.title}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {assessment.description}
            </p>

            <div className="space-y-2 mb-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Likelihood:</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${assessment.likelihood * 100}%` }}
                    />
                  </div>
                  <span className="font-semibold">{(assessment.likelihood * 100).toFixed(0)}%</span>
                </div>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Impact:</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-red-600 h-2 rounded-full"
                      style={{ width: `${assessment.impact * 100}%` }}
                    />
                  </div>
                  <span className="font-semibold">{(assessment.impact * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4 text-xs text-gray-500 border-t border-gray-200 dark:border-gray-700 pt-4">
              <span className="flex items-center gap-1">
                {assessment.assessment_type === 'user' && <Users className="w-3 h-3" />}
                {assessment.assessment_type === 'location' && <MapPin className="w-3 h-3" />}
                {assessment.assessment_type.replace('_', ' ')}
              </span>
              {assessment.subject_user_name && <span>Subject: {assessment.subject_user_name}</span>}
              <span>Assessed: {new Date(assessment.assessed_at).toLocaleDateString()}</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
