import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import api from '../api/axios';
import ChatMessage from '../components/app/ChatMessage';
import ChatStream from '../components/app/ChatStream';
import ChatInput from '../components/app/ChatInput';
import SearchIndicator from '../components/app/SearchIndicator';
import Spinner from '../components/ui/Spinner';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const genRequestId = () =>
  Math.random().toString(36).slice(2) + Date.now().toString(36);

export default function Chat() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState('');
  const [searchPhase, setSearchPhase] = useState(null);
  const [searchDomains, setSearchDomains] = useState([]);
  const [conversationId, setConversationId] = useState(id || searchParams.get('conversationId'));
  const bottomRef = useRef(null);
  const pollRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streaming, searchPhase]);

  useEffect(() => {
    if (conversationId) {
      api.get(`/conversations/${conversationId}`).then(({ data }) => {
        const msgs = data.data?.messages || [];
        setMessages(msgs.map(m => ({ role: m.role, content: m.content })));
      }).catch(() => {});
    } else {
      setMessages([]);
    }
  }, [conversationId]);

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  const startPolling = (requestId) => {
    stopPolling();
    pollRef.current = setInterval(async () => {
      try {
        const { data } = await api.get(`/chat/status/${requestId}`);
        const phase = data.data?.phase;
        const domains = data.data?.domains || [];
        if (phase === 'searching') {
          setSearchPhase('searching');
          if (domains.length > 0) setSearchDomains(domains);
        } else if (phase === 'thinking') {
          setSearchPhase('thinking');
        }
      } catch {}
    }, 500);
  };

  const handleSend = useCallback(async ({ message, searchEnabled, deepThink, files }) => {
    const displayMsg = message || (files?.length ? `Analyzing ${files.length} file(s)...` : '');
    if (displayMsg) {
      setMessages(prev => [...prev, { role: 'user', content: displayMsg }]);
    }
    setLoading(true);
    setStreaming('');
    setSearchPhase('thinking');
    setSearchDomains([]);

    const requestId = genRequestId();
    startPolling(requestId);

    try {
      const formData = new FormData();
      formData.append('message', message || '');
      formData.append('requestId', requestId);
      if (conversationId) formData.append('conversationId', conversationId);
      if (searchEnabled) formData.append('search_enabled', 'true');
      if (deepThink) formData.append('deep_think', 'true');
      if (files?.length) {
        files.forEach(f => formData.append('files', f));
      }

      const token = localStorage.getItem('token');
      const res = await fetch(`${BASE_URL}/api/v1/chat`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data = await res.json();
      const reply = data.data?.reply || 'No response.';
      setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
      if (!conversationId) setConversationId(data.data?.conversationId);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Something went wrong. Try again.' }]);
    }
    stopPolling();
    setLoading(false);
    setSearchPhase(null);
    setSearchDomains([]);
  }, [conversationId]);

  useEffect(() => () => stopPolling(), []);

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto">
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-text-muted">
            <div className="w-20 h-20 bg-primary/10 rounded-2xl flex items-center justify-center mb-6">
              <Sparkles size={36} className="text-primary" />
            </div>
            <h2 className="text-2xl font-bold text-text-primary mb-2">HDM AI</h2>
            <p className="text-sm">Ask anything, upload files, or enable Search.</p>
          </div>
        )}
        {messages.map((m, i) => <ChatMessage key={i} role={m.role} content={m.content} />)}
        {streaming && <ChatStream content={streaming} />}

        {loading && !streaming && searchPhase === 'searching' && (
          <SearchIndicator domains={searchDomains} />
        )}

        {loading && !streaming && searchPhase !== 'searching' && (
          <div className="flex items-center gap-2 text-text-muted text-sm pl-11">
            <Spinner size="sm" /> Thinking...
          </div>
        )}

        <div ref={bottomRef} />
      </div>
      <div className="pt-2 border-t border-border">
        <ChatInput onSend={handleSend} loading={loading} />
      </div>
    </div>
  );
}