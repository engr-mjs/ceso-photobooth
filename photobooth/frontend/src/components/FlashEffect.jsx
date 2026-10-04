import { motion } from 'framer-motion';

export default function FlashEffect({ active }) {
  if (!active) return null;
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: [0, 0.9, 0] }}
      transition={{ duration: 0.2, times: [0, 0.05, 1] }}
      className="fixed inset-0 z-flash pointer-events-none bg-white"
      aria-hidden="true" />
  );
}
