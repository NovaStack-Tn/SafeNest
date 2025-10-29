import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './store/authStore';
import { useThemeStore } from './store/themeStore';
import { useEffect } from 'react';

// Layouts
import { DashboardLayout } from './layouts/DashboardLayout';

// Pages
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Alerts } from './pages/Alerts';
import { Incidents } from './pages/Incidents';
import { Faces } from './pages/Faces';
import { AccessPoints } from './pages/AccessPoints';
import { LoginEvents } from './pages/LoginEvents';
import { Cameras } from './pages/Cameras';
import { CameraHistory } from './pages/CameraHistory';
import { Visitors } from './pages/Visitors';
import { Assets } from './pages/Assets';
import { ThreatIntel } from './pages/ThreatIntel';
import { Chat } from './pages/Chat';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public Route Component (redirect to dashboard if already logged in)
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

function App() {
  const { isDark, setTheme } = useThemeStore();

  // Initialize theme on mount
  useEffect(() => {
    setTheme(isDark);
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            }
          />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="alerts" element={<Alerts />} />
            
            {/* Access Control */}
            <Route path="access-points" element={<AccessPoints />} />
            <Route path="login-events" element={<LoginEvents />} />
            
            {/* Surveillance */}
            <Route path="cameras" element={<Cameras />} />
            <Route path="camera-history" element={<CameraHistory />} />
            <Route path="faces" element={<Faces />} />
            
            {/* Incident Management */}
            <Route path="incidents" element={<Incidents />} />
            
            {/* Threat Intelligence */}
            <Route path="threat-intel" element={<ThreatIntel />} />
            
            {/* Visitors & Assets */}
            <Route path="visitors" element={<Visitors />} />
            <Route path="assets" element={<Assets />} />
            
            {/* AI & Tools */}
            <Route path="chat" element={<Chat />} />
            <Route path="settings" element={<ComingSoon title="Settings" />} />
          </Route>

          {/* 404 Route */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>

        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: isDark ? '#1f2937' : '#ffffff',
              color: isDark ? '#f3f4f6' : '#111827',
              border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#ffffff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#ffffff',
              },
            },
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

// Temporary Coming Soon Component
const ComingSoon = ({ title }: { title: string }) => {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          {title}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          This feature is coming soon...
        </p>
      </div>
    </div>
  );
};

export default App;
