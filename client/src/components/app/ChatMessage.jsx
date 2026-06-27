import { useState } from 'react';
import { Bot, Download, Copy, Check } from 'lucide-react';

const LANG_MAP = {
  js: 'JavaScript', javascript: 'JavaScript', jsx: 'React JSX',
  ts: 'TypeScript', typescript: 'TypeScript', tsx: 'React TSX',
  py: 'Python', python: 'Python',
  html: 'HTML', css: 'CSS', scss: 'SCSS',
  java: 'Java', go: 'Go', rust: 'Rust', php: 'PHP', ruby: 'Ruby',
  bash: 'Bash', sh: 'Bash', powershell: 'PowerShell',
  json: 'JSON', yaml: 'YAML', xml: 'XML', sql: 'SQL',
  markdown: 'Markdown', md: 'Markdown', txt: 'Plain Text',
  c: 'C', cpp: 'C++', csharp: 'C#', swift: 'Swift', kotlin: 'Kotlin',
  dart: 'Dart', dockerfile: 'Dockerfile',
};

const EXT_MAP = {
  javascript: '.js', python: '.py', html: '.html', css: '.css',
  java: '.java', go: '.go', rust: '.rs', php: '.php', ruby: '.rb',
  bash: '.sh', json: '.json', sql: '.sql', markdown: '.md', txt: '.txt',
  c: '.c', cpp: '.cpp', typescript: '.ts',
};

function getLanguage(fence) {
  const raw = fence?.trim().toLowerCase() || '';
  return LANG_MAP[raw] || (raw ? raw.charAt(0).toUpperCase() + raw.slice(1) : 'Code');
}

function getExtension(lang) {
  const l = lang.toLowerCase();
  return EXT_MAP[l] || `.${l.replace(/[^a-z]/g, '') || 'txt'}`;
}

function parseMessageContent(text) {
  if (!text) return [{ type: 'text', content: '' }];
  const segments = [];
  const regex = /```(\S*)\n?([\s\S]*?)```/g;
  let lastIndex = 0, match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      const before = text.slice(lastIndex, match.index).trim();
      if (before) segments.push({ type: 'text', content: before });
    }
    const lang = getLanguage(match[1]);
    const code = match[2].trim();
    if (code) segments.push({ type: 'code', language: lang, extension: getExtension(lang), content: code });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < text.length) {
    const after = text.slice(lastIndex).trim();
    if (after) segments.push({ type: 'text', content: after });
  }
  if (segments.length === 0) segments.push({ type: 'text', content: text.trim() });
  return segments;
}

function downloadCode(text, filename) {
  const blob = new Blob([text], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

export default function ChatMessage({ role, content }) {
  const isUser = role === 'user';
  const segments = isUser ? [{ type: 'text', content }] : parseMessageContent(content);
  const [copiedIdx, setCopiedIdx] = useState(null);

  const copy = (text, i) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(i);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser ? 'bg-primary text-black' : 'bg-bg-tertiary text-text-secondary'}`}>
        {isUser ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        ) : (
          <Bot size={16} />
        )}
      </div>
      <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        {isUser ? (
          <div className="px-4 py-3 rounded-2xl rounded-tr-md bg-primary text-black text-sm">{content}</div>
        ) : (
          <div className="space-y-3">
            {segments.map((seg, i) =>
              seg.type === 'code' ? (
                <div key={i} className="bg-bg-tertiary border border-border rounded-xl overflow-hidden">
                  <div className="flex items-center justify-between px-3 py-1.5 bg-bg-secondary border-b border-border">
                    <span className="text-[10px] text-text-muted font-mono">{seg.language}</span>
                    <div className="flex items-center gap-1">
                      <button onClick={() => copy(seg.content, i)} className="p-1 text-text-muted hover:text-text-primary rounded">
                        {copiedIdx === i ? <Check size={14} className="text-success" /> : <Copy size={14} />}
                      </button>
                      <button onClick={() => downloadCode(seg.content, `code${seg.extension}`)} className="p-1 text-text-muted hover:text-text-primary rounded">
                        <Download size={14} />
                      </button>
                    </div>
                  </div>
                  <pre className="p-4 text-xs font-mono text-text-primary overflow-x-auto whitespace-pre-wrap">{seg.content}</pre>
                </div>
              ) : (
                <div key={i} className="px-4 py-3 rounded-2xl rounded-tl-md bg-bg-secondary border border-border text-text-primary text-sm whitespace-pre-wrap">{seg.content}</div>
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}