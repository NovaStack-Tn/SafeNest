import { useState, useEffect } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { X, Target } from 'lucide-react';
import { Button } from './Button';
import api from '@/lib/api';
import toast from 'react-hot-toast';

interface CreateRiskAssessmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  assessment?: any;
}

export const CreateRiskAssessmentModal = ({ 
  isOpen, 
  onClose, 
  assessment 
}: CreateRiskAssessmentModalProps) => {
  const queryClient = useQueryClient();
  const isEdit = !!assessment;

  const [formData, setFormData] = useState({
    threat: '',
    risk_level: 'medium',
    likelihood: 'possible',
    impact: 'moderate',
    vulnerability_analysis: '',
    impact_analysis: '',
    mitigation_strategy: '',
    residual_risk: '',
    estimated_cost: '',
    timeline: '',
    required_resources: '',
  });

  // Fetch threats for dropdown
  const { data: threats } = useQuery({
    queryKey: ['threats'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/threats/');
      return response.data.results || response.data;
    },
  });

  useEffect(() => {
    if (assessment) {
      setFormData({
        threat: assessment.threat || '',
        risk_level: assessment.risk_level || 'medium',
        likelihood: assessment.likelihood || 'possible',
        impact: assessment.impact || 'moderate',
        vulnerability_analysis: assessment.vulnerability_analysis || '',
        impact_analysis: assessment.impact_analysis || '',
        mitigation_strategy: assessment.mitigation_strategy || '',
        residual_risk: assessment.residual_risk || '',
        estimated_cost: assessment.estimated_cost || '',
        timeline: assessment.timeline || '',
        required_resources: assessment.required_resources || '',
      });
    }
  }, [assessment]);

  const mutation = useMutation({
    mutationFn: async (data: any) => {
      if (isEdit) {
        const response = await api.put(`/threat-intelligence/risk-assessments/${assessment.id}/`, data);
        return response.data;
      } else {
        const response = await api.post('/threat-intelligence/risk-assessments/', data);
        return response.data;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risk-assessments'] });
      toast.success(`Risk assessment ${isEdit ? 'updated' : 'created'} successfully!`);
      onClose();
      setFormData({
        threat: '',
        risk_level: 'medium',
        likelihood: 'possible',
        impact: 'moderate',
        vulnerability_analysis: '',
        impact_analysis: '',
        mitigation_strategy: '',
        residual_risk: '',
        estimated_cost: '',
        timeline: '',
        required_resources: '',
      });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || `Failed to ${isEdit ? 'update' : 'create'} risk assessment`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center sticky top-0 bg-white dark:bg-gray-800">
          <div className="flex items-center gap-3">
            <Target className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {isEdit ? 'Edit Risk Assessment' : 'Create Risk Assessment'}
            </h2>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Threat Selection */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Related Threat *
            </label>
            <select
              value={formData.threat}
              onChange={(e) => setFormData({ ...formData, threat: e.target.value })}
              required
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Select a threat</option>
              {threats?.map((threat: any) => (
                <option key={threat.id} value={threat.id}>
                  {threat.title} ({threat.severity})
                </option>
              ))}
            </select>
          </div>

          {/* Risk Level, Likelihood, Impact */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Risk Level *
              </label>
              <select
                value={formData.risk_level}
                onChange={(e) => setFormData({ ...formData, risk_level: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
                <option value="negligible">Negligible</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Likelihood *
              </label>
              <select
                value={formData.likelihood}
                onChange={(e) => setFormData({ ...formData, likelihood: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="certain">Certain</option>
                <option value="likely">Likely</option>
                <option value="possible">Possible</option>
                <option value="unlikely">Unlikely</option>
                <option value="rare">Rare</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Impact *
              </label>
              <select
                value={formData.impact}
                onChange={(e) => setFormData({ ...formData, impact: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="catastrophic">Catastrophic</option>
                <option value="severe">Severe</option>
                <option value="moderate">Moderate</option>
                <option value="minor">Minor</option>
                <option value="insignificant">Insignificant</option>
              </select>
            </div>
          </div>

          {/* Vulnerability Analysis */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Vulnerability Analysis *
            </label>
            <textarea
              value={formData.vulnerability_analysis}
              onChange={(e) => setFormData({ ...formData, vulnerability_analysis: e.target.value })}
              required
              rows={3}
              placeholder="What makes the organization vulnerable to this threat?"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Impact Analysis */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Impact Analysis *
            </label>
            <textarea
              value={formData.impact_analysis}
              onChange={(e) => setFormData({ ...formData, impact_analysis: e.target.value })}
              required
              rows={3}
              placeholder="What could happen if the threat is exploited?"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Mitigation Strategy */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Mitigation Strategy *
            </label>
            <textarea
              value={formData.mitigation_strategy}
              onChange={(e) => setFormData({ ...formData, mitigation_strategy: e.target.value })}
              required
              rows={3}
              placeholder="How can this risk be reduced or eliminated?"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Residual Risk */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Residual Risk
            </label>
            <textarea
              value={formData.residual_risk}
              onChange={(e) => setFormData({ ...formData, residual_risk: e.target.value })}
              rows={2}
              placeholder="What risk remains after mitigation?"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Additional Details */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Estimated Cost
              </label>
              <input
                type="text"
                value={formData.estimated_cost}
                onChange={(e) => setFormData({ ...formData, estimated_cost: e.target.value })}
                placeholder="e.g., $5,000 - $10,000"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Timeline
              </label>
              <input
                type="text"
                value={formData.timeline}
                onChange={(e) => setFormData({ ...formData, timeline: e.target.value })}
                placeholder="e.g., 2-4 weeks"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Required Resources
              </label>
              <input
                type="text"
                value={formData.required_resources}
                onChange={(e) => setFormData({ ...formData, required_resources: e.target.value })}
                placeholder="e.g., 2 engineers"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? 'Saving...' : (isEdit ? 'Update' : 'Create')} Assessment
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
