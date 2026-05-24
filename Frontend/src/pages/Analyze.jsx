import { useState } from 'react'
import { FileSearch, Loader2, Copy, Check, BarChart3, Smile, Hash, Users, Database, Layers, Zap } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/axios'

const ANALYSIS_TYPES = [
  { value: 'summary', label: 'Summary', icon: FileSearch, color: 'text-blue-400', bg: 'bg-blue-500/10', desc: 'Condense text into key points' },
  { value: 'sentiment', label: 'Sentiment', icon: Smile, color: 'text-yellow-400', bg: 'bg-yellow-500/10', desc: 'Analyze emotional tone' },
  { value: 'keywords', label: 'Keywords', icon: Hash, color: 'text-green-400', bg: 'bg-green-500/10', desc: 'Extract important terms' },
  { value: 'entities', label: 'Entities', icon: Users, color: 'text-purple-400', bg: 'bg-purple-500/10', desc: 'Find people, places, orgs' },
  { value: 'data', label: 'Data Extraction', icon: Database, color: 'text-orange-400', bg: 'bg-orange-500/10', desc: 'Extract structured data' },
  { value: 'full', label: 'Full Analysis', icon: Layers, color: 'text-pink-400', bg: 'bg-pink-500/10', desc: 'Complete breakdown' },
]

export default function Analyze() {
  const [content, setContent] = useState('')
  const [type, setType] = useState('summary')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [history, setHistory] = useState([])

  const analyze = async (e) => {
    e.preventDefault()
    if (!content.trim() || loading) return
    setLoading(true)
    setResult(null)

    try {
      const { data } = await api.post('/general/analyze', { content, analysis_type: type })
      setResult(data.data)
      setHistory(prev => [{
        id: Date.now(),
        type,
        content: content.slice(0, 200),
        result: data.data,
        timestamp: new Date().toISOString(),
      }, ...prev].slice(0, 20))
      toast.success('Analysis complete')
    } catch (err) {
      toast.error('Analysis failed')
    }
    setLoading(false)
  }

  const copyResult = () => {
    const text = typeof result?.result === 'object' ? JSON.stringify(result.result, null, 2) : result?.result
    navigator.clipboard.writeText(text || '')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    toast.success('Copied!')
  }

  const currentType = ANALYSIS_TYPES.find(t => t.value === type)

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-dark-800 px-6 py-4">
        <h1 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-lg flex items-center justify-center">
            <FileSearch size={18} className="text-blue-400" />
          </div>
          Content Analyzer
        </h1>

        <form onSubmit={analyze} className="space-y-3">
          <textarea
            value={content}
            onChange={e => setContent(e.target.value)}
            placeholder="Paste text, article, or data to analyze..."
            className="input-field h-32 resize-none text-sm"
          />
          <div className="flex items-center gap-3">
            <button type="submit" disabled={loading || !content.trim()} className="btn-primary flex items-center gap-2">
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
              Analyze
            </button>
            <span className="text-xs text-dark-500">{content.length} characters</span>
          </div>
        </form>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Analysis type selector */}
        <div className="max-w-4xl mx-auto mb-6">
          <h3 className="text-xs font-semibold text-dark-400 uppercase tracking-wider mb-3">Analysis Type</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {ANALYSIS_TYPES.map(t => (
              <button
                key={t.value}
                onClick={() => { setType(t.value); setResult(null) }}
                className={`flex items-center gap-3 p-3 rounded-xl text-left transition-all ${
                  type === t.value
                    ? 'bg-dark-800 border border-primary-500/30 ring-1 ring-primary-500/10'
                    : 'bg-dark-800/50 border border-dark-700/50 hover:border-dark-600'
                }`}
              >
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${t.bg}`}>
                  <t.icon size={18} className={t.color} />
                </div>
                <div>
                  <p className="text-sm font-medium text-white">{t.label}</p>
                  <p className="text-[10px] text-dark-500">{t.desc}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Result */}
        <div className="max-w-4xl mx-auto">
          {loading && (
            <div className="card flex items-center justify-center py-12">
              <div className="text-center">
                <Loader2 size={32} className="text-primary-400 animate-spin mx-auto mb-3" />
                <p className="text-dark-400 text-sm">Analyzing content...</p>
              </div>
            </div>
          )}

          {!loading && !result && history.length === 0 && (
            <div className="card flex items-center justify-center py-12">
              <div className="text-center">
                <BarChart3 size={32} className="text-dark-600 mx-auto mb-3" />
                <p className="text-dark-400 text-sm">Select analysis type and paste content above</p>
              </div>
            </div>
          )}

          {result && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${currentType?.bg}`}>
                    <currentType.icon size={16} className={currentType?.color} />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-white">{currentType?.label} Results</h3>
                    <p className="text-[10px] text-dark-500">Confidence: {((result.confidence || 0.85) * 100).toFixed(0)}%</p>
                  </div>
                </div>
                <button onClick={copyResult} className="btn-secondary text-xs flex items-center gap-1.5">
                  {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>

              {/* Render result based on type */}
              {type === 'sentiment' && result.result && (
                <div className="space-y-4">
                  <div className="flex items-center gap-4 p-4 bg-dark-900 rounded-xl">
                    <div className={`text-4xl ${result.result.score > 0 ? 'text-green-400' : result.result.score < 0 ? 'text-red-400' : 'text-yellow-400'}`}>
                      {result.result.score > 0 ? '😊' : result.result.score < 0 ? '😞' : '😐'}
                    </div>
                    <div>
                      <p className="text-white font-medium capitalize">{result.result.sentiment}</p>
                      <p className="text-dark-400 text-sm">Score: {result.result.score}</p>
                      <p className="text-dark-500 text-xs mt-1">{result.result.explanation}</p>
                    </div>
                  </div>
                </div>
              )}

              {type === 'keywords' && result.result && (
                <div className="flex flex-wrap gap-2">
                  {(Array.isArray(result.result) ? result.result : []).map((kw, i) => (
                    <span key={i} className="px-3 py-1.5 bg-dark-800 border border-dark-700 rounded-full text-sm text-dark-200">
                      #{kw}
                    </span>
                  ))}
                </div>
              )}

              {type === 'entities' && result.result && (
                <div className="space-y-2">
                  {(Array.isArray(result.result) ? result.result : []).map((e, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-dark-900 rounded-lg">
                      <span className="text-sm text-white">{e.name}</span>
                      <span className="px-2 py-0.5 bg-dark-800 rounded text-xs text-dark-400 capitalize">{e.type}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Default: show JSON or text */}
              {!['sentiment', 'keywords', 'entities'].includes(type) && (
                <pre className="bg-dark-900 p-4 rounded-xl text-sm text-dark-200 whitespace-pre-wrap font-sans leading-relaxed overflow-x-auto max-h-96 overflow-y-auto">
                  {typeof result.result === 'object' ? JSON.stringify(result.result, null, 2) : result.result}
                </pre>
              )}
            </div>
          )}

          {/* History */}
          {history.length > 1 && (
            <div className="mt-8">
              <h3 className="text-xs font-semibold text-dark-400 uppercase tracking-wider mb-3">Recent Analyses</h3>
              <div className="space-y-2">
                {history.slice(1, 6).map(h => {
                  const ht = ANALYSIS_TYPES.find(t => t.value === h.type)
                  return (
                    <button
                      key={h.id}
                      onClick={() => { setType(h.type); setContent(h.content); setResult(h.result) }}
                      className="w-full flex items-center gap-3 p-3 bg-dark-800/50 border border-dark-700/50 rounded-xl text-left hover:border-dark-600 transition-all"
                    >
                      <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${ht?.bg}`}>
                        <ht.icon size={14} className={ht?.color} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-dark-300 truncate">{h.content}</p>
                        <p className="text-[10px] text-dark-500">{ht?.label} • {new Date(h.timestamp).toLocaleTimeString()}</p>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}