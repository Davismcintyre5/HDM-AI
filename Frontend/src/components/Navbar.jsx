import { useContext, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { MessageSquare, BookOpen, Code2, Image, FileSearch, Settings, Key, LogOut, Menu, X } from 'lucide-react'

const navItems = [
  { to: '/chat', label: 'Chat', icon: MessageSquare },
  { to: '/learn', label: 'Learn', icon: BookOpen },
  { to: '/code', label: 'Code', icon: Code2 },
  { to: '/image', label: 'Image', icon: Image },
  { to: '/analyze', label: 'Analyze', icon: FileSearch },
]

export default function Navbar() {
  const { user, logout } = useContext(AuthContext)
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-900/95 backdrop-blur border-b border-dark-700">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/chat" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">HDM</span>
            </div>
            <span className="text-white font-semibold hidden sm:block">HDM AI</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                  location.pathname === to
                    ? 'bg-primary-600/20 text-primary-400'
                    : 'text-dark-300 hover:text-white hover:bg-dark-800'
                }`}
              >
                <Icon size={16} />
                {label}
              </Link>
            ))}
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            <Link
              to="/settings"
              className={`p-2 rounded-lg transition-colors ${
                location.pathname.startsWith('/settings')
                  ? 'bg-primary-600/20 text-primary-400'
                  : 'text-dark-300 hover:text-white hover:bg-dark-800'
              }`}
            >
              <Settings size={18} />
            </Link>
            <button
              onClick={logout}
              className="p-2 text-dark-300 hover:text-red-400 hover:bg-dark-800 rounded-lg transition-colors"
            >
              <LogOut size={18} />
            </button>
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2 text-dark-300 hover:text-white"
            >
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile nav */}
        {mobileOpen && (
          <div className="md:hidden pb-4 border-t border-dark-700 pt-2">
            {navItems.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  location.pathname === to
                    ? 'bg-primary-600/20 text-primary-400'
                    : 'text-dark-300 hover:text-white hover:bg-dark-800'
                }`}
              >
                <Icon size={16} />
                {label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  )
}