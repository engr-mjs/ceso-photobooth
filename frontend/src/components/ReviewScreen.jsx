import { motion } from 'framer-motion';

const ReviewScreen = ({ photos, onRetake, onGenerate, error }) => {
  return (
    <div className="text-center">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-primary-500 mb-2">
          Review Your Photos
        </h2>
        <p className="text-surface-500">
          Check your photos before generating the strip
        </p>
      </motion.div>

      <div className="grid grid-cols-3 gap-3 sm:gap-4 max-w-2xl mx-auto mb-8">
        {photos.map((photo, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: index * 0.15 }}
            className="relative aspect-[4/3] rounded-2xl overflow-hidden shadow-medium"
          >
            <img
              src={photo}
              alt={`Captured photo ${index + 1}`}
              className="w-full h-full object-cover"
              style={{ transform: 'scaleX(-1)' }}
            />
            <div className="absolute top-2 left-2 w-7 h-7 rounded-lg bg-primary-500/90 backdrop-blur-sm flex items-center justify-center">
              <span className="text-white text-xs font-bold">{index + 1}</span>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="flex flex-col sm:flex-row items-center justify-center gap-4"
      >
        <button
          onClick={onRetake}
          className="w-full sm:w-auto px-8 py-3.5 bg-surface-100 text-surface-500 font-semibold rounded-2xl hover:bg-surface-200 transition-all duration-300 flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Retake All
        </button>

        <button
          onClick={onGenerate}
          className="w-full sm:w-auto px-8 py-3.5 bg-primary-500 text-white font-semibold rounded-2xl shadow-medium hover:shadow-large hover:bg-primary-600 transition-all duration-300 flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Generate Strip
        </button>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-red-50 border border-red-200 rounded-2xl text-red-600 text-sm max-w-md mx-auto"
        >
          {error}
        </motion.div>
      )}
    </div>
  );
};

export default ReviewScreen;
