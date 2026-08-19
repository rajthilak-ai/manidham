import { useEffect, useRef } from 'react'
import { motion, useInView, useScroll, useTransform } from 'framer-motion'

export function FadeIn({ children, delay = 0, className = '' }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-80px' })

  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, y: 48 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  )
}

export function ParallaxSection({ image, children, className = '' }) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  })
  const y = useTransform(scrollYProgress, [0, 1], ['-12%', '12%'])

  return (
    <section ref={ref} className={`parallax-section ${className}`}>
      <motion.div className="parallax-bg" style={{ backgroundImage: `url(${image})`, y }} />
      <div className="parallax-overlay" />
      <div className="parallax-content">{children}</div>
    </section>
  )
}

export function TiltCard({ children, className = '' }) {
  const ref = useRef(null)

  useEffect(() => {
    const card = ref.current
    if (!card) return undefined

    const handleMove = (e) => {
      const rect = card.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      const rotateX = ((y - rect.height / 2) / rect.height) * -8
      const rotateY = ((x - rect.width / 2) / rect.width) * 8
      card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`
    }

    const reset = () => {
      card.style.transform = 'perspective(900px) rotateX(0) rotateY(0) translateY(0)'
    }

    card.addEventListener('mousemove', handleMove)
    card.addEventListener('mouseleave', reset)
    return () => {
      card.removeEventListener('mousemove', handleMove)
      card.removeEventListener('mouseleave', reset)
    }
  }, [])

  return (
    <div ref={ref} className={`tilt-card ${className}`}>
      {children}
    </div>
  )
}
