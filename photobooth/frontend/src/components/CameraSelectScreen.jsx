import { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';

export default function CameraSelectScreen({ onSelect, onBack }) {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [previewError, setPreviewError] = useState(null);
  const [isPreviewReady, setIsPreviewReady] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const stopStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
  }, []);

  const startPreview = useCallback(async (deviceId) => {
    stopStream();
    setIsPreviewReady(false);
    setPreviewError(null);

    try {
      const constraints = {
        video: deviceId
          ? { deviceId: { exact: deviceId }, width: { ideal: 1920 }, height: { ideal: 1080 } }
          : { width: { ideal: 1920 }, height: { ideal: 1080 } },
        audio: false,
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        try {
          await videoRef.current.play();
        } catch (_) {}
        setIsPreviewReady(true);
      }
    } catch (err) {
      if (err.name === 'NotAllowedError') {
        setPreviewError('Camera permission denied. Please allow camera access and reload.');
      } else if (err.name === 'NotReadableError') {
        setPreviewError('Camera is being used by another application. Close other apps using the camera.');
      } else if (err.name === 'OverconstrainedError' || err.name === 'NotFoundError') {
        // Retry with default camera if the exact device failed
        if (deviceId) {
          try {
            const fallback = await navigator.mediaDevices.getUserMedia({
              video: { width: { ideal: 1920 }, height: { ideal: 1080 } },
              audio: false,
            });
            streamRef.current = fallback;
            if (videoRef.current) {
              videoRef.current.srcObject = fallback;
              try { await videoRef.current.play(); } catch (_) {}
              setIsPreviewReady(true);
            }
            return;
          } catch (_) {}
        }
        setPreviewError('No camera found. Please connect a webcam.');
      } else {
        setPreviewError('Camera error: ' + (err.message || 'Unknown error'));
      }
    }
  }, [stopStream]);

  // On mount: request permission first, then enumerate devices, then start preview
  useEffect(() => {
    const init = async () => {
      // Step 1: request camera permission so deviceIds become available
      try {
        const permStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        permStream.getTracks().forEach(t => t.stop());
      } catch (err) {
        if (err.name === 'NotAllowedError') {
          setPreviewError('Camera permission denied. Please allow camera access and reload.');
          return;
        }
        // Other errors (e.g. no camera) — continue to enumeration
      }

      // Step 2: enumerate devices (now with real deviceIds)
      try {
        const allDevices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = allDevices.filter(d => d.kind === 'videoinput');
        setDevices(videoDevices);
        const firstId = videoDevices.length > 0 && videoDevices[0].deviceId ? videoDevices[0].deviceId : null;
        setSelectedDevice(firstId);

        // Step 3: start preview (works with null deviceId = default camera)
        startPreview(firstId);
      } catch (err) {
        console.warn('Could not enumerate devices:', err);
        startPreview(null);
      }
    };
    init();
    return () => stopStream();
  }, [stopStream, startPreview]);

  const handleSelect = () => {
    stopStream();
    onSelect(selectedDevice);
  };

  const handleRefresh = async () => {
    stopStream();
    setIsPreviewReady(false);
    setPreviewError(null);
    try {
      const allDevices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = allDevices.filter(d => d.kind === 'videoinput');
      setDevices(videoDevices);
      const stillValid = videoDevices.find(d => d.deviceId === selectedDevice);
      const nextId = stillValid ? selectedDevice : (videoDevices[0]?.deviceId || null);
      setSelectedDevice(nextId);
      startPreview(nextId);
    } catch (err) {
      console.warn('Could not refresh devices:', err);
      startPreview(null);
    }
  };

  const handlePickDevice = (deviceId) => {
    setSelectedDevice(deviceId);
    startPreview(deviceId);
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <div className="pt-6 pb-4 px-6 flex justify-between items-center">
        <button onClick={onBack} className="btn-ghost" type="button">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          Back
        </button>
        <button onClick={handleRefresh} className="btn-ghost" type="button">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Title */}
      <div className="px-6 pb-6 text-center">
        <motion.h2
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="font-pixel text-2xl sm:text-3xl text-neutral-900 tracking-wider"
        >
          SELECT CAMERA
        </motion.h2>
        <p className="text-neutral-400 text-sm mt-2">Choose which camera to use</p>
      </div>

      {/* Preview */}
      <div className="flex-1 flex items-center justify-center px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="w-full max-w-xl"
        >
          <div className="relative rounded-xl overflow-hidden bg-neutral-100 border border-neutral-200" style={{ aspectRatio: '4/3' }}>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
              style={{ transform: 'scaleX(-1)' }}
            />

            {!isPreviewReady && !previewError && (
              <div className="absolute inset-0 flex items-center justify-center bg-neutral-100">
                <div className="text-center">
                  <div className="w-8 h-8 mx-auto mb-3 border-2 border-neutral-200 border-t-neutral-900 rounded-full animate-spin" />
                  <p className="text-neutral-400 text-sm">Starting camera...</p>
                </div>
              </div>
            )}

            {previewError && (
              <div className="absolute inset-0 flex flex-col items-center justify-center p-6">
                <svg className="w-12 h-12 text-neutral-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <p className="text-neutral-400 text-sm text-center mb-3">{previewError}</p>
                <button onClick={handleRefresh} className="btn-ghost text-xs" type="button">
                  Try again
                </button>
              </div>
            )}

            {isPreviewReady && (
              <div className="absolute top-3 left-3 flex items-center gap-1.5 px-2.5 py-1 rounded-full" style={{ background: 'rgba(34,197,94,0.9)' }}>
                <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
                <span className="text-[10px] font-bold text-white uppercase tracking-wide">Live</span>
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Camera list + button */}
      <div className="pb-10 pt-6 px-6">
        {devices.length > 1 && (
          <div className="max-w-xl mx-auto mb-6">
            <p className="text-neutral-400 text-xs font-medium mb-3 uppercase tracking-wider">Available Cameras</p>
            <div className="grid gap-2">
              {devices.map((device, i) => (
                <button
                  key={device.deviceId || i}
                  onClick={() => handlePickDevice(device.deviceId)}
                  className={`w-full px-4 py-3 rounded-xl border text-left transition-all duration-150 flex items-center gap-3 ${
                    selectedDevice === device.deviceId
                      ? 'border-neutral-900 bg-neutral-50'
                      : 'border-neutral-200 bg-white hover:border-neutral-300'
                  }`}
                  type="button"
                >
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                    selectedDevice === device.deviceId ? 'bg-neutral-900 text-white' : 'bg-neutral-100 text-neutral-400'
                  }`}>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25h-9A2.25 2.25 0 002.25 7.5v9a2.25 2.25 0 002.25 2.25z" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-neutral-900 truncate">
                      {device.label || `Camera ${i + 1}`}
                    </p>
                  </div>
                  {selectedDevice === device.deviceId && (
                    <svg className="w-4 h-4 text-neutral-900 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-center">
          <motion.button
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleSelect}
            disabled={!isPreviewReady || !!previewError}
            className="btn-primary px-16 py-4 text-base font-bold"
            type="button"
          >
            START CAPTURING
          </motion.button>
        </div>
      </div>
    </div>
  );
}
