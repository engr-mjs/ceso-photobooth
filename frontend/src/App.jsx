import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import WelcomeScreen from './components/WelcomeScreen';
import CameraSelectScreen from './components/CameraSelectScreen';
import CaptureScreen from './components/CaptureScreen';
import ReviewScreen from './components/ReviewScreen';
import LoadingScreen from './components/LoadingScreen';
import ResultScreen from './components/ResultScreen';
import Footer from './components/Footer';
import { createSession, savePhoto, generateStrip } from './services/api';

const STATES = {
  WELCOME: 'welcome',
  CAMERA_SELECT: 'camera_select',
  CAPTURING: 'capturing',
  REVIEW: 'review',
  LOADING: 'loading',
  RESULT: 'result',
};

function App() {
  const [appState, setAppState] = useState(STATES.WELCOME);
  const [sessionId, setSessionId] = useState(null);
  const [selectedDeviceId, setSelectedDeviceId] = useState(null);
  const [capturedPhotos, setCapturedPhotos] = useState([]);
  const [resultData, setResultData] = useState(null);
  const [error, setError] = useState(null);

  const handleStartClick = useCallback(async () => {
    try {
      setError(null);
      setCapturedPhotos([]);
      setResultData(null);
      const response = await createSession();
      setSessionId(response.session_id);
      setAppState(STATES.CAMERA_SELECT);
    } catch (err) {
      setError(`Failed to start session: ${err.message}`);
    }
  }, []);

  const handleCameraSelect = useCallback((deviceId) => {
    setSelectedDeviceId(deviceId);
    setAppState(STATES.CAPTURING);
  }, []);

  const handleCameraSelectBack = useCallback(() => {
    setAppState(STATES.WELCOME);
  }, []);

  const handleCaptureComplete = useCallback((photos) => {
    setCapturedPhotos(photos);
    setAppState(STATES.REVIEW);
  }, []);

  const handleRetake = useCallback(() => {
    setCapturedPhotos([]);
    setAppState(STATES.CAPTURING);
  }, []);

  const handleGenerateStrip = useCallback(async () => {
    if (!sessionId || capturedPhotos.length !== 3) return;

    setAppState(STATES.LOADING);
    setError(null);

    try {
      for (let i = 0; i < capturedPhotos.length; i++) {
        await savePhoto(sessionId, i + 1, capturedPhotos[i]);
      }

      const stripResult = await generateStrip(sessionId);
      setResultData(stripResult);
      setAppState(STATES.RESULT);
    } catch (err) {
      setError(`Failed to generate strip: ${err.message}`);
      setAppState(STATES.REVIEW);
    }
  }, [sessionId, capturedPhotos]);

  const handleNewSession = useCallback(() => {
    setSessionId(null);
    setSelectedDeviceId(null);
    setCapturedPhotos([]);
    setResultData(null);
    setError(null);
    setAppState(STATES.WELCOME);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-4xl">
          <AnimatePresence mode="wait">
            {appState === STATES.WELCOME && (
              <motion.div
                key="welcome"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.4 }}
              >
                <WelcomeScreen onStart={handleStartClick} error={error} />
              </motion.div>
            )}

            {appState === STATES.CAMERA_SELECT && (
              <motion.div
                key="camera-select"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.4 }}
              >
                <CameraSelectScreen
                  onSelect={handleCameraSelect}
                  onBack={handleCameraSelectBack}
                  error={error}
                />
              </motion.div>
            )}

            {appState === STATES.CAPTURING && (
              <motion.div
                key="capturing"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.4 }}
              >
                <CaptureScreen
                  sessionId={sessionId}
                  deviceId={selectedDeviceId}
                  onComplete={handleCaptureComplete}
                  onCancel={handleNewSession}
                />
              </motion.div>
            )}

            {appState === STATES.REVIEW && (
              <motion.div
                key="review"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.4 }}
              >
                <ReviewScreen
                  photos={capturedPhotos}
                  onRetake={handleRetake}
                  onGenerate={handleGenerateStrip}
                  error={error}
                />
              </motion.div>
            )}

            {appState === STATES.LOADING && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                <LoadingScreen />
              </motion.div>
            )}

            {appState === STATES.RESULT && (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.4 }}
              >
                <ResultScreen
                  sessionId={sessionId}
                  resultData={resultData}
                  onNewSession={handleNewSession}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
