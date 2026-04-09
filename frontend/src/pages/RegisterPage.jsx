import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { UserPlus, AlertCircle, FileText, CheckCircle } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import { registerUser, loginUser, fetchCurrentUser } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState('ANALYST')
  const [idFile, setIdFile] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [pendingNotice, setPendingNotice] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if ((role === 'ANALYST' || role === 'COACH') && !idFile) {
      setError(`Please upload an ID verification document for the ${role} role.`)
      return
    }

    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('email', email)
      formData.append('password', password)
      formData.append('full_name', fullName)
      formData.append('role', role)
      if (idFile) {
        formData.append('id_document', idFile)
      }

      const registered = await registerUser(formData)

      if (registered.verification_status === 'PENDING') {
        setPendingNotice(true)
      } else {
        // Fans are auto-approved -> auto log in
        const tokenData = await loginUser({ email, password })
        const profile = await fetchCurrentUser(tokenData.access_token)
        login(tokenData.access_token, profile)
        navigate('/')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (pendingNotice) {
    return (
      <PageWrapper>
        <div style={{ maxWidth: '480px', margin: '60px auto', textAlign: 'center' }} className="glass-card">
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '14px',
            backgroundColor: 'rgba(0, 210, 255, 0.12)',
            color: 'var(--accent-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px auto'
          }}>
            <CheckCircle size={28} />
          </div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, marginBottom: '12px' }}>Registration Submitted</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '24px' }}>
            Your account (<strong style={{ color: 'var(--text-main)' }}>{email}</strong>) has been registered as <strong style={{ color: 'var(--accent-cyan)' }}>{role}</strong> and is currently <strong>pending administrator approval</strong>.
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '24px' }}>
            An administrator will review your uploaded ID document. You will be able to log in once approved.
          </p>
          <Link to="/login" className="btn-primary" style={{ display: 'inline-flex', width: '100%', justifyContent: 'center' }}>
            Return to Login
          </Link>
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper>
      <div style={{ maxWidth: '460px', margin: '30px auto' }}>
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card"
        >
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              backgroundColor: 'rgba(0, 210, 255, 0.1)',
              color: 'var(--accent-cyan)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 12px auto'
            }}>
              <UserPlus size={24} />
            </div>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Create an Account</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
              Join CricketIQ with role-based analytical privileges.
            </p>
          </div>

          {error && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 12px', borderRadius: '6px', backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--accent-red)', fontSize: '0.85rem', marginBottom: '18px' }}>
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                Full Name
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                placeholder="e.g. Rahul Dravid"
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-subtle)', color: 'var(--text-main)', fontSize: '0.9rem' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="coach@cricketiq.com"
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-subtle)', color: 'var(--text-main)', fontSize: '0.9rem' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-subtle)', color: 'var(--text-main)', fontSize: '0.9rem' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                Platform Role
              </label>
              <select
                value={role}
                onChange={e => { setRole(e.target.value); setError(''); }}
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-subtle)', color: 'var(--text-main)', fontSize: '0.9rem' }}
              >
                <option value="ANALYST">ANALYST (Requires ID Verification)</option>
                <option value="COACH">COACH (Requires ID Verification)</option>
                <option value="FAN">FAN (Immediate Access)</option>
              </select>
            </div>

            {/* Conditional ID Document Upload for Analyst & Coach */}
            {(role === 'ANALYST' || role === 'COACH') && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                style={{
                  padding: '14px',
                  backgroundColor: 'var(--bg-main)',
                  border: '1px dashed var(--accent-cyan)',
                  borderRadius: '8px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-cyan)', fontSize: '0.85rem', fontWeight: 700 }}>
                  <FileText size={16} /> Upload ID / Accreditation Proof
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Upload an ID badge, coaching accreditation, or analyst certificate for admin review.
                </p>
                <input
                  type="file"
                  required
                  accept="image/*,.pdf,.txt,.doc,.docx"
                  onChange={e => setIdFile(e.target.files[0])}
                  style={{ fontSize: '0.85rem', color: 'var(--text-main)', marginTop: '4px' }}
                />
              </motion.div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '12px', marginTop: '6px' }}
            >
              {loading ? 'Submitting Application...' : 'Register'}
            </button>
          </form>

          <p style={{ textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '20px' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>Log In</Link>
          </p>
        </motion.div>
      </div>
    </PageWrapper>
  )
}