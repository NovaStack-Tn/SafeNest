import { useState, useEffect } from 'react';
import { Search, Package, Laptop, Monitor, Phone, Car, Wrench, Eye, Edit, Trash2 } from 'lucide-react';
import axios from 'axios';
import AssetDetailModal from './AssetDetailModal';
import EditAssetModal from './EditAssetModal';
import DeleteAssetModal from './DeleteAssetModal';

interface Asset {
  id: number;
  name: string;
  asset_type: string;
  asset_tag: string;
  serial_number: string;
  status: string;
  assigned_to_name: string | null;
  location: string;
  condition: string;
  purchase_date: string;
  value: string;
  created_at: string;
}

export default function AssetsList() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  
  // Modals state
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedAssetId, setSelectedAssetId] = useState<number | null>(null);
  const [selectedAssetName, setSelectedAssetName] = useState<string>('');

  useEffect(() => {
    fetchAssets();
  }, [statusFilter]);

  const fetchAssets = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        console.warn('No access token found. Please login first.');
        setAssets([]);
        setLoading(false);
        return;
      }
      
      const params = statusFilter !== 'all' ? { status: statusFilter } : {};
      
      const response = await axios.get('http://localhost:8000/api/visitor-assets/assets/', {
        headers: { Authorization: `Bearer ${token}` },
        params,
      });
      
      setAssets(response.data.results || response.data);
    } catch (error: any) {
      console.error('Failed to fetch assets:', error);
      
      if (error.response?.status === 401) {
        console.warn('Token expired or invalid. Please login again.');
        localStorage.removeItem('access_token');
        setAssets([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      available: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      assigned: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      in_use: 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
      maintenance: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
      retired: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
    };

    return (
      <span className={`px-3 py-1 text-xs font-medium rounded-full ${styles[status as keyof typeof styles] || styles.available}`}>
        {status?.replace(/_/g, ' ').toUpperCase()}
      </span>
    );
  };

  const getAssetTypeIcon = (type: string) => {
    const icons: { [key: string]: JSX.Element } = {
      laptop: <Laptop className="h-5 w-5" />,
      desktop: <Monitor className="h-5 w-5" />,
      phone: <Phone className="h-5 w-5" />,
      vehicle: <Car className="h-5 w-5" />,
      equipment: <Wrench className="h-5 w-5" />,
      other: <Package className="h-5 w-5" />,
    };
    return icons[type] || <Package className="h-5 w-5" />;
  };

  const getConditionBadge = (condition: string) => {
    const styles = {
      excellent: 'bg-green-100 text-green-800',
      good: 'bg-blue-100 text-blue-800',
      fair: 'bg-yellow-100 text-yellow-800',
      poor: 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded ${styles[condition as keyof typeof styles] || styles.good}`}>
        {condition?.toUpperCase()}
      </span>
    );
  };

  const filteredAssets = assets.filter((asset) =>
    asset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    asset.asset_tag.toLowerCase().includes(searchQuery.toLowerCase()) ||
    asset.serial_number.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Calculate stats
  const totalAssets = assets.length;
  const availableAssets = assets.filter(a => a.status === 'available').length;
  const assignedAssets = assets.filter(a => a.status === 'assigned').length;
  const maintenanceAssets = assets.filter(a => a.status === 'maintenance').length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Assets</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalAssets}</p>
            </div>
            <Package className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Available</p>
              <p className="text-2xl font-bold text-green-600">{availableAssets}</p>
            </div>
            <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
              <Package className="h-5 w-5 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Assigned</p>
              <p className="text-2xl font-bold text-blue-600">{assignedAssets}</p>
            </div>
            <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
              <Package className="h-5 w-5 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Maintenance</p>
              <p className="text-2xl font-bold text-yellow-600">{maintenanceAssets}</p>
            </div>
            <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <Wrench className="h-5 w-5 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder="Search assets by name, tag, or serial number..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="all">All Status</option>
            <option value="available">Available</option>
            <option value="assigned">Assigned</option>
            <option value="in_use">In Use</option>
            <option value="maintenance">Maintenance</option>
            <option value="retired">Retired</option>
          </select>
        </div>
      </div>

      {/* Assets Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Asset
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Tag / Serial
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Condition
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Assigned To
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredAssets.map((asset) => (
                <tr key={asset.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <div className="text-gray-500">{getAssetTypeIcon(asset.asset_type)}</div>
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {asset.name}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">{asset.asset_tag}</div>
                    <div className="text-xs text-gray-500">{asset.serial_number}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900 dark:text-white capitalize">
                      {asset.asset_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(asset.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getConditionBadge(asset.condition)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {asset.assigned_to_name || 'Unassigned'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {asset.location || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => {
                          setSelectedAssetId(asset.id);
                          setShowDetailModal(true);
                        }}
                        className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                        title="View Details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => {
                          setSelectedAssetId(asset.id);
                          setShowEditModal(true);
                        }}
                        className="p-2 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors"
                        title="Edit"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => {
                          setSelectedAssetId(asset.id);
                          setSelectedAssetName(asset.name);
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

        {filteredAssets.length === 0 && (
          <div className="text-center py-12">
            <Package className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No assets found</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Try adjusting your search or filter criteria
            </p>
          </div>
        )}
      </div>

      {/* CRUD Modals */}
      <AssetDetailModal
        isOpen={showDetailModal}
        onClose={() => setShowDetailModal(false)}
        assetId={selectedAssetId}
        onEdit={(id: number) => {
          setSelectedAssetId(id);
          setShowEditModal(true);
        }}
        onDelete={(id: number) => {
          const asset = assets.find(a => a.id === id);
          setSelectedAssetId(id);
          setSelectedAssetName(asset?.name || '');
          setShowDeleteModal(true);
        }}
      />

      <EditAssetModal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        assetId={selectedAssetId}
        onSuccess={() => {
          fetchAssets();
          setShowEditModal(false);
        }}
      />

      <DeleteAssetModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        assetId={selectedAssetId}
        assetName={selectedAssetName}
        onSuccess={() => {
          fetchAssets();
          setShowDeleteModal(false);
        }}
      />
    </div>
  );
}
