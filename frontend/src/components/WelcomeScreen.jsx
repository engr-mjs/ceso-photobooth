import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { healthCheck } from '../services/api';
import { formatTime } from '../utils/helpers';

const WelcomeScreen = ({ onStart, error }) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [serverStatus, setServerStatus] = useState('checking');

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const checkServer = async () => {
      try {
        await healthCheck();
        setServerStatus('connected');
      } catch {
        setServerStatus('disconnected');
      }
    };
    checkServer();
    const interval = setInterval(checkServer, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="text-center flex flex-col items-center justify-center min-h-[70vh]">
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.1 }}
        className="mb-12"
      >
        <div className="mb-6">
          <div className="w-24 h-24 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-glow">
            <svg className="w-14 h-14 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
        </div>

        <h1 className="font-display text-5xl sm:text-6xl lg:text-7xl font-extrabold text-primary-500 mb-4 tracking-tight leading-tight">
          CESO
          <br />
          <span className="text-accent-500">Photobooth</span>
        </h1>

        <p className="text-xl sm:text-2xl text-surface-500 font-medium max-w-md mx-auto">
          Capture Memories Instantly
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.3 }}
        className="flex flex-col items-center gap-8"
      >
        <button
          onClick={onStart}
          disabled={serverStatus !== 'connected'}
          className="group relative px-12 py-5 bg-primary-500 text-white font-display font-bold text-xl rounded-2xl shadow-medium hover:shadow-large hover:bg-primary-600 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span className="relative z-10 flex items-center gap-3">
            <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Start Session
          </span>
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-primary-600 to-primary-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </button>

        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2 px-4 py-2 bg-white/80 rounded-xl shadow-soft">
            <div className={`w-2.5 h-2.5 rounded-full ${
              serverStatus === 'connected' ? 'bg-green-500' :
              serverStatus === 'checking' ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'
            }`} />
            <span className="text-sm font-medium text-surface-500">
              {serverStatus === 'connected' ? 'Server Online' :
               serverStatus === 'checking' ? 'Connecting...' : 'Server Offline'}
            </span>
          </div>

          <div className="flex items-center gap-2 px-4 py-2 bg-white/80 rounded-xl shadow-soft">
            <svg className="w-4 h-4 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm font-mono text-surface-500">{formatTime(currentTime)}</span>
          </div>
        </div>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8 p-4 bg-red-50 border border-red-200 rounded-2xl text-red-600 text-sm max-w-md mx-auto"
        >
          {error}
        </motion.div>
      )}
    </div>
  );
};

export default WelcomeScreen;
