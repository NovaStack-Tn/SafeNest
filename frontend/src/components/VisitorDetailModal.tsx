import { useState, useEffect } from 'react';
import { X, User, Building2, Mail, Phone, FileText, Shield, Clock, Loader2, Edit, Trash2 } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface VisitorDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  visitorId: number | null;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

export default function VisitorDetailModal({ isOpen, onClose, visitorId, onEdit, onDelete }: VisitorDetailModalProps) {
  const [visitor, setVisitor] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && visitorId) {
      fetchVisitorDetail();
    }
  }, [isOpen, visitorId]);

  const fetchVisitorDetail = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Please login first');
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:8000/api/visitor-assets/visitors/${visitorId}/`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setVisitor(response.data);
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        localStorage.removeItem('access_token');
      } else {
        toast.error('Failed to fetch visitor details');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const getStatusBadge = (status: string) => {
    const styles = {
      pre_registered: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
      checked_in: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      on_premises: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      checked_out: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
      blacklisted: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    };

    return (
      <span className={`px-3 py-1 text-sm font-medium rounded-full ${styles[status as keyof typeof styles] || styles.pre_registered}`}>
        {status?.replace(/_/g, ' ').toUpperCase()}
      </span>
    );
  };

  const getVisitorTypeIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      guest: '👤',
      contractor: '🔧',
      vendor: '📦',
      delivery: '🚚',
      interviewer: '💼',
      vip: '⭐',
      other: '👥',
    };
    return icons[type] || '👤';
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-8">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto" />
          <p className="text-gray-600 dark:text-gray-400 mt-4">Loading visitor details...</p>
        </div>
      </div>
    );
  }

  if (!visitor) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 bg-white rounded-full flex items-center justify-center text-indigo-600 font-bold text-2xl">
                {visitor.full_name?.charAt(0)}
              </div>
              <div>
                <h2 className="text-2xl font-bold">{visitor.full_name}</h2>
                <p className="text-indigo-100 text-sm mt-1">
                  {getVisitorTypeIcon(visitor.visitor_type)} {visitor.visitor_type?.replace(/_/g, ' ')}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {onEdit && (
                <button
                  onClick={() => {
                    onEdit(visitor.id);
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
                    onDelete(visitor.id);
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
          <div className="mt-4">
            {getStatusBadge(visitor.status)}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Contact Information */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <User className="h-5 w-5" />
              Contact Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
              <div className="flex items-center gap-3">
                <Mail className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Email</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {visitor.email || 'N/A'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Phone className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Phone</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {visitor.phone || 'N/A'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Building2 className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Company</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {visitor.company || 'N/A'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <User className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Host</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {visitor.host_name || 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Visit Details */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Visit Details
            </h3>
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg space-y-3">
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Purpose of Visit</p>
                <p className="text-sm text-gray-900 dark:text-white mt-1">
                  {visitor.purpose_of_visit}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Department</p>
                <p className="text-sm text-gray-900 dark:text-white mt-1">
                  {visitor.department_to_visit || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Identification */}
          {(visitor.id_type || visitor.id_number) && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Identification
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">ID Type</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {visitor.id_type || 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">ID Number</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {visitor.id_number || 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Security & Compliance */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Security & Compliance
            </h3>
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg space-y-2">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${visitor.requires_escort ? 'bg-yellow-500' : 'bg-gray-300'}`} />
                <span className="text-sm text-gray-900 dark:text-white">
                  {visitor.requires_escort ? 'Requires Escort' : 'No Escort Required'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${visitor.nda_signed ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="text-sm text-gray-900 dark:text-white">
                  {visitor.nda_signed ? 'NDA Signed' : 'No NDA'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${visitor.is_on_watchlist ? 'bg-red-500' : 'bg-gray-300'}`} />
                <span className="text-sm text-gray-900 dark:text-white">
                  {visitor.is_on_watchlist ? 'On Watchlist' : 'Not on Watchlist'}
                </span>
              </div>
              {visitor.risk_score > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Risk Score</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          visitor.risk_score >= 0.7 ? 'bg-red-500' : 
                          visitor.risk_score >= 0.4 ? 'bg-yellow-500' : 
                          'bg-green-500'
                        }`}
                        style={{ width: `${visitor.risk_score * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {(visitor.risk_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Visit History */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Visit History
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Total Visits</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {visitor.visit_count || 0}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Last Visit</p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {visitor.last_visit_at ? new Date(visitor.last_visit_at).toLocaleDateString() : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Created</p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {new Date(visitor.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>

          {/* Notes */}
          {visitor.notes && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Notes
              </h3>
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <p className="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">
                  {visitor.notes}
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
