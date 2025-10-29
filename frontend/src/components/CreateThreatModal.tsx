import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X, AlertTriangle, Sparkles } from 'lucide-react';
import { Button } from './Button';
import api from '@/lib/api';
import toast from 'react-hot-toast';

interface CreateThreatModalProps {
  isOpen: boolean;
  onClose: () => void;
  threat?: any; // Optional threat for edit mode
}

const THREAT_TYPES = [
  { value: 'physical', label: 'Physical Security' },
  { value: 'cyber', label: 'Cyber Security' },
  { value: 'insider', label: 'Insider Threat' },
  { value: 'terrorism', label: 'Terrorism' },
  { value: 'fraud', label: 'Fraud' },
  { value: 'data_breach', label: 'Data Breach' },
  { value: 'social_engineering', label: 'Social Engineering' },
  { value: 'other', label: 'Other' },
];

const SEVERITY_LEVELS = [
  { value: 'critical', label: 'Critical', color: 'bg-red-500' },
  { value: 'high', label: 'High', color: 'bg-orange-500' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-500' },
  { value: 'low', label: 'Low', color: 'bg-blue-500' },
  { value: 'info', label: 'Informational', color: 'bg-gray-500' },
];

export const CreateThreatModal = ({ isOpen, onClose, threat }: CreateThreatModalProps) => {
  const queryClient = useQueryClient();
  const isEditMode = !!threat;
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    threat_type: 'cyber',
    severity: 'medium',
    source: '',
    tags: [] as string[],
  });
  const [tagInput, setTagInput] = useState('');
  const [useAI, setUseAI] = useState(false);

  // Prefill form data when editing
  useEffect(() => {
    if (threat) {
      setFormData({
        title: threat.title || '',
        description: threat.description || '',
        threat_type: threat.threat_type || 'cyber',
        severity: threat.severity || 'medium',
        source: threat.source || '',
        tags: threat.tags || [],
      });
    }
  }, [threat]);

  const saveMutation = useMutation({
    mutationFn: async (data: any) => {
      if (isEditMode) {
        const response = await api.put(`/threat-intelligence/threats/${threat.id}/`, data);
        return response.data;
      } else {
        const response = await api.post('/threat-intelligence/threats/', data);
        return response.data;
      }
    },
    onSuccess: async (savedThreat) => {
      queryClient.invalidateQueries({ queryKey: ['threats'] });
      queryClient.invalidateQueries({ queryKey: ['threat-stats'] });
      
      if (useAI && !isEditMode) {
        toast.success('Threat created! Analyzing with AI...');
        try {
          await api.post(`/threat-intelligence/threats/${savedThreat.id}/ai_analyze/`);
          queryClient.invalidateQueries({ queryKey: ['threats'] });
          toast.success('AI analysis complete!');
        } catch (error) {
          toast.error('AI analysis failed, but threat was created');
        }
      } else {
        toast.success(isEditMode ? 'Threat updated successfully!' : 'Threat created successfully!');
      }
      
      handleClose();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || `Failed to ${isEditMode ? 'update' : 'create'} threat`);
    },
  });

  const handleClose = () => {
    setFormData({
      title: '',
      description: '',
      threat_type: 'cyber',
      severity: 'medium',
      source: '',
      tags: [],
    });
    setTagInput('');
    setUseAI(false);
    onClose();
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({ ...formData, tags: [...formData.tags, tagInput.trim()] });
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setFormData({ ...formData, tags: formData.tags.filter(t => t !== tag) });
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
              <AlertTriangle className="w-6 h-6 text-red-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {isEditMode ? 'Edit Threat' : 'Create New Threat'}
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
                placeholder="Enter threat title"
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
                placeholder="Describe the threat in detail"
                required
              />
            </div>

            {/* Threat Type and Severity */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Threat Type
                </label>
                <select
                  value={formData.threat_type}
                  onChange={(e) => setFormData({ ...formData, threat_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  {THREAT_TYPES.map(type => (
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
                placeholder="Where was this threat identified?"
              />
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tags
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  placeholder="Add tag and press Enter"
                />
                <Button type="button" onClick={handleAddTag} variant="secondary">
                  Add
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.tags.map(tag => (
                  <span
                    key={tag}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
                  >
                    {tag}
                    <button type="button" onClick={() => handleRemoveTag(tag)} className="hover:text-blue-600">
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* AI Analysis Option */}
            <div className="flex items-center gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <input
                type="checkbox"
                id="useAI"
                checked={useAI}
                onChange={(e) => setUseAI(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="useAI" className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
                <Sparkles className="w-4 h-4 text-blue-600" />
                Analyze with AI after creation (severity, attack vectors, indicators)
              </label>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4">
              <Button type="button" variant="secondary" onClick={handleClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={saveMutation.isPending}>
                {saveMutation.isPending 
                  ? (isEditMode ? 'Updating...' : 'Creating...') 
                  : (isEditMode ? 'Update Threat' : 'Create Threat')}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
