import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Shield,
  AlertTriangle,
  Camera,
  Users,
  MessageSquare,
  Settings,
  LogOut,
  DoorOpen,
  UserPlus,
  Package,
  Target,
  Eye,
  Activity,
  TrendingUp,
  Search,
  Crosshair,
  Database,
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useNavigate } from 'react-router-dom';
import logo from '@/assets/logo.png';

interface NavSection {
  title: string;
  items: NavItem[];
}

interface NavItem {
  icon: any;
  label: string;
  path: string;
}

const navSections: NavSection[] = [
  {
    title: 'Overview',
    items: [
      { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
      { icon: AlertTriangle, label: 'Alerts', path: '/alerts' },
    ],
  },
  {
    title: '🚪 Access Control',
    items: [
      { icon: DoorOpen, label: 'Access Points', path: '/access-points' },
      { icon: Users, label: 'Login Events', path: '/login-events' },
    ],
  },
  {
    title: '📹 Surveillance',
    items: [
      { icon: Camera, label: 'Cameras', path: '/cameras' },
      { icon: Eye, label: 'Face Recognition', path: '/faces' },
    ],
  },
  {
    title: '🚨 Incident Management',
    items: [
      { icon: Shield, label: 'Incidents', path: '/incidents' },
    ],
  },
  {
    title: '🛡️ Threat Intelligence',
    items: [
      { icon: Target, label: 'Threats', path: '/threats' },
      { icon: Activity, label: 'Alerts Intel', path: '/alerts-intel' },
      { icon: TrendingUp, label: 'Risk Assessments', path: '/risk-assessments' },
      { icon: Crosshair, label: 'Threat Indicators', path: '/threat-indicators' },
      { icon: Database, label: 'Watchlist', path: '/watchlist' },
      { icon: Search, label: 'Threat Hunting', path: '/threat-hunting' },
    ],
  },
  {
    title: '👥 Visitors & Assets',
    items: [
      { icon: UserPlus, label: 'Visitors', path: '/visitors' },
      { icon: Package, label: 'Assets', path: '/assets' },
    ],
  },
  {
    title: 'AI & Tools',
    items: [
      { icon: MessageSquare, label: 'AI Chat', path: '/chat' },
      { icon: Settings, label: 'Settings', path: '/settings' },
    ],
  },
];

export const Sidebar = () => {
  const logout = useAuthStore((state) => state.logout);
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <img src={logo} alt="SafeNest Logo" className="w-10 h-10 object-contain" />
          <span className="text-xl font-bold text-gray-900 dark:text-white">SafeNest</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-4 overflow-y-auto">
        {navSections.map((section, idx) => (
          <div key={idx}>
            <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
              {section.title}
            </h3>
            <div className="space-y-1">
              {section.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-colors duration-200 ${
                      isActive
                        ? 'bg-primary-50 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`
                  }
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium text-sm">{item.label}</span>
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* User Profile & Logout */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-3 px-2">
          <div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {user?.first_name} {user?.last_name}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">{user?.role}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center space-x-2 w-full px-4 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900 rounded-lg transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </div>
  );
};
