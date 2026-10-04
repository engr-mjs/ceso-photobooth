import { useState, useCallback, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Webcam from 'react-webcam';
import { useCamera } from '../hooks/useCamera';
import { photoAPI } from '../services/api';
import Countdown from './Countdown';
import FlashEffect from './FlashEffect';

const TOTAL = 3, CD_START = 3;
const MAX_UPLOAD_CHARS = 2500000;

const shrinkIfNeeded = (dataUrl) => new Promise((resolve) => {
  if (!dataUrl || dataUrl.length <= MAX_UPLOAD_CHARS) {
    resolve(dataUrl);
    return;
  }
  const img = new Image();
  img.onload = () => {
    const maxW = 1600;
    const scale = Math.min(1, maxW / img.width);
    const w = Math.round(img.width * scale);
    const h = Math.round(img.height * scale);
    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    canvas.getContext('2d').drawImage(img, 0, 0, w, h);
    resolve(canvas.toDataURL('image/jpeg', 0.9));
  };
  img.onerror = () => resolve(dataUrl);
  img.src = dataUrl;
});

export default function CaptureScreen({ sessionId, deviceId, onCaptureComplete, onCancel }) {
  const { webcamRef, isReady, error: camErr, onUserMedia, onUserMediaError, capture, getCameraConstraints, stopStream } = useCamera(deviceId);
  const [idx, setIdx] = useState(0);
  const [cd, setCd] = useState(null);
  const [busy, setBusy] = useState(false);
  const [flash, setFlash] = useState(false);
  const [previews, setPreviews] = useState([]);
  const cdRef = useRef(null);

  useEffect(() => {
    if (!busy && idx < TOTAL) startCd();
  }, [idx, busy]);

  const startCd = () => {
    let c = CD_START; setCd(c);
    cdRef.current = setInterval(() => { c--; if (c > 0) setCd(c); else { clearInterval(cdRef.current); setCd(null); doCapture(); } }, 1000);
  };

  const doCapture = useCallback(async () => {
    if (!webcamRef.current || busy) return;
    setBusy(true); setFlash(true);
    setTimeout(() => setFlash(false), 200);
    const img = capture();
    if (!img) { setBusy(false); return; }
    const newPreviews = [...previews, { i: idx, data: img }];
    setPreviews(newPreviews);
    try {
      const uploadData = await shrinkIfNeeded(img);
      await photoAPI.uploadBase64(sessionId, idx, uploadData);
    } catch(e) { console.error(e); }
    setTimeout(() => {
      setBusy(false);
      const next = idx + 1;
      if (next >= TOTAL) onCaptureComplete(newPreviews);
      else setIdx(next);
    }, 600);
  }, [idx, sessionId, previews, busy, capture, webcamRef, onCaptureComplete]);

  useEffect(() => () => {
    if (cdRef.current) clearInterval(cdRef.current);
    stopStream();
  }, [stopStream]);

  const handleCancel = () => {
    stopStream();
    onCancel();
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <FlashEffect active={flash} />

      {/* Header */}
      <div className="pt-4 pb-2 px-6 flex justify-between items-center">
        <button onClick={handleCancel} className="btn-ghost" type="button">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          Cancel
        </button>
        <div className="flex items-center gap-3">
          <span className="text-neutral-400 text-xs tabular-nums font-mono">{idx + 1} / {TOTAL}</span>
          <div className="flex gap-1.5">
            {Array.from({ length: TOTAL }).map((_, i) => (
              <div key={i} className="w-2 h-2 rounded-full transition-colors" style={{
                background: i < idx ? '#171717' : i === idx ? '#171717' : '#E5E5E5',
              }} />
            ))}
          </div>
        </div>
      </div>

      {/* Camera */}
      <div className="flex-1 flex items-center justify-center px-4">
        <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-3xl relative">
          <div className="relative rounded-xl overflow-hidden bg-neutral-100 border border-neutral-200" style={{ aspectRatio: '4/3' }}>
            {camErr ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center p-6">
                <p className="text-neutral-400 text-sm text-center">{camErr}</p>
              </div>
            ) : (
              <>
                <Webcam ref={webcamRef} audio={false} screenshotFormat="image/png" screenshotQuality={1.0}
                  mirrored
                  videoConstraints={getCameraConstraints()} onUserMedia={onUserMedia} onUserMediaError={onUserMediaError}
                  className="w-full h-full object-cover" key={deviceId} />
                {!isReady && (
                  <div className="absolute inset-0 flex items-center justify-center bg-neutral-100">
                    <div className="w-5 h-5 border-2 border-neutral-200 border-t-neutral-900 rounded-full animate-spin" />
                  </div>
                )}
              </>
            )}
            <AnimatePresence>{cd !== null && <Countdown value={cd} />}</AnimatePresence>
          </div>
        </motion.div>
      </div>

      {/* Thumbnails */}
      <div className="pb-4 pt-3 flex justify-center gap-3">
        {previews.map((p, i) => (
          <motion.div key={i} initial={{ opacity: 0, scale: 0.8, y: 12 }} animate={{ opacity: 1, scale: 1, y: 0 }}
            className="w-20 h-14 rounded-lg overflow-hidden border border-neutral-200">
            <img src={p.data} alt={`Photo ${p.i+1}`} className="w-full h-full object-cover" />
          </motion.div>
        ))}
        {Array.from({ length: TOTAL - previews.length }).map((_, i) => (
          <div key={`empty-${i}`} className="w-20 h-14 rounded-lg border border-dashed border-neutral-200" />
        ))}
      </div>
    </div>
  );
}
