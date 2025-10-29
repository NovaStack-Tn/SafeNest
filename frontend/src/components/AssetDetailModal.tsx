import { useState, useEffect } from 'react';
import { X, Package, Loader2, Edit, Trash2 } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface AssetDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  assetId: number | null;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

export default function AssetDetailModal({ isOpen, onClose, assetId, onEdit, onDelete }: AssetDetailModalProps) {
  const [asset, setAsset] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && assetId) {
      fetchAssetDetail();
    }
  }, [isOpen, assetId]);

  const fetchAssetDetail = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Please login first');
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:8000/api/visitor-assets/assets/${assetId}/`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setAsset(response.data);
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        localStorage.removeItem('access_token');
      } else {
        toast.error('Failed to fetch asset details');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  if (loading || !asset) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-8">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto" />
          <p className="text-gray-600 dark:text-gray-400 mt-4">Loading asset details...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 bg-white rounded-full flex items-center justify-center text-indigo-600">
                <Package className="h-8 w-8" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">{asset.name}</h2>
                <p className="text-indigo-100 text-sm mt-1">
                  {asset.asset_tag} • {asset.asset_type}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {onEdit && (
                <button
                  onClick={() => {
                    onEdit(asset.id);
                    onClose();
                  }}
                  className="p-2 hover:bg-indigo-500 rounded-lg transition-colors"
                  title="Edit"
                >
                  <Edit className="h-5 w-5" />
                </button>
              )}
              {onDelete && (
                <button
                  onClick={() => {
                    onDelete(asset.id);
                    onClose();
                  }}
                  className="p-2 hover:bg-red-500 rounded-lg transition-colors"
                  title="Delete"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              )}
              <button
                onClick={onClose}
                className="p-2 hover:bg-indigo-500 rounded-lg transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Serial Number</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {asset.serial_number || 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Status</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                {asset.status}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Condition</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                {asset.condition}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Location</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {asset.location || 'N/A'}
              </p>
            </div>
          </div>

          {/* Details */}
          {(asset.manufacturer || asset.model) && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Product Details
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                {asset.manufacturer && (
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Manufacturer</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {asset.manufacturer}
                    </p>
                  </div>
                )}
                {asset.model && (
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Model</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {asset.model}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Financial */}
          {(asset.purchase_cost || asset.current_value) && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Financial Information
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                {asset.purchase_cost && (
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Purchase Cost</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      ${asset.purchase_cost}
                    </p>
                  </div>
                )}
                {asset.current_value && (
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Current Value</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      ${asset.current_value}
                    </p>
                  </div>
                )}
                {asset.purchase_date && (
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Purchase Date</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {new Date(asset.purchase_date).toLocaleDateString()}
                    </p>
                  </div>
                )}
                {asset.warranty_expiry && (
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Warranty Expiry</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {new Date(asset.warranty_expiry).toLocaleDateString()}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Notes */}
          {asset.notes && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Notes
              </h3>
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <p className="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">
                  {asset.notes}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-900">
          <button
            onClick={onClose}
            className="w-full px-6 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
