// ====================================================================================================
// client/src/pages/Login.jsx
// ====================================================================================================
import { useState, useContext } from 'react'
import { Link } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { LogIn, Mail, Lock, Eye, EyeOff, Sparkles } from 'lucide-react'

export default function Login() {
  const { login } = useContext(AuthContext)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email.trim() || !password) return toast.error('Fill in all fields')
    setLoading(true)
    try {
      await login(email, password)
      toast.success('Welcome back!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-950 px-4">
      {/* Card Frame */}
      <div className="w-full max-w-md relative">
        {/* Subtle glow behind card */}
        <div className="absolute -inset-0.5 bg-gradient-to-b from-primary-500/20 to-transparent rounded-2xl blur opacity-50" />
        
        {/* Card */}
        <div className="relative bg-dark-900 border border-dark-700/50 rounded-2xl shadow-2xl overflow-hidden">
          {/* Top accent bar */}
          <div className="h-1 bg-gradient-to-r from-primary-500 via-primary-400 to-primary-600" />
          
          {/* Header */}
          <div className="text-center pt-8 pb-2 px-8">
            <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary-500/20 ring-1 ring-primary-500/30">
              <Sparkles size={24} className="text-white" />
            </div>
            <h1 className="text-xl font-bold text-white">Welcome back</h1>
            <p className="text-dark-400 text-sm mt-1">Sign in to your HDM AI account</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="px-8 pb-8 pt-4 space-y-4">
            {/* Email */}
            <div>
              <label className="block text-xs font-medium text-dark-400 mb-1.5 uppercase tracking-wider">Email</label>
              <div className="relative group">
                <div className="absolute inset-0 bg-primary-500/0 rounded-xl transition-all group-focus-within:bg-primary-500/5" />
                <Mail size={16} className="absolute left-3.5 top-3 text-dark-500 group-focus-within:text-primary-400 transition-colors" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="relative w-full bg-dark-800 border border-dark-600 rounded-xl px-4 py-2.5 pl-11 text-white placeholder-dark-500 text-sm outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/10 transition-all"
                  placeholder="you@example.com"
                  autoComplete="email"
                  autoFocus
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-medium text-dark-400 mb-1.5 uppercase tracking-wider">Password</label>
              <div className="relative group">
                <div className="absolute inset-0 bg-primary-500/0 rounded-xl transition-all group-focus-within:bg-primary-500/5" />
                <Lock size={16} className="absolute left-3.5 top-3 text-dark-500 group-focus-within:text-primary-400 transition-colors" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="relative w-full bg-dark-800 border border-dark-600 rounded-xl px-4 py-2.5 pl-11 pr-11 text-white placeholder-dark-500 text-sm outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/10 transition-all"
                  placeholder="••••••••"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-3 text-dark-500 hover:text-dark-300 transition-colors"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 disabled:cursor-wait text-white font-medium py-2.5 rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 active:scale-[0.98]"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <LogIn size={18} />
              )}
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Footer */}
          <div className="px-8 pb-6 text-center">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex-1 h-px bg-dark-800" />
              <span className="text-xs text-dark-600">or</span>
              <div className="flex-1 h-px bg-dark-800" />
            </div>
            <p className="text-dark-500 text-sm">
              Don't have an account?{' '}
              <Link to="/register" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
                Create one
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}