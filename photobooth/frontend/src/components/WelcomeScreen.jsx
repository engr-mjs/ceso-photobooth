import { motion } from 'framer-motion';
import { sessionAPI } from '../services/api';

export default function WelcomeScreen({ onStartSession, serverOnline }) {
  const handleStart = async () => {
    try {
      const r = await sessionAPI.create();
      onStartSession(r.data.session_id);
    } catch (e) {
      console.error('Failed to create session', e);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Main content centered */}
      <div className="flex-1 flex flex-col items-center justify-center px-6">
        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="font-pixel text-5xl sm:text-6xl lg:text-7xl text-neutral-900 tracking-wider mb-3"
        >
          PHOTOBOOTH
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-neutral-400 text-lg sm:text-xl font-light mb-12"
        >
          Capture memories instantly
        </motion.p>

        {/* Start button */}
        <motion.button
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={handleStart}
          className="px-16 py-5 rounded-xl text-base font-bold tracking-wide cursor-pointer border-none bg-neutral-900 text-white shadow-lg hover:bg-neutral-800 transition-colors"
          type="button"
        >
          START
        </motion.button>
      </div>

      {/* Footer */}
      <div className="pb-8 flex flex-col items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: serverOnline ? '#22C55E' : '#EF4444' }} />
          <span className="text-neutral-400 text-xs">{serverOnline ? 'Connected' : 'Offline'}</span>
        </div>
        <div className="flex flex-col items-center gap-1.5">
          <span className="text-neutral-300 text-[0.6rem] tracking-widest uppercase">Powered by</span>
          <img src="/assets/ceso.png" alt="CESO" className="h-5 object-contain opacity-50" />
        </div>
      </div>
    </div>
  );
}
