import { useState, useEffect, useRef } from 'react';
import { Play, Loader2, Copy, Check, Download, Upload, Plus, FileCode, Terminal, Zap, ChevronDown, X, Clock, History } from 'lucide-react';
import api from '../api/axios';
import Button from '../components/ui/Button';
import { useToast } from '../components/ui/Toast';

const LANGUAGES = [
  { name: 'Python', value: 'python', ext: '.py' },
  { name: 'JavaScript', value: 'javascript', ext: '.js' },
  { name: 'TypeScript', value: 'typescript', ext: '.ts' },
  { name: 'Java', value: 'java', ext: '.java' },
  { name: 'C', value: 'c', ext: '.c' },
  { name: 'C++', value: 'cpp', ext: '.cpp' },
  { name: 'Go', value: 'go', ext: '.go' },
  { name: 'Rust', value: 'rust', ext: '.rs' },
  { name: 'Bash', value: 'bash', ext: '.sh' },
  { name: 'SQL', value: 'sql', ext: '.sql' },
];

const STARTERS = {
  python: 'print("Hello, HDM AI!")',
  javascript: 'console.log("Hello, HDM AI!");',
  bash: 'echo "Hello, HDM AI!"',
  sql: 'SELECT "Hello, HDM AI!" AS greeting;',
};

export default function Code() {
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState(STARTERS.python);
  const [stdin, setStdin] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(true);
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [copied, setCopied] = useState(false);
  const [fileName, setFileName] = useState('untitled.py');
  const outputRef = useRef(null);
  const { addToast } = useToast();

  useEffect(() => {
    const saved = localStorage.getItem('hdm_code_history');
    if (saved) { try { setHistory(JSON.parse(saved)); } catch {} }
  }, []);

  useEffect(() => {
    if (history.length > 0) localStorage.setItem('hdm_code_history', JSON.stringify(history.slice(0, 50)));
  }, [history]);

  useEffect(() => {
    if (!selectedHistory) {
      setCode(STARTERS[language] || `// ${language}\n`);
      setFileName(`untitled${LANGUAGES.find(l => l.value === language)?.ext || '.txt'}`);
    }
  }, [language, selectedHistory]);

  const run = async () => {
    if (!code.trim()) return addToast('Write some code first', 'error');
    setLoading(true);
    setOutput('Running...');
    try {
      const { data } = await api.post('/general/execute', { language, code, stdin });
      const result = data.data;
      setOutput(result.stdout || result.stderr || 'No output');
      const item = { id: Date.now(), language, code, stdin, output: result.stdout || result.stderr, fileName, timestamp: new Date().toISOString(), status: result.exit_code === 0 ? 'success' : 'error' };
      setHistory(prev => [item, ...prev].slice(0, 50));
      setSelectedHistory(null);
      addToast(result.exit_code === 0 ? 'Executed' : 'Failed', result.exit_code === 0 ? 'success' : 'error');
      setTimeout(() => outputRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
    } catch (err) {
      setOutput(`Error: ${err.response?.data?.detail || err.message}`);
      addToast('Execution failed', 'error');
    }
    setLoading(false);
  };

  const loadHistoryItem = (item) => {
    setLanguage(item.language);
    setCode(item.code);
    setStdin(item.stdin || '');
    setFileName(item.fileName);
    setSelectedHistory(item.id);
  };

  const deleteHistoryItem = (id, e) => {
    e.stopPropagation();
    setHistory(prev => prev.filter(h => h.id !== id));
    if (selectedHistory === id) { setSelectedHistory(null); setCode(STARTERS[language] || ''); }
  };

  const newFile = () => { setCode(STARTERS[language] || ''); setStdin(''); setOutput(''); setFileName(`untitled${LANGUAGES.find(l => l.value === language)?.ext || '.txt'}`); setSelectedHistory(null); };

  const importFile = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => { setCode(ev.target.result); setFileName(file.name); addToast(`Imported: ${file.name}`, 'success'); };
      reader.readAsText(file);
    };
    input.click();
  };

  const downloadCode = () => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = fileName; a.click();
    URL.revokeObjectURL(url);
  };

  const copyCode = () => { navigator.clipboard.writeText(code); setCopied(true); setTimeout(() => setCopied(false), 2000); addToast('Copied!', 'success'); };
  const copyOutput = () => { if (!output) return; navigator.clipboard.writeText(output); addToast('Output copied!', 'success'); };

  const handleKeyDown = (e) => {
    if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); run(); }
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = e.target.selectionStart, end = e.target.selectionEnd;
      setCode(code.substring(0, start) + '    ' + code.substring(end));
      setTimeout(() => { e.target.selectionStart = e.target.selectionEnd = start + 4; }, 0);
    }
  };

  return (
    <div className="h-full flex">
      <div className={`${showHistory ? 'w-64' : 'w-0'} border-r border-border shrink-0 transition-all overflow-hidden flex flex-col`}>
        <div className="flex items-center justify-between p-3 border-b border-border">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider flex items-center gap-1.5"><Clock size={14} /> History</h3>
          <button onClick={() => { setHistory([]); localStorage.removeItem('hdm_code_history'); addToast('Cleared', 'info'); }} className="p-1 text-text-muted hover:text-danger rounded"><X size={14} /></button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {history.length === 0 && <div className="p-4 text-center"><History size={24} className="text-text-muted mx-auto mb-2 opacity-30" /><p className="text-xs text-text-muted">No history</p></div>}
          {history.map(item => (
            <div key={item.id} onClick={() => loadHistoryItem(item)}
              className={`group px-3 py-2.5 border-b border-border/50 cursor-pointer transition-colors ${selectedHistory === item.id ? 'bg-primary/10 border-l-2 border-l-primary' : 'hover:bg-bg-tertiary border-l-2 border-l-transparent'}`}>
              <div className="flex items-center justify-between">
                <span className="text-xs text-text-secondary truncate">{item.fileName}</span>
                <button onClick={(e) => deleteHistoryItem(item.id, e)} className="opacity-0 group-hover:opacity-100 p-0.5 text-text-muted hover:text-danger rounded"><X size={12} /></button>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className={`w-1.5 h-1.5 rounded-full ${item.status === 'success' ? 'bg-success' : 'bg-danger'}`} />
                <span className="text-[10px] text-text-muted">{new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-bg-secondary shrink-0">
          <div className="flex items-center gap-2">
            {!showHistory && <button onClick={() => setShowHistory(true)} className="p-1.5 text-text-muted hover:text-text-primary rounded-lg hover:bg-bg-tertiary"><History size={16} /></button>}
            <FileCode size={16} className="text-primary" />
            <input value={fileName} onChange={e => setFileName(e.target.value)} className="bg-transparent text-sm text-text-primary font-medium outline-none border-b border-transparent hover:border-border focus:border-primary px-1 w-48" />
            <div className="relative">
              <select value={language} onChange={e => setLanguage(e.target.value)} className="appearance-none bg-bg-tertiary border border-border rounded-lg px-3 py-1.5 text-xs text-text-secondary outline-none focus:border-primary pr-7">
                {LANGUAGES.map(l => <option key={l.value} value={l.value}>{l.name}</option>)}
              </select>
              <ChevronDown size={12} className="absolute right-2 top-2 text-text-muted pointer-events-none" />
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <button onClick={newFile} className="p-1.5 text-text-muted hover:text-text-primary rounded-lg hover:bg-bg-tertiary" title="New"><Plus size={16} /></button>
            <button onClick={importFile} className="p-1.5 text-text-muted hover:text-text-primary rounded-lg hover:bg-bg-tertiary" title="Import"><Upload size={16} /></button>
            <button onClick={downloadCode} className="p-1.5 text-text-muted hover:text-text-primary rounded-lg hover:bg-bg-tertiary" title="Download"><Download size={16} /></button>
            <button onClick={copyCode} className="p-1.5 text-text-muted hover:text-text-primary rounded-lg hover:bg-bg-tertiary" title="Copy">{copied ? <Check size={16} className="text-success" /> : <Copy size={16} />}</button>
            <div className="w-px h-5 bg-border mx-1" />
            <Button size="sm" onClick={run} loading={loading}>{loading ? 'Running' : 'Run'} <span className="text-[10px] opacity-60 ml-1">Ctrl+Enter</span></Button>
          </div>
        </div>

        <div className="flex-1 flex flex-col">
          <textarea value={code} onChange={e => setCode(e.target.value)} onKeyDown={handleKeyDown}
            className="flex-1 resize-none p-4 font-mono text-sm bg-bg text-text-primary outline-none" placeholder="Write your code here..." spellCheck={false} />

          <details className="group border-t border-border">
            <summary className="flex items-center gap-2 px-4 py-2 cursor-pointer text-xs text-text-muted hover:text-text-secondary select-none"><Terminal size={14} /> Input (stdin) <ChevronDown size={12} className="group-open:rotate-180 transition-transform" /></summary>
            <textarea value={stdin} onChange={e => setStdin(e.target.value)} placeholder="Enter input..." className="w-full h-20 resize-none px-4 py-2 bg-bg-tertiary border-t border-border text-sm text-text-secondary font-mono outline-none" spellCheck={false} />
          </details>

          <div ref={outputRef} className="border-t-2 border-border max-h-64 overflow-y-auto">
            <div className="flex items-center justify-between px-4 py-1.5 bg-bg-secondary sticky top-0 border-b border-border">
              <span className="text-xs font-medium text-text-muted flex items-center gap-2"><Zap size={12} className="text-yellow-400" /> Output</span>
              <button onClick={copyOutput} className="p-1 text-text-muted hover:text-text-primary rounded" disabled={!output}><Copy size={12} /></button>
            </div>
            <pre className={`p-4 font-mono text-sm whitespace-pre-wrap ${output.includes('Error') || output.includes('error') ? 'text-danger' : 'text-success'}`}>{output || 'Output will appear here...'}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}