import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Loader } from '@/components/Loader';
import { CreateThreatModal } from '@/components/CreateThreatModal';
import { ThreatDetailModal } from '@/components/ThreatDetailModal';
import { CreateAlertModal } from '@/components/CreateAlertModal';
import { CreateRiskAssessmentModal } from '@/components/CreateRiskAssessmentModal';
import { 
  Plus, AlertTriangle, Target, 
  Bell, Trash2, Edit, Search 
} from 'lucide-react';
import api from '@/lib/api';
import toast from 'react-hot-toast';

type TabType = 'threats' | 'alerts' | 'assessments';

export const ThreatIntel = () => {
  const [activeTab, setActiveTab] = useState<TabType>('threats');

  // Fetch statistics with auto-refetch for dynamic updates
  const { data: threatStats } = useQuery({
    queryKey: ['threat-stats'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/threats/statistics/');
      return response.data;
    },
    refetchInterval: 30000, // Auto-refetch every 30 seconds
    refetchOnWindowFocus: true, // Refetch when user returns to tab
  });

  const { data: alertStats } = useQuery({
    queryKey: ['alert-stats'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/alerts/statistics/');
      return response.data;
    },
    refetchInterval: 30000, // Auto-refetch every 30 seconds
    refetchOnWindowFocus: true, // Refetch when user returns to tab
  });

  const tabs = [
    { id: 'threats' as TabType, label: 'Threats', icon: AlertTriangle, count: threatStats?.total || 0 },
    { id: 'alerts' as TabType, label: 'Alerts', icon: Bell, count: alertStats?.total || 0 },
    { id: 'assessments' as TabType, label: 'Risk Assessments', icon: Target },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            🛡️ Threat Intelligence
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Analyze threats, manage alerts, and assess risks
          </p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Threats</p>
              <p className="text-3xl font-bold text-red-600 mt-2">
                {threatStats?.total || 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {threatStats?.new_count || 0} new
              </p>
            </div>
            <AlertTriangle className="w-12 h-12 text-red-600" />
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Critical Alerts</p>
              <p className="text-3xl font-bold text-orange-600 mt-2">
                {alertStats?.by_severity?.critical || 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {alertStats?.unresolved_count || 0} unresolved
              </p>
            </div>
            <Bell className="w-12 h-12 text-orange-600" />
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2
                  transition-colors duration-200
                  ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
                {tab.count !== undefined && (
                  <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 dark:bg-gray-700">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'threats' && <ThreatsTab />}
        {activeTab === 'alerts' && <AlertsTab />}
        {activeTab === 'assessments' && <RiskAssessmentsTab />}
      </div>
    </div>
  );
};

// Threats Tab
const ThreatsTab = () => {
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingThreat, setEditingThreat] = useState<any>(null);
  const [selectedThreat, setSelectedThreat] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/threat-intelligence/threats/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['threats'] });
      queryClient.invalidateQueries({ queryKey: ['threat-stats'] });
      toast.success('Threat deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete threat');
    },
  });

  const { data: threats, isLoading } = useQuery({
    queryKey: ['threats'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/threats/');
      return response.data.results || response.data;
    },
  });

  if (isLoading) return <Loader />;

  if (!threats || threats.length === 0) {
    return (
      <>
        <div className="text-center py-12">
          <AlertTriangle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Threats Found</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">Start tracking security threats and risks</p>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add First Threat
          </Button>
        </div>
        
        <CreateThreatModal 
          isOpen={isCreateModalOpen || !!editingThreat} 
          onClose={() => {
            setIsCreateModalOpen(false);
            setEditingThreat(null);
          }} 
          threat={editingThreat}
        />
        <ThreatDetailModal isOpen={!!selectedThreat} onClose={() => setSelectedThreat(null)} threat={selectedThreat} />
      </>
    );
  }

  // Filter threats based on search term
  const filteredThreats = threats?.filter((threat: any) => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      threat.title?.toLowerCase().includes(search) ||
      threat.description?.toLowerCase().includes(search) ||
      threat.threat_type?.toLowerCase().includes(search) ||
      threat.severity?.toLowerCase().includes(search) ||
      threat.status?.toLowerCase().includes(search) ||
      threat.source?.toLowerCase().includes(search)
    );
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center gap-4">
        <h2 className="text-xl font-semibold">Security Threats</h2>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Threat
        </Button>
      </div>
      
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Search threats by title, description, type, severity, status, or source..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {searchTerm && (
          <button
            onClick={() => setSearchTerm('')}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            ✕
          </button>
        )}
      </div>
      
      {/* Results count */}
      {searchTerm && (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {filteredThreats?.length || 0} result{filteredThreats?.length !== 1 ? 's' : ''} found
        </p>
      )}
      
      {/* No results message */}
      {searchTerm && filteredThreats?.length === 0 && (
        <div className="text-center py-12">
          <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Threats Found</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            No threats match your search "{searchTerm}"
          </p>
          <Button variant="ghost" onClick={() => setSearchTerm('')}>
            Clear Search
          </Button>
        </div>
      )}
      
      {/* Threats Grid */}
      {(!searchTerm || filteredThreats?.length > 0) && (
      <div className="grid gap-4">
        {filteredThreats?.map((threat: any) => (
          <Card key={threat.id} className="p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {threat.title}
                  </h3>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    threat.severity === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                    threat.severity === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                    threat.severity === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                  }`}>
                    {threat.severity}
                  </span>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    threat.status === 'new' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                    threat.status === 'investigating' ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' :
                    threat.status === 'confirmed' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                    'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  }`}>
                    {threat.status}
                  </span>
                  {threat.alert_count !== undefined && threat.alert_count > 0 && (
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200 flex items-center gap-1">
                      <Bell className="w-3 h-3" />
                      {threat.alert_count} alert{threat.alert_count > 1 ? 's' : ''}
                    </span>
                  )}
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                  {threat.description}
                </p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Type: {threat.threat_type}</span>
                  {threat.source && <span>Source: {threat.source}</span>}
                  <span>{new Date(threat.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={() => setSelectedThreat(threat)}>
                  View Details
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setEditingThreat(threat)}>
                  <Edit className="w-4 h-4" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => {
                    if (confirm('Are you sure you want to delete this threat?')) {
                      deleteMutation.mutate(threat.id);
                    }
                  }}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
      )}
      
      <CreateThreatModal 
        isOpen={isCreateModalOpen || !!editingThreat} 
        onClose={() => {
          setIsCreateModalOpen(false);
          setEditingThreat(null);
        }} 
        threat={editingThreat}
      />
      <ThreatDetailModal isOpen={!!selectedThreat} onClose={() => setSelectedThreat(null)} threat={selectedThreat} />
    </div>
  );
};

// Alerts Tab
const AlertsTab = () => {
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingAlert, setEditingAlert] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const acknowledgeMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await api.post(`/threat-intelligence/alerts/${id}/acknowledge/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alert acknowledged');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/threat-intelligence/alerts/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alert-stats'] });
      toast.success('Alert deleted');
    },
  });

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/alerts/');
      return response.data.results || response.data;
    },
  });

  if (isLoading) return <Loader />;

  if (!alerts || alerts.length === 0) {
    return (
      <>
        <div className="text-center py-12">
          <Bell className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Alerts Found</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">Security alerts will appear here</p>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Create First Alert
          </Button>
        </div>
        
        <CreateAlertModal 
          isOpen={isCreateModalOpen || !!editingAlert} 
          onClose={() => {
            setIsCreateModalOpen(false);
            setEditingAlert(null);
          }} 
          alert={editingAlert}
        />
      </>
    );
  }

  // Filter alerts based on search term
  const filteredAlerts = alerts?.filter((alert: any) => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      alert.title?.toLowerCase().includes(search) ||
      alert.description?.toLowerCase().includes(search) ||
      alert.alert_type?.toLowerCase().includes(search) ||
      alert.severity?.toLowerCase().includes(search) ||
      alert.status?.toLowerCase().includes(search) ||
      alert.source?.toLowerCase().includes(search)
    );
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center gap-4">
        <h2 className="text-xl font-semibold">Security Alerts</h2>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Alert
        </Button>
      </div>
      
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Search alerts by title, description, type, severity, status, or source..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {searchTerm && (
          <button
            onClick={() => setSearchTerm('')}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            ✕
          </button>
        )}
      </div>
      
      {/* Results count */}
      {searchTerm && (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {filteredAlerts?.length || 0} result{filteredAlerts?.length !== 1 ? 's' : ''} found
        </p>
      )}
      
      {/* No results message */}
      {searchTerm && filteredAlerts?.length === 0 && (
        <div className="text-center py-12">
          <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Alerts Found</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            No alerts match your search "{searchTerm}"
          </p>
          <Button variant="ghost" onClick={() => setSearchTerm('')}>
            Clear Search
          </Button>
        </div>
      )}
      
      {/* Alerts Grid */}
      {(!searchTerm || filteredAlerts?.length > 0) && (
      <div className="grid gap-4">
        {filteredAlerts?.map((alert: any) => (
          <Card key={alert.id} className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Bell className="w-5 h-5 text-orange-500" />
                  <h3 className="text-lg font-semibold">{alert.title}</h3>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                    alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {alert.severity}
                  </span>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">
                  {alert.description}
                </p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Type: {alert.alert_type}</span>
                  <span>Status: {alert.status}</span>
                  <span>{new Date(alert.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <div className="flex gap-2">
                {alert.status === 'new' && (
                  <Button variant="ghost" size="sm" onClick={() => acknowledgeMutation.mutate(alert.id)}>
                    Acknowledge
                  </Button>
                )}
                <Button variant="ghost" size="sm" onClick={() => setEditingAlert(alert)}>
                  <Edit className="w-4 h-4" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => {
                    if (confirm('Delete this alert?')) {
                      deleteMutation.mutate(alert.id);
                    }
                  }}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
      )}
      
      <CreateAlertModal 
        isOpen={isCreateModalOpen || !!editingAlert} 
        onClose={() => {
          setIsCreateModalOpen(false);
          setEditingAlert(null);
        }} 
        alert={editingAlert}
      />
    </div>
  );
};

// Risk Assessments Tab
const RiskAssessmentsTab = () => {
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedAssessment, setSelectedAssessment] = useState<any>(null);
  
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/threat-intelligence/risk-assessments/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risk-assessments'] });
      toast.success('Risk assessment deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete risk assessment');
    },
  });

  const { data: assessments, isLoading } = useQuery({
    queryKey: ['risk-assessments'],
    queryFn: async () => {
      const response = await api.get('/threat-intelligence/risk-assessments/');
      return response.data.results || response.data;
    },
  });

  if (isLoading) return <Loader />;

  if (!assessments || assessments.length === 0) {
    return (
      <>
        <div className="text-center py-12">
          <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Risk Assessments</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">Create assessments to analyze threat impact and likelihood</p>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Create First Assessment
          </Button>
        </div>
        <CreateRiskAssessmentModal 
          isOpen={isCreateModalOpen} 
          onClose={() => setIsCreateModalOpen(false)} 
        />
      </>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Risk Assessments</h2>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Assessment
        </Button>
      </div>
      <div className="grid gap-4">
        {assessments?.map((assessment: any) => (
          <Card key={assessment.id} className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-semibold mb-2">{assessment.threat_details?.title}</h3>
                <div className="flex gap-2 mb-3">
                  <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                    Risk: {assessment.risk_level}
                  </span>
                  <span className="px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">
                    Likelihood: {assessment.likelihood}
                  </span>
                  <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                    Impact: {assessment.impact}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{assessment.vulnerability_analysis}</p>
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={() => setSelectedAssessment(assessment)}>
                  <Edit className="w-4 h-4" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => {
                    if (confirm('Delete this risk assessment?')) {
                      deleteMutation.mutate(assessment.id);
                    }
                  }}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
      <CreateRiskAssessmentModal 
        isOpen={isCreateModalOpen || !!selectedAssessment} 
        onClose={() => {
          setIsCreateModalOpen(false);
          setSelectedAssessment(null);
        }}
        assessment={selectedAssessment}
      />
    </div>
  );
};
