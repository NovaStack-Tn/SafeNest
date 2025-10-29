import { useState, useEffect } from 'react';
import { X, Save, Loader2 } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface EditAssetModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  assetId: number | null;
}

export default function EditAssetModal({ isOpen, onClose, onSuccess, assetId }: EditAssetModalProps) {
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    asset_type: 'laptop',
    asset_tag: '',
    serial_number: '',
    status: 'available',
    condition: 'good',
    manufacturer: '',
    model: '',
    location: '',
    purchase_date: '',
    purchase_cost: '',
    current_value: '',
    warranty_expiry: '',
    notes: '',
  });

  useEffect(() => {
    if (isOpen && assetId) {
      fetchAssetData();
    }
  }, [isOpen, assetId]);

  const fetchAssetData = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Please login first');
      return;
    }
    
    setFetching(true);
    try {
      const response = await axios.get(
        `http://localhost:8000/api/visitor-assets/assets/${assetId}/`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setFormData({
        ...response.data,
        purchase_date: response.data.purchase_date || '',
        warranty_expiry: response.data.warranty_expiry || '',
        purchase_cost: response.data.purchase_cost || '',
        current_value: response.data.current_value || '',
      });
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        localStorage.removeItem('access_token');
      } else {
        toast.error('Failed to fetch asset data');
      }
    } finally {
      setFetching(false);
    }
  };

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Please login first');
      return;
    }
    
    setLoading(true);

    try {
      const dataToSend: any = {
        name: formData.name,
        asset_type: formData.asset_type,
        asset_tag: formData.asset_tag,
        status: formData.status,
        condition: formData.condition,
      };

      if (formData.serial_number) dataToSend.serial_number = formData.serial_number;
      if (formData.manufacturer) dataToSend.manufacturer = formData.manufacturer;
      if (formData.model) dataToSend.model = formData.model;
      if (formData.location) dataToSend.location = formData.location;
      if (formData.purchase_date) dataToSend.purchase_date = formData.purchase_date;
      if (formData.purchase_cost) dataToSend.purchase_cost = parseFloat(formData.purchase_cost);
      if (formData.current_value) dataToSend.current_value = parseFloat(formData.current_value);
      if (formData.warranty_expiry) dataToSend.warranty_expiry = formData.warranty_expiry;
      if (formData.notes) dataToSend.notes = formData.notes;

      await axios.patch(
        `http://localhost:8000/api/visitor-assets/assets/${assetId}/`,
        dataToSend,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      toast.success('Asset updated successfully!');
      if (onSuccess) onSuccess();
      onClose();
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        localStorage.removeItem('access_token');
      } else {
        toast.error(error.response?.data?.error || 'Failed to update asset');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  if (fetching) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-8">
          <Loader2 className="h-12 w-12 animate-spin text-green-600 mx-auto" />
          <p className="text-gray-600 dark:text-gray-400 mt-4">Loading asset data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-green-700 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Save className="h-8 w-8" />
              <div>
                <h2 className="text-2xl font-bold">Edit Asset</h2>
                <p className="text-green-100 text-sm mt-1">Update asset information</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-green-200 transition-colors"
              disabled={loading}
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Form - Similar to Create but with update */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Asset Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Asset Type <span className="text-red-500">*</span>
              </label>
              <select
                name="asset_type"
                value={formData.asset_type}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="laptop">💻 Laptop</option>
                <option value="desktop">🖥️ Desktop</option>
                <option value="phone">📱 Phone</option>
                <option value="tablet">📱 Tablet</option>
                <option value="monitor">🖥️ Monitor</option>
                <option value="vehicle">🚗 Vehicle</option>
                <option value="equipment">🔧 Equipment</option>
                <option value="furniture">🪑 Furniture</option>
                <option value="other">📦 Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Asset Tag <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="asset_tag"
                value={formData.asset_tag}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Serial Number
              </label>
              <input
                type="text"
                name="serial_number"
                value={formData.serial_number}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Status <span className="text-red-500">*</span>
              </label>
              <select
                name="status"
                value={formData.status}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="available">Available</option>
                <option value="assigned">Assigned</option>
                <option value="in_use">In Use</option>
                <option value="maintenance">Maintenance</option>
                <option value="retired">Retired</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Condition <span className="text-red-500">*</span>
              </label>
              <select
                name="condition"
                value={formData.condition}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="excellent">Excellent</option>
                <option value="good">Good</option>
                <option value="fair">Fair</option>
                <option value="poor">Poor</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Location
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Notes
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
        </form>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-900">
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-6 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Updating...
                </>
              ) : (
                <>
                  <Save className="h-5 w-5" />
                  Update Asset
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
