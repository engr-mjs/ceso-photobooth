import { motion } from 'framer-motion';

export default function Countdown({ value }) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="absolute inset-0 flex items-center justify-center z-20 pointer-events-none"
      role="timer" aria-live="assertive" aria-label={`${value} seconds`}>
      <div className="absolute inset-0 bg-white/70" />
      <motion.div key={value}
        initial={{ scale: 0.3, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 1.5, opacity: 0 }}
        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
        className="relative z-10"
      >
        <span className="text-7xl font-light text-neutral-900 tabular-nums">{value}</span>
      </motion.div>
    </motion.div>
  );
}
