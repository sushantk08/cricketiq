import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Bot, Send, Sparkles, ShieldCheck, Award, Zap, RefreshCw } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import { fetchMatches, fetchAIMatchAnalysis, askAIAnalyst } from '../services/api'

const samplePrompts = [
  'What caused the biggest shift in win probability?',
  'Who was the most disciplined bowler in the death overs?',
  'Why did the chasing team lose momentum in the middle overs?',
]

export default function AIAnalystPage() {
  const [matches, setMatches] = useState([])
  const [selectedMatchId, setSelectedMatchId] = useState(1)
  const [report, setReport] = useState(null)
  const [reportLoading, setReportLoading] = useState(false)

  // Chat state
  const [question, setQuestion] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [chatLoading, setChatLoading] = useState(false)

  useEffect(() => {
    fetchMatches().then(data => {
      setMatches(data)
      const matchWithData = data.find(m => m.id === 1) || data[0]
      if (matchWithData) setSelectedMatchId(matchWithData.id)
    }).catch(console.error)
  }, [])

  const handleGenerateReport = async () => {
    if (!selectedMatchId) return
    setReportLoading(true)
    try {
      const data = await fetchAIMatchAnalysis(Number(selectedMatchId))
      setReport(data)
    } catch (err) {
      console.error(err)
    } finally {
      setReportLoading(false)
    }
  }

  const handleAsk = async (queryText) => {
    const q = queryText || question
    if (!q.trim()) return
    setChatLoading(true)

    const userMessage = { sender: 'user', text: q }
    setChatHistory(prev => [...prev, userMessage])
    setQuestion('')

    try {
      const res = await askAIAnalyst(q, Number(selectedMatchId))
      const aiMessage = {
        sender: 'ai',
        text: res.answer,
        references: res.referenced_data
      }
      setChatHistory(prev => [...prev, aiMessage])
    } catch (err) {
      setChatHistory(prev => [...prev, { sender: 'ai', text: 'Sorry, I encountered an issue analyzing telemetry data.' }])
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <PageWrapper>
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--accent-blue)', fontWeight: 700, fontSize: '0.85rem', marginBottom: '8px' }}>
          <Bot size={16} /> Grounded Cricket Strategy Assistant
        </div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>AI Match Analyst</h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Synthesize tactical match reports and ask natural-language strategy questions grounded in PostgreSQL telemetry.
        </p>
      </div>

      {/* Match Selection Header */}
      <div className="glass-card" style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <label style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--accent-cyan)' }}>
            Match Context:
          </label>
          <select
            value={selectedMatchId}
            onChange={e => { setSelectedMatchId(Number(e.target.value)); setReport(null); }}
            style={{
              padding: '8px 14px',
              borderRadius: '8px',
              backgroundColor: 'var(--bg-main)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-main)',
              fontSize: '0.9rem',
              minWidth: '320px'
            }}
          >
            {matches.map(m => (
              <option key={m.id} value={m.id}>
                {m.title} {m.id === 1 ? '★ (Full Match Data)' : ''}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleGenerateReport}
          disabled={reportLoading}
          className="btn-primary"
          style={{ fontSize: '0.85rem' }}
        >
          {reportLoading ? <RefreshCw size={15} className="animate-spin" /> : <Sparkles size={15} />}
          {reportLoading ? 'Synthesizing...' : 'Generate Factual Match Report'}
        </button>
      </div>

      {/* Generated Report Card */}
      {report && (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card"
          style={{ marginBottom: '32px', border: '1px solid rgba(0, 210, 255, 0.35)' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>
              AI MATCH REPORT • {report.match_title}
            </span>
            <div
  style={{
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    color: report.grounded_in_database_facts
      ? 'var(--accent-green)'
      : 'var(--accent-orange)',
    fontSize: '0.75rem',
    fontWeight: 700,
  }}
>
  <ShieldCheck size={14} />
  {report.grounded_in_database_facts
    ? 'Grounded in Database Facts'
    : 'Generated Analysis — Verify Facts'}
</div>
          </div>

          <p style={{ fontSize: '1.05rem', lineHeight: 1.6, marginBottom: '20px', color: 'var(--text-main)' }}>
            {report.summary}
          </p>

          {/* Top Performers */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px', marginBottom: '20px' }}>
            <div style={{ backgroundColor: 'var(--bg-main)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Top Batting Performer</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>{report.best_batter}</div>
            </div>

            <div style={{ backgroundColor: 'var(--bg-main)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Top Bowling Performer</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-orange)' }}>{report.best_bowler}</div>
            </div>
          </div>

          {/* Key Turning Points List */}
          {report.turning_point_insights.length > 0 && (
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Zap size={14} /> Critical Match Turning Points
              </div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {report.turning_point_insights.map((pt, i) => (
                  <li key={i} style={{ fontSize: '0.85rem', color: 'var(--text-muted)', paddingLeft: '12px', borderLeft: '2px solid var(--accent-cyan)' }}>
                    {pt}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </motion.div>
      )}

      {/* Strategy Q&A Section */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.15rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Bot size={20} color="var(--accent-cyan)" /> Ask the Strategy Intelligence Assistant
        </h3>

        {/* Quick Prompts */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleAsk(p)}
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-muted)',
                padding: '6px 12px',
                borderRadius: '16px',
                fontSize: '0.8rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent-cyan)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Chat Stream Window */}
        <div style={{ minHeight: '160px', maxHeight: '360px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '20px', paddingRight: '8px' }}>
          {chatHistory.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', margin: 'auto' }}>
              Ask any tactical question about match leverage, bowling matchups, or phase trends above.
            </p>
          ) : (
            chatHistory.map((msg, i) => (
              <div
                key={i}
                style={{
                  alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '82%',
                  backgroundColor: msg.sender === 'user' ? 'var(--accent-blue)' : 'var(--bg-main)',
                  border: msg.sender === 'user' ? 'none' : '1px solid var(--border-subtle)',
                  color: '#ffffff',
                  padding: '12px 16px',
                  borderRadius: '12px',
                  fontSize: '0.9rem',
                  lineHeight: 1.5
                }}
              >
                <div>{msg.text}</div>
                
                
              </div>
            ))
          )}
        </div>

        {/* Chat Input Bar */}
        <form onSubmit={e => { e.preventDefault(); handleAsk(); }} style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="Ask about win probability swings, phase execution, or matchups..."
            style={{
              flex: 1,
              padding: '12px 16px',
              borderRadius: '8px',
              backgroundColor: 'var(--bg-main)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-main)',
              fontSize: '0.9rem'
            }}
          />
          <button
            type="submit"
            disabled={chatLoading || !question.trim()}
            className="btn-primary"
            style={{ padding: '0 20px' }}
          >
            {chatLoading ? <RefreshCw size={16} className="animate-spin" /> : <Send size={16} />}
          </button>
        </form>
      </div>
    </PageWrapper>
  )
}