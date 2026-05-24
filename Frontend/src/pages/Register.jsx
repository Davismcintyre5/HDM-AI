// ====================================================================================================
// client/src/pages/Register.jsx
// ====================================================================================================
import { useState, useContext } from 'react'
import { Link } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { UserPlus, Mail, User, Lock, Eye, EyeOff, Sparkles, Check, X, X as Close, FileText, Shield } from 'lucide-react'

const PASSWORD_RULES = [
  { label: 'At least 8 characters', check: (p) => p.length >= 8 },
  { label: 'One uppercase letter', check: (p) => /[A-Z]/.test(p) },
  { label: 'One lowercase letter', check: (p) => /[a-z]/.test(p) },
  { label: 'One number', check: (p) => /\d/.test(p) },
]

const TERMS_SECTIONS = [
  { title: '1. Acceptance of Terms', content: 'By accessing or using HDM AI ("the Service"), you agree to be bound by these Terms of Service. If you do not agree to all terms, do not use the Service. Your continued use constitutes acceptance of any updates to these terms.' },
  { title: '2. Description of Service', content: 'HDM AI provides an artificial intelligence platform including conversational AI, code execution, image generation, content analysis, learning tools, and business data integration. Features may change without prior notice.' },
  { title: '3. User Accounts', content: 'You are responsible for maintaining account security and confidentiality. Provide accurate, complete information during registration. You must be at least 13 years old. One person per account — sharing credentials is prohibited.' },
  { title: '4. Acceptable Use', content: 'Do not use HDM AI for illegal activities, generating harmful content, spreading misinformation, harassing others, violating intellectual property rights, or attempting to breach system security. We reserve the right to suspend accounts.' },
  { title: '5. API Keys', content: 'API keys grant programmatic access to HDM AI. You are fully responsible for all activity under your keys. Revoked keys are permanently deleted. Do not expose keys in client-side code or public repositories.' },
  { title: '6. External Data', content: 'When connecting external systems (ERP, CRM, databases), you warrant you have authorization to access that data. HDM AI acts as a data processor — you remain the data controller for your connected systems.' },
  { title: '7. Intellectual Property', content: 'HDM AI and its original content are protected by copyright and other laws. You retain ownership of data you input. AI-generated outputs are yours to use, but may not be unique — similar prompts may produce similar results.' },
  { title: '8. Limitation of Liability', content: 'HDM AI is provided "as is" without warranties of any kind. We are not liable for indirect, incidental, or consequential damages. Our total liability is limited to the amount paid for the Service in the preceding 12 months.' },
  { title: '9. Termination', content: 'You may delete your account at any time from Settings. We may suspend or terminate accounts for terms violations. Upon termination, your data is permanently deleted. Certain provisions survive termination.' },
  { title: '10. Governing Law', content: 'These terms are governed by applicable laws. Disputes shall be resolved through binding arbitration. Class action waivers apply where permitted. For questions, contact legal@hdmai.com.' },
]

const PRIVACY_SECTIONS = [
  { title: '1. Information We Collect', content: 'We collect email addresses, usernames, and usage metrics (requests, tokens used). Chat content and uploaded files are processed to provide AI responses. API keys are encrypted at rest. We do not collect payment information.' },
  { title: '2. How We Use Information', content: 'Information is used to authenticate users, process AI requests, improve the Service, and prevent abuse. Usage data helps us optimize performance. We do not use your data to train AI models without explicit consent.' },
  { title: '3. Data Storage & Security', content: 'All data is stored in MongoDB databases with access controls. Third-party API keys are encrypted using AES-256-CBC. We use HTTPS for all communications. Regular security reviews are conducted.' },
  { title: '4. Third-Party Providers', content: 'HDM AI uses Groq and Google Gemini for AI processing. Prompts are sent to these providers. External system keys you provide are used only to fetch data at your request. We do not sell or share your data with advertisers.' },
  { title: '5. Cookies & Tracking', content: 'We use essential cookies for authentication (JWT tokens stored locally). No third-party tracking cookies. We do not use analytics services that track you across sites. Session data is stored in your browser.' },
  { title: '6. Data Retention', content: 'Your data is retained while your account is active. Conversations and files are stored until you delete them or your account. Deleted data is permanently removed from our systems within 30 days.' },
  { title: '7. Your Rights', content: 'You have the right to access, correct, or delete your personal data. Export functionality is available upon request. You can delete your account at Settings → Security, which removes all associated data.' },
  { title: '8. Children Privacy', content: 'HDM AI is not intended for users under 13 years of age. We do not knowingly collect data from children. If we learn we have collected data from a child under 13, we will delete it immediately.' },
  { title: '9. International Data', content: 'Data is processed and stored in your deployment region. Cross-border data transfers comply with applicable regulations. Users outside the deployment region consent to data processing in that jurisdiction.' },
  { title: '10. Contact & Updates', content: 'We may update this Privacy Policy periodically. Material changes will be notified via email. For privacy questions or data requests, contact privacy@hdmai.com. Last updated: May 2026.' },
]

export default function Register() {
  const { register } = useContext(AuthContext)
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [focusedPassword, setFocusedPassword] = useState(false)
  const [overlay, setOverlay] = useState(null) // 'terms' | 'privacy'

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email.trim() || !username.trim() || !password) return toast.error('Fill in all fields')
    if (password.length < 8) return toast.error('Password must be at least 8 characters')
    setLoading(true)
    try {
      await register(email, username, password)
      toast.success('Account created!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    }
    setLoading(false)
  }

  const allRulesPassed = PASSWORD_RULES.every(r => r.check(password))
  const passwordStrength = PASSWORD_RULES.filter(r => r.check(password)).length

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-950 px-4">
      {/* Card Frame */}
      <div className="w-full max-w-md relative">
        <div className="absolute -inset-0.5 bg-gradient-to-b from-primary-500/20 to-transparent rounded-2xl blur opacity-50" />
        
        <div className="relative bg-dark-900 border border-dark-700/50 rounded-2xl shadow-2xl overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-primary-500 via-purple-400 to-primary-600" />
          
          {/* Header */}
          <div className="text-center pt-8 pb-2 px-8">
            <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary-500/20 ring-1 ring-primary-500/30">
              <UserPlus size={24} className="text-white" />
            </div>
            <h1 className="text-xl font-bold text-white">Create account</h1>
            <p className="text-dark-400 text-sm mt-1">Get started with HDM AI</p>
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

            {/* Username */}
            <div>
              <label className="block text-xs font-medium text-dark-400 mb-1.5 uppercase tracking-wider">Username</label>
              <div className="relative group">
                <div className="absolute inset-0 bg-primary-500/0 rounded-xl transition-all group-focus-within:bg-primary-500/5" />
                <User size={16} className="absolute left-3.5 top-3 text-dark-500 group-focus-within:text-primary-400 transition-colors" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="relative w-full bg-dark-800 border border-dark-600 rounded-xl px-4 py-2.5 pl-11 text-white placeholder-dark-500 text-sm outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/10 transition-all"
                  placeholder="johndoe"
                  autoComplete="username"
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
                  onFocus={() => setFocusedPassword(true)}
                  onBlur={() => { if (!password) setFocusedPassword(false) }}
                  className="relative w-full bg-dark-800 border border-dark-600 rounded-xl px-4 py-2.5 pl-11 pr-11 text-white placeholder-dark-500 text-sm outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/10 transition-all"
                  placeholder="Min. 8 characters"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-3 text-dark-500 hover:text-dark-300 transition-colors"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>

              {focusedPassword && (
                <div className="mt-2 space-y-1.5">
                  <div className="flex gap-1">
                    {[1, 2, 3, 4].map((i) => (
                      <div
                        key={i}
                        className={`flex-1 h-1 rounded-full transition-all ${
                          passwordStrength >= i
                            ? i <= 2 ? 'bg-red-400' : i === 3 ? 'bg-yellow-400' : 'bg-green-400'
                            : 'bg-dark-700'
                        }`}
                      />
                    ))}
                  </div>
                  {PASSWORD_RULES.map((rule) => {
                    const passed = rule.check(password)
                    return (
                      <div key={rule.label} className="flex items-center gap-2">
                        {passed ? <Check size={12} className="text-green-400" /> : <X size={12} className="text-dark-600" />}
                        <span className={`text-xs ${passed ? 'text-green-400' : 'text-dark-500'}`}>{rule.label}</span>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>

            {/* Legal links */}
            <p className="text-xs text-dark-500 text-center">
              By creating an account, you agree to our{' '}
              <button type="button" onClick={() => setOverlay('terms')} className="text-primary-400 hover:text-primary-300 underline transition-colors">Terms</button>
              {' '}&amp;{' '}
              <button type="button" onClick={() => setOverlay('privacy')} className="text-primary-400 hover:text-primary-300 underline transition-colors">Privacy Policy</button>
            </p>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading || !allRulesPassed}
              className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 active:scale-[0.98]"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <UserPlus size={18} />
              )}
              {loading ? 'Creating account...' : 'Create Account'}
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
              Already have an account?{' '}
              <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>

      {/* Legal Overlay */}
      {overlay && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-dark-900 border border-dark-700 rounded-2xl w-full max-w-lg max-h-[80vh] flex flex-col shadow-2xl">
            <div className="flex items-center justify-between p-5 border-b border-dark-800">
              <h2 className="text-white font-semibold flex items-center gap-2">
                {overlay === 'terms' ? (
                  <FileText size={18} className="text-primary-400" />
                ) : (
                  <Shield size={18} className="text-primary-400" />
                )}
                {overlay === 'terms' ? 'Terms of Service' : 'Privacy Policy'}
              </h2>
              <button onClick={() => setOverlay(null)} className="p-1.5 text-dark-400 hover:text-white rounded-lg hover:bg-dark-800 transition-colors">
                <Close size={18} />
              </button>
            </div>
            <div className="p-5 overflow-y-auto text-sm text-dark-300 leading-relaxed space-y-4">
              {(overlay === 'terms' ? TERMS_SECTIONS : PRIVACY_SECTIONS).map((section) => (
                <div key={section.title}>
                  <h3 className="text-white font-medium text-sm">{section.title}</h3>
                  <p className="mt-1">{section.content}</p>
                </div>
              ))}
            </div>
            <div className="p-4 border-t border-dark-800">
              <button onClick={() => setOverlay(null)} className="btn-primary w-full text-sm">I Understand</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}