import { useRef, useState, useCallback, useEffect } from 'react';

export const useCamera = (deviceId = null) => {
  const webcamRef = useRef(null);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState(null);
  const [flash, setFlash] = useState(false);

  const onUserMedia = useCallback(() => {
    setIsReady(true);
    setError(null);
  }, []);

  const onUserMediaError = useCallback((err) => {
    setIsReady(false);
    if (err.name === 'NotAllowedError') {
      setError('Camera access denied. Please allow camera permissions.');
    } else if (err.name === 'NotFoundError') {
      setError('No camera found. Please connect a camera.');
    } else if (err.name === 'NotReadableError') {
      setError('Camera is in use by another application. Close other apps using the camera.');
    } else {
      setError(`Camera error: ${err.message || err}`);
    }
  }, []);

  const capture = useCallback(() => {
    if (!webcamRef.current) {
      throw new Error('Camera not ready');
    }

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) {
      throw new Error('Failed to capture photo');
    }

    setFlash(true);
    setTimeout(() => setFlash(false), 300);

    return imageSrc;
  }, []);

  return {
    webcamRef,
    isReady,
    error,
    flash,
    onUserMedia,
    onUserMediaError,
    capture,
    deviceId,
  };
};
