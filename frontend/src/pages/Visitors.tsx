import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { UserPlus, Users, Clock, CheckCircle } from 'lucide-react';

export const Visitors = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Visitor Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Track visitors, contractors, and temporary access
          </p>
        </div>
        <Button>
          <UserPlus className="w-4 h-4 mr-2" />
          Register Visitor
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Today's Visitors</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">23</p>
            </div>
            <Users className="w-12 h-12 text-primary-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Checked In</p>
              <p className="text-3xl font-bold text-green-600 mt-2">18</p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Checked Out</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">5</p>
            </div>
            <Clock className="w-12 h-12 text-blue-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Pre-Registered</p>
              <p className="text-3xl font-bold text-purple-600 mt-2">12</p>
            </div>
            <UserPlus className="w-12 h-12 text-purple-600" />
          </div>
        </Card>
      </div>

      <Card className="p-12">
        <div className="text-center">
          <Users className="w-20 h-20 text-gray-400 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            Visitor & Asset Management
          </h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Complete visitor management system with check-in/out, badges, and asset tracking coming soon.
          </p>
        </div>
      </Card>
    </div>
  );
};
