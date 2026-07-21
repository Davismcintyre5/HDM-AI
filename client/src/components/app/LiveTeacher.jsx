import { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, PhoneOff, FileText, X, SkipForward, ArrowLeft } from 'lucide-react';
import TeacherAvatar from './TeacherAvatar';
import api from '../../api/axios';
import { useToast } from '../ui/Toast';

export default function LiveTeacher({ language = 'en', topic = '', onClose, onReturn }) {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [status, setStatus] = useState('idle');
  const [notes, setNotes] = useState([]);
  const [showNotes, setShowNotes] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const recognitionRef = useRef(null);
  const notesScrollRef = useRef(null);
  const { addToast } = useToast();

  const langMap = { en: 'en-US', fr: 'fr-FR', sw: 'sw-KE' };
  const langCode = langMap[language] || 'en-US';

  useEffect(() => {
    if (showNotes && notesScrollRef.current) {
      notesScrollRef.current.scrollTop = notesScrollRef.current.scrollHeight;
    }
  }, [notes, showNotes]);

  const speak = (text) => {
    const synth = window.speechSynthesis;
    synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.rate = 0.95;
    utterance.onstart = () => { setIsSpeaking(true); setStatus('speaking'); };
    utterance.onend = () => { setIsSpeaking(false); setStatus('idle'); };
    utterance.onerror = () => { setIsSpeaking(false); setStatus('idle'); };
    synth.speak(utterance);
  };

  const startListening = () => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) { addToast('Speech not supported', 'error'); return; }

    const recognition = new SpeechRecognition();
    recognition.lang = langCode;
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => { setIsListening(true); setStatus('listening'); setHasStarted(true); };

    recognition.onresult = async (e) => {
      const text = e.results[0][0].transcript;
      setIsListening(false);
      setStatus('thinking');
      setNotes(prev => [...prev, { role: 'user', content: text }]);

      try {
        const { data } = await api.post('/general/learn', {
          topic: topic || 'General',
          subject: 'general',
          level: 'intermediate',
          message: `Keep it brief — 2-3 sentences spoken naturally like a teacher. ${text}`,
          session_id: null,
        });
        const reply = data.data.reply;
        setNotes(prev => [...prev, { role: 'assistant', content: reply }]);
        speak(reply);
      } catch {
        setStatus('idle');
        const fallback = 'Sorry, I had trouble. Tap the mic to try again.';
        setNotes(prev => [...prev, { role: 'assistant', content: fallback }]);
        speak(fallback);
      }
    };

    recognition.onerror = (e) => {
      setIsListening(false);
      setStatus('idle');
      if (e.error === 'not-allowed') addToast('Microphone access denied', 'error');
      else if (e.error === 'no-speech') addToast('No speech detected. Tap mic to try again.', 'info');
      else if (e.error === 'network') addToast('Network error', 'error');
    };

    recognition.onend = () => setIsListening(false);
    recognitionRef.current = recognition;
    try { recognition.start(); } catch { setIsListening(false); }
  };

  const stopListening = () => {
    if (recognitionRef.current) { recognitionRef.current.abort(); setIsListening(false); setStatus('idle'); }
  };

  const endSession = () => {
    stopListening();
    window.speechSynthesis.cancel();
    if (onClose) onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-bg p-4">
      {/* Top bar */}
      <div className="absolute top-4 left-4 right-4 flex items-center justify-between">
        <button onClick={onReturn} className="p-2 text-text-muted hover:text-text-primary rounded-lg hover:bg-bg-tertiary transition-colors">
          <ArrowLeft size={20} />
        </button>
        <div className="flex items-center gap-2">
          <button onClick={() => setShowNotes(true)} className="p-2 text-text-muted hover:text-primary rounded-lg hover:bg-bg-tertiary transition-colors">
            <FileText size={20} />
          </button>
          <button onClick={endSession} className="p-2 text-text-muted hover:text-danger rounded-lg hover:bg-bg-tertiary transition-colors">
            <PhoneOff size={20} />
          </button>
        </div>
      </div>

      {/* Status */}
      <p className="text-xs text-text-muted mb-6 tracking-wider uppercase">
        {!hasStarted && 'Tap the microphone to begin'}
        {status === 'listening' && '🎤 Listening...'}
        {status === 'thinking' && '🤔 Thinking...'}
        {status === 'speaking' && '🔊 Speaking...'}
        {status === 'idle' && hasStarted && 'Tap mic to ask a question'}
      </p>

      {/* Avatar */}
      <div className={`transform transition-all duration-500 ${
        isSpeaking ? 'scale-110' : 'scale-100'
      } ${status === 'listening' ? 'animate-float' : ''}`}>
        <TeacherAvatar
          speaking={isSpeaking}
          emotion={status === 'thinking' ? 'thinking' : status === 'speaking' ? 'speaking' : 'idle'}
        />
      </div>

      {/* Mic button */}
      <div className="flex justify-center mt-8">
        {!isListening ? (
          <button
            onClick={startListening}
            disabled={isSpeaking}
            className="w-20 h-20 rounded-full bg-primary text-black flex items-center justify-center hover:bg-primary-hover transition-all disabled:opacity-50 shadow-2xl shadow-primary/30 active:scale-95"
          >
            <Mic size={32} />
          </button>
        ) : (
          <button
            onClick={stopListening}
            className="w-20 h-20 rounded-full bg-danger text-white flex items-center justify-center animate-pulse shadow-2xl shadow-danger/30 active:scale-95"
          >
            <MicOff size={32} />
          </button>
        )}
      </div>

      {hasStarted && (
        <button
          onClick={() => { setHasStarted(false); setNotes([]); addToast('New topic started', 'info'); }}
          className="flex items-center gap-1.5 mt-6 px-4 py-2 rounded-full bg-bg-tertiary border border-border text-text-secondary text-xs font-medium hover:text-text-primary transition-colors"
        >
          <SkipForward size={14} /> New Topic
        </button>
      )}

      <p className="text-xs text-text-muted mt-6 text-center max-w-xs">
        Mr. HDM only speaks when you tap the mic
      </p>

      {/* Notes panel */}
      {showNotes && (
        <div className="fixed inset-y-0 right-0 w-full sm:w-96 bg-bg-secondary border-l border-border z-50 flex flex-col shadow-2xl animate-slideIn">
          <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
            <h3 className="text-sm font-semibold text-text-primary">Session Notes</h3>
            <button onClick={() => setShowNotes(false)} className="p-1.5 text-text-muted hover:text-text-primary rounded-lg hover:bg-bg-tertiary"><X size={18} /></button>
          </div>
          <div ref={notesScrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4 smooth-scroll">
            {notes.length === 0 ? (
              <p className="text-sm text-text-muted text-center py-12">No notes yet.</p>
            ) : (
              notes.map((n, i) => (
                <div key={i} className={`flex ${n.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
                  <div className={`max-w-[90%] px-3 py-2 rounded-xl text-sm ${
                    n.role === 'user' ? 'bg-primary/10 text-text-primary rounded-br-sm' : 'bg-bg-tertiary text-text-secondary rounded-bl-sm'
                  }`}>
                    <p className="text-[9px] text-text-muted uppercase tracking-wider mb-0.5">{n.role === 'user' ? 'You' : 'Mr. HDM'}</p>
                    <p>{n.content}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {showNotes && <div className="fixed inset-0 bg-black/40 z-40 sm:hidden" onClick={() => setShowNotes(false)} />}

      <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
        @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
        .animate-fadeIn { animation: fadeIn 0.3s ease-out; }
        .animate-slideIn { animation: slideIn 0.3s ease-out; }
        .animate-float { animation: float 2s ease-in-out infinite; }
        .smooth-scroll { scroll-behavior: smooth; }
      `}</style>
    </div>
  );
}