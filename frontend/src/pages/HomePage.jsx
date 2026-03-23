import React from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { PlayCircle, Compass, Bot, TrendingUp, ShieldCheck, Zap } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'

const featureCards = [
  {
    title: 'Decision Replay',
    desc: 'Counterfactual "what-if" engine. Evaluate alternative bowler and batting choices with win-probability impact.',
    path: '/replay',
    icon: PlayCircle,
    color: 'var(--accent-cyan)'
  },
  {
    title: 'Turning Point Detector',
    desc: 'Automated inflection detector ranking high-leverage wickets and momentum swings ball-by-ball.',
    path: '/matches',
    icon: Zap,
    color: 'var(--accent-orange)'
  },
  {
    title: 'Scenario Simulator',
    desc: 'Sandbox simulator to alter score, wickets, and overs to recalculate win likelihood and risk tiers.',
    path: '/scenarios',
    icon: Compass,
    color: 'var(--accent-green)'
  },
  {
    title: 'AI Match Analyst',
    desc: 'Grounded natural-language match breakdowns synthesized from PostgreSQL ground-truth telemetry.',
    path: '/ai-analyst',
    icon: Bot,
    color: 'var(--accent-blue)'
  },
]

export default function HomePage() {
  return (
    <PageWrapper>
      {/* Hero Section with Spring Animation */}
      <div style={{ textAlign: 'center', padding: '40px 0 60px 0' }}>
        <motion.span
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 14px',
            borderRadius: '20px',
            backgroundColor: 'rgba(0, 210, 255, 0.1)',
            border: '1px solid rgba(0, 210, 255, 0.3)',
            color: 'var(--accent-cyan)',
            fontSize: '0.85rem',
            fontWeight: 600,
            marginBottom: '16px'
          }}
        >
          <TrendingUp size={15} /> Machine Learning & Strategy Intelligence
        </motion.span>

        <motion.h1
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          style={{ fontSize: '3rem', fontWeight: 800, lineHeight: 1.15, marginBottom: '16px' }}
        >
          Cricket Intelligence Beyond the <br />
          <span style={{
            background: 'linear-gradient(135deg, #00d2ff, #3b82f6)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Standard Scorecard
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          style={{ color: 'var(--text-muted)', fontSize: '1.15rem', maxWidth: '640px', margin: '0 auto 28px auto' }}
        >
          Explore real-time win probabilities, investigate tactical turning points, and simulate counterfactual decisions.
        </motion.p>
      </div>

      {/* Interactive Feature Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '20px'
      }}>
        {featureCards.map((card, i) => {
          const Icon = card.icon
          return (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.08 }}
              whileHover={{ y: -4 }}
              className="glass-card"
              style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
            >
              <div>
                <div style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: card.color,
                  marginBottom: '16px'
                }}>
                  <Icon size={22} />
                </div>
                <h3 style={{ fontSize: '1.2rem', marginBottom: '8px' }}>{card.title}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.5, marginBottom: '20px' }}>
                  {card.desc}
                </p>
              </div>

              <Link to={card.path} className="btn-primary" style={{ width: 'fit-content', fontSize: '0.85rem' }}>
                Launch Module &rarr;
              </Link>
            </motion.div>
          )
        })}
      </div>
    </PageWrapper>
  )
}