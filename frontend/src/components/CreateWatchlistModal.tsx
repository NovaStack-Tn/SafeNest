import { useState, useEffect } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { X, Eye } from 'lucide-react';
import { Button } from './Button';
import api from '@/lib/api';
import toast from 'react-hot-toast';

interface CreateWatchlistModalProps {
  isOpen: boolean;
  onClose: () => void;
  entry?: any;
}

export const CreateWatchlistModal = ({ 
  isOpen, 
  onClose, 
  entry 
}: CreateWatchlistModalProps) => {
  const queryClient = useQueryClient();
  const isEdit = !!entry;

  const [formData, setFormData] = useState({
    threat: '',
    watchlist_type: 'person',
    subject_name: '',
    subject_id: '',
    description: '',
    risk_level: 'medium',
    reason: '',
    alert_on_detection: true,
    auto_notify: false,
    action_instructions: '',
    notes: '',
    expiry_date: '',
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
    if (entry) {
      setFormData({
        threat: entry.threat || '',
        watchlist_type: entry.watchlist_type || 'person',
        subject_name: entry.subject_name || '',
        subject_id: entry.subject_id || '',
        description: entry.description || '',
        risk_level: entry.risk_level || 'medium',
        reason: entry.reason || '',
        alert_on_detection: entry.alert_on_detection ?? true,
        auto_notify: entry.auto_notify ?? false,
        action_instructions: entry.action_instructions || '',
        notes: entry.notes || '',
        expiry_date: entry.expiry_date || '',
      });
    }
  }, [entry]);

  const mutation = useMutation({
    mutationFn: async (data: any) => {
      if (isEdit) {
        const response = await api.put(`/threat-intelligence/watchlists/${entry.id}/`, data);
        return response.data;
      } else {
        const response = await api.post('/threat-intelligence/watchlists/', data);
        return response.data;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
      toast.success(`Watchlist entry ${isEdit ? 'updated' : 'created'} successfully!`);
      onClose();
      setFormData({
        threat: '',
        watchlist_type: 'person',
        subject_name: '',
        subject_id: '',
        description: '',
        risk_level: 'medium',
        reason: '',
        alert_on_detection: true,
        auto_notify: false,
        action_instructions: '',
        notes: '',
        expiry_date: '',
      });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || `Failed to ${isEdit ? 'update' : 'create'} watchlist entry`);
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
            <Eye className="w-6 h-6 text-purple-600" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {isEdit ? 'Edit Watchlist Entry' : 'Add to Watchlist'}
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

          {/* Type & Risk Level */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Watchlist Type *
              </label>
              <select
                value={formData.watchlist_type}
                onChange={(e) => setFormData({ ...formData, watchlist_type: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="person">Person</option>
                <option value="vehicle">Vehicle</option>
                <option value="organization">Organization</option>
                <option value="location">Location</option>
                <option value="device">Device</option>
                <option value="other">Other</option>
              </select>
            </div>

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
              </select>
            </div>
          </div>

          {/* Subject Name & ID */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Subject Name *
              </label>
              <input
                type="text"
                value={formData.subject_name}
                onChange={(e) => setFormData({ ...formData, subject_name: e.target.value })}
                required
                placeholder="e.g., John Doe, License XYZ123..."
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Subject ID
              </label>
              <input
                type="text"
                value={formData.subject_id}
                onChange={(e) => setFormData({ ...formData, subject_id: e.target.value })}
                placeholder="Badge ID, License, MAC address..."
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
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
              rows={2}
              placeholder="Brief description of the subject..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Reason */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Reason for Watchlist *
            </label>
            <textarea
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              required
              rows={2}
              placeholder="Why is this subject being monitored?"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Action Instructions */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
              Action Instructions
            </label>
            <textarea
              value={formData.action_instructions}
              onChange={(e) => setFormData({ ...formData, action_instructions: e.target.value })}
              rows={2}
              placeholder="What should security personnel do upon detection?"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Alert Options */}
          <div className="space-y-3">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.alert_on_detection}
                onChange={(e) => setFormData({ ...formData, alert_on_detection: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <span className="text-sm text-gray-900 dark:text-white">
                Alert on Detection
              </span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.auto_notify}
                onChange={(e) => setFormData({ ...formData, auto_notify: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <span className="text-sm text-gray-900 dark:text-white">
                Auto-Notify Security Team
              </span>
            </label>
          </div>

          {/* Notes & Expiry */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Internal Notes
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
                placeholder="Additional notes (internal only)..."
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                Expiry Date
              </label>
              <input
                type="date"
                value={formData.expiry_date}
                onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <p className="text-xs text-gray-500 mt-1">Leave empty for permanent monitoring</p>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? 'Saving...' : (isEdit ? 'Update' : 'Add to')} Watchlist
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
