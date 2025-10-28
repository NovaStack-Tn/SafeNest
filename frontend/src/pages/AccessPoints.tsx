import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { DoorOpen, Plus, MapPin, Clock } from 'lucide-react';

export const AccessPoints = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Access Points
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage doors, gates, turnstiles, and entry points
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add Access Point
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Points</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">24</p>
            </div>
            <DoorOpen className="w-12 h-12 text-primary-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active</p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">22</p>
            </div>
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Locked</p>
              <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-2">2</p>
            </div>
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Today's Access</p>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">847</p>
            </div>
            <Clock className="w-12 h-12 text-blue-600" />
          </div>
        </Card>
      </div>

      {/* Coming Soon Content */}
      <Card className="p-12">
        <div className="text-center">
          <DoorOpen className="w-20 h-20 text-gray-400 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            Access Points Management
          </h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-6">
            Full CRUD interface for managing physical access points is coming soon. Features will include:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto text-left">
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <MapPin className="w-5 h-5 text-primary-600 mb-2" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Location Management</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Map-based access point configuration</p>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Clock className="w-5 h-5 text-primary-600 mb-2" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Schedule Rules</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Time-based access control</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
