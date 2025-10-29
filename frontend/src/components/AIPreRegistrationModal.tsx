import { useState } from 'react';
import { X, Sparkles, Mail, FileText, MessageSquare, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

interface AIPreRegistrationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (extractedData: any) => void;
}

export default function AIPreRegistrationModal({ isOpen, onClose, onSuccess }: AIPreRegistrationModalProps) {
  const [sourceType, setSourceType] = useState<'email' | 'form' | 'message'>('email');
  const [text, setText] = useState('');
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractedData, setExtractedData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleExtract = async () => {
    if (!text.trim()) {
      setError('Please enter some text to extract information from');
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Please login first to use AI features');
      return;
    }

    setIsExtracting(true);
    setError(null);

    try {
      const response = await axios.post(
        'http://localhost:8000/api/visitor-assets/visitors/ai-extract/',
        {
          text: text,
          source_type: sourceType,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.data.success) {
        setExtractedData(response.data);
      } else {
        setError(response.data.error || 'Failed to extract information');
      }
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Session expired. Please login again.');
        localStorage.removeItem('access_token');
      } else {
        setError(err.response?.data?.error || 'Failed to connect to AI service');
      }
    } finally {
      setIsExtracting(false);
    }
  };

  const handleCreateVisitor = () => {
    if (extractedData && onSuccess) {
      onSuccess(extractedData.extracted_data);
    }
    handleClose();
  };

  const handleClose = () => {
    setText('');
    setExtractedData(null);
    setError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="h-8 w-8" />
              <div>
                <h2 className="text-2xl font-bold">AI Pre-Registration</h2>
                <p className="text-purple-100 text-sm mt-1">
                  Paste email or form content to automatically extract visitor information
                </p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="text-white hover:text-purple-200 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Source Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Source Type
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'email', label: 'Email', icon: Mail },
                { value: 'form', label: 'Form', icon: FileText },
                { value: 'message', label: 'Message', icon: MessageSquare },
              ].map(({ value, label, icon: Icon }) => (
                <button
                  key={value}
                  onClick={() => setSourceType(value as any)}
                  className={`
                    flex items-center justify-center gap-2 p-4 rounded-lg border-2 transition-all
                    ${
                      sourceType === value
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }
                  `}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Text Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Paste Content Here
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={`Example:\n\nSubject: Visitor Registration\n\nJohn Doe from ABC Corp will be visiting tomorrow at 2 PM for HVAC maintenance.\nPhone: +1234567890\nEmail: john.doe@abc.com\n\nPlease prepare a contractor pass.`}
              className="w-full h-48 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
              disabled={isExtracting}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-red-800 dark:text-red-200">Error</p>
                <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Extracted Data Display */}
          {extractedData && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                <CheckCircle className="h-5 w-5" />
                <span className="font-semibold">
                  Information Extracted Successfully (Confidence: {(extractedData.confidence * 100).toFixed(0)}%)
                </span>
              </div>

              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <h3 className="font-semibold text-green-900 dark:text-green-100 mb-3">Extracted Data:</h3>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(extractedData.extracted_data).map(([key, value]) => (
                    <div key={key}>
                      <span className="text-xs font-medium text-green-700 dark:text-green-300 uppercase">
                        {key.replace(/_/g, ' ')}
                      </span>
                      <p className="text-sm text-green-900 dark:text-green-100 mt-1">
                        {value as string || 'N/A'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-900">
          <div className="flex justify-end gap-3">
            <button
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
              disabled={isExtracting}
            >
              Cancel
            </button>
            
            {!extractedData ? (
              <button
                onClick={handleExtract}
                disabled={isExtracting || !text.trim()}
                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isExtracting ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Extracting...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5" />
                    Extract Information
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={handleCreateVisitor}
                className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <CheckCircle className="h-5 w-5" />
                Create Visitor
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
