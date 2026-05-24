// ====================================================================================================
// client/src/pages/Chat.jsx — FINAL with streaming fix
// ====================================================================================================
import { useState, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Sparkles, Brain, Search, FileText, X, Paperclip, Send,
  PanelRight, MessageSquare, ChevronRight
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/axios'
import ChatMessage from '../components/ChatMessage'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5002/api/v1'

export default function Chat() {
  const { conversationId } = useParams()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [searchEnabled, setSearchEnabled] = useState(false)
  const [deepThink, setDeepThink] = useState(false)
  const [files, setFiles] = useState([])
  const [likedMessages, setLikedMessages] = useState({})
  const [streamingText, setStreamingText] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const [userMessages, setUserMessages] = useState([])
  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const messageRefs = useRef({})

  useEffect(() => {
    if (conversationId) {
      loadMessages(conversationId)
      loadUserMessages(conversationId)
    } else {
      setMessages([])
      setUserMessages([])
    }
  }, [conversationId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  useEffect(() => {
    inputRef.current?.focus()
  }, [conversationId])

  const loadMessages = async (convId) => {
    try {
      const { data } = await api.get(`/general/conversations/${convId}`)
      setMessages((data.data || []).map(m => ({
        content: m.content,
        isUser: m.role === 'user',
        timestamp: m.timestamp,
      })))
    } catch {
      navigate('/chat')
    }
  }

  const loadUserMessages = async (convId) => {
    try {
      const { data } = await api.get(`/general/conversations/${convId}`)
      setUserMessages((data.data || []).filter(m => m.role === 'user'))
    } catch {}
  }

  const scrollToMessage = (index) => {
    const userMsgIndex = index * 2
    const el = messageRefs.current[userMsgIndex]
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      el.classList.add('ring-2', 'ring-primary-500', 'rounded-lg')
      setTimeout(() => el.classList.remove('ring-2', 'ring-primary-500', 'rounded-lg'), 2000)
    }
  }

  const toggleLike = (i) => setLikedMessages(prev => ({ ...prev, [i]: prev[i] === 'liked' ? null : 'liked' }))
  const toggleDislike = (i) => setLikedMessages(prev => ({ ...prev, [i]: prev[i] === 'disliked' ? null : 'disliked' }))

  const handleSend = async (e) => {
    e?.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { content: userMsg, isUser: true }])
    setLoading(true)
    setStreamingText('')

    // Try streaming first
    try {
      const formData = new FormData()
      formData.append('message', userMsg)
      formData.append('interface', 'client')
      formData.append('search_enabled', searchEnabled)
      formData.append('deep_think', deepThink)
      if (conversationId) formData.append('conversation_id', conversationId)

      const token = localStorage.getItem('hdm_token')
      const response = await fetch(`${API_BASE}/general/chat/stream`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
      })

      if (!response.ok) throw new Error('Stream failed')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let fullText = ''
      let newConvId = conversationId

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const text = decoder.decode(value)
        const lines = text.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.chunk) {
                fullText += data.chunk
                setStreamingText(fullText)
              }
              if (data.conversation_id) newConvId = data.conversation_id
              if (data.done) {
                setMessages(prev => [...prev, { content: fullText, isUser: false }])
                setStreamingText('')
                if (!conversationId && newConvId) {
                  navigate(`/chat/${newConvId}`, { replace: true })
                }
              }
            } catch {}
          }
        }
      }
} catch {
  // Silent fallback to normal chat — no toast
  try {
    const { data } = await api.post('/general/chat', {
      message: userMsg,
      conversation_id: conversationId || undefined,
      interface: 'client',
    })
    setMessages(prev => [...prev, { content: data.data.reply, isUser: false }])
    if (!conversationId && data.data.conversation_id) {
      navigate(`/chat/${data.data.conversation_id}`, { replace: true })
    }
  } catch {
    setMessages(prev => [...prev, { content: 'Sorry, something went wrong.', isUser: false }])
  }
  setStreamingText('')
}
    setLoading(false)
    setFiles([])
  }

  const handleFileSelect = (e) => {
    setFiles(prev => [...prev, ...Array.from(e.target.files)].slice(0, 5))
    e.target.value = ''
  }

  const removeFile = (i) => setFiles(prev => prev.filter((_, idx) => idx !== i))

  return (
    <div className="h-full flex">
      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
            {messages.length === 0 && !streamingText && (
              <div className="h-[60vh] flex items-center justify-center">
                <div className="text-center max-w-lg">
                  <div className="w-20 h-20 bg-gradient-to-br from-primary-600/20 to-purple-600/20 rounded-2xl flex items-center justify-center mx-auto mb-6 ring-1 ring-primary-500/20">
                    <Sparkles size={36} className="text-primary-400" />
                  </div>
                  <h2 className="text-2xl font-bold text-white mb-3">HDM AI Assistant</h2>
                  <p className="text-dark-400 mb-8">Upload files, enable Deep Think, or connect business data.</p>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { icon: Brain, title: 'Deep Think', action: () => setDeepThink(!deepThink), active: deepThink },
                      { icon: Search, title: 'Search', action: () => setSearchEnabled(!searchEnabled), active: searchEnabled },
                      { icon: FileText, title: 'Upload Files', action: () => fileInputRef.current?.click(), active: files.length > 0 },
                      { icon: Sparkles, title: 'Quick Start', action: () => setInput('What can you help me with?'), active: false },
                    ].map(({ icon: Icon, title, action, active }) => (
                      <button key={title} onClick={action} className={`p-4 rounded-xl text-left transition-all ${active ? 'bg-primary-600/10 border border-primary-500/30' : 'bg-dark-800/50 border border-dark-700/50 hover:border-dark-600'}`}>
                        <Icon size={20} className={active ? 'text-primary-400' : 'text-dark-400'} />
                        <p className="text-sm font-medium text-white mt-2">{title}</p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} ref={el => messageRefs.current[i] = el} className="transition-all duration-300">
                <ChatMessage
                  message={msg.content}
                  isUser={msg.isUser}
                  onLike={() => toggleLike(i)}
                  onDislike={() => toggleDislike(i)}
                  likedMessages={likedMessages[i]}
                />
              </div>
            ))}

            {streamingText && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-dark-700 ring-1 ring-dark-600 flex items-center justify-center">
                  <Sparkles size={14} className="text-primary-400" />
                </div>
                <div className="max-w-[80%]">
                  <div className="px-4 py-3 rounded-2xl rounded-tl-md bg-dark-800 text-dark-100 border border-dark-700/50 text-sm leading-relaxed">
                    <p className="whitespace-pre-wrap">
                      {streamingText}
                      <span className="inline-block w-2 h-4 bg-primary-400 ml-0.5 animate-pulse" />
                    </p>
                  </div>
                </div>
              </div>
            )}

            {loading && !streamingText && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-dark-700 flex items-center justify-center">
                  <Sparkles size={14} className="text-primary-400 animate-pulse" />
                </div>
                <div className="flex gap-1.5 items-center px-4 py-3">
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce [animation-delay:0ms]"></div>
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce [animation-delay:150ms]"></div>
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce [animation-delay:300ms]"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="flex-shrink-0 border-t border-dark-800 bg-dark-950/90 backdrop-blur">
          <div className="max-w-3xl mx-auto px-4 py-3">
            <div className="flex items-center gap-2 mb-2">
              <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs cursor-pointer transition-all bg-dark-800 text-dark-300 hover:text-white hover:bg-dark-700">
                <Paperclip size={13} /> Files
                <input ref={fileInputRef} type="file" multiple className="hidden" onChange={handleFileSelect} accept=".pdf,.png,.jpg,.csv,.xlsx,.txt,.md,.py,.js,.json" />
              </label>
              <button onClick={() => setSearchEnabled(!searchEnabled)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${searchEnabled ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' : 'bg-dark-800 text-dark-300 hover:text-white hover:bg-dark-700'}`}>
                <Search size={13} /> {searchEnabled ? 'Search ON' : 'Search'}
              </button>
              <button onClick={() => setDeepThink(!deepThink)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${deepThink ? 'bg-purple-600/20 text-purple-400 border border-purple-500/30' : 'bg-dark-800 text-dark-300 hover:text-white hover:bg-dark-700'}`}>
                <Brain size={13} /> {deepThink ? 'Deep Think ON' : 'Deep Think'}
              </button>
              {conversationId && (
                <button
                  onClick={() => { setShowHistory(!showHistory); if (!showHistory) loadUserMessages(conversationId) }}
                  className={`ml-auto p-1.5 rounded-lg transition-all ${showHistory ? 'bg-primary-600/20 text-primary-400' : 'text-dark-400 hover:text-white hover:bg-dark-800'}`}
                  title="Chat history"
                >
                  <PanelRight size={16} />
                </button>
              )}
            </div>
            {files.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-2">
                {files.map((f, i) => (
                  <div key={i} className="flex items-center gap-1.5 px-2.5 py-1 bg-dark-800 border border-dark-600 rounded-lg text-xs text-dark-300">
                    <FileText size={11} className="text-dark-500" />
                    <span className="max-w-[100px] truncate">{f.name}</span>
                    <button onClick={() => removeFile(i)} className="text-dark-500 hover:text-red-400"><X size={11} /></button>
                  </div>
                ))}
              </div>
            )}
            <form onSubmit={handleSend} className="flex gap-2">
              <input ref={inputRef} value={input} onChange={e => setInput(e.target.value)} placeholder="Type your message..." className="input-field flex-1 text-sm" disabled={loading} />
              <button type="submit" disabled={loading || !input.trim()} className={`btn-primary px-4 ${deepThink ? 'bg-purple-600 hover:bg-purple-700' : ''}`}>
                <Send size={18} />
              </button>
            </form>
            <p className="text-[11px] text-dark-500 text-center mt-2">HDM AI can make mistakes. Verify important information.</p>
          </div>
        </div>
      </div>

      {showHistory && conversationId && (
        <div className="w-72 border-l border-dark-800 bg-dark-900 flex flex-col flex-shrink-0">
          <div className="flex items-center justify-between p-3 border-b border-dark-800">
            <h3 className="text-xs font-semibold text-dark-300 uppercase tracking-wider flex items-center gap-1.5">
              <MessageSquare size={14} /> Chat History
            </h3>
            <button onClick={() => setShowHistory(false)} className="p-1 text-dark-400 hover:text-white rounded">
              <X size={14} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {userMessages.map((msg, i) => (
              <button
                key={i}
                onClick={() => scrollToMessage(i)}
                className="w-full text-left p-2.5 rounded-lg hover:bg-dark-800 transition-colors group"
              >
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-primary-600/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-[10px] text-primary-400 font-bold">U</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-dark-400 truncate">
                      {msg.content?.substring(0, 60)}{(msg.content?.length || 0) > 60 ? '...' : ''}
                    </p>
                    {msg.timestamp && (
                      <p className="text-[10px] text-dark-600 mt-0.5">
                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    )}
                  </div>
                  <ChevronRight size={12} className="text-dark-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </button>
            ))}
            {userMessages.length === 0 && (
              <p className="text-xs text-dark-600 text-center py-8">No messages yet</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}