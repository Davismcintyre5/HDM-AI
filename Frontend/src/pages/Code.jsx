import { useState, useEffect, useRef } from 'react'
import {
  Play, Loader2, Trash2, Clock, FileCode, Upload, Download,
  Copy, Check, ChevronDown, X, History, Plus, FolderOpen,
  Sun, Moon, Terminal, Zap
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/axios'

const LANGUAGES = [
  { name: 'Python', value: 'python', icon: '🐍', ext: '.py' },
  { name: 'JavaScript', value: 'javascript', icon: '🟨', ext: '.js' },
  { name: 'TypeScript', value: 'typescript', icon: '🔷', ext: '.ts' },
  { name: 'Java', value: 'java', icon: '☕', ext: '.java' },
  { name: 'C', value: 'c', icon: '⚙️', ext: '.c' },
  { name: 'C++', value: 'cpp', icon: '⚡', ext: '.cpp' },
  { name: 'Go', value: 'go', icon: '🔵', ext: '.go' },
  { name: 'Rust', value: 'rust', icon: '🦀', ext: '.rs' },
  { name: 'Ruby', value: 'ruby', icon: '💎', ext: '.rb' },
  { name: 'PHP', value: 'php', icon: '🐘', ext: '.php' },
  { name: 'Bash', value: 'bash', icon: '💻', ext: '.sh' },
  { name: 'SQL', value: 'sql', icon: '🗄️', ext: '.sql' },
]

const STARTER_CODE = {
  python: '# Write your Python code here\nprint("Hello, HDM AI!")\n',
  javascript: '// Write your JavaScript code here\nconsole.log("Hello, HDM AI!");\n',
  typescript: '// Write your TypeScript code here\nconst greeting: string = "Hello, HDM AI!";\nconsole.log(greeting);\n',
  java: '// Write your Java code here\nclass Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, HDM AI!");\n    }\n}\n',
  c: '// Write your C code here\n#include <stdio.h>\n\nint main() {\n    printf("Hello, HDM AI!\\n");\n    return 0;\n}\n',
  cpp: '// Write your C++ code here\n#include <iostream>\n\nint main() {\n    std::cout << "Hello, HDM AI!" << std::endl;\n    return 0;\n}\n',
  go: '// Write your Go code here\npackage main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, HDM AI!")\n}\n',
  rust: '// Write your Rust code here\nfn main() {\n    println!("Hello, HDM AI!");\n}\n',
  ruby: '# Write your Ruby code here\nputs "Hello, HDM AI!"\n',
  php: '// Write your PHP code here\n<?php\necho "Hello, HDM AI!";\n',
  bash: '# Write your Bash code here\necho "Hello, HDM AI!"\n',
  sql: '-- Write your SQL code here\nSELECT "Hello, HDM AI!" AS greeting;\n',
}

export default function Code() {
  const [language, setLanguage] = useState('python')
  const [code, setCode] = useState(STARTER_CODE['python'])
  const [stdin, setStdin] = useState('')
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(true)
  const [selectedHistory, setSelectedHistory] = useState(null)
  const [copied, setCopied] = useState(false)
  const [theme, setTheme] = useState('dark')
  const [fileName, setFileName] = useState('untitled')
  const editorRef = useRef(null)
  const outputRef = useRef(null)

  // Load history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('hdm_code_history')
    if (saved) {
      try {
        setHistory(JSON.parse(saved))
      } catch {}
    }
  }, [])

  // Save history to localStorage
  useEffect(() => {
    if (history.length > 0) {
      localStorage.setItem('hdm_code_history', JSON.stringify(history.slice(0, 50)))
    }
  }, [history])

  // Update starter code when language changes
  useEffect(() => {
    if (!selectedHistory) {
      setCode(STARTER_CODE[language] || '')
      setFileName(`untitled${LANGUAGES.find(l => l.value === language)?.ext || ''}`)
    }
  }, [language, selectedHistory])

  const runCode = async () => {
    if (!code.trim()) {
      toast.error('Write some code first!')
      return
    }

    setLoading(true)
    setOutput('Running...')

    try {
      const { data } = await api.post('/general/execute', {
        language,
        code,
        stdin,
      })

      const result = data.data
      const display = result.stdout || result.stderr || 'No output'
      setOutput(display)

      // Add to history
      const historyItem = {
        id: Date.now(),
        language,
        code,
        stdin,
        output: display,
        fileName,
        timestamp: new Date().toISOString(),
        status: result.exit_code === 0 ? 'success' : 'error',
        execution_time_ms: result.execution_time_ms || 0,
      }

      setHistory(prev => [historyItem, ...prev].slice(0, 50))
      setSelectedHistory(null)

      if (result.exit_code === 0) {
        toast.success(`Executed in ${result.execution_time_ms || 0}ms`)
      } else {
        toast.error('Execution failed')
      }

      // Scroll output into view
      setTimeout(() => {
        outputRef.current?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    } catch (err) {
      setOutput(`Error: ${err.response?.data?.detail || err.message}`)
      toast.error('Execution failed')
    }
    setLoading(false)
  }

  const loadHistoryItem = (item) => {
    setLanguage(item.language)
    setCode(item.code)
    setStdin(item.stdin || '')
    setFileName(item.fileName)
    setSelectedHistory(item.id)
  }

  const deleteHistoryItem = (id, e) => {
    e.stopPropagation()
    setHistory(prev => prev.filter(h => h.id !== id))
    if (selectedHistory === id) {
      setSelectedHistory(null)
      setCode(STARTER_CODE[language] || '')
    }
    toast.success('Deleted')
  }

  const clearAllHistory = () => {
    if (!confirm('Clear all execution history?')) return
    setHistory([])
    localStorage.removeItem('hdm_code_history')
    toast.success('History cleared')
  }

  const newFile = () => {
    setCode(STARTER_CODE[language] || '')
    setStdin('')
    setOutput('')
    setFileName(`untitled${LANGUAGES.find(l => l.value === language)?.ext || ''}`)
    setSelectedHistory(null)
  }

  const importFile = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.py,.js,.ts,.java,.c,.cpp,.go,.rs,.rb,.php,.sh,.sql,.txt'
    input.onchange = (e) => {
      const file = e.target.files[0]
      if (!file) return

      const reader = new FileReader()
      reader.onload = (event) => {
        setCode(event.target.result)
        setFileName(file.name)
        toast.success(`Imported: ${file.name}`)
      }
      reader.readAsText(file)
    }
    input.click()
  }

  const downloadCode = () => {
    const blob = new Blob([code], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fileName
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Downloaded!')
  }

  const copyCode = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    toast.success('Copied!')
  }

  const copyOutput = () => {
    if (!output) return
    navigator.clipboard.writeText(output)
    toast.success('Output copied!')
  }

  const handleKeyDown = (e) => {
    // Ctrl+Enter to run
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault()
      runCode()
    }
    // Tab for indentation
    if (e.key === 'Tab') {
      e.preventDefault()
      const start = e.target.selectionStart
      const end = e.target.selectionEnd
      const newCode = code.substring(0, start) + '    ' + code.substring(end)
      setCode(newCode)
      setTimeout(() => {
        e.target.selectionStart = e.target.selectionEnd = start + 4
      }, 0)
    }
  }

  const currentLang = LANGUAGES.find(l => l.value === language)

  return (
    <div className="h-full flex">
      {/* History sidebar */}
      <div className={`${showHistory ? 'w-64' : 'w-0'} border-r border-dark-800 flex-shrink-0 transition-all duration-200 overflow-hidden flex flex-col`}>
        <div className="flex items-center justify-between p-3 border-b border-dark-800">
          <h3 className="text-xs font-semibold text-dark-300 uppercase tracking-wider flex items-center gap-1.5">
            <Clock size={14} /> History
          </h3>
          <div className="flex items-center gap-1">
            <button onClick={clearAllHistory} className="p-1 text-dark-400 hover:text-red-400 rounded" title="Clear all">
              <Trash2 size={14} />
            </button>
            <button onClick={() => setShowHistory(false)} className="p-1 text-dark-400 hover:text-white rounded">
              <X size={14} />
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          {history.length === 0 && (
            <div className="p-4 text-center">
              <History size={24} className="text-dark-600 mx-auto mb-2" />
              <p className="text-xs text-dark-500">No history yet</p>
            </div>
          )}
          {history.map((item) => (
            <div
              key={item.id}
              onClick={() => loadHistoryItem(item)}
              className={`group px-3 py-2.5 border-b border-dark-800/50 cursor-pointer transition-colors ${
                selectedHistory === item.id
                  ? 'bg-primary-600/10 border-l-2 border-l-primary-500'
                  : 'hover:bg-dark-800/50 border-l-2 border-l-transparent'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 min-w-0">
                  <span className="text-xs">{LANGUAGES.find(l => l.value === item.language)?.icon || '📄'}</span>
                  <span className="text-xs text-dark-300 truncate">{item.fileName || 'untitled'}</span>
                </div>
                <button
                  onClick={(e) => deleteHistoryItem(item.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-0.5 text-dark-400 hover:text-red-400 rounded transition-all"
                >
                  <X size={12} />
                </button>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className={`w-1.5 h-1.5 rounded-full ${item.status === 'success' ? 'bg-green-400' : 'bg-red-400'}`} />
                <span className="text-[10px] text-dark-500">
                  {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
                {item.execution_time_ms > 0 && (
                  <span className="text-[10px] text-dark-600">{item.execution_time_ms}ms</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main editor */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Toolbar */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-dark-800 bg-dark-900/50 flex-shrink-0">
          <div className="flex items-center gap-2">
            {/* History toggle */}
            {!showHistory && (
              <button
                onClick={() => setShowHistory(true)}
                className="p-1.5 text-dark-400 hover:text-white rounded-lg hover:bg-dark-800"
                title="Show history"
              >
                <History size={16} />
              </button>
            )}

            {/* File name */}
            <div className="flex items-center gap-2">
              <FileCode size={16} className="text-primary-400" />
              <input
                value={fileName}
                onChange={(e) => setFileName(e.target.value)}
                className="bg-transparent text-sm text-white font-medium outline-none border-b border-transparent hover:border-dark-600 focus:border-primary-500 px-1 w-48"
              />
            </div>

            {/* Language selector */}
            <div className="relative">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="appearance-none bg-dark-800 border border-dark-600 rounded-lg px-3 py-1.5 text-xs text-dark-200 outline-none focus:border-primary-500 cursor-pointer pr-7"
              >
                {LANGUAGES.map((lang) => (
                  <option key={lang.value} value={lang.value}>
                    {lang.icon} {lang.name}
                  </option>
                ))}
              </select>
              <ChevronDown size={12} className="absolute right-2 top-2 text-dark-400 pointer-events-none" />
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            {/* New file */}
            <button onClick={newFile} className="p-1.5 text-dark-400 hover:text-white rounded-lg hover:bg-dark-800" title="New file">
              <Plus size={16} />
            </button>

            {/* Import */}
            <button onClick={importFile} className="p-1.5 text-dark-400 hover:text-white rounded-lg hover:bg-dark-800" title="Import file">
              <Upload size={16} />
            </button>

            {/* Download */}
            <button onClick={downloadCode} className="p-1.5 text-dark-400 hover:text-white rounded-lg hover:bg-dark-800" title="Download">
              <Download size={16} />
            </button>

            {/* Copy */}
            <button onClick={copyCode} className="p-1.5 text-dark-400 hover:text-white rounded-lg hover:bg-dark-800" title="Copy code">
              {copied ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
            </button>

            {/* Theme toggle */}
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-1.5 text-dark-400 hover:text-white rounded-lg hover:bg-dark-800"
              title="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </button>

            {/* Divider */}
            <div className="w-px h-5 bg-dark-700 mx-1" />

            {/* Run button */}
            <button
              onClick={runCode}
              disabled={loading}
              className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                loading
                  ? 'bg-dark-700 text-dark-400 cursor-wait'
                  : 'bg-green-600 hover:bg-green-700 text-white shadow-lg shadow-green-600/20'
              }`}
            >
              {loading ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Play size={16} />
              )}
              {loading ? 'Running...' : 'Run'}
              <span className="text-[10px] opacity-60 ml-0.5">Ctrl+Enter</span>
            </button>
          </div>
        </div>

        {/* Editor + Output split */}
        <div className="flex-1 flex flex-col">
          {/* Code editor */}
          <div className="flex-1 relative">
            <textarea
              ref={editorRef}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              onKeyDown={handleKeyDown}
              className={`w-full h-full resize-none p-4 font-mono text-sm leading-relaxed outline-none ${
                theme === 'dark'
                  ? 'bg-dark-950 text-dark-100'
                  : 'bg-gray-50 text-gray-900'
              }`}
              placeholder="Write your code here..."
              spellCheck={false}
              style={{ tabSize: 4 }}
            />
            {/* Line count */}
            <div className="absolute bottom-3 right-3 text-[10px] text-dark-600 pointer-events-none">
              {code.split('\n').length} lines • {code.length} chars
            </div>
          </div>

          {/* Stdin input (collapsible) */}
          <div className="border-t border-dark-800">
            <details className="group">
              <summary className="flex items-center gap-2 px-4 py-2 cursor-pointer text-xs text-dark-400 hover:text-dark-300 select-none">
                <Terminal size={14} />
                Input (stdin)
                <ChevronDown size={12} className="group-open:rotate-180 transition-transform" />
              </summary>
              <textarea
                value={stdin}
                onChange={(e) => setStdin(e.target.value)}
                placeholder="Enter input for your program..."
                className="w-full h-20 resize-none px-4 py-2 bg-dark-900 border-t border-dark-800 text-sm text-dark-200 font-mono outline-none"
                spellCheck={false}
              />
            </details>
          </div>

          {/* Output panel */}
          <div
            ref={outputRef}
            className="border-t-2 border-dark-700 max-h-64 overflow-y-auto"
          >
            <div className="flex items-center justify-between px-4 py-1.5 bg-dark-900 sticky top-0 border-b border-dark-800">
              <span className="text-xs font-medium text-dark-400 flex items-center gap-2">
                <Zap size={12} className="text-yellow-400" />
                Output
              </span>
              <button
                onClick={copyOutput}
                className="p-1 text-dark-400 hover:text-white rounded"
                title="Copy output"
                disabled={!output}
              >
                <Copy size={12} />
              </button>
            </div>
            <pre className={`p-4 font-mono text-sm leading-relaxed whitespace-pre-wrap ${
              output.includes('Error') || output.includes('error')
                ? 'text-red-400'
                : 'text-green-400'
            } ${theme === 'dark' ? 'bg-dark-950' : 'bg-gray-900'}`}>
              {output || 'Output will appear here...'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  )
}