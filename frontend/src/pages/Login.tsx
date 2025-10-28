import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, Loader2 } from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Card } from '@/components/Card';
import api from '@/lib/api';
import { useAuthStore } from '@/store/authStore';
import toast from 'react-hot-toast';

export const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setUser = useAuthStore((state) => state.setUser);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Step 1: Get JWT tokens
      const tokenResponse = await api.post('/auth/token/', {
        username,
        password,
      });

      const { access, refresh } = tokenResponse.data;

      // Store tokens immediately
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);

      // Step 2: Fetch user data with the token
      const userResponse = await api.get('/users/me/');
      const user = userResponse.data;

      // Set user in auth store
      setUser(user);

      toast.success(`Welcome back, ${user.first_name || user.username}!`);
      
      // Navigate to dashboard
      navigate('/dashboard');
    } catch (error: any) {
      // Clear tokens on error
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      const errorMessage = error.response?.data?.detail 
        || error.response?.data?.message 
        || 'Login failed. Please check your credentials.';
      
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card className="p-8">
          {/* Logo & Title */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900 mb-4">
              <Shield className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">SafeNest</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Smart Access & Incident Management
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              autoComplete="username"
            />

            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              autoComplete="current-password"
            />

            <Button
              type="submit"
              className="w-full"
              disabled={loading}
              loading={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              <strong>Demo Credentials:</strong>
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500">
              Username: <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">admin</code>
              <br />
              Password: <code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">admin123</code>
            </p>
          </div>
        </Card>

        {/* Footer */}
        <p className="text-center mt-6 text-sm text-gray-600 dark:text-gray-400">
          © 2025 SafeNest. All rights reserved.
        </p>
      </motion.div>
    </div>
  );
};
