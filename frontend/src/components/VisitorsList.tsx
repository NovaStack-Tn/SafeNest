import { useState, useEffect } from 'react';
import { Search, UserCheck, UserX, AlertTriangle, Sparkles, Eye, Edit, Trash2 } from 'lucide-react';
import axios from 'axios';
import VisitorDetailModal from './VisitorDetailModal';
import EditVisitorModal from './EditVisitorModal';
import DeleteConfirmationModal from './DeleteConfirmationModal';

interface Visitor {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  company: string;
  visitor_type: string;
  status: string;
  purpose_of_visit: string;
  host_name: string;
  risk_score: number;
  ai_extracted: boolean;
  ai_confidence: number | null;
  created_at: string;
}

export default function VisitorsList() {
  const [visitors, setVisitors] = useState<Visitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  
  // Modals state
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedVisitorId, setSelectedVisitorId] = useState<number | null>(null);
  const [selectedVisitorName, setSelectedVisitorName] = useState<string>('');

  useEffect(() => {
    fetchVisitors();
  }, [statusFilter]);

  const fetchVisitors = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        console.warn('No access token found. Please login first.');
        // Return empty array instead of throwing error
        setVisitors([]);
        setLoading(false);
        return;
      }
      
      const params = statusFilter !== 'all' ? { status: statusFilter } : {};
      
      const response = await axios.get('http://localhost:8000/api/visitor-assets/visitors/', {
        headers: { Authorization: `Bearer ${token}` },
        params,
      });
      
      setVisitors(response.data.results || response.data);
    } catch (error: any) {
      console.error('Failed to fetch visitors:', error);
      
      // Handle 401 specifically
      if (error.response?.status === 401) {
        console.warn('Token expired or invalid. Please login again.');
        localStorage.removeItem('access_token');
        setVisitors([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      pre_registered: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
      checked_in: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      on_premises: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      checked_out: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
      blacklisted: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status as keyof typeof styles] || styles.pre_registered}`}>
        {status.replace(/_/g, ' ').toUpperCase()}
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

  const getRiskBadge = (riskScore: number) => {
    if (riskScore >= 0.7) {
      return <span className="px-2 py-1 bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400 text-xs font-medium rounded-full">High Risk</span>;
    } else if (riskScore >= 0.4) {
      return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400 text-xs font-medium rounded-full">Medium Risk</span>;
    }
    return <span className="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 text-xs font-medium rounded-full">Low Risk</span>;
  };

  const filteredVisitors = visitors.filter((visitor) =>
    visitor.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    visitor.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
    visitor.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search visitors by name, company, or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <div className="flex gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="all">All Status</option>
            <option value="pre_registered">Pre-Registered</option>
            <option value="checked_in">Checked In</option>
            <option value="on_premises">On Premises</option>
            <option value="checked_out">Checked Out</option>
          </select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Visitors</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{visitors.length}</p>
            </div>
            <div className="bg-blue-100 dark:bg-blue-900/20 p-3 rounded-lg">
              <UserCheck className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">On Premises</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {visitors.filter(v => v.status === 'on_premises').length}
              </p>
            </div>
            <div className="bg-green-100 dark:bg-green-900/20 p-3 rounded-lg">
              <UserCheck className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">AI Extracted</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {visitors.filter(v => v.ai_extracted).length}
              </p>
            </div>
            <div className="bg-purple-100 dark:bg-purple-900/20 p-3 rounded-lg">
              <Sparkles className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">High Risk</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {visitors.filter(v => v.risk_score >= 0.7).length}
              </p>
            </div>
            <div className="bg-red-100 dark:bg-red-900/20 p-3 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Visitors Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Visitor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Risk
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Host
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredVisitors.map((visitor) => (
                <tr key={visitor.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                        {visitor.full_name.charAt(0)}
                      </div>
                      <div className="ml-4">
                        <div className="flex items-center gap-2">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {visitor.full_name}
                          </div>
                          {visitor.ai_extracted && (
                            <span title="AI Extracted">
                              <Sparkles className="h-4 w-4 text-purple-500" />
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">{visitor.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">{visitor.company || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-2xl" title={visitor.visitor_type}>
                      {getVisitorTypeIcon(visitor.visitor_type)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(visitor.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getRiskBadge(visitor.risk_score)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {visitor.host_name || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => {
                          setSelectedVisitorId(visitor.id);
                          setShowDetailModal(true);
                        }}
                        className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                        title="View Details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => {
                          setSelectedVisitorId(visitor.id);
                          setShowEditModal(true);
                        }}
                        className="p-2 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors"
                        title="Edit"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => {
                          setSelectedVisitorId(visitor.id);
                          setSelectedVisitorName(visitor.full_name);
                          setShowDeleteModal(true);
                        }}
                        className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredVisitors.length === 0 && (
          <div className="text-center py-12">
            <UserX className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No visitors found</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Try adjusting your search or filter criteria
            </p>
          </div>
        )}
      </div>

      {/* CRUD Modals */}
      <VisitorDetailModal
        isOpen={showDetailModal}
        onClose={() => setShowDetailModal(false)}
        visitorId={selectedVisitorId}
        onEdit={(id) => {
          setSelectedVisitorId(id);
          setShowEditModal(true);
        }}
        onDelete={(id) => {
          const visitor = visitors.find(v => v.id === id);
          setSelectedVisitorId(id);
          setSelectedVisitorName(visitor?.full_name || '');
          setShowDeleteModal(true);
        }}
      />

      <EditVisitorModal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        visitorId={selectedVisitorId}
        onSuccess={() => {
          fetchVisitors();
          setShowEditModal(false);
        }}
      />

      <DeleteConfirmationModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        visitorId={selectedVisitorId}
        visitorName={selectedVisitorName}
        onSuccess={() => {
          fetchVisitors();
          setShowDeleteModal(false);
        }}
      />
    </div>
  );
}
