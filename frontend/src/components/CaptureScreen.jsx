import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useCamera } from '../hooks/useCamera';
import { sleep } from '../utils/helpers';

const CaptureScreen = ({ sessionId, deviceId, onComplete, onCancel }) => {
  const { webcamRef, isReady, error: cameraError, onUserMedia, onUserMediaError, capture, flash } = useCamera(deviceId);
  const [countdown, setCountdown] = useState(null);
  const [photoIndex, setPhotoIndex] = useState(0);
  const [photos, setPhotos] = useState([]);
  const [phase, setPhase] = useState('ready');
  const [isCapturing, setIsCapturing] = useState(false);

  const totalPhotos = 3;
  const countdownDuration = 3;

  const runCountdown = useCallback(async (onDone) => {
    for (let i = countdownDuration; i >= 1; i--) {
      setCountdown(i);
      await sleep(1000);
    }
    setCountdown(null);
    onDone();
  }, [countdownDuration]);

  const takePhoto = useCallback(async () => {
    setIsCapturing(true);
    try {
      const imageData = capture();
      const newPhotos = [...photos, imageData];
      setPhotos(newPhotos);
      setPhotoIndex((prev) => prev + 1);
      return newPhotos;
    } catch (err) {
      throw err;
    } finally {
      setIsCapturing(false);
    }
  }, [capture, photos]);

  useEffect(() => {
    if (!isReady || isCapturing) return;

    const startCaptureSequence = async () => {
      setPhase('counting');

      for (let i = 0; i < totalPhotos; i++) {
        setPhotoIndex(i);
        await runCountdown(async () => {
          const newPhotos = await takePhoto();
          if (i < totalPhotos - 1) {
            await sleep(2000);
          }
        });
      }

      setPhase('complete');
    };

    startCaptureSequence();
  }, [isReady]);

  useEffect(() => {
    if (phase === 'complete' && photos.length === totalPhotos) {
      onComplete(photos);
    }
  }, [phase, photos, onComplete, totalPhotos]);

  const videoConstraints = deviceId
    ? { deviceId: { exact: deviceId }, width: { ideal: 1280 }, height: { ideal: 720 } }
    : { width: { ideal: 1280 }, height: { ideal: 720 } };

  return (
    <div className="text-center">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mb-6"
      >
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-primary-500 mb-2">
          {phase === 'ready' && 'Get Ready!'}
          {phase === 'counting' && `Photo ${photoIndex + 1} of ${totalPhotos}`}
          {phase === 'complete' && 'All Photos Captured!'}
        </h2>
        <p className="text-surface-500">
          {phase === 'counting' && 'Look at the camera and smile!'}
          {phase === 'complete' && 'Processing your photos...'}
        </p>
      </motion.div>

      <div className="relative mx-auto max-w-2xl mb-8">
        <div className="webcam-container aspect-[4/3] bg-primary-500/5 rounded-3xl overflow-hidden shadow-large">
          <video
            ref={webcamRef}
            autoPlay
            playsInline
            muted
            onUserMedia={onUserMedia}
            onUserMediaError={onUserMediaError}
            videoConstraints={videoConstraints}
            className="w-full h-full object-cover"
            style={{ transform: 'scaleX(-1)' }}
          />

          {!isReady && (
            <div className="absolute inset-0 flex items-center justify-center bg-primary-500/5 rounded-3xl">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin" />
                <p className="text-primary-500 font-medium">Starting camera...</p>
              </div>
            </div>
          )}

          <AnimatePresence>
            {countdown !== null && (
              <motion.div
                key={countdown}
                initial={{ scale: 2, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.5, opacity: 0 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                className="absolute inset-0 flex items-center justify-center"
              >
                <div className="w-32 h-32 sm:w-40 sm:h-40 rounded-full bg-primary-500/90 backdrop-blur-sm flex items-center justify-center shadow-glow">
                  <span className="font-display text-6xl sm:text-7xl font-bold text-white">
                    {countdown}
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {flash && (
            <div className="absolute inset-0 bg-white flash-overlay rounded-3xl" />
          )}

          {isCapturing && (
            <div className="absolute inset-0 bg-white/30 rounded-3xl" />
          )}
        </div>
      </div>

      <div className="flex justify-center gap-4 mb-6">
        {Array.from({ length: totalPhotos }).map((_, i) => (
          <motion.div
            key={i}
            initial={{ scale: 0.8, opacity: 0.3 }}
            animate={{
              scale: photos[i] ? 1.1 : i === photoIndex ? 1 : 0.8,
              opacity: photos[i] ? 1 : i === photoIndex ? 0.8 : 0.3,
            }}
            transition={{ duration: 0.3 }}
            className={`w-12 h-12 sm:w-16 sm:h-16 rounded-xl border-2 flex items-center justify-center transition-colors ${
              photos[i]
                ? 'bg-primary-500 border-primary-500 text-white'
                : i === photoIndex
                ? 'bg-primary-100 border-primary-300 text-primary-500'
                : 'bg-surface-100 border-surface-200 text-surface-400'
            }`}
          >
            {photos[i] ? (
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <span className="font-semibold text-sm">{i + 1}</span>
            )}
          </motion.div>
        ))}
      </div>

      <div className="flex justify-center">
        <button
          onClick={onCancel}
          className="px-6 py-2.5 text-surface-500 font-medium rounded-xl hover:bg-surface-100 transition-colors"
        >
          Cancel
        </button>
      </div>

      {cameraError && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-red-50 border border-red-200 rounded-2xl text-red-600 text-sm max-w-md mx-auto"
        >
          {cameraError}
        </motion.div>
      )}
    </div>
  );
};

export default CaptureScreen;
