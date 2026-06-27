import { useState, useEffect, useRef } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  MessageSquare, Settings, LogOut, FileSearch, Code, Image, BookOpen,
  Plus, Trash2, Pencil, Check, X, ChevronDown, PanelLeftClose
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import { useToast } from '../ui/Toast';

const links = [
  { to: '/chat', icon: MessageSquare, label: 'Chat' },
  { to: '/analyze', icon: FileSearch, label: 'Analyze' },
  { to: '/code', icon: Code, label: 'Code' },
  { to: '/image', icon: Image, label: 'Image' },
  { to: '/learn', icon: BookOpen, label: 'Learn' },
];

export default function Sidebar({ collapsed, onToggle }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { addToast } = useToast();
  const [conversations, setConversations] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [profileOpen, setProfileOpen] = useState(false);
  const editInputRef = useRef(null);

  useEffect(() => {
    if (user) loadConversations();
  }, [user, location.pathname]);

  useEffect(() => {
    if (editingId && editInputRef.current) {
      editInputRef.current.focus();
      editInputRef.current.select();
    }
  }, [editingId]);

  const loadConversations = async () => {
    try {
      const { data } = await api.get('/conversations');
      setConversations(data.data || []);
    } catch {}
  };

  const newChat = () => navigate('/chat');
  const selectConversation = (id) => navigate(`/chat/${id}`);

  const startRename = (conv, e) => {
    e.stopPropagation();
    setEditingId(conv._id);
    setEditTitle(conv.title || 'New Chat');
  };

  const saveRename = async (convId) => {
    if (editTitle.trim()) {
      setConversations(prev => prev.map(c => c._id === convId ? { ...c, title: editTitle.trim() } : c));
    }
    setEditingId(null);
    setEditTitle('');
  };

  const deleteConversation = async (convId, e) => {
    e.stopPropagation();
    try {
      await api.delete(`/conversations/${convId}`);
      setConversations(prev => prev.filter(c => c._id !== convId));
      if (location.pathname.includes(convId)) navigate('/chat');
      addToast('Deleted', 'info');
    } catch {
      addToast('Failed to delete', 'error');
    }
  };

  const handleLogout = () => { logout(); navigate('/login'); };

  if (collapsed) {
    return (
      <aside className="hidden lg:flex flex-col w-16 bg-bg-secondary border-r border-border shrink-0 items-center py-3 gap-1">
        <button onClick={onToggle} className="p-2 text-text-muted hover:text-text-primary hover:bg-bg-tertiary rounded-lg mb-2">
          <PanelLeftClose size={18} />
        </button>
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} className={({ isActive }) => `p-2.5 rounded-lg transition-colors ${isActive ? 'bg-primary/20 text-primary' : 'text-text-muted hover:text-text-primary hover:bg-bg-tertiary'}`} title={label}>
            <Icon size={20} />
          </NavLink>
        ))}
        <div className="flex-1" />
        <NavLink to="/settings" className={({ isActive }) => `p-2.5 rounded-lg transition-colors ${isActive ? 'bg-primary/20 text-primary' : 'text-text-muted hover:text-text-primary hover:bg-bg-tertiary'}`} title="Settings">
          <Settings size={20} />
        </NavLink>
        <button onClick={handleLogout} className="p-2.5 text-text-muted hover:text-danger hover:bg-bg-tertiary rounded-lg" title="Logout">
          <LogOut size={20} />
        </button>
      </aside>
    );
  }

  return (
    <aside className="hidden lg:flex flex-col w-64 bg-bg-secondary border-r border-border shrink-0">
      <div className="flex items-center justify-between h-14 px-4 border-b border-border shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-black font-bold text-sm">H</span>
          </div>
          <span className="text-text-primary font-semibold">HDM AI</span>
        </div>
        <button onClick={onToggle} className="p-1.5 text-text-muted hover:text-text-primary hover:bg-bg-tertiary rounded-lg">
          <PanelLeftClose size={16} />
        </button>
      </div>

      <div className="p-3">
        <button onClick={newChat} className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary hover:bg-primary-hover text-black rounded-lg text-sm font-medium transition-colors">
          <Plus size={16} /> New Chat
        </button>
      </div>

      <nav className="px-2 space-y-0.5">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-primary/10 text-primary font-medium' : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary'}`
            }>
            <Icon size={18} /> {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-4 py-2"><div className="border-t border-border" /></div>

      <div className="flex-1 overflow-y-auto px-2">
        <p className="px-3 py-1 text-xs font-medium text-text-muted uppercase tracking-wider">Recent Chats</p>
        <div className="space-y-0.5">
          {conversations.map(conv => (
            <div key={conv._id} onClick={() => selectConversation(conv._id)}
              className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${location.pathname.includes(conv._id) ? 'bg-bg-tertiary text-text-primary' : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'}`}>
              <MessageSquare size={14} className="shrink-0 text-text-muted" />
              {editingId === conv._id ? (
                <div className="flex-1 flex items-center gap-1 min-w-0" onClick={e => e.stopPropagation()}>
                  <input ref={editInputRef} value={editTitle} onChange={e => setEditTitle(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') saveRename(conv._id); if (e.key === 'Escape') { setEditingId(null); setEditTitle(''); } }}
                    className="flex-1 bg-bg-tertiary border border-border rounded px-2 py-0.5 text-xs text-text-primary min-w-0 outline-none focus:border-primary" />
                  <button onClick={() => saveRename(conv._id)} className="p-0.5 text-success"><Check size={14} /></button>
                  <button onClick={() => { setEditingId(null); setEditTitle(''); }} className="p-0.5 text-text-muted hover:text-text-primary"><X size={14} /></button>
                </div>
              ) : (
                <>
                  <span className="flex-1 text-xs truncate">{conv.title || 'New Chat'}</span>
                  <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={e => startRename(conv, e)} className="p-1 text-text-muted hover:text-text-primary rounded"><Pencil size={12} /></button>
                    <button onClick={e => deleteConversation(conv._id, e)} className="p-1 text-text-muted hover:text-danger rounded"><Trash2 size={12} /></button>
                  </div>
                </>
              )}
            </div>
          ))}
          {conversations.length === 0 && <p className="px-3 py-4 text-xs text-text-muted text-center">No conversations yet</p>}
        </div>
      </div>

      <div className="border-t border-border p-2">
        <button onClick={() => setProfileOpen(!profileOpen)} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-bg-tertiary transition-colors">
          <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center shrink-0">
            <span className="text-primary text-sm font-bold">{user?.username?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}</span>
          </div>
          <div className="flex-1 text-left min-w-0">
            <p className="text-sm text-text-primary truncate">{user?.username || user?.email || 'User'}</p>
          </div>
          <ChevronDown size={14} className={`text-text-muted transition-transform ${profileOpen ? 'rotate-180' : ''}`} />
        </button>
        {profileOpen && (
          <div className="mt-1 px-2 space-y-0.5">
            <NavLink to="/settings" onClick={() => setProfileOpen(false)}
              className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${isActive ? 'bg-primary/10 text-primary' : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary'}`}>
              <Settings size={16} /> Settings
            </NavLink>
            <button onClick={handleLogout} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-text-secondary hover:text-danger hover:bg-bg-tertiary transition-colors">
              <LogOut size={16} /> Sign Out
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}