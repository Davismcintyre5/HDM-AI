// ====================================================================================================
// client/src/App.jsx
// ====================================================================================================
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useContext, useState, useEffect } from 'react'
import { AuthContext } from './context/AuthContext'
import Sidebar from './components/Sidebar'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Chat from './pages/Chat'
import Learn from './pages/Learn'
import Code from './pages/Code'
import Image from './pages/Image'
import Analyze from './pages/Analyze'
import Settings from './pages/Settings'
import { Menu, PanelLeft } from 'lucide-react'

export default function App() {
  const { user, loading } = useContext(AuthContext)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024)

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 1024)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    setSidebarOpen(false)
  }, [location.pathname])

  useEffect(() => {
    const saved = localStorage.getItem('hdm_sidebar_collapsed')
    if (saved) setSidebarCollapsed(saved === 'true')
  }, [])

  const toggleSidebar = () => {
    const newState = !sidebarCollapsed
    setSidebarCollapsed(newState)
    localStorage.setItem('hdm_sidebar_collapsed', String(newState))
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-950">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-dark-400 text-sm">Loading HDM AI...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-dark-950">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    )
  }

  return (
    <div className="h-screen flex bg-dark-950 overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onToggle={toggleSidebar}
      />

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile top bar */}
        <div className="lg:hidden flex items-center h-14 px-4 border-b border-dark-800 bg-dark-900 flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 -ml-2 text-dark-300 hover:text-white rounded-lg hover:bg-dark-800"
          >
            <Menu size={20} />
          </button>
          <div className="flex items-center gap-2 ml-3">
            <div className="w-7 h-7 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xs">HDM</span>
            </div>
            <span className="text-white font-semibold text-sm">HDM AI</span>
          </div>
        </div>

        {/* Desktop collapse toggle */}
        <div className="hidden lg:flex items-center h-0">
          {sidebarCollapsed && (
            <button
              onClick={toggleSidebar}
              className="absolute top-3 left-3 z-10 p-2 bg-dark-900 border border-dark-700 rounded-lg text-dark-400 hover:text-white shadow-lg"
            >
              <PanelLeft size={18} />
            </button>
          )}
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
            <Route path="/chat/:conversationId" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
            <Route path="/learn" element={<ProtectedRoute><Learn /></ProtectedRoute>} />
            <Route path="/code" element={<ProtectedRoute><Code /></ProtectedRoute>} />
            <Route path="/image" element={<ProtectedRoute><Image /></ProtectedRoute>} />
            <Route path="/analyze" element={<ProtectedRoute><Analyze /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
            <Route path="/settings/:tab" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/chat" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}