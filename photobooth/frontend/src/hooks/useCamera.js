import { useState, useCallback, useRef, useEffect } from 'react';

export function useCamera(initialDeviceId) {
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState(null);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(initialDeviceId || null);
  const webcamRef = useRef(null);
  const streamRef = useRef(null);

  const stopStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => stopStream();
  }, [stopStream]);

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices()
      .then((all) => {
        const video = all.filter(d => d.kind === 'videoinput');
        setDevices(video);
        // Only auto-select first device if no initial device was provided
        if (!initialDeviceId && video.length > 0 && !selectedDevice) {
          setSelectedDevice(video[0].deviceId);
        }
      })
      .catch(() => {});
  }, [initialDeviceId]);

  const onUserMedia = useCallback((stream) => {
    stopStream();
    streamRef.current = stream;
    setIsReady(true);
    setError(null);
  }, [stopStream]);

  const onUserMediaError = useCallback((err) => {
    setIsReady(false);
    if (err.name === 'NotAllowedError') {
      setError('Camera permission denied. Please allow camera access and reload.');
    } else if (err.name === 'NotFoundError') {
      setError('No camera found. Please connect a webcam.');
    } else if (err.name === 'NotReadableError') {
      setError('Camera is being used by another application.');
    } else {
      setError('Camera error: ' + (err.message || 'Unknown error'));
    }
  }, []);

  const capture = useCallback(() => {
    if (!webcamRef.current) return null;
    return webcamRef.current.getScreenshot();
  }, []);

  const getCameraConstraints = useCallback(() => {
    if (selectedDevice) {
      return { deviceId: { exact: selectedDevice }, width: { ideal: 1920 }, height: { ideal: 1080 } };
    }
    return { width: { ideal: 1920 }, height: { ideal: 1080 } };
  }, [selectedDevice]);

  return {
    webcamRef, isReady, error, devices, selectedDevice,
    onUserMedia, onUserMediaError, capture, getCameraConstraints, stopStream,
  };
}
