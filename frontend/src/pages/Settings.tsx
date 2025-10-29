import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { User, Lock, Bell, Shield, Moon, Sun } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore } from '@/store/themeStore';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  department: string;
  employee_id: string;
  two_factor_enabled: boolean;
  organization_name: string;
  role_name: string;
}

interface ProfileFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  department: string;
}

interface PasswordFormData {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

export const Settings = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const { setUser } = useAuthStore();
  const { isDark, toggleTheme } = useThemeStore();
  const queryClient = useQueryClient();
  const token = localStorage.getItem('access_token');

  // Fetch user profile
  const { data: profile, isLoading } = useQuery<UserProfile>({
    queryKey: ['user-profile'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/users/me/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    },
  });

  // Profile form state
  const [profileForm, setProfileForm] = useState<ProfileFormData>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    department: '',
  });

  // Password form state
  const [passwordForm, setPasswordForm] = useState<PasswordFormData>({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });

  // Initialize profile form when data loads
  useEffect(() => {
    if (profile) {
      setProfileForm({
        first_name: profile.first_name || '',
        last_name: profile.last_name || '',
        email: profile.email || '',
        phone: profile.phone || '',
        department: profile.department || '',
      });
    }
  }, [profile]);

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: async (data: ProfileFormData) => {
      const response = await axios.patch(`${API_URL}/users/me/`, data, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    },
    onSuccess: (data) => {
      toast.success('Profile updated successfully');
      queryClient.invalidateQueries({ queryKey: ['user-profile'] });
      setUser(data);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update profile');
    },
  });

  // Change password mutation
  const changePasswordMutation = useMutation({
    mutationFn: async (data: { old_password: string; new_password: string }) => {
      const response = await axios.post(`${API_URL}/users/change-password/`, data, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Password changed successfully');
      setPasswordForm({
        old_password: '',
        new_password: '',
        confirm_password: '',
      });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to change password');
    },
  });

  // Toggle 2FA mutation
  const toggle2FAMutation = useMutation({
    mutationFn: async (enabled: boolean) => {
      const response = await axios.patch(
        `${API_URL}/users/me/`,
        { two_factor_enabled: enabled },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    },
    onSuccess: (data) => {
      toast.success(`Two-factor authentication ${data.two_factor_enabled ? 'enabled' : 'disabled'}`);
      queryClient.invalidateQueries({ queryKey: ['user-profile'] });
    },
    onError: () => {
      toast.error('Failed to update 2FA settings');
    },
  });

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfileMutation.mutate(profileForm);
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('New passwords do not match');
      return;
    }

    if (passwordForm.new_password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    changePasswordMutation.mutate({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    });
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'appearance', label: 'Appearance', icon: isDark ? Moon : Sun },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-600 dark:text-gray-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar Tabs */}
        <div className="w-64 flex-shrink-0">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary-50 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-6">
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                  Profile Information
                </h2>
                
                {/* Read-only info */}
                <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Username</p>
                      <p className="font-medium text-gray-900 dark:text-white">{profile?.username}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Employee ID</p>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {profile?.employee_id || 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Organization</p>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {profile?.organization_name}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Role</p>
                      <p className="font-medium text-gray-900 dark:text-white capitalize">
                        {profile?.role_name?.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                </div>

                <form onSubmit={handleProfileSubmit} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        First Name
                      </label>
                      <input
                        type="text"
                        value={profileForm.first_name}
                        onChange={(e) =>
                          setProfileForm({ ...profileForm, first_name: e.target.value })
                        }
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Last Name
                      </label>
                      <input
                        type="text"
                        value={profileForm.last_name}
                        onChange={(e) =>
                          setProfileForm({ ...profileForm, last_name: e.target.value })
                        }
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={profileForm.email}
                      onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Phone
                    </label>
                    <input
                      type="tel"
                      value={profileForm.phone}
                      onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Department
                    </label>
                    <input
                      type="text"
                      value={profileForm.department}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, department: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>

                  <div className="flex justify-end pt-4">
                    <button
                      type="submit"
                      disabled={updateProfileMutation.isPending}
                      className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {updateProfileMutation.isPending ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Security</h2>

                {/* Change Password */}
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                    <Lock className="w-5 h-5 mr-2" />
                    Change Password
                  </h3>
                  <form onSubmit={handlePasswordSubmit} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Current Password
                      </label>
                      <input
                        type="password"
                        value={passwordForm.old_password}
                        onChange={(e) =>
                          setPasswordForm({ ...passwordForm, old_password: e.target.value })
                        }
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        New Password
                      </label>
                      <input
                        type="password"
                        value={passwordForm.new_password}
                        onChange={(e) =>
                          setPasswordForm({ ...passwordForm, new_password: e.target.value })
                        }
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        required
                      />
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Must be at least 8 characters
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Confirm New Password
                      </label>
                      <input
                        type="password"
                        value={passwordForm.confirm_password}
                        onChange={(e) =>
                          setPasswordForm({ ...passwordForm, confirm_password: e.target.value })
                        }
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        required
                      />
                    </div>
                    <div className="flex justify-end pt-4">
                      <button
                        type="submit"
                        disabled={changePasswordMutation.isPending}
                        className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {changePasswordMutation.isPending ? 'Changing...' : 'Change Password'}
                      </button>
                    </div>
                  </form>
                </div>

                {/* Two-Factor Authentication */}
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                    <Shield className="w-5 h-5 mr-2" />
                    Two-Factor Authentication
                  </h3>
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        Two-Factor Authentication
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Add an extra layer of security to your account
                      </p>
                    </div>
                    <button
                      onClick={() => toggle2FAMutation.mutate(!profile?.two_factor_enabled)}
                      disabled={toggle2FAMutation.isPending}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        profile?.two_factor_enabled ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'
                      } disabled:opacity-50`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          profile?.two_factor_enabled ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                  Notification Preferences
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Manage how you receive notifications about security events and updates.
                </p>
                <div className="space-y-4">
                  {[
                    { label: 'Security Alerts', description: 'Get notified about security incidents and threats' },
                    { label: 'System Updates', description: 'Receive updates about system maintenance and new features' },
                    { label: 'Face Recognition', description: 'Notifications when unknown faces are detected' },
                    { label: 'Access Control', description: 'Alerts for unauthorized access attempts' },
                  ].map((item, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{item.label}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{item.description}</p>
                      </div>
                      <button
                        className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary-600"
                      >
                        <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Appearance Tab */}
            {activeTab === 'appearance' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                  Appearance
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Customize how SafeNest looks on your device.
                </p>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center">
                      {isDark ? (
                        <Moon className="w-5 h-5 mr-3 text-gray-900 dark:text-white" />
                      ) : (
                        <Sun className="w-5 h-5 mr-3 text-gray-900 dark:text-white" />
                      )}
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Dark Mode</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {isDark ? 'Dark mode is enabled' : 'Light mode is enabled'}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={toggleTheme}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        isDark ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          isDark ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
