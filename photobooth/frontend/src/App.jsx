import { useState, useCallback, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import WelcomeScreen from './components/WelcomeScreen';
import CameraSelectScreen from './components/CameraSelectScreen';
import CaptureScreen from './components/CaptureScreen';
import ReviewScreen from './components/ReviewScreen';
import ProcessingScreen from './components/ProcessingScreen';
import ResultScreen from './components/ResultScreen';
import { serverAPI } from './services/api';

const SCREENS = {
  WELCOME: 'welcome',
  CAMERA_SELECT: 'camera_select',
  CAPTURE: 'capture',
  REVIEW: 'review',
  PROCESSING: 'processing',
  RESULT: 'result',
};

export default function App() {
  const [currentScreen, setCurrentScreen] = useState(SCREENS.WELCOME);
  const [sessionId, setSessionId] = useState(null);
  const [selectedDeviceId, setSelectedDeviceId] = useState(null);
  const [capturedPhotos, setCapturedPhotos] = useState([]);
  const [stripUrl, setStripUrl] = useState(null);
  const [qrUrl, setQrUrl] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [serverInfo, setServerInfo] = useState(null);
  const [serverOnline, setServerOnline] = useState(false);

  useEffect(() => {
    checkServer();
    const interval = setInterval(checkServer, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkServer = async () => {
    try {
      const res = await serverAPI.getHealth();
      setServerOnline(true);
      setServerInfo(res.data);
    } catch {
      setServerOnline(false);
    }
  };

  const handleStartSession = useCallback((sid) => {
    setSessionId(sid);
    setCapturedPhotos([]);
    setStripUrl(null);
    setQrUrl(null);
    setDownloadUrl(null);
    setCurrentScreen(SCREENS.CAMERA_SELECT);
  }, []);

  const handleCameraSelect = useCallback((deviceId) => {
    setSelectedDeviceId(deviceId);
    setCurrentScreen(SCREENS.CAPTURE);
  }, []);

  const handleCameraSelectBack = useCallback(() => {
    setCurrentScreen(SCREENS.WELCOME);
  }, []);

  const handleCaptureComplete = useCallback((photos) => {
    setCapturedPhotos(photos);
    setCurrentScreen(SCREENS.REVIEW);
  }, []);

  const handleRetake = useCallback(() => {
    setCapturedPhotos([]);
    setCurrentScreen(SCREENS.CAPTURE);
  }, []);

  const handleGenerateStrip = useCallback(() => {
    setCurrentScreen(SCREENS.PROCESSING);
  }, []);

  const handleStripReady = useCallback((data) => {
    setStripUrl(data.strip_url);
    setQrUrl(data.qr_code_url);
    setDownloadUrl(data.download_url);
    setSessionId(data.session_id);
    setCurrentScreen(SCREENS.RESULT);
  }, []);

  const handleNewSession = useCallback(() => {
    setSessionId(null);
    setSelectedDeviceId(null);
    setCapturedPhotos([]);
    setStripUrl(null);
    setQrUrl(null);
    setDownloadUrl(null);
    setCurrentScreen(SCREENS.WELCOME);
  }, []);

  return (
    <div className="min-h-screen gradient-bg text-white overflow-hidden">
      <AnimatePresence mode="wait">
        {currentScreen === SCREENS.WELCOME && (
          <WelcomeScreen key="welcome" onStartSession={handleStartSession}
            serverOnline={serverOnline} serverInfo={serverInfo} />
        )}
        {currentScreen === SCREENS.CAMERA_SELECT && (
          <CameraSelectScreen key="camera-select"
            onSelect={handleCameraSelect} onBack={handleCameraSelectBack} />
        )}
        {currentScreen === SCREENS.CAPTURE && (
          <CaptureScreen key="capture" sessionId={sessionId} deviceId={selectedDeviceId}
            onCaptureComplete={handleCaptureComplete} onCancel={handleNewSession} />
        )}
        {currentScreen === SCREENS.REVIEW && (
          <ReviewScreen key="review" photos={capturedPhotos} sessionId={sessionId}
            onRetake={handleRetake} onGenerate={handleGenerateStrip} onStripReady={handleStripReady} />
        )}
        {currentScreen === SCREENS.PROCESSING && (
          <ProcessingScreen key="processing" sessionId={sessionId} onComplete={handleStripReady} />
        )}
        {currentScreen === SCREENS.RESULT && (
          <ResultScreen key="result" stripUrl={stripUrl} qrUrl={qrUrl}
            downloadUrl={downloadUrl} sessionId={sessionId} onNewSession={handleNewSession} />
        )}
      </AnimatePresence>
    </div>
  );
}
