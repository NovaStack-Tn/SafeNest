import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Camera,
  UserPlus,
  Users,
  AlertCircle,
  CheckCircle,
  Clock,
  Eye,
} from 'lucide-react';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Loader } from '@/components/Loader';
import { ImageCapture } from '@/components/ImageCapture';
import api from '@/lib/api';
import toast from 'react-hot-toast';

interface FaceIdentity {
  id: number;
  person_label: string;
  person_meta: any;
  photo: string | null;
  is_active: boolean;
  enrollment_status: 'pending' | 'enrolled' | 'failed';
  created_at: string;
  embeddings_count: number;
}

export const Faces = () => {
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [showDetectModal, setShowDetectModal] = useState(false);
  const [selectedIdentity, setSelectedIdentity] = useState<FaceIdentity | null>(null);
  const queryClient = useQueryClient();

  // Fetch identities
  const { data: identities, isLoading } = useQuery<FaceIdentity[]>({
    queryKey: ['face-identities'],
    queryFn: async () => {
      const response = await api.get('/faces/identities/');
      return response.data.results || response.data;
    },
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['face-stats'],
    queryFn: async () => {
      const response = await api.get('/faces/detections/statistics/');
      return response.data;
    },
  });

  const statCards = [
    {
      icon: Users,
      label: 'Enrolled Faces',
      value: identities?.filter(i => i.enrollment_status === 'enrolled').length || 0,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      icon: CheckCircle,
      label: 'Matched Today',
      value: stats?.matched || 0,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      icon: AlertCircle,
      label: 'Unmatched',
      value: stats?.unmatched || 0,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
    },
    {
      icon: Eye,
      label: 'Total Detections',
      value: stats?.total || 0,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ];

  if (isLoading) return <Loader text="Loading face recognition..." />;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Face Recognition
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage face identities and detections
          </p>
        </div>
        <div className="flex space-x-3">
          <Button
            onClick={() => setShowDetectModal(true)}
            variant="secondary"
          >
            <Camera className="w-4 h-4 mr-2" />
            Detect Faces
          </Button>
          <Button onClick={() => setShowEnrollModal(true)}>
            <UserPlus className="w-4 h-4 mr-2" />
            Enroll New Face
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                    {stat.value}
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Enrolled Identities */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Enrolled Identities
        </h2>

        {!identities || identities.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">
              No face identities enrolled yet
            </p>
            <Button
              onClick={() => setShowEnrollModal(true)}
              className="mt-4"
            >
              <UserPlus className="w-4 h-4 mr-2" />
              Enroll First Face
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {identities.map((identity) => (
              <FaceIdentityCard
                key={identity.id}
                identity={identity}
                onSelect={setSelectedIdentity}
              />
            ))}
          </div>
        )}
      </Card>

      {/* Modals */}
      {showEnrollModal && (
        <EnrollFaceModal
          onClose={() => setShowEnrollModal(false)}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['face-identities'] });
            setShowEnrollModal(false);
          }}
        />
      )}

      {showDetectModal && (
        <DetectFaceModal
          onClose={() => setShowDetectModal(false)}
        />
      )}
    </div>
  );
};

// Face Identity Card Component
const FaceIdentityCard = ({
  identity,
  onSelect,
}: {
  identity: FaceIdentity;
  onSelect: (identity: FaceIdentity) => void;
}) => {
  const statusConfig = {
    enrolled: { icon: CheckCircle, color: 'text-green-600', label: 'Enrolled' },
    pending: { icon: Clock, color: 'text-yellow-600', label: 'Pending' },
    failed: { icon: AlertCircle, color: 'text-red-600', label: 'Failed' },
  };

  const status = statusConfig[identity.enrollment_status];

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => onSelect(identity)}
    >
      <div className="flex items-start space-x-4">
        <div className="w-16 h-16 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
          {identity.photo ? (
            <img
              src={identity.photo}
              alt={identity.person_label}
              className="w-full h-full object-cover"
            />
          ) : (
            <Users className="w-8 h-8 text-gray-400" />
          )}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 dark:text-white">
            {identity.person_label}
          </h3>
          <div className="flex items-center space-x-2 mt-1">
            <status.icon className={`w-4 h-4 ${status.color}`} />
            <span className={`text-sm ${status.color}`}>{status.label}</span>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {identity.embeddings_count || 0} embeddings
          </p>
        </div>
      </div>
    </motion.div>
  );
};

// Enroll Face Modal
const EnrollFaceModal = ({
  onClose,
  onSuccess,
}: {
  onClose: () => void;
  onSuccess: () => void;
}) => {
  const [personLabel, setPersonLabel] = useState('');
  const [capturedImages, setCapturedImages] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!personLabel || capturedImages.length === 0) {
      toast.error('Please provide a name and at least one image');
      return;
    }

    setLoading(true);
    try {
      // Create identity
      const identityResponse = await api.post('/faces/identities/', {
        person_label: personLabel,
        enrollment_status: 'pending',
      });

      // Upload images for enrollment
      const formData = new FormData();
      capturedImages.forEach((file) => {
        formData.append('images', file);
      });

      await api.post(`/faces/identities/${identityResponse.data.id}/enroll/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      toast.success(`Face enrollment started for ${personLabel}!`);
      onSuccess();
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to enroll face');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-2xl w-full my-8 shadow-2xl"
      >
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
          <UserPlus className="w-6 h-6 mr-2 text-primary-600" />
          Enroll New Face
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Name Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Person Name *
            </label>
            <input
              type="text"
              value={personLabel}
              onChange={(e) => setPersonLabel(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              placeholder="e.g., John Doe"
              required
            />
          </div>

          {/* Image Capture Component */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Capture Photos *
            </label>
            <ImageCapture
              onImagesCapture={setCapturedImages}
              maxImages={5}
              mode="multiple"
              guidanceText="Take 3-5 clear photos from different angles. Ensure good lighting and face the camera directly. Remove sunglasses or masks."
            />
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button
              type="button"
              onClick={onClose}
              variant="secondary"
              className="flex-1"
              disabled={loading}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              className="flex-1" 
              loading={loading}
              disabled={!personLabel || capturedImages.length === 0}
            >
              {loading ? 'Enrolling...' : `Enroll ${capturedImages.length} Photo(s)`}
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

// Detect Face Modal
const DetectFaceModal = ({ onClose }: { onClose: () => void }) => {
  const [capturedImages, setCapturedImages] = useState<File[]>([]);
  const [detections, setDetections] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleDetect = async () => {
    if (capturedImages.length === 0) {
      toast.error('Please capture an image first');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('image', capturedImages[0]);

      const response = await api.post('/faces/detections/detect/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setDetections(response.data.detections || []);
      
      if (response.data.count === 0) {
        toast.error('No faces detected in the image');
      } else {
        toast.success(`Detected ${response.data.count} face(s)!`);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to detect faces');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-2xl w-full my-8 shadow-2xl max-h-[90vh] overflow-y-auto"
      >
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
          <Camera className="w-6 h-6 mr-2 text-primary-600" />
          Detect & Recognize Faces
        </h2>

        <div className="space-y-6">
          {/* Image Capture */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Capture or Upload Image
            </label>
            <ImageCapture
              onImagesCapture={setCapturedImages}
              maxImages={1}
              mode="single"
              guidanceText="Upload or take a photo with faces you want to detect. Multiple faces can be detected in one image."
            />
          </div>

          {/* Detection Results */}
          {detections.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-3 bg-gradient-to-br from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-xl p-4 border border-green-200 dark:border-green-800"
            >
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  Detection Results ({detections.length} face{detections.length > 1 ? 's' : ''})
                </h3>
              </div>
              
              <div className="space-y-2">
                {detections.map((det, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 text-xs font-medium rounded">
                            Face {idx + 1}
                          </span>
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            Confidence: {(det.confidence * 100).toFixed(1)}%
                          </span>
                        </div>

                        {det.identity_label ? (
                          <div className="flex items-center space-x-2 mb-2">
                            <CheckCircle className="w-4 h-4 text-green-600" />
                            <span className="font-semibold text-green-700 dark:text-green-400">
                              Matched: {det.identity_label}
                            </span>
                            {det.similarity && (
                              <span className="text-xs text-gray-500">
                                ({(det.similarity * 100).toFixed(1)}% similar)
                              </span>
                            )}
                          </div>
                        ) : (
                          <div className="flex items-center space-x-2 mb-2">
                            <AlertCircle className="w-4 h-4 text-yellow-600" />
                            <span className="text-sm text-yellow-700 dark:text-yellow-400">
                              Unknown Person
                            </span>
                          </div>
                        )}

                        {(det.age || det.gender) && (
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {det.age && `Age: ~${det.age}`}
                            {det.age && det.gender && ' • '}
                            {det.gender && `Gender: ${det.gender === 'M' ? 'Male' : 'Female'}`}
                          </p>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button
              onClick={onClose}
              variant="secondary"
              className="flex-1"
            >
              Close
            </Button>
            <Button
              onClick={handleDetect}
              className="flex-1"
              loading={loading}
              disabled={capturedImages.length === 0 || loading}
            >
              <Camera className="w-4 h-4 mr-2" />
              {loading ? 'Detecting...' : 'Detect Faces'}
            </Button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
