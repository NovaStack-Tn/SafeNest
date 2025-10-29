import { useState } from 'react';
import { Users, Package, Activity, UserPlus, Sparkles } from 'lucide-react';
import AIPreRegistrationModal from './AIPreRegistrationModal';
import CreateVisitorModal from './CreateVisitorModal';
import CreateAssetModal from './CreateAssetModal';
import VisitorsList from './VisitorsList';
import AssetsList from './AssetsList';

interface TabProps {
  active: string;
  onChange: (tab: string) => void;
}

const Tabs = ({ active, onChange }: TabProps) => {
  const tabs = [
    { id: 'visitors', label: 'Visitors', icon: Users },
    { id: 'assets', label: 'Assets', icon: Package },
    { id: 'movements', label: 'Movements', icon: Activity },
  ];

  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <nav className="flex space-x-8" aria-label="Tabs">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => onChange(tab.id)}
              className={`
                flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${
                  active === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }
              `}
            >
              <Icon className="h-5 w-5" />
              {tab.label}
            </button>
          );
        })}
      </nav>
    </div>
  );
};

export default function VisitorsAssets() {
  const [activeTab, setActiveTab] = useState('visitors');
  const [showAIModal, setShowAIModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showCreateAssetModal, setShowCreateAssetModal] = useState(false);
  const [prefilledData, setPrefilledData] = useState<any>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleAISuccess = (extractedData: any) => {
    setPrefilledData({
      ...extractedData,
      ai_extracted: true,
    });
    setShowAIModal(false);
    setShowCreateModal(true);
  };

  const handleCreateSuccess = () => {
    setRefreshKey(prev => prev + 1);
    setShowCreateModal(false);
    setPrefilledData(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Users className="h-8 w-8" />
            👥 Visitors & Assets
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage visitors, contractors, assets, and inventory with AI-powered features
          </p>
        </div>
        
        <div className="flex gap-3">
          {activeTab === 'visitors' && (
            <>
              <button
                onClick={() => setShowAIModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg"
              >
                <Sparkles className="h-5 w-5" />
                AI Pre-Register
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <UserPlus className="h-5 w-5" />
                Add Visitor
              </button>
            </>
          )}
          {activeTab === 'assets' && (
            <button
              onClick={() => {
                console.log('🔵 Button clicked! Opening modal...');
                console.log('Current showCreateAssetModal:', showCreateAssetModal);
                setShowCreateAssetModal(true);
                console.log('After setState - should be true');
              }}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Package className="h-5 w-5" />
              Add Asset
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs active={activeTab} onChange={setActiveTab} />

      {/* Tab Content */}
      {activeTab === 'visitors' && <VisitorsList key={refreshKey} />}
      
      {activeTab === 'assets' && <AssetsList key={refreshKey} />}
      
      {activeTab === 'movements' && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Movements Content</h2>
          <p className="text-gray-500">Movement logs will be displayed here</p>
        </div>
      )}

      {/* AI Pre-Registration Modal */}
      <AIPreRegistrationModal
        isOpen={showAIModal}
        onClose={() => setShowAIModal(false)}
        onSuccess={handleAISuccess}
      />

      {/* Create Visitor Modal */}
      <CreateVisitorModal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setPrefilledData(null);
        }}
        onSuccess={handleCreateSuccess}
        prefilledData={prefilledData}
      />

      {/* Create Asset Modal */}
      <CreateAssetModal
        isOpen={showCreateAssetModal}
        onClose={() => setShowCreateAssetModal(false)}
        onSuccess={() => {
          setRefreshKey(prev => prev + 1);
          setShowCreateAssetModal(false);
        }}
      />
    </div>
  );
}
