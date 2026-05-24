import { useState, useContext, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import {
  User, Shield, Key, ArrowUpRight, ArrowDownRight,
  Activity, Zap, Save, Plus, Eye, EyeOff,
  Copy, Check, Trash2, RefreshCw, AlertTriangle, X, Globe, Server,
  MessageSquare, ExternalLink, Code, Terminal,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/axios'

const TABS = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'api-keys', label: 'API Keys', icon: Key },
  { id: 'security', label: 'Security', icon: Shield },
]

const INBOUND_PROVIDERS = [
  { value: 'openai', label: 'OpenAI', icon: Globe },
  { value: 'anthropic', label: 'Anthropic', icon: Globe },
  { value: 'deepseek', label: 'DeepSeek', icon: Globe },
  { value: 'google', label: 'Google', icon: Globe },
  { value: 'erp', label: 'ERP System', icon: Server },
  { value: 'crm', label: 'CRM System', icon: Server },
  { value: 'database', label: 'Database', icon: Server },
  { value: 'custom', label: 'Custom API', icon: Server },
]

const PROVIDER_COLORS = {
  openai: 'bg-green-600/20 text-green-400',
  anthropic: 'bg-orange-600/20 text-orange-400',
  deepseek: 'bg-blue-600/20 text-blue-400',
  google: 'bg-red-600/20 text-red-400',
  erp: 'bg-purple-600/20 text-purple-400',
  crm: 'bg-teal-600/20 text-teal-400',
  database: 'bg-yellow-600/20 text-yellow-400',
  custom: 'bg-gray-600/20 text-gray-400',
}

export default function Settings() {
  const { tab } = useParams()
  const navigate = useNavigate()
  const { user, logout } = useContext(AuthContext)

  const [activeTab, setActiveTab] = useState(tab || 'profile')
  const [activeSubtab, setActiveSubtab] = useState('outbound')

  // Profile
  const [username, setUsername] = useState(user?.username || '')
  const [editingProfile, setEditingProfile] = useState(false)

  // Outbound
  const [outboundKeys, setOutboundKeys] = useState([])
  const [showOutboundCreate, setShowOutboundCreate] = useState(false)
  const [newOutboundName, setNewOutboundName] = useState('')
  const [newOutboundFull, setNewOutboundFull] = useState(null)
  const [showKeyId, setShowKeyId] = useState(null)
  const [copiedId, setCopiedId] = useState(null)
  // Quick query from outbound
  const [quickQuery, setQuickQuery] = useState('')
  const [queryResult, setQueryResult] = useState(null)
  const [queryLoading, setQueryLoading] = useState(false)
  const [selectedOutboundKey, setSelectedOutboundKey] = useState(null)

  // Inbound
  const [inboundKeys, setInboundKeys] = useState([])
  const [showInboundCreate, setShowInboundCreate] = useState(false)
  const [inboundForm, setInboundForm] = useState({
    provider: 'erp', name: '', api_key: '', base_url: '', api_structure: '',
  })
  const [editingInboundId, setEditingInboundId] = useState(null)
  const [testingId, setTestingId] = useState(null)

  // Security
  const [deletePassword, setDeletePassword] = useState('')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  useEffect(() => {
    if (tab && TABS.find(t => t.id === tab)) setActiveTab(tab)
  }, [tab])

  useEffect(() => {
    if (activeTab === 'api-keys') { loadOutboundKeys(); loadInboundKeys() }
    if (activeTab === 'profile') { loadOutboundKeys(); loadInboundKeys() }
  }, [activeTab])

  // ==================================================================
  // OUTBOUND
  // ==================================================================
  const loadOutboundKeys = async () => {
    try { const { data } = await api.get('/api-keys/outbound'); setOutboundKeys(data.data || []) } catch {}
  }

  const createOutboundKey = async (e) => {
    e.preventDefault()
    try {
      const { data } = await api.post('/api-keys/outbound', { project: 'general', name: newOutboundName })
      setNewOutboundFull(data.data.full_key)
      setShowOutboundCreate(false)
      setNewOutboundName('')
      loadOutboundKeys()
      toast.success('Key created!')
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed') }
  }

  const revokeOutboundKey = async (keyId) => {
    if (!confirm('Permanently delete this key?')) return
    try {
      await api.delete(`/api-keys/outbound/${keyId}`)
      setOutboundKeys(prev => prev.filter(k => k.id !== keyId))
      toast.success('Key deleted')
    } catch { toast.error('Failed') }
  }

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 3000)
    toast.success('Copied!')
  }

  // Quick chat query using outbound key
  const quickChatQuery = async () => {
    if (!quickQuery.trim() || !selectedOutboundKey) return
    setQueryLoading(true)
    setQueryResult(null)
    try {
      const { data } = await api.post('/general/chat', {
        message: quickQuery,
        interface: 'client',
      })
      setQueryResult(data.data)
    } catch (err) {
      toast.error('Query failed')
    }
    setQueryLoading(false)
  }

  // ==================================================================
  // INBOUND
  // ==================================================================
  const loadInboundKeys = async () => {
    try { const { data } = await api.get('/api-keys/inbound'); setInboundKeys(data.data || []) } catch {}
  }

  const createInboundKey = async (e) => {
    e.preventDefault()
    try {
      let api_structure = null
      if (inboundForm.api_structure.trim()) {
        try {
          api_structure = JSON.parse(inboundForm.api_structure)
        } catch {
          // Try parsing key:value format
          api_structure = {}
          inboundForm.api_structure.split('\n').forEach(line => {
            const [key, ...rest] = line.split(':')
            if (key && rest.length) {
              api_structure[key.trim().toLowerCase()] = rest.join(':').trim()
            }
          })
        }
      }

      await api.post('/api-keys/inbound', {
        provider: inboundForm.provider,
        name: inboundForm.name,
        api_key: inboundForm.api_key,
        base_url: inboundForm.base_url || undefined,
        api_structure: api_structure || undefined,
      })
      setShowInboundCreate(false)
      resetInboundForm()
      loadInboundKeys()
      toast.success('External key stored')
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed') }
  }

  const updateInboundKey = async (keyId) => {
    try {
      let api_structure = null
      if (inboundForm.api_structure.trim()) {
        try { api_structure = JSON.parse(inboundForm.api_structure) } catch { api_structure = null }
      }
      await api.put(`/api-keys/inbound/${keyId}`, {
        name: inboundForm.name,
        api_key: inboundForm.api_key || undefined,
        base_url: inboundForm.base_url || undefined,
        api_structure: api_structure || undefined,
      })
      setEditingInboundId(null)
      resetInboundForm()
      loadInboundKeys()
      toast.success('Key updated')
    } catch { toast.error('Failed') }
  }

  const deleteInboundKey = async (keyId) => {
    if (!confirm('Permanently delete?')) return
    try {
      await api.delete(`/api-keys/inbound/${keyId}`)
      setInboundKeys(prev => prev.filter(k => k.id !== keyId))
      toast.success('Key deleted')
    } catch { toast.error('Failed') }
  }

  const testInboundKey = async (keyId) => {
    setTestingId(keyId)
    try {
      const { data } = await api.post(`/api-keys/inbound/${keyId}/test`, {})
      toast[data.data.success ? 'success' : 'error'](data.data.message)
      loadInboundKeys()
    } catch { toast.error('Test failed') }
    setTestingId(null)
  }

  const editInboundKey = (key) => {
    setEditingInboundId(key.id)
    const structure = key.api_structure
      ? Object.entries(key.api_structure).map(([k, v]) => `${k}: ${v}`).join('\n')
      : ''
    setInboundForm({
      provider: key.provider,
      name: key.name,
      api_key: '',
      base_url: key.base_url || '',
      api_structure: structure,
    })
  }

  const resetInboundForm = () => {
    setInboundForm({ provider: 'erp', name: '', api_key: '', base_url: '', api_structure: '' })
  }

  // ==================================================================
  // PROFILE
  // ==================================================================
  const saveProfile = () => { toast.success('Profile updated'); setEditingProfile(false) }

  // ==================================================================
  // SECURITY
  // ==================================================================
  const deleteAccount = async () => {
    if (!deletePassword) return toast.error('Enter password')
    try {
      await api.delete('/auth/account', { data: { password: deletePassword } })
      toast.success('Account deleted')
      logout(); navigate('/login')
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed') }
  }

  // ==================================================================
  // RENDER
  // ==================================================================
  return (
    <div className="h-full flex">
      {/* Tab sidebar */}
      <div className="w-56 border-r border-dark-800 flex-shrink-0 p-3 space-y-1">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => { setActiveTab(id); navigate(`/settings/${id}`, { replace: true }) }}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              activeTab === id ? 'bg-primary-600/15 text-primary-400 font-medium' : 'text-dark-300 hover:text-white hover:bg-dark-800'
            }`}
          >
            <Icon size={16} /> {label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* PROFILE */}
        {activeTab === 'profile' && (
          <div className="max-w-2xl">
            <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2"><User size={20} className="text-primary-400" /> Profile</h2>
            <div className="card mb-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-primary-600/20 rounded-full flex items-center justify-center"><User size={28} className="text-primary-400" /></div>
                <div><h3 className="text-white font-medium">{user?.email}</h3><p className="text-dark-400 text-sm">Free Plan</p></div>
                <button onClick={() => setEditingProfile(!editingProfile)} className="ml-auto text-sm text-primary-400 hover:text-primary-300">{editingProfile ? 'Cancel' : 'Edit'}</button>
              </div>
              {editingProfile ? (
                <div className="space-y-4">
                  <div><label className="block text-sm text-dark-300 mb-1.5">Username</label><input value={username} onChange={(e) => setUsername(e.target.value)} className="input-field" /></div>
                  <div><label className="block text-sm text-dark-300 mb-1.5">Email</label><input value={user?.email || ''} disabled className="input-field opacity-50" /></div>
                  <button onClick={saveProfile} className="btn-primary flex items-center gap-2"><Save size={16} /> Save</button>
                </div>
              ) : (
                <div className="space-y-3">
                  {[['Username', username || 'Not set'], ['Email', user?.email], ['Plan', 'Free']].map(([l, v]) => (
                    <div key={l} className="flex items-center justify-between py-2 border-t border-dark-800 first:border-0"><span className="text-dark-400 text-sm">{l}</span><span className="text-white text-sm">{v}</span></div>
                  ))}
                </div>
              )}
            </div>
            <div className="card">
              <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2"><Activity size={16} className="text-primary-400" /> Overview</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
                  { label: 'Outbound', value: outboundKeys.length, icon: ArrowUpRight, color: 'text-blue-400' },
                  { label: 'Inbound', value: inboundKeys.length, icon: ArrowDownRight, color: 'text-green-400' },
                  { label: 'Requests', value: '0', icon: Activity, color: 'text-yellow-400' },
                  { label: 'Tokens', value: '0', icon: Zap, color: 'text-purple-400' },
                ].map(({ label, value, icon: Icon, color }) => (
                  <div key={label} className="text-center p-3 bg-dark-900 rounded-lg"><Icon size={20} className={`${color} mx-auto mb-1`} /><p className="text-lg font-semibold text-white">{value}</p><p className="text-xs text-dark-400">{label}</p></div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* API KEYS */}
        {activeTab === 'api-keys' && (
          <div className="max-w-3xl">
            <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2"><Key size={20} className="text-primary-400" /> API Keys</h2>

            {/* Subtabs */}
            <div className="flex gap-1 mb-6 bg-dark-800 rounded-lg p-1 w-fit">
              {[
                { id: 'outbound', label: 'Outbound', icon: ArrowUpRight, desc: 'Keys for apps to call HDM AI' },
                { id: 'inbound', label: 'Inbound', icon: ArrowDownRight, desc: 'External keys HDM AI uses' },
              ].map(({ id, label, icon: Icon }) => (
                <button key={id} onClick={() => setActiveSubtab(id)} className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm transition-colors ${activeSubtab === id ? 'bg-primary-600 text-white' : 'text-dark-300 hover:text-white'}`}><Icon size={14} /> {label}</button>
              ))}
            </div>

            {/* OUTBOUND */}
            {activeSubtab === 'outbound' && (
              <>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm text-dark-400">Generate keys for external apps to call HDM AI APIs</p>
                  <button onClick={() => setShowOutboundCreate(true)} className="btn-primary text-sm flex items-center gap-1.5"><Plus size={16} /> New Key</button>
                </div>

                {newOutboundFull && (
                  <div className="card mb-4 border-primary-600/30 bg-primary-600/5">
                    <div className="flex items-center gap-2 mb-3"><AlertTriangle size={16} className="text-yellow-400" /><p className="text-sm text-yellow-400 font-medium">Save your key — it won't be shown again!</p></div>
                    <div className="flex gap-2">
                      <code className="flex-1 bg-dark-950 p-3 rounded-lg text-xs break-all font-mono border border-dark-700">{showKeyId === 'new' ? newOutboundFull : '•'.repeat(48)}</code>
                      <button onClick={() => setShowKeyId(showKeyId === 'new' ? null : 'new')} className="btn-secondary px-3">{showKeyId === 'new' ? <EyeOff size={16} /> : <Eye size={16} />}</button>
                      <button onClick={() => copyToClipboard(newOutboundFull, 'new')} className="btn-secondary px-3">{copiedId === 'new' ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}</button>
                    </div>
                  </div>
                )}

                {showOutboundCreate && (
                  <form onSubmit={createOutboundKey} className="card mb-4 space-y-4">
                    <h3 className="text-sm font-medium text-white">New Outbound Key</h3>
                    <input value={newOutboundName} onChange={(e) => setNewOutboundName(e.target.value)} placeholder="Key name (e.g., My App)" className="input-field text-sm" required />
                    <div className="flex gap-2"><button type="submit" className="btn-primary text-sm">Create</button><button type="button" onClick={() => setShowOutboundCreate(false)} className="btn-secondary text-sm">Cancel</button></div>
                  </form>
                )}

                {/* Quick Chat Query */}
                {outboundKeys.length > 0 && (
                  <div className="card mb-4 border-primary-600/20 bg-primary-600/5">
                    <h3 className="text-sm font-medium text-white mb-3 flex items-center gap-2"><Terminal size={16} className="text-primary-400" /> Quick Test Query</h3>
                    <p className="text-xs text-dark-400 mb-3">Test your key by asking a question. The response comes from HDM AI using your key's permissions.</p>
                    <div className="flex gap-2 mb-3">
                      <select
                        value={selectedOutboundKey || ''}
                        onChange={(e) => setSelectedOutboundKey(e.target.value)}
                        className="input-field text-sm w-48"
                      >
                        <option value="">Select a key...</option>
                        {outboundKeys.map(k => <option key={k.id} value={k.id}>{k.name} ({k.key_prefix})</option>)}
                      </select>
                    </div>
                    {selectedOutboundKey && (
                      <div className="flex gap-2">
                        <input
                          value={quickQuery}
                          onChange={(e) => setQuickQuery(e.target.value)}
                          placeholder="e.g., What can you help me with?"
                          className="input-field flex-1 text-sm"
                          onKeyDown={(e) => e.key === 'Enter' && quickChatQuery()}
                        />
                        <button onClick={quickChatQuery} disabled={queryLoading || !quickQuery.trim()} className="btn-primary text-sm flex items-center gap-1.5">
                          <MessageSquare size={14} /> Query
                        </button>
                      </div>
                    )}
                    {queryLoading && <p className="text-xs text-dark-400 mt-2">Querying...</p>}
                    {queryResult && (
                      <div className="mt-3 p-3 bg-dark-900 rounded-lg border border-dark-700">
                        <p className="text-xs text-dark-500 mb-1">Response:</p>
                        <p className="text-sm text-dark-200 whitespace-pre-wrap">{queryResult.reply}</p>
                        <p className="text-xs text-dark-500 mt-2">Tokens: {queryResult.tokens_used} • Conv: {queryResult.conversation_id?.slice(0, 8)}...</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Key list */}
                <div className="space-y-3">
                  {outboundKeys.length === 0 && <div className="card text-center py-12"><ArrowUpRight size={32} className="text-dark-600 mx-auto mb-3" /><p className="text-dark-400 text-sm">No outbound keys</p></div>}
                  {outboundKeys.map(key => (
                    <div key={key.id} className={`card hover:border-dark-600 transition-colors cursor-pointer ${selectedOutboundKey === key.id ? 'border-primary-600/50' : ''}`} onClick={() => setSelectedOutboundKey(selectedOutboundKey === key.id ? null : key.id)}>
                      <div className="flex items-center justify-between">
                        <div><h4 className="text-white text-sm font-medium">{key.name}</h4><p className="text-dark-500 text-xs mt-0.5 font-mono">{key.key_prefix}</p></div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-dark-500">{key.last_used ? `Used ${new Date(key.last_used).toLocaleDateString()}` : 'Never used'}</span>
                          <button onClick={(e) => { e.stopPropagation(); revokeOutboundKey(key.id) }} className="p-1.5 text-dark-400 hover:text-red-400 rounded-lg hover:bg-dark-800"><Trash2 size={14} /></button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 p-4 bg-dark-800/50 border border-dark-700 rounded-xl">
                  <h4 className="text-sm font-medium text-white mb-2">How to use</h4>
                  <code className="block bg-dark-950 p-3 rounded-lg text-xs text-primary-400 font-mono">curl -H "x-api-key: YOUR_KEY" http://localhost:5002/api/v1/general/chat</code>
                </div>
              </>
            )}

            {/* INBOUND */}
            {activeSubtab === 'inbound' && (
              <>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm text-dark-400">Store external system keys for HDM AI to fetch and analyze data</p>
                  <button onClick={() => { setShowInboundCreate(true); setEditingInboundId(null); resetInboundForm() }} className="btn-primary text-sm flex items-center gap-1.5"><Plus size={16} /> Add Key</button>
                </div>

                {(showInboundCreate || editingInboundId) && (
                  <form onSubmit={(e) => { e.preventDefault(); editingInboundId ? updateInboundKey(editingInboundId) : createInboundKey(e) }} className="card mb-4 space-y-4">
                    <h3 className="text-sm font-medium text-white">{editingInboundId ? 'Edit External Key' : 'Add External Key'}</h3>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs text-dark-400 mb-1.5">Provider</label>
                        <select value={inboundForm.provider} onChange={(e) => setInboundForm({ ...inboundForm, provider: e.target.value })} className="input-field text-sm">
                          {INBOUND_PROVIDERS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs text-dark-400 mb-1.5">Display Name</label>
                        <input value={inboundForm.name} onChange={(e) => setInboundForm({ ...inboundForm, name: e.target.value })} placeholder="e.g., Production ERP" className="input-field text-sm" required />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs text-dark-400 mb-1.5">API Key</label>
                      <input value={inboundForm.api_key} onChange={(e) => setInboundForm({ ...inboundForm, api_key: e.target.value })} placeholder={editingInboundId ? 'Leave blank to keep current' : 'hdm_out_xxx...'} className="input-field text-sm" type="password" required={!editingInboundId} />
                    </div>

                    <div>
                      <label className="block text-xs text-dark-400 mb-1.5">Base URL {['erp','crm','database','custom'].includes(inboundForm.provider) ? '(required)' : '(auto-filled for known providers)'}</label>
                      <input value={inboundForm.base_url} onChange={(e) => setInboundForm({ ...inboundForm, base_url: e.target.value })} placeholder="https://api.example.com" className="input-field text-sm" />
                    </div>

                    <div>
                      <label className="block text-xs text-dark-400 mb-1.5 flex items-center gap-2">
                        <Code size={14} />
                        API Structure (endpoint mapping)
                      </label>
                      <p className="text-xs text-dark-500 mb-2">Map resource names to API paths. One per line. Format: resource: /api/path</p>
                      <textarea
                        value={inboundForm.api_structure}
                        onChange={(e) => setInboundForm({ ...inboundForm, api_structure: e.target.value })}
                        placeholder={`products: /tenant/inventory/products
invoices: /tenant/finance/invoices
customers: /tenant/crm/customers
sales: /tenant/finance/sales
inventory: /tenant/inventory/stock
employees: /tenant/hr/employees
orders: /tenant/sales/orders`}
                        className="input-field h-40 text-sm font-mono resize-none"
                        spellCheck={false}
                      />
                      <p className="text-xs text-dark-500 mt-1">
                        HDM AI uses this to call the right endpoint when you ask "show products" or "analyze invoices"
                      </p>
                    </div>

                    <div className="flex gap-2">
                      <button type="submit" className="btn-primary text-sm">{editingInboundId ? 'Update Key' : 'Store Key Securely'}</button>
                      <button type="button" onClick={() => { setShowInboundCreate(false); setEditingInboundId(null); resetInboundForm() }} className="btn-secondary text-sm">Cancel</button>
                    </div>
                  </form>
                )}

                <div className="space-y-3">
                  {inboundKeys.length === 0 && !showInboundCreate && (
                    <div className="card text-center py-12"><ArrowDownRight size={32} className="text-dark-600 mx-auto mb-3" /><p className="text-dark-400 text-sm">No external keys</p></div>
                  )}
                  {inboundKeys.map(key => (
                    <div key={key.id} className="card hover:border-dark-600 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${key.is_verified ? 'bg-green-400' : 'bg-yellow-400'}`} />
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="text-white text-sm font-medium">{key.name}</h4>
                              <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${PROVIDER_COLORS[key.provider] || ''}`}>{INBOUND_PROVIDERS.find(p => p.value === key.provider)?.label || key.provider}</span>
                            </div>
                            <p className="text-dark-500 text-xs mt-0.5">{key.key_prefix} {key.base_url ? `• ${key.base_url}` : ''}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <button onClick={() => testInboundKey(key.id)} disabled={testingId === key.id} className="p-1.5 text-dark-400 hover:text-blue-400 rounded-lg hover:bg-dark-800" title="Test">{testingId === key.id ? <RefreshCw size={14} className="animate-spin" /> : <RefreshCw size={14} />}</button>
                          <button onClick={() => editInboundKey(key)} className="p-1.5 text-dark-400 hover:text-white rounded-lg hover:bg-dark-800" title="Edit"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg></button>
                          <button onClick={() => deleteInboundKey(key.id)} className="p-1.5 text-dark-400 hover:text-red-400 rounded-lg hover:bg-dark-800" title="Delete"><Trash2 size={14} /></button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}

        {/* SECURITY */}
        {activeTab === 'security' && (
          <div className="max-w-2xl">
            <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2"><Shield size={20} className="text-primary-400" /> Security</h2>
            <div className="card mb-4">
              <h3 className="text-sm font-medium text-white mb-4">Change Password</h3>
              <div className="space-y-3"><input type="password" placeholder="Current password" className="input-field text-sm" /><input type="password" placeholder="New password" className="input-field text-sm" /><input type="password" placeholder="Confirm new password" className="input-field text-sm" /><button className="btn-primary text-sm">Update Password</button></div>
            </div>
            <div className="card mb-4">
              <h3 className="text-sm font-medium text-white mb-4">Active Session</h3>
              <div className="flex items-center justify-between py-2"><div><p className="text-white text-sm">Current Session</p><p className="text-dark-400 text-xs">Windows • Chrome</p></div><span className="bg-green-600/20 text-green-400 px-2 py-0.5 rounded text-xs font-medium">Active</span></div>
            </div>
            <div className="card border-red-600/20 bg-red-600/5">
              <h3 className="text-sm font-medium text-red-400 mb-2 flex items-center gap-2"><AlertTriangle size={16} /> Delete Account</h3>
              <p className="text-xs text-dark-400 mb-3">Permanently delete your account and ALL data.</p>
              {!showDeleteConfirm ? (
                <button onClick={() => setShowDeleteConfirm(true)} className="bg-red-600/20 hover:bg-red-600/30 text-red-400 px-4 py-2 rounded-lg text-sm font-medium">Delete My Account</button>
              ) : (
                <div className="space-y-3 p-4 bg-dark-900 rounded-lg border border-red-600/30">
                  <p className="text-sm text-red-400">Enter your password to confirm:</p>
                  <input type="password" value={deletePassword} onChange={(e) => setDeletePassword(e.target.value)} placeholder="Your password" className="input-field text-sm" autoFocus />
                  <div className="flex gap-2"><button onClick={deleteAccount} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium">Permanently Delete</button><button onClick={() => { setShowDeleteConfirm(false); setDeletePassword('') }} className="btn-secondary text-sm">Cancel</button></div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}