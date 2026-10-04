import { useState } from 'react';
import { motion } from 'framer-motion';

export default function ReviewScreen({ photos, sessionId, onRetake, onGenerate, onStripReady }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setLoading(true); setError(null);
    try {
      const r = await fetch('/api/sessions/' + sessionId + '/generate-strip', { method: 'POST' });
      if (!r.ok) { const e = await r.json(); throw new Error(e.detail || 'Failed'); }
      onStripReady(await r.json());
    } catch (e) { setError(e.message); setLoading(false); }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="min-h-screen flex flex-col items-center justify-center px-6 py-10 bg-white">

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8">
        <h2 className="text-xl font-semibold text-neutral-900 mb-1">Review</h2>
        <p className="text-neutral-400 text-sm">Check your photos before generating the strip</p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08 }}
        className="flex gap-3 mb-8 flex-wrap justify-center">
        {photos.map((p, i) => (
          <motion.div key={i} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.05 + i * 0.06 }}
            className="relative">
            <div className="w-40 h-28 rounded-lg overflow-hidden border border-neutral-200">
              <img src={p.data} alt={`Photo ${i+1}`} className="w-full h-full object-cover" />
            </div>
            <span className="absolute -bottom-2 left-1/2 -translate-x-1/2 text-[0.6rem] font-medium text-neutral-400 bg-white px-1.5">
              {i + 1}
            </span>
          </motion.div>
        ))}
      </motion.div>

      {error && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          className="rounded-md px-4 py-2.5 mb-6 text-sm text-red-600 bg-red-50 border border-red-100" role="alert">
          {error}
        </motion.div>
      )}

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
        className="flex gap-2.5">
        <button onClick={onRetake} disabled={loading} className="btn-secondary" type="button">
          Retake
        </button>
        <button onClick={handleGenerate} disabled={loading} className="btn-primary" type="button">
          {loading ? (
            <><div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Generating...</>
          ) : 'Generate Strip'}
        </button>
      </motion.div>

      <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
        className="mt-4 text-neutral-300 text-[0.6rem] font-mono">
        {sessionId}
      </motion.p>
    </motion.div>
  );
}
