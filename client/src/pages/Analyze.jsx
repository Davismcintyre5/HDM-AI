import { useState, useRef } from 'react';
import { FileSearch, Loader2, Copy, Check, BarChart3, Smile, Hash, Users, Database, Layers, Paperclip, X, FileText } from 'lucide-react';
import api from '../api/axios';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { useToast } from '../components/ui/Toast';

const TYPES = [
  { value: 'summary', label: 'Summary', icon: FileSearch, color: 'text-blue-400', desc: 'Condense into key points' },
  { value: 'sentiment', label: 'Sentiment', icon: Smile, color: 'text-yellow-400', desc: 'Analyze emotional tone' },
  { value: 'keywords', label: 'Keywords', icon: Hash, color: 'text-green-400', desc: 'Extract important terms' },
  { value: 'entities', label: 'Entities', icon: Users, color: 'text-purple-400', desc: 'Find people, places, orgs' },
  { value: 'data', label: 'Data Extraction', icon: Database, color: 'text-orange-400', desc: 'Extract structured data' },
  { value: 'full', label: 'Full Analysis', icon: Layers, color: 'text-pink-400', desc: 'Complete breakdown' },
];

export default function Analyze() {
  const [content, setContent] = useState('');
  const [type, setType] = useState('summary');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [files, setFiles] = useState([]);
  const fileInputRef = useRef(null);
  const { addToast } = useToast();

  const handleFileSelect = (e) => {
    const selected = Array.from(e.target.files);
    setFiles(prev => [...prev, ...selected].slice(0, 3));
    e.target.value = '';
  };

  const removeFile = (i) => setFiles(prev => prev.filter((_, idx) => idx !== i));

  const analyze = async (e) => {
    e.preventDefault();
    const hasContent = content.trim().length > 0;
    const hasFiles = files.length > 0;
    if ((!hasContent && !hasFiles) || loading) return;
    setLoading(true);
    setResult(null);

    try {
      let textToAnalyze = content;

      if (hasFiles) {
        for (const file of files) {
          const fileText = await file.text();
          textToAnalyze += `\n\n[File: ${file.name}]\n${fileText.slice(0, 5000)}`;
        }
      }

      const { data } = await api.post('/general/analyze', { content: textToAnalyze, analysis_type: type });
      setResult(data.data || data);
      addToast('Analysis complete', 'success');
      setFiles([]);
    } catch (err) {
      addToast(err.response?.data?.error || 'Analysis failed', 'error');
    }
    setLoading(false);
  };

  const copyResult = () => {
    const text = typeof result?.result === 'object' ? JSON.stringify(result.result, null, 2) : result?.result;
    navigator.clipboard.writeText(text || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    addToast('Copied!', 'success');
  };

  const currentType = TYPES.find(t => t.value === type);

  return (
    <div className="h-full flex flex-col max-w-4xl mx-auto">
      <div className="flex-shrink-0 border-b border-border px-6 py-4">
        <h1 className="text-lg font-semibold text-text-primary flex items-center gap-2 mb-4">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center"><FileSearch size={18} className="text-primary" /></div>
          Content Analyzer
        </h1>
        <form onSubmit={analyze} className="space-y-3">
          <textarea value={content} onChange={e => setContent(e.target.value)} placeholder="Paste text, article, or data to analyze..." className="w-full h-32 bg-bg-tertiary border border-border rounded-xl p-3 text-text-primary placeholder-text-muted text-sm resize-none focus:outline-none focus:border-primary" />

          {files.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {files.map((f, i) => (
                <div key={i} className="flex items-center gap-1.5 px-2.5 py-1 bg-bg-tertiary border border-border rounded-lg text-xs text-text-secondary">
                  <FileText size={12} />
                  <span className="max-w-[150px] truncate">{f.name}</span>
                  <button type="button" onClick={() => removeFile(i)} className="text-text-muted hover:text-danger"><X size={12} /></button>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center gap-3">
            <Button type="submit" disabled={loading || (!content.trim() && files.length === 0)} loading={loading} size="sm">Analyze</Button>
            <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs cursor-pointer bg-bg-tertiary text-text-secondary hover:text-text-primary hover:bg-border transition-colors">
              <Paperclip size={14} /> Upload File
              <input ref={fileInputRef} type="file" className="hidden" onChange={handleFileSelect} accept=".txt,.md,.csv,.json,.html,.xml,.log" />
            </label>
            <span className="text-xs text-text-muted">{content.length} characters</span>
          </div>
        </form>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mb-6">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">Analysis Type</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {TYPES.map(t => (
              <button key={t.value} onClick={() => { setType(t.value); setResult(null); }}
                className={`flex items-center gap-3 p-3 rounded-xl text-left transition-all ${type === t.value ? 'bg-primary/10 border border-primary/30' : 'bg-bg-secondary border border-border hover:border-text-muted'}`}>
                <div className="w-9 h-9 rounded-lg flex items-center justify-center bg-bg-tertiary"><t.icon size={18} className={t.color} /></div>
                <div><p className="text-sm font-medium text-text-primary">{t.label}</p><p className="text-[10px] text-text-muted">{t.desc}</p></div>
              </button>
            ))}
          </div>
        </div>

        {loading && (
          <div className="flex justify-center py-12">
            <div className="text-center"><Loader2 size={32} className="text-primary animate-spin mx-auto mb-3" /><p className="text-text-muted text-sm">Analyzing...</p></div>
          </div>
        )}

        {!loading && !result && (
          <Card className="text-center py-12"><BarChart3 size={32} className="text-text-muted mx-auto mb-3 opacity-30" /><p className="text-text-muted text-sm">Select analysis type and paste content or upload a file</p></Card>
        )}

        {result && (
          <Card>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-bg-tertiary"><currentType.icon size={16} className={currentType.color} /></div>
                <div><h3 className="text-sm font-medium text-text-primary">{currentType.label} Results</h3><p className="text-[10px] text-text-muted">Confidence: {((result.confidence || 0.85) * 100).toFixed(0)}%</p></div>
              </div>
              <Button variant="ghost" size="sm" onClick={copyResult}>{copied ? <Check size={14} className="text-success" /> : <Copy size={14} />} {copied ? 'Copied' : 'Copy'}</Button>
            </div>

            {type === 'sentiment' && result.result && (
              <div className="p-4 bg-bg-tertiary rounded-xl flex items-center gap-4">
                <div className={`text-4xl ${result.result.score > 0 ? 'text-success' : result.result.score < 0 ? 'text-danger' : 'text-yellow-400'}`}>
                  {result.result.score > 0 ? '😊' : result.result.score < 0 ? '😞' : '😐'}
                </div>
                <div><p className="text-text-primary font-medium capitalize">{result.result.sentiment}</p><p className="text-text-secondary text-sm">Score: {result.result.score}</p></div>
              </div>
            )}

            {type === 'keywords' && result.result && (
              <div className="flex flex-wrap gap-2">{(Array.isArray(result.result) ? result.result : []).map((kw, i) => <span key={i} className="px-3 py-1.5 bg-bg-tertiary border border-border rounded-full text-sm text-text-secondary">#{kw}</span>)}</div>
            )}

            {type === 'entities' && result.result && (
              <div className="space-y-2">{(Array.isArray(result.result) ? result.result : []).map((e, i) => <div key={i} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg"><span className="text-sm text-text-primary">{e.name}</span><span className="px-2 py-0.5 bg-bg-secondary rounded text-xs text-text-muted capitalize">{e.type}</span></div>)}</div>
            )}

            {!['sentiment', 'keywords', 'entities'].includes(type) && (
              <pre className="bg-bg-tertiary p-4 rounded-xl text-sm text-text-secondary whitespace-pre-wrap overflow-x-auto max-h-96 overflow-y-auto">{typeof result.result === 'object' ? JSON.stringify(result.result, null, 2) : result.result}</pre>
            )}
          </Card>
        )}
      </div>
    </div>
  );
}