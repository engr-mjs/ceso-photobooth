import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const PHASES = [
  { label: 'Loading photos...', dur: 900 },
  { label: 'Applying template...', dur: 1100 },
  { label: 'Generating strip...', dur: 900 },
  { label: 'Creating QR code...', dur: 700 },
  { label: 'Finalizing...', dur: 400 },
];

export default function ProcessingScreen({ sessionId, onComplete }) {
  const [phase, setPhase] = useState(0);
  const [prog, setProg] = useState(0);

  useEffect(() => {
    let t, p;
    if (phase < PHASES.length) {
      const inc = 100 / (PHASES[phase].dur / 40);
      p = setInterval(() => setProg(v => Math.min(v + inc, 100)), 40);
      t = setTimeout(() => { setPhase(v => v + 1); setProg(0); }, PHASES[phase].dur);
    } else {
      (async () => {
        try {
          const r = await fetch('/api/sessions/' + sessionId + '/generate-strip', { method: 'POST' });
          if (!r.ok) throw new Error((await r.json()).detail || 'Failed');
          onComplete(await r.json());
        } catch (e) { console.error(e); setPhase(0); setProg(0); }
      })();
    }
    return () => { clearTimeout(t); clearInterval(p); };
  }, [phase]);

  const total = phase < PHASES.length ? ((phase / PHASES.length) * 100) + (prog / PHASES.length) : 100;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="min-h-screen flex flex-col items-center justify-center px-6 bg-white">

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
        className="flex flex-col items-center">
        <div className="w-10 h-10 rounded-full border-2 border-neutral-100 border-t-neutral-900 animate-spin mb-6" />

        <h2 className="text-lg font-semibold text-neutral-900 mb-1">Creating your strip</h2>
        <p className="text-neutral-400 text-sm mb-6" aria-live="polite">
          {phase < PHASES.length ? PHASES[phase].label : 'Done'}
        </p>

        <div className="w-48 h-1 rounded-full overflow-hidden bg-neutral-100 mb-2"
          role="progressbar" aria-valuenow={Math.round(Math.min(total, 100))} aria-valuemin={0} aria-valuemax={100}>
          <div className="h-full rounded-full bg-neutral-900 transition-all duration-200 ease-out"
            style={{ width: Math.min(total, 100) + '%' }} />
        </div>
        <span className="text-neutral-300 text-[0.6rem] tabular-nums">{Math.round(Math.min(total, 100))}%</span>

        <div className="mt-4 flex gap-1">
          {PHASES.map((_, i) => (
            <div key={i} className="w-1 h-1 rounded-full transition-colors duration-150" style={{
              background: i <= phase ? '#171717' : '#E5E5E5',
            }} />
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}
