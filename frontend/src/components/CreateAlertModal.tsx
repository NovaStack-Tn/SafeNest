import { useState, useEffect } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { X, Bell, Link2 } from 'lucide-react';
import { Button } from './Button';
import api from '@/lib/api';
import toast from 'react-hot-toast';

interface CreateAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  alert?: any; // Optional alert for edit mode
}

const ALERT_TYPES = [
  { value: 'intrusion', label: 'Intrusion Detection' },
  { value: 'anomaly', label: 'Anomaly Detected' },
  { value: 'unauthorized_access', label: 'Unauthorized Access' },
  { value: 'suspicious_activity', label: 'Suspicious Activity' },
  { value: 'policy_violation', label: 'Policy Violation' },
  { value: 'system', label: 'System Alert' },
  { value: 'face_recognition', label: 'Face Recognition' },
  { value: 'other', label: 'Other' },
];

const SEVERITY_LEVELS = [
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
  { value: 'info', label: 'Informational' },
];

export const CreateAlertModal = ({ isOpen, onClose, alert }: CreateAlertModalProps) => {
  const queryClient = useQueryClient();
  const isEditMode = !!alert;
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    alert_type: 'suspicious_activity',
    severity: 'medium',
    source: '',
    threat: '', // Related threat ID
  });

  // Prefill form data when editing
  useEffect(() => {
    if (alert) {
      setFormData({
        title: alert.title || '',
        description: alert.description || '',
        alert_type: alert.alert_type || 'suspicious_activity',
        severity: alert.severity || 'medium',
        source: alert.source || '',
        threat: alert.threat || '',
      });
    }
  }, [alert]);

  // Fetch threats for dropdown
  const { data: threats } = useQuery({
    queryKey: ['threats'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/threats/');
      return response.data.results || response.data;
    },
    enabled: isOpen, // Only fetch when modal is open
  });

  const saveMutation = useMutation({
    mutationFn: async (data: any) => {
      if (isEditMode) {
        const response = await api.put(`/threat-intelligence/alerts/${alert.id}/`, data);
        return response.data;
      } else {
        const response = await api.post('/threat-intelligence/alerts/', data);
        return response.data;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alert-stats'] });
      queryClient.invalidateQueries({ queryKey: ['threat-alerts'] });
      toast.success(isEditMode ? 'Alert updated successfully!' : 'Alert created successfully!');
      handleClose();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || `Failed to ${isEditMode ? 'update' : 'create'} alert`);
    },
  });

  const handleClose = () => {
    setFormData({
      title: '',
      description: '',
      alert_type: 'suspicious_activity',
      severity: 'medium',
      source: '',
      threat: '',
    });
    onClose();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.description) {
      toast.error('Please fill in all required fields');
      return;
    }
    saveMutation.mutate(formData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={handleClose} />

        <div className="inline-block w-full max-w-2xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-gray-800 shadow-xl rounded-lg">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <Bell className="w-6 h-6 text-orange-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {isEditMode ? 'Edit Alert' : 'Create New Alert'}
              </h3>
            </div>
            <button onClick={handleClose} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Title *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                placeholder="Enter alert title"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description *
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                placeholder="Describe the alert"
                required
              />
            </div>

            {/* Alert Type and Severity */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Alert Type
                </label>
                <select
                  value={formData.alert_type}
                  onChange={(e) => setFormData({ ...formData, alert_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  {ALERT_TYPES.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Severity
                </label>
                <select
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  {SEVERITY_LEVELS.map(level => (
                    <option key={level.value} value={level.value}>{level.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Source */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Source
              </label>
              <input
                type="text"
                value={formData.source}
                onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                placeholder="System component that generated this alert"
              />
            </div>

            {/* Related Threat */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                <Link2 className="w-4 h-4" />
                Related Threat (Optional)
              </label>
              <select
                value={formData.threat}
                onChange={(e) => setFormData({ ...formData, threat: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="">No related threat</option>
                {threats?.map((threat: any) => (
                  <option key={threat.id} value={threat.id}>
                    {threat.title} ({threat.severity} - {threat.status})
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Link this alert to an existing threat for correlation
              </p>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4">
              <Button type="button" variant="secondary" onClick={handleClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={saveMutation.isPending}>
                {saveMutation.isPending 
                  ? (isEditMode ? 'Updating...' : 'Creating...') 
                  : (isEditMode ? 'Update Alert' : 'Create Alert')}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
