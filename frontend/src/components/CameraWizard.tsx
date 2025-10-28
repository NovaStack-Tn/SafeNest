import { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, X, Check, ArrowLeft } from 'lucide-react';
import { Button } from './Button';

interface CameraWizardProps {
  onComplete: (images: File[]) => void;
  onCancel: () => void;
  personName: string;
}

const CAPTURE_INSTRUCTIONS = [
  {
    step: 1,
    emoji: '📸',
    title: 'Face Forward',
    description: 'Look straight at the camera',
  },
  {
    step: 2,
    emoji: '↖️',
    title: 'Turn Left',
    description: 'Turn your head 45° to the left',
  },
  {
    step: 3,
    emoji: '↗️',
    title: 'Turn Right',
    description: 'Turn your head 45° to the right',
  },
];

export const CameraWizard = ({ onComplete, onCancel, personName }: CameraWizardProps) => {
  const [capturedImages, setCapturedImages] = useState<File[]>([]);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const currentStep = Math.min(capturedImages.length, 2);
  const instruction = CAPTURE_INSTRUCTIONS[currentStep];

  // Start camera on mount
  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      setCameraError(null);
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user',
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });
      
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
          setIsCameraReady(true);
        };
      }
    } catch (error: any) {
      console.error('Camera error:', error);
      setCameraError('Unable to access camera. Please allow camera permissions.');
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
    setIsCameraReady(false);
  };

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !isCameraReady) {
      console.error('Camera not ready');
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
      console.error('Video not ready');
      return;
    }
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Flip horizontally (mirror)
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    
    canvas.toBlob((blob) => {
      if (!blob) return;
      
      const file = new File(
        [blob],
        `${personName.replace(/\s+/g, '_')}_${Date.now()}.jpg`,
        { type: 'image/jpeg' }
      );
      
      const newImages = [...capturedImages, file];
      setCapturedImages(newImages);
      
      if (newImages.length >= 3) {
        stopCamera();
      }
    }, 'image/jpeg', 0.92);
  }, [capturedImages, isCameraReady, personName]);

  const removeImage = (index: number) => {
    const newImages = capturedImages.filter((_, i) => i !== index);
    setCapturedImages(newImages);
    
    if (newImages.length < 3 && !stream) {
      startCamera();
    }
  };

  const handleFinish = () => {
    if (capturedImages.length >= 3) {
      onComplete(capturedImages);
    }
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 text-white">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={onCancel}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h2 className="text-lg font-bold">Enrolling: {personName}</h2>
              <p className="text-sm text-white/90">
                {capturedImages.length} of 3 photos captured
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{capturedImages.length}/3</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-6 bg-gray-900">
        <div className="max-w-6xl w-full">
          <AnimatePresence mode="wait">
            {/* Camera View */}
            {capturedImages.length < 3 && (
              <motion.div
                key="camera"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="grid grid-cols-1 lg:grid-cols-3 gap-6"
              >
                {/* Left Side - Camera Feed */}
                <div className="lg:col-span-2 space-y-4">
                  {/* Camera Feed */}
                  <div className="relative aspect-video bg-black rounded-2xl overflow-hidden shadow-2xl" style={{ maxHeight: '500px' }}>
                  {cameraError ? (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-800 text-white p-8 text-center">
                      <div>
                        <Camera className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                        <p className="text-lg font-semibold mb-2">Camera Access Denied</p>
                        <p className="text-sm text-gray-400">{cameraError}</p>
                        <Button onClick={startCamera} className="mt-4">
                          Try Again
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        className="w-full h-full object-cover"
                        style={{ transform: 'scaleX(-1)' }}
                      />
                      
                      {!isCameraReady && (
                        <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
                          <div className="text-white text-center">
                            <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                            <p>Starting camera...</p>
                          </div>
                        </div>
                      )}
                      
                      {/* Face Guide */}
                      {isCameraReady && (
                        <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                          <div className="w-48 h-64 border-4 border-white/60 rounded-3xl shadow-2xl"></div>
                        </div>
                      )}
                    </>
                  )}
                  </div>

                  {/* Capture Button */}
                  {isCameraReady && !cameraError && (
                    <div className="flex justify-center">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={capturePhoto}
                        className="w-20 h-20 rounded-full bg-white shadow-2xl flex items-center justify-center border-4 border-gray-300 hover:border-blue-500 transition-all"
                      >
                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600"></div>
                      </motion.button>
                    </div>
                  )}
                </div>

                {/* Right Side - Instructions */}
                <div className="lg:col-span-1">
                  <motion.div
                    key={currentStep}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl p-6 text-white shadow-2xl h-full flex flex-col justify-center"
                  >
                    <div className="text-center space-y-4">
                      <div className="text-6xl mb-4">{instruction.emoji}</div>
                      <div>
                        <div className="text-sm font-semibold text-white/80 mb-2">
                          Step {instruction.step} of 3
                        </div>
                        <div className="text-3xl font-bold mb-3">{instruction.title}</div>
                        <div className="text-lg text-white/90">{instruction.description}</div>
                      </div>
                      
                      {/* Tips */}
                      <div className="mt-6 pt-6 border-t border-white/20 text-left space-y-2">
                        <div className="text-sm font-semibold mb-3">Tips:</div>
                        <div className="flex items-start space-x-2 text-sm text-white/80">
                          <span>✓</span>
                          <span>Look directly at the camera</span>
                        </div>
                        <div className="flex items-start space-x-2 text-sm text-white/80">
                          <span>✓</span>
                          <span>Ensure good lighting</span>
                        </div>
                        <div className="flex items-start space-x-2 text-sm text-white/80">
                          <span>✓</span>
                          <span>Remove glasses if possible</span>
                        </div>
                        <div className="flex items-start space-x-2 text-sm text-white/80">
                          <span>✓</span>
                          <span>Keep your face in the frame</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </motion.div>
            )}

            {/* Preview & Complete */}
            {capturedImages.length >= 3 && (
              <motion.div
                key="complete"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="max-w-4xl mx-auto space-y-6"
              >
                <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl p-6 text-center text-white">
                  <Check className="w-12 h-12 mx-auto mb-3" />
                  <h3 className="text-2xl font-bold mb-2">Great Job!</h3>
                  <p className="text-white/90">You've captured all 3 required photos</p>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  {capturedImages.map((file, index) => (
                    <div key={index} className="relative group aspect-square">
                      <img
                        src={URL.createObjectURL(file)}
                        alt={`Capture ${index + 1}`}
                        className="w-full h-full object-cover rounded-xl"
                      />
                      <div className="absolute top-2 left-2 bg-blue-600 text-white px-2 py-1 rounded text-xs font-bold">
                        {CAPTURE_INSTRUCTIONS[index].title}
                      </div>
                      <button
                        onClick={() => removeImage(index)}
                        className="absolute top-2 right-2 bg-red-500 text-white p-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>

                <div className="flex space-x-3">
                  <Button
                    onClick={onCancel}
                    variant="secondary"
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleFinish}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    <Check className="w-4 h-4 mr-2" />
                    Complete Enrollment
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};
