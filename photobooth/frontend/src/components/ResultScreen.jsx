import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function ResultScreen({ stripUrl, qrUrl, downloadUrl, sessionId, onNewSession }) {
  const [showQR, setShowQR] = useState(false);
  useEffect(() => { const t = setTimeout(() => setShowQR(true), 200); return () => clearTimeout(t); }, []);

  return (
    <div className="h-screen overflow-hidden bg-white flex flex-col">
      {/* Header */}
      <div className="pt-4 pb-2 px-6 text-center flex-shrink-0">
        <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
          <div className="w-8 h-8 mx-auto mb-2 rounded-full bg-neutral-900 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
          </div>
          <h1 className="font-pixel text-xl text-neutral-900 tracking-wider mb-0.5">PHOTOBOOTH</h1>
          <p className="text-neutral-400 text-xs">Your strip is ready</p>
        </motion.div>
      </div>

      {/* Content */}
      <div className="flex-1 flex items-center justify-center px-6 min-h-0">
        <div className="flex flex-col lg:flex-row items-center justify-center gap-8 lg:gap-12 max-w-4xl w-full">
          {/* Strip preview */}
          <motion.div initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}
            className="flex-shrink-0 flex justify-center">
            <div className="relative">
              <div className="rounded-xl overflow-hidden border border-neutral-200 shadow-sm">
                {stripUrl && <img src={stripUrl} alt="Generated photobooth strip" className="block max-w-[260px] max-h-[58vh] object-contain" loading="lazy" />}
              </div>
              <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 bg-white px-3 py-1 rounded-full border border-neutral-200">
                <span className="text-[0.6rem] text-neutral-400 font-mono">{sessionId?.slice(0, 8)}</span>
              </div>
            </div>
          </motion.div>

          {/* QR + actions */}
          <motion.div initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
            className="flex-1 flex flex-col items-center w-full max-w-sm">
            <h2 className="text-xl font-semibold text-neutral-900 mb-1">Download your strip</h2>
            <p className="text-neutral-400 text-sm mb-4 text-center">Scan with your phone to save it</p>

            {showQR && qrUrl && (
              <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
                className="w-48 h-48 rounded-xl overflow-hidden p-3 mb-5 border border-neutral-200 bg-white shadow-sm">
                <img src={qrUrl} alt="QR code for download" className="w-full h-full object-contain" />
              </motion.div>
            )}

            <div className="w-full flex flex-col gap-3">
              {downloadUrl && (
                <a href={downloadUrl} target="_blank" rel="noopener noreferrer"
                  className="btn-primary w-full text-sm py-3.5">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                  </svg>
                  Open Download Page
                </a>
              )}
              {stripUrl && (
                <a href={stripUrl} download={`photobooth_${sessionId}.png`}
                  className="btn-secondary w-full text-sm py-3.5">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                  </svg>
                  Download Directly
                </a>
              )}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <div className="pb-5 pt-2 flex-shrink-0 flex flex-col items-center gap-3">
        <button onClick={onNewSession} className="btn-ghost" type="button">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          New Session
        </button>
        <div className="flex flex-col items-center gap-1">
          <span className="text-neutral-300 text-[0.55rem] tracking-widest uppercase">Powered by</span>
          <img src="/assets/ceso.png" alt="CESO" className="h-4 object-contain opacity-40" />
        </div>
      </div>
    </div>
  );
}
