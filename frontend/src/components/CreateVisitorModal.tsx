import { useState } from 'react';
import { X, UserPlus, Loader2, Sparkles } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface CreateVisitorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  prefilledData?: any;
}

export default function CreateVisitorModal({ isOpen, onClose, onSuccess, prefilledData }: CreateVisitorModalProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    first_name: prefilledData?.first_name || '',
    last_name: prefilledData?.last_name || '',
    email: prefilledData?.email || '',
    phone: prefilledData?.phone || '',
    company: prefilledData?.company || '',
    visitor_type: prefilledData?.visitor_type || 'guest',
    purpose_of_visit: prefilledData?.purpose_of_visit || '',
    department_to_visit: prefilledData?.department_to_visit || '',
    id_type: prefilledData?.id_type || '',
    id_number: prefilledData?.id_number || '',
    requires_escort: prefilledData?.requires_escort || false,
    nda_signed: prefilledData?.nda_signed || false,
    notes: prefilledData?.notes || '',
    ai_extracted: prefilledData?.ai_extracted || false,
    ai_confidence: prefilledData?.ai_confidence || null,
  });

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Please login first to create visitors');
      return;
    }
    
    setLoading(true);

    try {
      // Prepare data - remove organization as backend adds it automatically
      const dataToSend: any = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        visitor_type: formData.visitor_type,
        purpose_of_visit: formData.purpose_of_visit,
        requires_escort: formData.requires_escort || false,
        nda_signed: formData.nda_signed || false,
        ai_extracted: formData.ai_extracted || false,
      };

      // Add optional fields only if they have values
      if (formData.email) dataToSend.email = formData.email;
      if (formData.phone) dataToSend.phone = formData.phone;
      if (formData.company) dataToSend.company = formData.company;
      if (formData.department_to_visit) dataToSend.department_to_visit = formData.department_to_visit;
      if (formData.id_type) dataToSend.id_type = formData.id_type;
      if (formData.id_number) dataToSend.id_number = formData.id_number;
      if (formData.notes) dataToSend.notes = formData.notes;
      if (formData.ai_confidence) dataToSend.ai_confidence = formData.ai_confidence;

      await axios.post(
        'http://localhost:8000/api/visitor-assets/visitors/',
        dataToSend,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      toast.success('Visitor created successfully!');
      if (onSuccess) onSuccess();
      handleClose();
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        localStorage.removeItem('access_token');
      } else {
        console.error('Create error:', error.response?.data);
        const errorMsg = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        JSON.stringify(error.response?.data) || 
                        'Failed to create visitor';
        toast.error(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      company: '',
      visitor_type: 'guest',
      purpose_of_visit: '',
      department_to_visit: '',
      id_type: '',
      id_number: '',
      requires_escort: false,
      nda_signed: false,
      notes: '',
      ai_extracted: false,
      ai_confidence: null,
    });
    onClose();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <UserPlus className="h-8 w-8" />
              <div>
                <h2 className="text-2xl font-bold">Create Visitor</h2>
                <p className="text-blue-100 text-sm mt-1">
                  {prefilledData?.ai_extracted && (
                    <span className="flex items-center gap-1">
                      <Sparkles className="h-4 w-4" />
                      Pre-filled with AI extracted data
                    </span>
                  )}
                  {!prefilledData?.ai_extracted && 'Register a new visitor'}
                </p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="text-white hover:text-blue-200 transition-colors"
              disabled={loading}
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Personal Information */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Personal Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  First Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Last Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Phone
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
          </div>

          {/* Company & Visit Details */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Company & Visit Details
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Company
                </label>
                <input
                  type="text"
                  name="company"
                  value={formData.company}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Visitor Type <span className="text-red-500">*</span>
                </label>
                <select
                  name="visitor_type"
                  value={formData.visitor_type}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="guest">👤 Guest</option>
                  <option value="contractor">🔧 Contractor</option>
                  <option value="vendor">📦 Vendor</option>
                  <option value="delivery">🚚 Delivery</option>
                  <option value="interviewer">💼 Job Candidate</option>
                  <option value="vip">⭐ VIP</option>
                  <option value="other">👥 Other</option>
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Purpose of Visit <span className="text-red-500">*</span>
                </label>
                <textarea
                  name="purpose_of_visit"
                  value={formData.purpose_of_visit}
                  onChange={handleChange}
                  required
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Department to Visit
                </label>
                <input
                  type="text"
                  name="department_to_visit"
                  value={formData.department_to_visit}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
          </div>

          {/* Identification */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Identification
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  ID Type
                </label>
                <input
                  type="text"
                  name="id_type"
                  value={formData.id_type}
                  onChange={handleChange}
                  placeholder="Driver's License, Passport, etc."
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  ID Number
                </label>
                <input
                  type="text"
                  name="id_number"
                  value={formData.id_number}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
          </div>

          {/* Security & Compliance */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Security & Compliance
            </h3>
            <div className="space-y-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="requires_escort"
                  checked={formData.requires_escort}
                  onChange={handleChange}
                  className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Requires Escort
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="nda_signed"
                  checked={formData.nda_signed}
                  onChange={handleChange}
                  className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  NDA Signed
                </span>
              </label>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Notes
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="Additional notes or comments..."
            />
          </div>
        </form>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-900">
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="px-6 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <UserPlus className="h-5 w-5" />
                  Create Visitor
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
