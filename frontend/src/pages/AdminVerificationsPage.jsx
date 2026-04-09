import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { ShieldCheck, CheckCircle2, XCircle, FileText, RefreshCw, ExternalLink } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import { useAuth } from '../context/AuthContext'
import { fetchPendingVerifications, verifyUserAccount } from '../services/api'

export default function AdminVerificationsPage() {
  const { token } = useAuth()
  const [pendingList, setPendingList] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionLoadingId, setActionLoadingId] = useState(null)
  const [message, setMessage] = useState('')

  const loadPending = () => {
    setLoading(true)
    fetchPendingVerifications(token)
      .then(setPendingList)
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (token) loadPending()
  }, [token])

  const handleAction = async (userId, action) => {
    setActionLoadingId(userId)
    try {
      await verifyUserAccount(token, userId, action)
      setMessage(`User #${userId} has been ${action === 'APPROVE' ? 'approved' : 'rejected'}.`)
      setPendingList(prev => prev.filter(u => u.id !== userId))
    } catch (err) {
      setMessage(`Error: ${err.message}`)
    } finally {
      setActionLoadingId(null)
    }
  }

  const handleViewDocument = async (userId) => {
    try {
      const res = await fetch(`/api/admin/users/${userId}/document`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to load document')
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      window.open(url, '_blank')
    } catch (err) {
      alert('Could not open document: ' + err.message)
    }
  }

  return (
    <PageWrapper>
      <div style={{ marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--accent-orange)', fontWeight: 700, fontSize: '0.85rem', marginBottom: '8px' }}>
            <ShieldCheck size={16} /> Administrative Portal
          </div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>User ID Verifications</h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Review submitted credentials and grant access for Analyst and Coach roles.
          </p>
        </div>

        <button onClick={loadPending} className="btn-primary" style={{ fontSize: '0.85rem' }}>
          <RefreshCw size={15} /> Refresh Queue
        </button>
      </div>

      {message && (
        <div style={{ padding: '12px 16px', borderRadius: '8px', backgroundColor: 'rgba(0, 210, 255, 0.1)', border: '1px solid rgba(0, 210, 255, 0.25)', color: 'var(--accent-cyan)', fontSize: '0.9rem', marginBottom: '20px' }}>
          {message}
        </div>
      )}

      {loading ? (
        <p style={{ color: 'var(--text-muted)' }}>Loading verification queue...</p>
      ) : pendingList.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '40px' }}>
          <CheckCircle2 size={36} color="var(--accent-green)" style={{ margin: '0 auto 12px auto' }} />
          <h3 style={{ fontSize: '1.2rem', marginBottom: '6px' }}>Verification Queue is Clear</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>There are no analysts or coaches currently awaiting review.</p>
        </div>
      ) : (
        <div className="glass-card" style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>
                <th style={{ padding: '12px 8px' }}>User ID</th>
                <th style={{ padding: '12px 8px' }}>Name</th>
                <th style={{ padding: '12px 8px' }}>Email</th>
                <th style={{ padding: '12px 8px' }}>Requested Role</th>
                <th style={{ padding: '12px 8px' }}>Submitted ID Document</th>
                <th style={{ padding: '12px 8px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pendingList.map(u => (
                <tr key={u.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                  <td style={{ padding: '14px 8px', fontWeight: 700, color: 'var(--text-muted)' }}>#{u.id}</td>
                  <td style={{ padding: '14px 8px', fontWeight: 600 }}>{u.full_name || 'N/A'}</td>
                  <td style={{ padding: '14px 8px', color: 'var(--accent-cyan)' }}>{u.email}</td>
                  <td style={{ padding: '14px 8px' }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: 800,
                      backgroundColor: u.role === 'COACH' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(0, 210, 255, 0.15)',
                      color: u.role === 'COACH' ? 'var(--accent-blue)' : 'var(--accent-cyan)'
                    }}>
                      {u.role}
                    </span>
                  </td>
                  <td style={{ padding: '14px 8px' }}>
                    {u.has_id_document ? (
                      <button
                        onClick={() => handleViewDocument(u.id)}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                          background: 'none',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: '6px',
                          padding: '6px 12px',
                          color: 'var(--text-main)',
                          fontSize: '0.8rem',
                          cursor: 'pointer'
                        }}
                      >
                        <FileText size={14} color="var(--accent-cyan)" />
                        View ID Proof <ExternalLink size={12} />
                      </button>
                    ) : (
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No document</span>
                    )}
                  </td>
                  <td style={{ padding: '14px 8px', textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: '8px' }}>
                      <button
                        onClick={() => handleAction(u.id, 'APPROVE')}
                        disabled={actionLoadingId === u.id}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          padding: '6px 12px',
                          borderRadius: '6px',
                          backgroundColor: 'var(--accent-green)',
                          color: '#fff',
                          border: 'none',
                          fontWeight: 600,
                          fontSize: '0.8rem',
                          cursor: 'pointer'
                        }}
                      >
                        <CheckCircle2 size={14} /> Approve
                      </button>
                      <button
                        onClick={() => handleAction(u.id, 'REJECT')}
                        disabled={actionLoadingId === u.id}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          padding: '6px 12px',
                          borderRadius: '6px',
                          backgroundColor: 'rgba(239, 68, 68, 0.15)',
                          color: 'var(--accent-red)',
                          border: '1px solid rgba(239, 68, 68, 0.3)',
                          fontWeight: 600,
                          fontSize: '0.8rem',
                          cursor: 'pointer'
                        }}
                      >
                        <XCircle size={14} /> Reject
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </PageWrapper>
  )
}