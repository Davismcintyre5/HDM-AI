import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import api from '../api/axios';
import ChatMessage from '../components/app/ChatMessage';
import ChatStream from '../components/app/ChatStream';
import ChatInput from '../components/app/ChatInput';
import Spinner from '../components/ui/Spinner';

export default function Chat() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState('');
  const [conversationId, setConversationId] = useState(id || searchParams.get('conversationId'));
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, streaming]);

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

const handleSend = useCallback(async ({ message, searchEnabled, deepThink, files }) => {
  const displayMsg = message || (files?.length ? `Analyzing ${files.length} file(s)...` : '');
  if (displayMsg) {
    setMessages(prev => [...prev, { role: 'user', content: displayMsg }]);
  }
  setLoading(true);
  setStreaming('');

  try {
    const formData = new FormData();
    formData.append('message', message || '');
    if (conversationId) formData.append('conversationId', conversationId);
    if (searchEnabled) formData.append('search_enabled', 'true');
    if (deepThink) formData.append('deep_think', 'true');
    if (files?.length) {
      files.forEach(f => formData.append('files', f));
    }

    const token = localStorage.getItem('token');
    const res = await fetch('/api/v1/chat/general', {
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
  setLoading(false);
}, [conversationId]);

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto">
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-text-muted">
            <div className="w-20 h-20 bg-primary/10 rounded-2xl flex items-center justify-center mb-6">
              <Sparkles size={36} className="text-primary" />
            </div>
            <h2 className="text-2xl font-bold text-text-primary mb-2">HDM AI Assistant</h2>
            <p className="text-sm">Ask anything, upload files, or enable Deep Think.</p>
          </div>
        )}
        {messages.map((m, i) => <ChatMessage key={i} role={m.role} content={m.content} />)}
        {streaming && <ChatStream content={streaming} />}
        {loading && !streaming && (
          <div className="flex items-center gap-2 text-text-muted text-sm pl-11"><Spinner size="sm" /> Thinking...</div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="pt-2 border-t border-border">
        <ChatInput onSend={handleSend} loading={loading} />
      </div>
    </div>
  );
}