import { useState, useRef, useEffect } from 'react';
import { Send, Search, Brain, Paperclip, FileText, X } from 'lucide-react';
import Button from '../ui/Button';

export default function ChatInput({ onSend, loading }) {
  const [message, setMessage] = useState('');
  const [searchEnabled, setSearchEnabled] = useState(false);
  const [deepThink, setDeepThink] = useState(false);
  const [files, setFiles] = useState([]);
  const fileInputRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const hasText = message.trim().length > 0;
    const hasFiles = files.length > 0;
    if ((!hasText && !hasFiles) || loading) return;
    onSend({ message: message.trim(), searchEnabled, deepThink, files });
    setMessage('');
    setFiles([]);
  };

  const handleFileSelect = (e) => {
    setFiles(prev => [...prev, ...Array.from(e.target.files)].slice(0, 5));
    e.target.value = '';
  };

  const removeFile = (i) => setFiles(prev => prev.filter((_, idx) => idx !== i));

  const canSend = message.trim().length > 0 || files.length > 0;

  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs cursor-pointer bg-bg-tertiary text-text-secondary hover:text-text-primary hover:bg-border transition-colors">
          <Paperclip size={14} /> Files
          <input ref={fileInputRef} type="file" multiple className="hidden" onChange={handleFileSelect} />
        </label>
        <button
          type="button"
          onClick={() => setSearchEnabled(!searchEnabled)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${searchEnabled ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'bg-bg-tertiary text-text-secondary hover:text-text-primary border border-transparent'}`}
        >
          <Search size={14} /> {searchEnabled ? 'Search ON' : 'Search'}
        </button>
        <button
          type="button"
          onClick={() => setDeepThink(!deepThink)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${deepThink ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' : 'bg-bg-tertiary text-text-secondary hover:text-text-primary border border-transparent'}`}
        >
          <Brain size={14} /> {deepThink ? 'Deep Think ON' : 'Deep Think'}
        </button>
      </div>

      {files.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {files.map((f, i) => (
            <div key={i} className="flex items-center gap-1.5 px-2.5 py-1 bg-bg-tertiary border border-border rounded-lg text-xs text-text-secondary">
              <FileText size={12} />
              <span className="max-w-[120px] truncate">{f.name}</span>
              <button onClick={() => removeFile(i)} className="text-text-muted hover:text-danger"><X size={12} /></button>
            </div>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          ref={inputRef}
          value={message}
          onChange={e => setMessage(e.target.value)}
          placeholder={files.length > 0 ? `Ask about ${files.length} file(s) or send...` : 'Type your message...'}
          className="flex-1 px-4 py-2.5 bg-bg-tertiary border border-border rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-primary text-sm"
          disabled={loading}
        />
        <Button type="submit" size="sm" loading={loading} disabled={!canSend}>
          <Send size={18} />
        </Button>
      </form>
    </div>
  );
}