import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { downloadStrip, getPreviewUrl, getQRUrl } from '../services/api';

const ResultScreen = ({ sessionId, resultData, onNewSession }) => {
  const [showQR, setShowQR] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowQR(true), 500);
    return () => clearTimeout(timer);
  }, []);

  if (!resultData) return null;

  const previewUrl = getPreviewUrl(sessionId);
  const qrUrl = getQRUrl(sessionId);
  const downloadUrl = downloadStrip(sessionId);

  return (
    <div className="text-center">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-primary-500 mb-2">
          Your Strip is Ready!
        </h2>
        <p className="text-surface-500">
          Scan the QR code or download directly
        </p>
      </motion.div>

      <div className="flex flex-col lg:flex-row items-center justify-center gap-8 max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex-shrink-0"
        >
          <div className="relative">
            <div className="strip-shadow rounded-3xl overflow-hidden bg-white p-2">
              <img
                src={previewUrl}
                alt="Photobooth strip"
                className="w-48 sm:w-56 h-auto rounded-2xl"
              />
            </div>
            <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 px-4 py-1 bg-accent-500 text-white text-xs font-semibold rounded-full shadow-medium">
              High Quality
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex flex-col items-center gap-6"
        >
          {showQR && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4 }}
              className="p-4 bg-white rounded-2xl shadow-medium"
            >
              <img
                src={qrUrl}
                alt="QR Code to download strip"
                className="w-40 h-40 sm:w-48 sm:h-48"
              />
            </motion.div>
          )}

          <p className="text-sm text-surface-500 text-center max-w-xs">
            Scan this QR code with your phone to download the photo strip
          </p>

          <div className="flex flex-col sm:flex-row items-center gap-3">
            <a
              href={downloadUrl}
              download
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary-500 text-white font-semibold rounded-2xl shadow-medium hover:shadow-large hover:bg-primary-600 transition-all duration-300"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download Strip
            </a>

            <button
              onClick={onNewSession}
              className="inline-flex items-center gap-2 px-6 py-3 bg-surface-100 text-surface-500 font-semibold rounded-2xl hover:bg-surface-200 transition-all duration-300"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Session
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ResultScreen;
