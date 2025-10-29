import { useState, useEffect } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { X, AlertOctagon } from 'lucide-react';
import { Button } from './Button';
import api from '@/lib/api';
import toast from 'react-hot-toast';

interface CreateIndicatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  indicator?: any;
}

export const CreateIndicatorModal = ({ 
  isOpen, 
  onClose, 
  indicator 
}: CreateIndicatorModalProps) => {
  const queryClient = useQueryClient();
  const isEdit = !!indicator;

  const [formData, setFormData] = useState({
    threat: '',
    indicator_type: 'ip_address',
    value: '',
    description: '',
    confidence: 'medium',
    source: '',
    action_taken: '',
    tags: '',
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
    if (indicator) {
      setFormData({
        threat: indicator.threat || '',
        indicator_type: indicator.indicator_type || 'ip_address',
        value: indicator.value || '',
        description: indicator.description || '',
        confidence: indicator.confidence || 'medium',
        source: indicator.source || '',
        action_taken: indicator.action_taken || '',
        tags: indicator.tags?.join(', ') || '',
      });
    }
  }, [indicator]);

  const mutation = useMutation({
    mutationFn: async (data: any) => {
      const payload = {
        ...data,
        tags: data.tags ? data.tags.split(',').map((t: string) => t.trim()).filter(Boolean) : [],
      };
      
      if (isEdit) {
        const response = await api.put(`/threat-intelligence/indicators/${indicator.id}/`, payload);
        return response.data;
      } else {
        const response = await api.post('/threat-intelligence/indicators/', payload);
        return response.data;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['threat-indicators'] });
      toast.success(`Indicator ${isEdit ? 'updated' : 'created'} successfully!`);
      onClose();
      setFormData({
        threat: '',
        indicator_type: 'ip_address',
        value: '',
        description: '',
        confidence: 'medium',
        source: '',
        action_taken: '',
        tags: '',
      });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || `Failed to ${isEdit ? 'update' : 'create'} indicator`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center sticky top-0 bg-white dark:bg-gray-800">
          <div className="flex items-center gap-3">
            <AlertOctagon className="w-6 h-6 text-orange-600" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {isEdit ? 'Edit Indicator' : 'Add Threat Indicator'}
            </h2>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Related Threat */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Related Threat (Optional)
            </label>
            <select
              value={formData.threat}
              onChange={(e) => setFormData({ ...formData, threat: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">No related threat</option>
              {threats?.map((threat: any) => (
                <option key={threat.id} value={threat.id}>
                  {threat.title} ({threat.severity})
                </option>
              ))}
            </select>
          </div>

          {/* Indicator Type & Confidence */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Indicator Type *
              </label>
              <select
                value={formData.indicator_type}
                onChange={(e) => setFormData({ ...formData, indicator_type: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="ip_address">IP Address</option>
                <option value="domain">Domain</option>
                <option value="url">URL</option>
                <option value="email">Email</option>
                <option value="hash">File Hash</option>
                <option value="user_agent">User Agent</option>
                <option value="registry_key">Registry Key</option>
                <option value="cryptocurrency">Cryptocurrency Address</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Confidence *
              </label>
              <select
                value={formData.confidence}
                onChange={(e) => setFormData({ ...formData, confidence: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>

          {/* Value */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Indicator Value *
            </label>
            <input
              type="text"
              value={formData.value}
              onChange={(e) => setFormData({ ...formData, value: e.target.value })}
              required
              placeholder="e.g., 192.168.1.100, malicious-domain.com, abc123hash..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Description *
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              required
              rows={3}
              placeholder="Describe why this indicator is suspicious or malicious..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Source */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Source
            </label>
            <input
              type="text"
              value={formData.source}
              onChange={(e) => setFormData({ ...formData, source: e.target.value })}
              placeholder="e.g., VirusTotal, Internal Analysis, Threat Feed..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Action Taken */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Action Taken
            </label>
            <textarea
              value={formData.action_taken}
              onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
              rows={2}
              placeholder="Actions taken to mitigate this indicator..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              placeholder="malware, phishing, c2, ransomware..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Buttons */}
          <div className="flex gap-3 justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? 'Saving...' : (isEdit ? 'Update' : 'Add')} Indicator
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
