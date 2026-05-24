import { useContext, useState, useEffect, useRef } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import {
  MessageSquare, BookOpen, Code2, Image, FileSearch,
  Settings, Key, LogOut, ChevronLeft, ChevronRight,
  Plus, Trash2, Pencil, Check, X, User, ChevronDown,
  Menu, PanelLeft, PanelLeftClose
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/axios'

const NAV_ITEMS = [
  { to: '/chat', label: 'Chat', icon: MessageSquare },
  { to: '/learn', label: 'Learn', icon: BookOpen },
  { to: '/code', label: 'Code', icon: Code2 },
  { to: '/image', label: 'Image', icon: Image },
  { to: '/analyze', label: 'Analyze', icon: FileSearch },
]

export default function Sidebar({ collapsed, open, onClose, onToggle }) {
  const { user, logout } = useContext(AuthContext)
  const location = useLocation()
  const navigate = useNavigate()
  const [conversations, setConversations] = useState([])
  const [editingId, setEditingId] = useState(null)
  const [editTitle, setEditTitle] = useState('')
  const [profileOpen, setProfileOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024)
  const editInputRef = useRef(null)

  // Track screen size
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 1024)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    if (user) loadConversations()
  }, [user, location.pathname])

  useEffect(() => {
    if (editingId && editInputRef.current) {
      editInputRef.current.focus()
      editInputRef.current.select()
    }
  }, [editingId])

  const loadConversations = async () => {
    try {
      const { data } = await api.get('/general/conversations')
      setConversations(data.data || [])
    } catch {}
  }

  const newChat = () => { navigate('/chat'); if (isMobile) onClose() }
  const selectConversation = (convId) => { navigate(`/chat/${convId}`); if (isMobile) onClose() }

  const startRename = (conv, e) => { e.stopPropagation(); setEditingId(conv.id); setEditTitle(conv.title || 'New Chat') }

  const saveRename = async (convId) => {
    if (editTitle.trim()) {
      setConversations(prev => prev.map(c => c.id === convId ? { ...c, title: editTitle.trim() } : c))
      toast.success('Renamed')
    }
    setEditingId(null); setEditTitle('')
  }

  const cancelRename = (e) => { e?.stopPropagation(); setEditingId(null); setEditTitle('') }

  const deleteConversation = async (convId, e) => {
    e.stopPropagation()
    if (!confirm('Delete this conversation?')) return
    try {
      await api.delete(`/general/conversations/${convId}`)
      setConversations(prev => prev.filter(c => c.id !== convId))
      if (location.pathname.includes(convId)) navigate('/chat')
      toast.success('Deleted')
    } catch { toast.error('Failed to delete') }
  }

  const handleLogout = () => { logout(); navigate('/login') }
  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/')

  // Mobile: overlay sidebar
  if (isMobile) {
    return (
      <>
        {/* Mobile overlay */}
        {open && (
          <div className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm" onClick={onClose} />
        )}
        
        {/* Mobile sidebar — slides from left */}
        <div className={`fixed inset-y-0 left-0 z-50 w-72 bg-dark-900 border-r border-dark-800 transform transition-transform duration-200 flex flex-col ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}>
          <SidebarContent
            conversations={conversations}
            editingId={editingId}
            editTitle={editTitle}
            profileOpen={profileOpen}
            user={user}
            location={location}
            onNewChat={newChat}
            onSelectConv={selectConversation}
            onStartRename={startRename}
            onSaveRename={saveRename}
            onCancelRename={cancelRename}
            onDeleteConv={deleteConversation}
            onToggleProfile={() => setProfileOpen(!profileOpen)}
            onLogout={handleLogout}
            onClose={onClose}
            isMobile={true}
            editInputRef={editInputRef}
            setEditTitle={setEditTitle}
            isActive={isActive}
            setProfileOpen={setProfileOpen}
          />
        </div>
      </>
    )
  }

  // Desktop: collapsible sidebar
  if (collapsed) {
    return (
      <div className="hidden lg:flex flex-col w-16 bg-dark-900 border-r border-dark-800 flex-shrink-0 items-center py-3 gap-1">
        <button onClick={onToggle} className="p-2 text-dark-400 hover:text-white hover:bg-dark-800 rounded-lg mb-2">
          <PanelLeft size={18} />
        </button>
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <Link key={to} to={to} className={`p-2.5 rounded-lg transition-colors ${isActive(to) ? 'bg-primary-600/20 text-primary-400' : 'text-dark-400 hover:text-white hover:bg-dark-800'}`} title={label}>
            <Icon size={20} />
          </Link>
        ))}
        <div className="flex-1" />
        <Link to="/settings" className={`p-2.5 rounded-lg transition-colors ${isActive('/settings') ? 'bg-primary-600/20 text-primary-400' : 'text-dark-400 hover:text-white hover:bg-dark-800'}`} title="Settings">
          <Settings size={20} />
        </Link>
        <button onClick={handleLogout} className="p-2.5 text-dark-400 hover:text-red-400 hover:bg-dark-800 rounded-lg" title="Logout">
          <LogOut size={20} />
        </button>
      </div>
    )
  }

  // Desktop: expanded sidebar
  return (
    <div className="hidden lg:flex flex-col w-64 bg-dark-900 border-r border-dark-800 flex-shrink-0">
      <SidebarContent
        conversations={conversations}
        editingId={editingId}
        editTitle={editTitle}
        profileOpen={profileOpen}
        user={user}
        location={location}
        onNewChat={newChat}
        onSelectConv={selectConversation}
        onStartRename={startRename}
        onSaveRename={saveRename}
        onCancelRename={cancelRename}
        onDeleteConv={deleteConversation}
        onToggleProfile={() => setProfileOpen(!profileOpen)}
        onLogout={handleLogout}
        onToggle={onToggle}
        isMobile={false}
        editInputRef={editInputRef}
        setEditTitle={setEditTitle}
        isActive={isActive}
        setProfileOpen={setProfileOpen}
      />
    </div>
  )
}

// Shared sidebar content
function SidebarContent({
  conversations, editingId, editTitle, profileOpen, user, location,
  onNewChat, onSelectConv, onStartRename, onSaveRename, onCancelRename,
  onDeleteConv, onToggleProfile, onLogout, onClose, onToggle,
  isMobile, editInputRef, setEditTitle, isActive, setProfileOpen,
}) {
  return (
    <>
      {/* Header */}
      <div className="flex items-center justify-between h-14 px-4 border-b border-dark-800 flex-shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">HDM</span>
          </div>
          <span className="text-white font-semibold">HDM AI</span>
        </div>
        {isMobile ? (
          <button onClick={onClose} className="p-1.5 text-dark-400 hover:text-white hover:bg-dark-800 rounded-lg">
            <X size={18} />
          </button>
        ) : (
          <button onClick={onToggle} className="p-1.5 text-dark-400 hover:text-white hover:bg-dark-800 rounded-lg">
            <PanelLeftClose size={16} />
          </button>
        )}
      </div>

      {/* New Chat */}
      <div className="p-3">
        <button onClick={onNewChat} className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium transition-colors">
          <Plus size={16} /> New Chat
        </button>
      </div>

      {/* Navigation */}
      <nav className="px-2 space-y-0.5">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <Link key={to} to={to} onClick={isMobile ? onClose : undefined}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              isActive(to) ? 'bg-primary-600/15 text-primary-400 font-medium' : 'text-dark-300 hover:text-white hover:bg-dark-800'
            }`}>
            <Icon size={18} /> {label}
          </Link>
        ))}
      </nav>

      <div className="px-4 py-2"><div className="border-t border-dark-800"></div></div>

      {/* History */}
      <div className="flex-1 overflow-y-auto px-2">
        <p className="px-3 py-1 text-xs font-medium text-dark-500 uppercase tracking-wider">Recent Chats</p>
        <div className="space-y-0.5">
          {conversations.map(conv => (
            <div key={conv.id} onClick={() => onSelectConv(conv.id)}
              className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                location.pathname.includes(conv.id) ? 'bg-dark-800 text-white' : 'text-dark-300 hover:bg-dark-800/50 hover:text-white'
              }`}>
              <MessageSquare size={14} className="flex-shrink-0 text-dark-500" />
              {editingId === conv.id ? (
                <div className="flex-1 flex items-center gap-1 min-w-0" onClick={e => e.stopPropagation()}>
                  <input ref={editInputRef} value={editTitle} onChange={e => setEditTitle(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') onSaveRename(conv.id); if (e.key === 'Escape') onCancelRename() }}
                    className="flex-1 bg-dark-700 border border-dark-600 rounded px-2 py-0.5 text-xs text-white min-w-0 outline-none focus:border-primary-500" />
                  <button onClick={() => onSaveRename(conv.id)} className="p-0.5 text-green-400"><Check size={14} /></button>
                  <button onClick={onCancelRename} className="p-0.5 text-dark-400 hover:text-white"><X size={14} /></button>
                </div>
              ) : (
                <>
                  <span className="flex-1 text-xs truncate">{conv.title || 'New Chat'}</span>
                  <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={e => onStartRename(conv, e)} className="p-1 text-dark-400 hover:text-white rounded"><Pencil size={12} /></button>
                    <button onClick={e => onDeleteConv(conv.id, e)} className="p-1 text-dark-400 hover:text-red-400 rounded"><Trash2 size={12} /></button>
                  </div>
                </>
              )}
            </div>
          ))}
          {conversations.length === 0 && <p className="px-3 py-4 text-xs text-dark-500 text-center">No conversations yet</p>}
        </div>
      </div>

      {/* Profile */}
      <div className="border-t border-dark-800 p-2">
        <button onClick={onToggleProfile} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-dark-800 transition-colors">
          <div className="w-8 h-8 bg-primary-600/30 rounded-full flex items-center justify-center flex-shrink-0">
            <User size={16} className="text-primary-400" />
          </div>
          <div className="flex-1 text-left min-w-0">
            <p className="text-sm text-white truncate">{user?.email || 'User'}</p>
            <p className="text-xs text-dark-500">Free Plan</p>
          </div>
          <ChevronDown size={14} className={`text-dark-400 transition-transform ${profileOpen ? 'rotate-180' : ''}`} />
        </button>

        {profileOpen && (
          <div className="mt-1 px-2 space-y-0.5">
            <Link to="/settings" onClick={() => { setProfileOpen(false); if (isMobile) onClose?.() }}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive('/settings') && !isActive('/settings/keys') ? 'bg-primary-600/15 text-primary-400' : 'text-dark-300 hover:text-white hover:bg-dark-800'
              }`}>
              <Settings size={16} /> Settings
            </Link>
            <Link to="/settings/api-keys" onClick={() => { setProfileOpen(false); if (isMobile) onClose?.() }}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive('/settings/keys') ? 'bg-primary-600/15 text-primary-400' : 'text-dark-300 hover:text-white hover:bg-dark-800'
              }`}>
              <Key size={16} /> API Keys
            </Link>
            <button onClick={onLogout} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-dark-300 hover:text-red-400 hover:bg-dark-800 transition-colors">
              <LogOut size={16} /> Sign Out
            </button>
          </div>
        )}
      </div>
    </>
  )
}