import { useState } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { Database, Mail, Lock, LogIn, UserPlus } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login, register, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!email.trim()) {
      setError('Please enter your email')
      return
    }
    if (!password) {
      setError('Please enter your password')
      return
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    setSubmitting(true)
    try {
      if (isRegister) {
        await register(email.trim(), password)
      } else {
        await login(email.trim(), password)
      }
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-transparent">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-slate-200 bg-white/90 backdrop-blur-sm p-8 shadow-xl">
          <div className="flex items-center justify-center gap-2 mb-6">
            <div className="p-2 rounded-xl bg-teal-100">
              <Database className="text-teal-600" size={28} />
            </div>
            <h1 className="text-xl font-semibold text-teal-700">SQL Generator Tool</h1>
          </div>
          <h2 className="text-lg font-medium text-slate-700 text-center mb-6">
            {isRegister ? 'Create an account' : 'Sign in with your email'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-slate-600 mb-1.5 font-medium">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full pl-10 pr-4 py-3 rounded-lg bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500"
                  autoComplete="email"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm text-slate-600 mb-1.5 font-medium">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-3 rounded-lg bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500"
                  autoComplete={isRegister ? 'new-password' : 'current-password'}
                />
              </div>
            </div>
            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-2 text-sm text-red-700">
                {error}
              </div>
            )}
            <button
              type="submit"
              disabled={submitting}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-lg bg-teal-600 hover:bg-teal-500 text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? (
                <span className="animate-pulse">Please wait...</span>
              ) : isRegister ? (
                <>
                  <UserPlus size={20} />
                  Register
                </>
              ) : (
                <>
                  <LogIn size={20} />
                  Sign in
                </>
              )}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-slate-600">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              type="button"
              onClick={() => {
                setIsRegister(!isRegister)
                setError('')
              }}
              className="text-teal-600 hover:text-teal-500 font-medium"
            >
              {isRegister ? 'Sign in' : 'Register'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
