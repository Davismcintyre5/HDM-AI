import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

const FALLBACK_SOURCES = ['the web', 'news sources', 'recent articles'];

export default function SearchIndicator({ domains = [] }) {
  const sources = domains.length > 0 ? domains : FALLBACK_SOURCES;
  const [idx, setIdx] = useState(0);
  const [blink, setBlink] = useState(true);

  useEffect(() => {
    setIdx(0);
  }, [domains.join(',')]);

  useEffect(() => {
    if (sources.length <= 1) return;
    const timer = setInterval(() => {
      setBlink(false);
      setTimeout(() => {
        setIdx(prev => (prev + 1) % sources.length);
        setBlink(true);
      }, 180);
    }, 900);
    return () => clearInterval(timer);
  }, [sources.length]);

  return (
    <div className="flex items-center gap-2 pl-11 text-sm text-blue-400">
      <Search size={14} className="animate-pulse shrink-0" />
      <span
        className={`font-medium transition-opacity duration-150 ${
          blink ? 'opacity-100' : 'opacity-0'
        }`}
      >
        Searching {sources[idx]}...
      </span>
      <span className="flex gap-0.5">
        <span className="w-1 h-1 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-1 h-1 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-1 h-1 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </span>
    </div>
  );
}