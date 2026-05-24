import { useState } from 'react'
import { Play, Loader2 } from 'lucide-react'
import api from '../api/axios'

const LANGUAGES = [
  'python', 'javascript', 'typescript', 'java', 'c', 'cpp',
  'csharp', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'sql', 'bash',
]

export default function CodeEditor() {
  const [language, setLanguage] = useState('python')
  const [code, setCode] = useState('print("Hello, HDM AI!")')
  const [stdin, setStdin] = useState('')
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)

  const runCode = async () => {
    setLoading(true)
    setOutput('Running...')
    try {
      const { data } = await api.post('/general/execute', { language, code, stdin })
      if (data.data.success) {
        setOutput(data.data.stdout || data.data.stderr || 'No output')
      } else {
        setOutput(`Error: ${data.data.error || 'Execution failed'}`)
      }
    } catch (err) {
      setOutput(`Error: ${err.response?.data?.detail || err.message}`)
    }
    setLoading(false)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-[calc(100vh-12rem)]">
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="input-field w-40"
          >
            {LANGUAGES.map((lang) => (
              <option key={lang} value={lang}>{lang}</option>
            ))}
          </select>
          <button onClick={runCode} disabled={loading} className="btn-primary flex items-center gap-2">
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
            Run
          </button>
        </div>
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="flex-1 input-field font-mono text-sm resize-none"
          placeholder="Write your code here..."
          spellCheck={false}
        />
        <input
          value={stdin}
          onChange={(e) => setStdin(e.target.value)}
          placeholder="Stdin (optional)"
          className="input-field text-sm"
        />
      </div>
      <div className="flex flex-col">
        <label className="text-sm text-dark-400 mb-2">Output</label>
        <pre className="flex-1 bg-dark-900 border border-dark-600 rounded-lg p-4 font-mono text-sm text-green-400 overflow-auto whitespace-pre-wrap">
          {output || 'Output will appear here...'}
        </pre>
      </div>
    </div>
  )
}