import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, Upload, X, Check, RotateCw, Image as ImageIcon } from 'lucide-react';
import { Button } from './Button';

interface ImageCaptureProps {
  onImagesCapture: (files: File[]) => void;
  maxImages?: number;
  mode?: 'single' | 'multiple';
  showPreview?: boolean;
  guidanceText?: string;
}

export const ImageCapture = ({
  onImagesCapture,
  maxImages = 5,
  mode = 'multiple',
  showPreview = true,
  guidanceText,
}: ImageCaptureProps) => {
  const [captureMode, setCaptureMode] = useState<'upload' | 'camera' | null>(null);
  const [capturedImages, setCapturedImages] = useState<File[]>([]);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Start camera
  const startCamera = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 1280, height: 720 },
        audio: false,
      });
      
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }
      setIsCameraActive(true);
      setCaptureMode('camera');
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Unable to access camera. Please check permissions.');
    }
  }, []);

  // Stop camera
  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  }, [stream]);

  // Capture photo from camera
  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) {
      console.error('Video or canvas ref not available');
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    // Check if video is ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
      console.error('Video not ready');
      return;
    }
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      console.error('Could not get canvas context');
      return;
    }

    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert to blob
    canvas.toBlob((blob) => {
      if (!blob) {
        console.error('Failed to create blob from canvas');
        return;
      }
      
      const file = new File(
        [blob],
        `capture-${Date.now()}.jpg`,
        { type: 'image/jpeg' }
      );
      
      const newImages = [...capturedImages, file];
      setCapturedImages(newImages);
      onImagesCapture(newImages);
      
      if (mode === 'single' || newImages.length >= maxImages) {
        stopCamera();
      }
    }, 'image/jpeg', 0.95);
  }, [capturedImages, maxImages, mode, onImagesCapture, stopCamera]);

  // Handle file upload
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    
    if (files.length === 0) return;
    
    const validFiles = files.slice(0, maxImages - capturedImages.length);
    const newImages = [...capturedImages, ...validFiles];
    
    setCapturedImages(newImages);
    onImagesCapture(newImages);
    setCaptureMode('upload');
  };

  // Remove image
  const removeImage = (index: number) => {
    const newImages = capturedImages.filter((_, i) => i !== index);
    setCapturedImages(newImages);
    onImagesCapture(newImages);
  };

  // Reset
  const reset = () => {
    setCapturedImages([]);
    setCaptureMode(null);
    stopCamera();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-4">
      {/* Guidance Text */}
      {guidanceText && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <ImageIcon className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm text-blue-900 dark:text-blue-100 font-medium">Photo Guidelines</p>
              <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">{guidanceText}</p>
            </div>
          </div>
        </div>
      )}

      {/* Mode Selection */}
      {!captureMode && capturedImages.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-2 gap-4"
        >
          {/* Upload Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => fileInputRef.current?.click()}
            className="group relative overflow-hidden rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-400 transition-all p-8 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700"
          >
            <div className="flex flex-col items-center space-y-3">
              <div className="p-4 rounded-full bg-white dark:bg-gray-800 shadow-lg group-hover:shadow-xl transition-shadow">
                <Upload className="w-8 h-8 text-primary-600 dark:text-primary-400" />
              </div>
              <div className="text-center">
                <p className="font-semibold text-gray-900 dark:text-white">Upload Photo</p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Choose from files
                </p>
              </div>
            </div>
          </motion.button>

          {/* Camera Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={startCamera}
            className="group relative overflow-hidden rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-400 transition-all p-8 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700"
          >
            <div className="flex flex-col items-center space-y-3">
              <div className="p-4 rounded-full bg-white dark:bg-gray-800 shadow-lg group-hover:shadow-xl transition-shadow">
                <Camera className="w-8 h-8 text-primary-600 dark:text-primary-400" />
              </div>
              <div className="text-center">
                <p className="font-semibold text-gray-900 dark:text-white">Take Photo</p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Use camera
                </p>
              </div>
            </div>
          </motion.button>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple={mode === 'multiple'}
            onChange={handleFileUpload}
            className="hidden"
          />
        </motion.div>
      )}

      {/* Camera View */}
      <AnimatePresence>
        {isCameraActive && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative rounded-xl overflow-hidden bg-black shadow-2xl"
          >
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-auto mirror"
              style={{ transform: 'scaleX(-1)' }}
            />
            
            {/* Camera Overlay Guide */}
            <div className="absolute inset-0 pointer-events-none">
              {/* Face Guide Frame */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-64 h-80 border-4 border-white/60 rounded-3xl shadow-lg"></div>
              </div>
              
              {/* Step-by-Step Instructions */}
              <div className="absolute top-4 left-0 right-0 px-4">
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-4 shadow-2xl max-w-md mx-auto">
                  <div className="text-center space-y-2">
                    {capturedImages.length === 0 && (
                      <>
                        <div className="text-2xl font-bold text-white">📸 Photo 1 of 3</div>
                        <div className="text-lg font-semibold text-white">Face Forward</div>
                        <div className="text-sm text-white/90">
                          Look straight at the camera
                        </div>
                      </>
                    )}
                    {capturedImages.length === 1 && (
                      <>
                        <div className="text-2xl font-bold text-white">📸 Photo 2 of 3</div>
                        <div className="text-lg font-semibold text-white">Turn Left</div>
                        <div className="text-sm text-white/90">
                          Turn your head 45° to the left
                        </div>
                      </>
                    )}
                    {capturedImages.length === 2 && (
                      <>
                        <div className="text-2xl font-bold text-white">📸 Photo 3 of 3</div>
                        <div className="text-lg font-semibold text-white">Turn Right</div>
                        <div className="text-sm text-white/90">
                          Turn your head 45° to the right
                        </div>
                      </>
                    )}
                    {capturedImages.length >= 3 && (
                      <>
                        <div className="text-2xl font-bold text-white">✅ Great!</div>
                        <div className="text-sm text-white/90">
                          You can add more or finish
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Camera Controls */}
            <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/90 via-black/50 to-transparent">
              <div className="flex items-center justify-between max-w-md mx-auto">
                <Button
                  onClick={stopCamera}
                  variant="secondary"
                  className="bg-white/20 hover:bg-white/30 text-white border-white/30 backdrop-blur-sm"
                >
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </Button>
                
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={capturePhoto}
                  className="w-20 h-20 rounded-full bg-white shadow-2xl flex items-center justify-center border-4 border-white/50 hover:border-white transition-all"
                  title="Click to capture"
                >
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600"></div>
                </motion.button>

                <div className="text-white text-right">
                  <div className="text-2xl font-bold">{capturedImages.length}</div>
                  <div className="text-xs text-white/80">of {maxImages}</div>
                </div>
              </div>
            </div>

            <canvas ref={canvasRef} className="hidden" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Preview Grid */}
      {showPreview && capturedImages.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-3"
        >
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Captured Images ({capturedImages.length}/{maxImages})
            </p>
            <button
              onClick={reset}
              className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 flex items-center"
            >
              <RotateCw className="w-3.5 h-3.5 mr-1" />
              Start Over
            </button>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {capturedImages.map((file, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="relative group aspect-square rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800"
              >
                <img
                  src={URL.createObjectURL(file)}
                  alt={`Capture ${index + 1}`}
                  className="w-full h-full object-cover"
                />
                
                {/* Success Badge */}
                <div className="absolute top-2 right-2 p-1.5 rounded-full bg-green-500 shadow-lg">
                  <Check className="w-3 h-3 text-white" />
                </div>

                {/* Remove Button */}
                <button
                  onClick={() => removeImage(index)}
                  className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                >
                  <X className="w-6 h-6 text-white" />
                </button>
              </motion.div>
            ))}

            {/* Add More Button */}
            {capturedImages.length < maxImages && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  if (captureMode === 'camera') {
                    startCamera();
                  } else {
                    fileInputRef.current?.click();
                  }
                }}
                className="aspect-square rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-400 flex flex-col items-center justify-center space-y-2 transition-colors"
              >
                {captureMode === 'camera' ? (
                  <Camera className="w-6 h-6 text-gray-400" />
                ) : (
                  <Upload className="w-6 h-6 text-gray-400" />
                )}
                <span className="text-xs text-gray-500 dark:text-gray-400">Add More</span>
              </motion.button>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
};
