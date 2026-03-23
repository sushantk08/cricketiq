import React from 'react'
import { motion } from 'framer-motion'

export default function PageWrapper({ children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '32px 24px'
      }}
    >
      {children}
    </motion.div>
  )
}