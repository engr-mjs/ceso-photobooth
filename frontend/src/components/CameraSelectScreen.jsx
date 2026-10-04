import { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';

const CameraSelectScreen = ({ onSelect, onBack, error }) => {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [previewStream, setPreviewStream] = useState(null);
  const [previewError, setPreviewError] = useState(null);
  const [isPreviewReady, setIsPreviewReady] = useState(false);
  const videoRef = useRef(null);

  useEffect(() => {
    const getDevices = async () => {
      try {
        const allDevices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = allDevices.filter((d) => d.kind === 'videoinput');
        setDevices(videoDevices);
        if (videoDevices.length > 0) {
          setSelectedDevice(videoDevices[0].deviceId);
        }
      } catch (err) {
        console.warn('Could not enumerate devices:', err);
      }
    };
    getDevices();
  }, []);

  const startPreview = useCallback(async (deviceId) => {
    if (previewStream) {
      previewStream.getTracks().forEach((t) => t.stop());
    }
    setIsPreviewReady(false);
    setPreviewError(null);

    try {
      const constraints = {
        video: {
          deviceId: deviceId ? { exact: deviceId } : undefined,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      setPreviewStream(stream);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      if (err.name === 'NotAllowedError') {
        setPreviewError('Camera access denied. Please allow camera permissions.');
      } else if (err.name === 'NotReadableError') {
        setPreviewError('Camera is in use by another application. Close other apps using the camera.');
      } else {
        setPreviewError(`Camera error: ${err.message}`);
      }
    }
  }, [previewStream]);

  useEffect(() => {
    if (selectedDevice) {
      startPreview(selectedDevice);
    }
    return () => {
      if (previewStream) {
        previewStream.getTracks().forEach((t) => t.stop());
      }
    };
  }, [selectedDevice]);

  const handleVideoLoaded = () => {
    setIsPreviewReady(true);
  };

  const handleSelect = () => {
    if (previewStream) {
      previewStream.getTracks().forEach((t) => t.stop());
    }
    onSelect(selectedDevice);
  };

  const handleRefresh = async () => {
    const allDevices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = allDevices.filter((d) => d.kind === 'videoinput');
    setDevices(videoDevices);
  };

  return (
    <div className="text-center">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-primary-500 mb-2">
          Select Camera
        </h2>
        <p className="text-surface-500">
          Choose which camera to use for the session
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.15 }}
        className="relative mx-auto max-w-lg mb-8"
      >
        <div className="webcam-container aspect-[4/3] bg-primary-500/5 rounded-3xl overflow-hidden shadow-large">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            onLoadedData={handleVideoLoaded}
            className="w-full h-full object-cover"
            style={{ transform: 'scaleX(-1)' }}
          />

          {!isPreviewReady && !previewError && (
            <div className="absolute inset-0 flex items-center justify-center bg-primary-500/5 rounded-3xl">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin" />
                <p className="text-primary-500 font-medium">Loading preview...</p>
              </div>
            </div>
          )}

          {previewError && (
            <div className="absolute inset-0 flex items-center justify-center bg-red-50 rounded-3xl">
              <div className="text-center p-6">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
                  <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <p className="text-red-600 font-medium mb-2">{previewError}</p>
                <button
                  onClick={handleRefresh}
                  className="text-sm text-primary-500 font-medium hover:underline"
                >
                  Refresh cameras
                </button>
              </div>
            </div>
          )}
        </div>

        {isPreviewReady && (
          <div className="absolute top-3 right-3 flex items-center gap-1.5 px-3 py-1 bg-green-500/90 backdrop-blur-sm rounded-full">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
            <span className="text-xs font-semibold text-white">LIVE</span>
          </div>
        )}
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="max-w-lg mx-auto"
      >
        {devices.length > 1 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-surface-500 mb-3">
              Available Cameras
            </label>
            <div className="grid gap-2">
              {devices.map((device) => (
                <button
                  key={device.deviceId}
                  onClick={() => setSelectedDevice(device.deviceId)}
                  className={`w-full px-4 py-3 rounded-xl border-2 text-left transition-all duration-200 flex items-center gap-3 ${
                    selectedDevice === device.deviceId
                      ? 'border-primary-500 bg-primary-50 shadow-soft'
                      : 'border-surface-200 bg-white hover:border-surface-300'
                  }`}
                >
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    selectedDevice === device.deviceId
                      ? 'bg-primary-500 text-white'
                      : 'bg-surface-100 text-surface-400'
                  }`}>
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-primary-500 truncate">
                      {device.label || `Camera ${devices.indexOf(device) + 1}`}
                    </p>
                    <p className="text-xs text-surface-400 truncate">
                      {device.deviceId.slice(0, 20)}...
                    </p>
                  </div>
                  {selectedDevice === device.deviceId && (
                    <svg className="w-5 h-5 text-primary-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {devices.length === 0 && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-2xl text-yellow-700 text-sm">
            No cameras detected. Please connect a camera and click refresh.
          </div>
        )}

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            onClick={onBack}
            className="w-full sm:w-auto px-6 py-3 bg-surface-100 text-surface-500 font-semibold rounded-2xl hover:bg-surface-200 transition-all duration-300"
          >
            Back
          </button>

          <button
            onClick={handleRefresh}
            className="w-full sm:w-auto px-6 py-3 bg-surface-100 text-surface-500 font-semibold rounded-2xl hover:bg-surface-200 transition-all duration-300 flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>

          <button
            onClick={handleSelect}
            disabled={!isPreviewReady || !!previewError}
            className="w-full sm:w-auto px-8 py-3 bg-primary-500 text-white font-semibold rounded-2xl shadow-medium hover:shadow-large hover:bg-primary-600 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Start Capturing
          </button>
        </div>
      </motion.div>

      {(error || previewError) && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-red-50 border border-red-200 rounded-2xl text-red-600 text-sm max-w-md mx-auto"
        >
          {error || previewError}
        </motion.div>
      )}
    </div>
  );
};

export default CameraSelectScreen;
