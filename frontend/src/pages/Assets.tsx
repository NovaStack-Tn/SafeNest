import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Package, Plus, TrendingUp, MapPin } from 'lucide-react';

export const Assets = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Asset Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Track equipment, devices, vehicles, and inventory
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add Asset
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Assets</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">358</p>
            </div>
            <Package className="w-12 h-12 text-primary-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Assigned</p>
              <p className="text-3xl font-bold text-green-600 mt-2">312</p>
            </div>
            <TrendingUp className="w-12 h-12 text-green-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Available</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">46</p>
            </div>
            <Package className="w-12 h-12 text-blue-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">In Maintenance</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">8</p>
            </div>
            <MapPin className="w-12 h-12 text-yellow-600" />
          </div>
        </Card>
      </div>

      <Card className="p-12">
        <div className="text-center">
          <Package className="w-20 h-20 text-gray-400 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            Asset Tracking System
          </h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-6">
            Comprehensive asset lifecycle management with AI-powered predictive maintenance coming soon.
          </p>
        </div>
      </Card>
    </div>
  );
};
