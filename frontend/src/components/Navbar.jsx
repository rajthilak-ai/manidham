import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

const links = [
  { href: '#home', label: 'Home' },
  { href: '#education', label: 'Education' },
  { href: '#blood', label: 'Blood Donation' },
  { href: '#food', label: 'Food Redistribution' },
  { href: '#get-involved', label: 'Get Involved' },
  { href: '#admin', label: 'Dashboard' },
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <motion.header
      className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      <div className="container navbar-inner">
        <a href="#home" className="brand">
          <span className="brand-mark">M</span>
          <span>
            <strong>Manidham</strong>
            <small>Trust for Humanity</small>
          </span>
        </a>

        <button
          type="button"
          className="menu-toggle"
          aria-label="Toggle menu"
          onClick={() => setOpen((value) => !value)}
        >
          <span />
          <span />
          <span />
        </button>

        <nav className={`nav-links ${open ? 'open' : ''}`}>
          {links.map((link) => (
            <a key={link.href} href={link.href} onClick={() => setOpen(false)}>
              {link.label}
            </a>
          ))}
        </nav>
      </div>
    </motion.header>
  )
}
