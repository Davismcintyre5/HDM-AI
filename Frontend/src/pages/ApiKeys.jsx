import { useState, useEffect } from 'react'
import { Plus, Trash2, Copy, Check, Key } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/axios'

const PROJECTS = ['general', 'smartpos', 'spark', 'vibe', 'vault', 'erp', 'widget']

export default function ApiKeys() {
  const [keys, setKeys] = useState([])
  const [showCreate, setShowCreate] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyProject, setNewKeyProject] = useState('general')
  const [newKeyFull, setNewKeyFull] = useState(null)
  const [copied, setCopied] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => { loadKeys() }, [])

  const loadKeys = async () => {
    try {
      const { data } = await api.get('/api-keys')
      setKeys(data.data || [])
    } catch (err) {
      toast.error('Failed to load API keys')
    }
  }

  const createKey = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await api.post('/api-keys', { project: newKeyProject, name: newKeyName })
      setNewKeyFull(data.data.full_key)
      setShowCreate(false)
      setNewKeyName('')
      loadKeys()
      toast.success('API key created!')
    } catch (err) {
      toast.error('Failed to create key')
    }
    setLoading(false)
  }

  const revokeKey = async (keyId) => {
    try {
      await api.delete(`/api-keys/${keyId}`)
      loadKeys()
      toast.success('Key revoked')
    } catch (err) {
      toast.error('Failed to revoke key')
    }
  }

  const copyKey = () => {
    navigator.clipboard.writeText(newKeyFull)
    setCopied(true)
    setTimeout(() => setCopied(false), 3000)
    toast.success('Copied!')
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-white flex items-center gap-2">
          <Key size={20} className="text-primary-400" />
          API Keys
        </h1>
        <button onClick={() => setShowCreate(true)} className="btn-primary text-sm flex items-center gap-1">
          <Plus size={16} /> New Key
        </button>
      </div>

      {newKeyFull && (
        <div className="card mb-4 border-primary-600/50 bg-primary-600/5">
          <p className="text-sm text-primary-300 mb-2">⚠️ Copy your key now — it won't be shown again!</p>
          <div className="flex gap-2">
            <code className="flex-1 bg-dark-900 p-2 rounded text-xs text-primary-400 break-all">{newKeyFull}</code>
            <button onClick={copyKey} className="btn-primary text-sm px-3">
              {copied ? <Check size={16} /> : <Copy size={16} />}
            </button>
          </div>
        </div>
      )}

      {showCreate && (
        <form onSubmit={createKey} className="card mb-4 space-y-3">
          <input value={newKeyName} onChange={(e) => setNewKeyName(e.target.value)} placeholder="Key name (e.g., My App)" className="input-field text-sm" required />
          <select value={newKeyProject} onChange={(e) => setNewKeyProject(e.target.value)} className="input-field text-sm">
            {PROJECTS.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <div className="flex gap-2">
            <button type="submit" disabled={loading} className="btn-primary text-sm">Create</button>
            <button type="button" onClick={() => setShowCreate(false)} className="btn-secondary text-sm">Cancel</button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {keys.map((key) => (
          <div key={key.id} className="card flex items-center justify-between">
            <div>
              <p className="text-white font-medium text-sm">{key.name}</p>
              <p className="text-dark-400 text-xs mt-1">
                {key.project} • {key.key_prefix} • Created {new Date(key.created_at).toLocaleDateString()}
              </p>
            </div>
            <button onClick={() => revokeKey(key.id)} className="p-2 text-dark-400 hover:text-red-400 transition-colors">
              <Trash2 size={16} />
            </button>
          </div>
        ))}
        {keys.length === 0 && (
          <div className="card text-center text-dark-400 text-sm">
            No API keys yet. Create one to get started.
          </div>
        )}
      </div>
    </div>
  )
}