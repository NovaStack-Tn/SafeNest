import { AlertTriangle, Loader2, X } from 'lucide-react';
import { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  visitorId: number | null;
  visitorName?: string;
}

export default function DeleteConfirmationModal({
  isOpen,
  onClose,
  onSuccess,
  visitorId,
  visitorName,
}: DeleteConfirmationModalProps) {
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleDelete = async () => {
    if (!visitorId) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Please login first');
      return;
    }

    setLoading(true);
    try {
      await axios.delete(
        `http://localhost:8000/api/visitor-assets/visitors/${visitorId}/`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      toast.success('Visitor deleted successfully!');
      if (onSuccess) onSuccess();
      onClose();
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        localStorage.removeItem('access_token');
      } else {
        toast.error(error.response?.data?.error || 'Failed to delete visitor');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full">
        {/* Header */}
        <div className="bg-red-600 p-6 text-white rounded-t-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-white bg-opacity-20 p-3 rounded-full">
                <AlertTriangle className="h-6 w-6" />
              </div>
              <h2 className="text-xl font-bold">Delete Visitor</h2>
            </div>
            <button
              onClick={onClose}
              disabled={loading}
              className="text-white hover:text-red-200 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <p className="text-gray-700 dark:text-gray-300 mb-4">
            Are you sure you want to delete{' '}
            <span className="font-bold text-gray-900 dark:text-white">
              {visitorName || 'this visitor'}
            </span>
            ?
          </p>
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-sm text-red-800 dark:text-red-200">
              ⚠️ This action cannot be undone. All associated data including visit history, passes, and logs will be permanently deleted.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-900 rounded-b-xl">
          <div className="flex justify-end gap-3">
            <button
              onClick={onClose}
              disabled={loading}
              className="px-6 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleDelete}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Deleting...
                </>
              ) : (
                <>
                  <AlertTriangle className="h-5 w-5" />
                  Delete Visitor
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
