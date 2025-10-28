import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Camera, Plus, Video, Eye, AlertCircle } from 'lucide-react';

export const Cameras = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Camera Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Monitor and manage IP/RTSP cameras for surveillance
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add Camera
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Cameras</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">12</p>
            </div>
            <Camera className="w-12 h-12 text-primary-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Online</p>
              <p className="text-3xl font-bold text-green-600 mt-2">10</p>
            </div>
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Recording</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">8</p>
            </div>
            <Video className="w-12 h-12 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Alerts Today</p>
              <p className="text-3xl font-bold text-red-600 mt-2">3</p>
            </div>
            <AlertCircle className="w-12 h-12 text-red-600" />
          </div>
        </Card>
      </div>

      {/* Coming Soon */}
      <Card className="p-12">
        <div className="text-center">
          <Eye className="w-20 h-20 text-gray-400 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            Camera Surveillance System
          </h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-6">
            Advanced camera management with live streaming, recording, and AI-powered analytics coming soon.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto text-left">
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Video className="w-5 h-5 text-primary-600 mb-2" />
              <h3 className="font-semibold mb-1">Live Streaming</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Real-time multi-camera wall</p>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Eye className="w-5 h-5 text-primary-600 mb-2" />
              <h3 className="font-semibold mb-1">AI Detection</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Behavior & object analysis</p>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <AlertCircle className="w-5 h-5 text-primary-600 mb-2" />
              <h3 className="font-semibold mb-1">Smart Alerts</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Motion & perimeter breach</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
