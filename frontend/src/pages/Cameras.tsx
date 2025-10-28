import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Camera, Video, Eye, AlertCircle, StopCircle, Play, History } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export const Cameras = () => {
  const navigate = useNavigate();
  const [isStreaming, setIsStreaming] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [detections, setDetections] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [liveBoundingBoxes, setLiveBoundingBoxes] = useState<any[]>([]);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const detectionIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  // Fetch stats
  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 10000); // Update every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('No token found, skipping stats fetch');
        return;
      }
      
      const response = await axios.get('http://localhost:8000/api/faces/detections/statistics/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error: any) {
      if (error.response?.status === 401) {
        console.log('Unauthorized - please login');
        // Don't spam console with auth errors
      } else {
        console.error('Failed to fetch stats:', error);
      }
    }
  };

  const startCamera = async () => {
    try {
      console.log('Requesting camera access...');
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      
      console.log('Camera access granted, stream obtained');
      setStream(mediaStream);
      
      if (videoRef.current) {
        console.log('Attaching stream to video element...');
        videoRef.current.srcObject = mediaStream;
        
        // Add event listener for when video is ready
        videoRef.current.onloadedmetadata = () => {
          console.log('Video metadata loaded');
          setIsStreaming(true);
          
          // Update video dimensions
          if (videoRef.current) {
            setVideoSize({
              width: videoRef.current.videoWidth,
              height: videoRef.current.videoHeight
            });
          }
          
          videoRef.current?.play().then(() => {
            console.log('Video playing successfully');
            toast.success('📹 Camera started - Face detection active');
            // Start face detection
            startFaceDetection();
          }).catch(err => {
            console.error('Play error:', err);
            toast.error('Failed to play video');
          });
        };
        
        // Also try to play immediately in case metadata is already loaded
        if (videoRef.current.readyState >= 2) {
          console.log('Video already ready, playing now');
          setIsStreaming(true);
          await videoRef.current.play();
          toast.success('📹 Camera started - Face detection active');
          startFaceDetection();
        }
      } else {
        console.error('Video element not found!');
        toast.error('Video element not available');
      }
      
    } catch (error: any) {
      console.error('Camera error:', error);
      if (error.name === 'NotAllowedError') {
        toast.error('❌ Camera access denied. Please allow camera access.');
      } else if (error.name === 'NotFoundError') {
        toast.error('❌ No camera found on this device.');
      } else {
        toast.error('❌ Failed to access camera');
      }
      setIsStreaming(false);
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
    setIsStreaming(false);
    stopFaceDetection();
    toast('Camera stopped', { icon: '📹' });
  };

  const startFaceDetection = () => {
    // Run detection every 3 seconds
    detectionIntervalRef.current = setInterval(() => {
      detectFace();
    }, 3000);
  };

  const stopFaceDetection = () => {
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
      detectionIntervalRef.current = null;
    }
  };

  const detectFace = async () => {
    if (!videoRef.current || !canvasRef.current || isDetecting) return;
    
    setIsDetecting(true);
    
    try {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      
      ctx.drawImage(video, 0, 0);
      
      // Convert canvas to blob
      canvas.toBlob(async (blob) => {
        if (!blob) return;
        
        const formData = new FormData();
        formData.append('image', blob, 'capture.jpg');
        formData.append('camera_id', '1'); // You can make this dynamic
        
        try {
          const token = localStorage.getItem('access_token');
          if (!token) {
            console.log('No token found, cannot detect faces');
            toast.error('Please login to use face detection');
            stopCamera();
            return;
          }
          
          const response = await axios.post(
            'http://localhost:8000/api/faces/detections/detect/',
            formData,
            {
              headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'multipart/form-data',
              },
            }
          );
          
          if (response.data.detections && response.data.detections.length > 0) {
            const newDetections = response.data.detections;
            setDetections(prev => [...newDetections, ...prev].slice(0, 10));
            
            // Update live bounding boxes
            setLiveBoundingBoxes(newDetections.map((det: any) => ({
              ...det,
              timestamp: Date.now()
            })));
            
            // Clear bounding boxes after 2.5 seconds
            setTimeout(() => {
              setLiveBoundingBoxes([]);
            }, 2500);
            
            // Show notifications for detections
            newDetections.forEach((det: any) => {
              if (det.identity_label) {
                toast.success(
                  `✅ Recognized: ${det.identity_label} (${(det.similarity * 100).toFixed(1)}%)`,
                  { duration: 5000 }
                );
              } else {
                toast.error(
                  `⚠️ Unknown Person Detected!`,
                  { duration: 5000 }
                );
              }
            });
            
            // Refresh stats
            fetchStats();
          } else {
            // Clear bounding boxes if no faces detected
            setLiveBoundingBoxes([]);
          }
        } catch (error) {
          console.error('Detection error:', error);
        }
      }, 'image/jpeg', 0.95);
    } catch (error) {
      console.error('Capture error:', error);
    } finally {
      setIsDetecting(false);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

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
        <div className="flex space-x-3">
          <Button onClick={() => navigate('/camera-history')} variant="secondary">
            <History className="w-4 h-4 mr-2" />
            View History
          </Button>
          {!isStreaming ? (
            <Button onClick={startCamera}>
              <Play className="w-4 h-4 mr-2" />
              Start Camera
            </Button>
          ) : (
            <Button onClick={stopCamera} variant="secondary">
              <StopCircle className="w-4 h-4 mr-2" />
              Stop Camera
            </Button>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Detections</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                {stats?.total || 0}
              </p>
            </div>
            <Camera className="w-12 h-12 text-primary-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Matched</p>
              <p className="text-3xl font-bold text-green-600 mt-2">{stats?.matched || 0}</p>
            </div>
            <Eye className="w-12 h-12 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Unknown</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">{stats?.unmatched || 0}</p>
            </div>
            <AlertCircle className="w-12 h-12 text-yellow-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Today</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">{stats?.today || 0}</p>
            </div>
            <Video className="w-12 h-12 text-blue-600" />
          </div>
        </Card>
      </div>

      {/* Live Camera Feed */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center">
              <Camera className="w-6 h-6 mr-2" />
              Live Surveillance Feed
              {isDetecting && (
                <span className="ml-3 text-sm text-blue-600 dark:text-blue-400 animate-pulse">
                  Detecting...
                </span>
              )}
            </h2>
            {isStreaming && (
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-red-600 dark:text-red-400">LIVE</span>
              </div>
            )}
          </div>

          <div className="relative aspect-video bg-gray-900 rounded-lg overflow-hidden">
            {/* Always render video element */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={`w-full h-full object-cover ${!isStreaming ? 'hidden' : ''}`}
              style={{ transform: 'scaleX(-1)' }}
            />
            
            {/* Bounding box overlay */}
            {isStreaming && liveBoundingBoxes.length > 0 && (
              <div ref={overlayRef} className="absolute inset-0 pointer-events-none">
                {liveBoundingBoxes.map((det, idx) => {
                  const bbox = det.bbox;
                  if (!bbox || !videoRef.current) return null;
                  
                  const videoElement = videoRef.current;
                  const containerWidth = videoElement.offsetWidth;
                  const containerHeight = videoElement.offsetHeight;
                  const videoWidth = videoElement.videoWidth;
                  const videoHeight = videoElement.videoHeight;
                  
                  // Calculate scaling
                  const scaleX = containerWidth / videoWidth;
                  const scaleY = containerHeight / videoHeight;
                  
                  // Mirror x coordinate for flipped video
                  const x = (videoWidth - bbox[0] - bbox[2]) * scaleX;
                  const y = bbox[1] * scaleY;
                  const w = bbox[2] * scaleX;
                  const h = bbox[3] * scaleY;
                  
                  const isMatched = det.identity_label;
                  const borderColor = isMatched ? 'border-green-500' : 'border-red-500';
                  const bgColor = isMatched ? 'bg-green-500' : 'bg-red-500';
                  const textColor = 'text-white';
                  
                  return (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0 }}
                      className={`absolute border-4 ${borderColor}`}
                      style={{
                        left: `${x}px`,
                        top: `${y}px`,
                        width: `${w}px`,
                        height: `${h}px`,
                      }}
                    >
                      {/* Label above box */}
                      <div className={`absolute -top-8 left-0 ${bgColor} ${textColor} px-3 py-1 rounded text-sm font-bold shadow-lg whitespace-nowrap`}>
                        {isMatched ? (
                          <span>✅ {det.identity_label}</span>
                        ) : (
                          <span>⚠️ UNKNOWN</span>
                        )}
                      </div>
                      {/* Confidence below box */}
                      {det.similarity && (
                        <div className={`absolute -bottom-7 left-0 ${bgColor} ${textColor} px-2 py-0.5 rounded text-xs shadow-lg`}>
                          {(det.similarity * 100).toFixed(1)}%
                        </div>
                      )}
                    </motion.div>
                  );
                })}
              </div>
            )}
            
            {/* Placeholder when camera is off */}
            {!isStreaming && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <Camera className="w-20 h-20 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Camera is not active</p>
                  <Button onClick={startCamera}>
                    <Play className="w-4 h-4 mr-2" />
                    Start Live Surveillance
                  </Button>
                </div>
              </div>
            )}
            
            {/* Overlay when streaming */}
            {isStreaming && (
              <div className="absolute top-4 right-4 space-y-2">
                <div className="px-3 py-1 bg-black/60 rounded-lg text-white text-sm font-mono">
                  {new Date().toLocaleTimeString()}
                </div>
                <div className="px-3 py-1 bg-blue-600/80 rounded-lg text-white text-sm">
                  Face Detection: Active
                </div>
              </div>
            )}
          </div>
          <canvas ref={canvasRef} className="hidden" />
        </div>
      </Card>

      {/* Recent Detections */}
      {detections.length > 0 && (
        <Card className="p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Recent Detections
          </h2>
          <div className="space-y-3">
            <AnimatePresence>
              {detections.map((det, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className={`p-4 rounded-lg border-2 ${
                    det.identity_label
                      ? 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700'
                      : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {det.identity_label ? (
                        <Eye className="w-6 h-6 text-green-600" />
                      ) : (
                        <AlertCircle className="w-6 h-6 text-yellow-600" />
                      )}
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {det.identity_label || 'Unknown Person'}
                        </p>
                        {det.similarity && (
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            Confidence: {(det.similarity * 100).toFixed(1)}%
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Just now</p>
                      {det.age && (
                        <p className="text-xs text-gray-500">~{det.age} years</p>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </Card>
      )}
    </div>
  );
};
