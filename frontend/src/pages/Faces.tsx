import { useState, useRef, useEffect } from 'react';
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
  ArrowRight,
  Upload,
  X,
} from 'lucide-react';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Loader } from '@/components/Loader';
import { CameraWizard } from '@/components/CameraWizard';
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
                onSelect={() => {}}
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

// Enroll Face Modal - Wizard Style
const EnrollFaceModal = ({
  onClose,
  onSuccess,
}: {
  onClose: () => void;
  onSuccess: () => void;
}) => {
  const [step, setStep] = useState<'name' | 'camera'>('name');
  const [personLabel, setPersonLabel] = useState('');

  const handleNameSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!personLabel.trim()) {
      toast.error('Please enter a person name');
      return;
    }
    setStep('camera');
  };

  const handleCameraComplete = async (images: File[]) => {
    try {
      // Create identity
      const identityResponse = await api.post('/faces/identities/', {
        person_label: personLabel,
        enrollment_status: 'pending',
      });

      // Upload images for enrollment
      const formData = new FormData();
      images.forEach((file) => {
        formData.append('images', file);
      });

      await api.post(`/faces/identities/${identityResponse.data.id}/enroll/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      toast.success(`✅ Face enrollment started for ${personLabel}!`);
      onSuccess();
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to enroll face');
      setStep('name'); // Go back to name step on error
    }
  };

  const handleCameraCancel = () => {
    setStep('name');
  };

  if (step === 'camera') {
    return (
      <CameraWizard
        personName={personLabel}
        onComplete={handleCameraComplete}
        onCancel={handleCameraCancel}
      />
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-md w-full shadow-2xl"
      >
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <UserPlus className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Enroll New Face
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Let's start by entering the person's name
          </p>
        </div>

        <form onSubmit={handleNameSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              Person's Full Name
            </label>
            <input
              type="text"
              value={personLabel}
              onChange={(e) => setPersonLabel(e.target.value)}
              className="w-full px-4 py-4 text-lg border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all"
              placeholder="e.g., John Doe"
              autoFocus
              required
            />
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              This name will be used to identify the person
            </p>
          </div>

          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
            <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2 flex items-center">
              <Camera className="w-4 h-4 mr-2" />
              Next Step: Photo Capture
            </h3>
            <p className="text-sm text-blue-700 dark:text-blue-300">
              After entering the name, you'll be guided through capturing 3 photos:
            </p>
            <ul className="text-sm text-blue-700 dark:text-blue-300 mt-2 space-y-1 ml-4">
              <li>• Face forward (straight)</li>
              <li>• Turn left (45 degrees)</li>
              <li>• Turn right (45 degrees)</li>
            </ul>
          </div>

          <div className="flex space-x-3 pt-4">
            <Button
              type="button"
              onClick={onClose}
              variant="secondary"
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              Continue
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

// Detect Face Modal
const DetectFaceModal = ({ onClose }: { onClose: () => void }) => {
  const [mode, setMode] = useState<'upload' | 'camera'>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [detections, setDetections] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Cleanup camera on unmount or when closing modal
  useEffect(() => {
    return () => {
      if (stream) {
        console.log('Cleaning up camera stream');
        stream.getTracks().forEach(track => {
          track.stop();
          console.log('Stopped track:', track.kind);
        });
      }
    };
  }, [stream]);

  // Stop camera when modal closes
  const handleClose = () => {
    stopCamera();
    onClose();
  };

  const startCamera = async () => {
    try {
      console.log('Requesting camera access...');
      
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'user',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false,
      });
      
      console.log('Camera access granted, stream:', mediaStream);
      console.log('Stream tracks:', mediaStream.getTracks());
      
      setStream(mediaStream);
      
      // Use setTimeout to ensure video element is rendered
      setTimeout(() => {
        if (videoRef.current) {
          console.log('Setting video srcObject');
          videoRef.current.srcObject = mediaStream;
          
          // Try to play immediately
          videoRef.current.play()
            .then(() => {
              console.log('Video playing successfully');
              setIsCameraActive(true);
            })
            .catch(err => {
              console.error('Video play error:', err);
              // Try with loadedmetadata event
              videoRef.current!.onloadedmetadata = () => {
                console.log('Video metadata loaded, trying play again');
                videoRef.current?.play()
                  .then(() => {
                    console.log('Video playing after metadata load');
                    setIsCameraActive(true);
                  })
                  .catch(e => {
                    console.error('Second play attempt failed:', e);
                    toast.error('Failed to start video playback');
                  });
              };
            });
        } else {
          console.error('Video ref is null');
        }
      }, 100);
    } catch (error: any) {
      console.error('Camera error:', error);
      const errorMsg = error.name === 'NotAllowedError' 
        ? 'Camera access denied. Please allow camera permissions in your browser.'
        : error.name === 'NotFoundError'
        ? 'No camera found on your device.'
        : 'Unable to access camera. Please check your camera settings.';
      toast.error(errorMsg);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (video.readyState !== video.HAVE_ENOUGH_DATA) return;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Mirror the image
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    
    canvas.toBlob((blob) => {
      if (!blob) return;
      
      const file = new File([blob], `detection-${Date.now()}.jpg`, { type: 'image/jpeg' });
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setDetections([]);
      stopCamera();
    }, 'image/jpeg', 0.92);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setDetections([]);
    }
  };

  const handleDetect = async () => {
    if (!selectedFile) {
      toast.error('Please select an image first');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('image', selectedFile);

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
          {/* Mode Selector */}
          <div className="flex space-x-2 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
            <button
              onClick={() => {
                setMode('upload');
                stopCamera();
              }}
              className={`flex-1 py-2 px-4 rounded-md font-medium transition-all ${
                mode === 'upload'
                  ? 'bg-white dark:bg-gray-800 text-primary-600 shadow'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              <Upload className="w-4 h-4 inline mr-2" />
              Upload Photo
            </button>
            <button
              onClick={() => {
                setMode('camera');
                setSelectedFile(null);
                setPreview(null);
                setDetections([]);
              }}
              className={`flex-1 py-2 px-4 rounded-md font-medium transition-all ${
                mode === 'camera'
                  ? 'bg-white dark:bg-gray-800 text-primary-600 shadow'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              <Camera className="w-4 h-4 inline mr-2" />
              Take Photo
            </button>
          </div>

          {/* Upload Mode */}
          {mode === 'upload' && !preview && (
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-8 text-center hover:border-primary-500 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
                id="detect-file-input"
              />
              <label
                htmlFor="detect-file-input"
                className="cursor-pointer flex flex-col items-center"
              >
                <Upload className="w-16 h-16 text-gray-400 mb-4" />
                <span className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Click to upload image
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  PNG, JPG up to 10MB
                </span>
              </label>
            </div>
          )}

          {/* Camera Mode */}
          {mode === 'camera' && !preview && (
            <div className="space-y-4">
              {!stream ? (
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-8 text-center">
                  <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Click below to start your camera
                  </p>
                  <Button onClick={startCamera} className="mx-auto">
                    <Camera className="w-4 h-4 mr-2" />
                    Start Camera
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="relative aspect-video bg-black rounded-xl overflow-hidden">
                    {!isCameraActive && (
                      <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
                        <div className="text-white text-center">
                          <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                          <p>Starting camera...</p>
                        </div>
                      </div>
                    )}
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      muted
                      className="w-full h-full object-cover"
                      style={{ transform: 'scaleX(-1)' }}
                      onCanPlay={() => {
                        console.log('Video can play');
                        if (!isCameraActive) {
                          setIsCameraActive(true);
                        }
                      }}
                    />
                    {isCameraActive && (
                      <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                        <div className="w-48 h-64 border-4 border-white/60 rounded-3xl"></div>
                      </div>
                    )}
                  </div>
                  <div className="flex justify-center space-x-3">
                    <Button
                      onClick={stopCamera}
                      variant="secondary"
                    >
                      <X className="w-4 h-4 mr-2" />
                      Cancel
                    </Button>
                    <Button 
                      onClick={capturePhoto}
                      disabled={!isCameraActive}
                    >
                      <Camera className="w-4 h-4 mr-2" />
                      Capture Photo
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Image Preview */}
          {preview && (
            <div className="space-y-3">
              <div className="relative rounded-xl overflow-hidden border-2 border-gray-200 dark:border-gray-700">
                <img src={preview} alt="Preview" className="w-full h-auto" />
                <button
                  onClick={() => {
                    setSelectedFile(null);
                    setPreview(null);
                    setDetections([]);
                  }}
                  className="absolute top-3 right-3 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          <canvas ref={canvasRef} className="hidden" />

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
              onClick={handleClose}
              variant="secondary"
              className="flex-1"
            >
              Close
            </Button>
            <Button
              onClick={handleDetect}
              className="flex-1"
              loading={loading}
              disabled={!selectedFile || loading}
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
