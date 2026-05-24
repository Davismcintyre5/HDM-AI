import { useState, useRef } from 'react'
import { Send, Plus, Search, Brain, FileText, X, Paperclip } from 'lucide-react'

export default function ChatInput({ onSend, loading, disabled }) {
  const [message, setMessage] = useState('')
  const [searchEnabled, setSearchEnabled] = useState(false)
  const [deepThink, setDeepThink] = useState(false)
  const [files, setFiles] = useState([])
  const fileInputRef = useRef(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!message.trim() || loading || disabled) return
    onSend({
      message: message.trim(),
      searchEnabled,
      deepThink,
      files,
    })
    setMessage('')
    setFiles([])
  }

  const handleFileSelect = (e) => {
    const selected = Array.from(e.target.files)
    setFiles(prev => [...prev, ...selected].slice(0, 5)) // Max 5 files
    e.target.value = ''
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="flex-shrink-0 border-t border-dark-800 bg-dark-950/80 backdrop-blur">
      <div className="max-w-3xl mx-auto px-4 py-3">
        {/* Toggles row */}
        <div className="flex items-center gap-2 mb-2">
          {/* File upload */}
          <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs cursor-pointer transition-colors bg-dark-800 text-dark-300 hover:text-white hover:bg-dark-700">
            <Paperclip size={14} />
            Files
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={handleFileSelect}
              accept=".pdf,.png,.jpg,.jpeg,.csv,.xlsx,.xls,.txt,.md,.py,.js,.json"
            />
          </label>

          {/* Search toggle */}
          <button
            type="button"
            onClick={() => setSearchEnabled(!searchEnabled)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              searchEnabled
                ? 'bg-blue-600/20 text-blue-400 border border-blue-600/50'
                : 'bg-dark-800 text-dark-300 hover:text-white hover:bg-dark-700 border border-transparent'
            }`}
          >
            <Search size={14} />
            {searchEnabled ? 'Search ON' : 'Search'}
          </button>

          {/* Deep Think toggle */}
          <button
            type="button"
            onClick={() => setDeepThink(!deepThink)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              deepThink
                ? 'bg-purple-600/20 text-purple-400 border border-purple-600/50'
                : 'bg-dark-800 text-dark-300 hover:text-white hover:bg-dark-700 border border-transparent'
            }`}
          >
            <Brain size={14} />
            {deepThink ? 'Deep Think ON' : 'Deep Think'}
          </button>
        </div>

        {/* Uploaded files */}
        {files.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2">
            {files.map((file, i) => (
              <div
                key={i}
                className="flex items-center gap-1.5 px-2.5 py-1 bg-dark-800 border border-dark-600 rounded-lg text-xs text-dark-300"
              >
                <FileText size={12} className="text-dark-400" />
                <span className="max-w-[120px] truncate">{file.name}</span>
                <button
                  onClick={() => removeFile(i)}
                  className="text-dark-400 hover:text-red-400 transition-colors"
                >
                  <X size={12} />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Input row */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              files.length > 0
                ? `Ask about ${files.length} file(s)...`
                : deepThink
                ? 'Ask a complex question... (Deep Think)'
                : 'Type your message...'
            }
            className="input-field flex-1 text-sm"
            disabled={loading || disabled}
            autoFocus
          />
          <button
            type="submit"
            disabled={loading || disabled || !message.trim()}
            className={`btn-primary px-4 flex items-center gap-2 ${
              deepThink ? 'bg-purple-600 hover:bg-purple-700' : ''
            }`}
          >
            <Send size={18} />
          </button>
        </form>

        {/* Footer hint */}
        <p className="text-xs text-dark-500 text-center mt-2">
          {deepThink
            ? 'Deep Think uses more tokens for thorough reasoning'
            : 'HDM AI can make mistakes. Verify important information.'}
        </p>
      </div>
    </div>
  )
}