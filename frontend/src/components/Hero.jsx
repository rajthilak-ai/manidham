import { motion } from 'framer-motion'
import { IMAGES } from '../constants/images'

export default function Hero() {
  return (
    <section id="home" className="hero">
      <div className="hero-bg" style={{ backgroundImage: `url(${IMAGES.hero})` }} />
      <div className="hero-overlay" />
      <div className="hero-shapes">
        <motion.div
          className="shape shape-1"
          animate={{ y: [0, -18, 0], rotate: [0, 8, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="shape shape-2"
          animate={{ y: [0, 22, 0], rotate: [0, -10, 0] }}
          transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      <div className="container hero-content">
        <motion.p
          className="eyebrow"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          Serving communities with compassion
        </motion.p>
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
        >
          Empowering lives through
          <span> Education</span>, <span>Blood</span>, and <span>Food</span>
        </motion.h1>
        <motion.p
          className="hero-subtitle"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          Manidham Trust connects underprivileged children with learning opportunities,
          links blood donors directly to patients in need, and redistributes surplus food
          from hotels to orphanages and old age homes.
        </motion.p>
        <motion.div
          className="hero-actions"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.65 }}
        >
          <a href="#get-involved" className="btn btn-primary">Join the Mission</a>
          <a href="#blood" className="btn btn-secondary">Find a Donor</a>
        </motion.div>

        <div className="hero-stats">
          {[
            ['3', 'Core Initiatives'],
            ['100%', 'Direct Impact'],
            ['24/7', 'Community Support'],
          ].map(([value, label], index) => (
            <motion.div
              key={label}
              className="stat-card"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8 + index * 0.1 }}
            >
              <strong>{value}</strong>
              <span>{label}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
