import { useState, useRef, useEffect } from 'react';
import { BookOpen, Send, Brain, Layers, Target, ChevronRight, X, Mic, MicOff, Volume2, VolumeX, User, RotateCcw, Square, Headphones } from 'lucide-react';
import api from '../api/axios';
import ChatMessage from '../components/app/ChatMessage';
import TeacherAvatar from '../components/app/TeacherAvatar';
import LiveTeacher from '../components/app/LiveTeacher';
import Button from '../components/ui/Button';
import { useToast } from '../components/ui/Toast';

const SUBJECTS = [
  { value: 'general', label: 'General' },
  { value: 'programming', label: 'Programming' },
  { value: 'math', label: 'Mathematics' },
  { value: 'science', label: 'Science' },
  { value: 'history', label: 'History' },
  { value: 'language', label: 'Language' },
];

const LEVELS = ['beginner', 'intermediate', 'advanced'];

const LANGUAGES = [
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'sw', label: 'Kiswahili', flag: '🇰🇪' },
];

export default function Learn() {
  const [sessionId, setSessionId] = useState(null);
  const [topic, setTopic] = useState('');
  const [subject, setSubject] = useState('general');
  const [level, setLevel] = useState('beginner');
  const [language, setLanguage] = useState('en');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sessionInfo, setSessionInfo] = useState(null);

  const [showAvatar, setShowAvatar] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [avatarSpeaking, setAvatarSpeaking] = useState(false);
  const [avatarEmotion, setAvatarEmotion] = useState('idle');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [liveMode, setLiveMode] = useState(false);
  const recognitionRef = useRef(null);

  const [showQuiz, setShowQuiz] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [answerResult, setAnswerResult] = useState(null);

  const [flashcards, setFlashcards] = useState(null);
  const [showFlashcards, setShowFlashcards] = useState(false);
  const [flashcardIndex, setFlashcardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);

  const messagesEndRef = useRef(null);
  const { addToast } = useToast();

  useEffect(() => {
    const saved = localStorage.getItem('learn_session');
    if (saved) {
      try {
        const data = JSON.parse(saved);
        setSessionId(data.sessionId);
        setSessionInfo(data.sessionInfo);
        setProgress(data.progress || 0);
        setTopic(data.topic || '');
        setSubject(data.subject || 'general');
        setLevel(data.level || 'beginner');
      } catch {}
    }
  }, []);

  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('learn_session', JSON.stringify({ sessionId, sessionInfo, progress, topic, subject, level }));
    }
  }, [sessionId, progress, sessionInfo]);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const speakText = (text) => {
    if (!soundEnabled) return;
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;
    utterance.rate = 0.9;
    utterance.onstart = () => { setIsSpeaking(true); setAvatarSpeaking(true); setAvatarEmotion('speaking'); };
    utterance.onend = () => { setIsSpeaking(false); setAvatarSpeaking(false); setAvatarEmotion('idle'); };
    utterance.onerror = () => { setIsSpeaking(false); setAvatarSpeaking(false); setAvatarEmotion('idle'); };
    synth.speak(utterance);
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setAvatarSpeaking(false);
    setAvatarEmotion('idle');
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) { addToast('Speech recognition not supported', 'error'); return; }

    const langMap = { en: 'en-US', fr: 'fr-FR', sw: 'sw-KE' };
    const recognition = new SpeechRecognition();
    recognition.lang = langMap[language] || 'en-US';
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (e) => {
      const transcript = Array.from(e.results).map(r => r[0].transcript).join('');
      if (e.results[0].isFinal) setMessage(prev => prev + (prev ? ' ' : '') + transcript);
    };
    recognition.onerror = (e) => {
      setIsListening(false);
      switch (e.error) {
        case 'not-allowed': addToast('Microphone access denied', 'error'); break;
        case 'no-speech': addToast('No speech detected', 'info'); break;
        case 'network': addToast('Network error', 'error'); break;
        default: addToast('Could not hear you', 'error');
      }
    };
    recognition.onend = () => setIsListening(false);
    recognitionRef.current = recognition;
    try { recognition.start(); } catch { setIsListening(false); addToast('Microphone error', 'error'); }
  };

  const stopListening = () => {
    if (recognitionRef.current) { recognitionRef.current.abort(); setIsListening(false); }
  };

  const newSession = () => {
    stopSpeaking(); stopListening();
    localStorage.removeItem('learn_session');
    setSessionId(null); setSessionInfo(null); setMessages([]);
    setProgress(0); setTopic(''); setSubject('general'); setLevel('beginner');
    addToast('New topic started', 'info');
  };

  const startSession = async (e) => {
    e?.preventDefault();
    if (!message.trim() || loading) return;
    setLoading(true);
    setAvatarEmotion('thinking');
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    const msg = message;
    setMessage('');
    try {
      const { data } = await api.post('/general/learn', { topic: topic || 'General', subject, level, message: msg, session_id: sessionId });
      const reply = data.data.reply;
      setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
      setSessionId(data.data.session_id);
      setProgress(data.data.progress || 0);
      setSessionInfo({ topic: topic || 'General', subject, level });
      setAvatarEmotion('happy');
      setTimeout(() => setAvatarEmotion('idle'), 2000);
      speakText(reply);
    } catch {
      addToast('Failed', 'error');
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong.' }]);
      setAvatarEmotion('idle');
    }
    setLoading(false);
  };

  const generateQuiz = async () => {
    if (!sessionId) return addToast('Start a session first', 'error');
    try {
      const { data } = await api.post('/general/learn/quiz', { session_id: sessionId, topic: topic || 'General', level, num_questions: 5 });
      setQuiz(data.data); setCurrentQuestion(0); setSelectedAnswer(null); setAnswerResult(null); setShowQuiz(true);
      addToast('Quiz ready!', 'success');
    } catch { addToast('Failed', 'error'); }
  };

  const submitAnswer = async (idx) => {
    if (answerResult) return;
    setSelectedAnswer(idx);
    try {
      const { data } = await api.post('/general/learn/quiz/submit', { session_id: sessionId, question_index: currentQuestion, answer_index: idx, quiz_data: quiz.questions, session_data: { correct_answers: answerResult?.is_correct ? 1 : 0 } });
      setAnswerResult(data.data);
    } catch { addToast('Failed', 'error'); }
  };

  const nextQuestion = () => {
    if (currentQuestion < (quiz?.questions?.length || 0) - 1) { setCurrentQuestion(p => p + 1); setSelectedAnswer(null); setAnswerResult(null); }
    else { setShowQuiz(false); addToast('Quiz complete!', 'success'); }
  };

  const generateFlashcards = async () => {
    if (!sessionId) return addToast('Start a session first', 'error');
    try {
      const { data } = await api.post('/general/learn/flashcards', { session_id: sessionId, topic: topic || 'General', level });
      setFlashcards(data.data); setFlashcardIndex(0); setShowAnswer(false); setShowFlashcards(true);
    } catch { addToast('Failed', 'error'); }
  };

  const nextFlashcard = () => {
    if (flashcardIndex < (flashcards?.flashcards?.length || 0) - 1) { setFlashcardIndex(p => p + 1); setShowAnswer(false); }
    else { setShowFlashcards(false); addToast('All reviewed!', 'success'); }
  };

  return (
    <div className="h-full flex">
      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex-shrink-0 border-b border-border px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-lg font-semibold text-text-primary flex items-center gap-2"><BookOpen size={20} className="text-primary" /> Learning Studio</h1>
              {sessionInfo && <p className="text-sm text-text-secondary mt-0.5">{sessionInfo.topic} • {sessionInfo.subject} • {sessionInfo.level}</p>}
            </div>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="secondary" onClick={generateQuiz}><Brain size={15} className="mr-1" /> Quiz</Button>
              <Button size="sm" variant="secondary" onClick={generateFlashcards}><Layers size={15} className="mr-1" /> Flashcards</Button>
            </div>
          </div>

          <div className="flex items-center gap-3 mt-3 flex-wrap">
            <button onClick={() => setLiveMode(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-primary text-black hover:bg-primary-hover transition-colors">
              <Headphones size={14} /> Live Teacher
            </button>

            <button onClick={() => setShowAvatar(!showAvatar)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${showAvatar ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-bg-tertiary text-text-secondary hover:text-text-primary border border-transparent'}`}>
              <User size={14} /> {showAvatar ? 'Mr HDM ON' : 'Mr HDM'}
            </button>

            <button onClick={() => { setSoundEnabled(!soundEnabled); if (soundEnabled) stopSpeaking(); }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${soundEnabled ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-bg-tertiary text-text-secondary hover:text-text-primary border border-transparent'}`}>
              <Volume2 size={14} /> {soundEnabled ? 'Sound ON' : 'Sound'}
            </button>

            {isSpeaking && (
              <button onClick={stopSpeaking} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-danger/20 text-danger border border-danger/30">
                <Square size={14} /> Stop
              </button>
            )}

            <div className="flex items-center gap-1 bg-bg-tertiary rounded-lg p-1">
              {LANGUAGES.map(l => (
                <button key={l.code} onClick={() => setLanguage(l.code)}
                  className={`px-2 py-1 rounded text-xs transition-colors ${language === l.code ? 'bg-primary text-black' : 'text-text-secondary hover:text-text-primary'}`} title={l.label}>
                  {l.flag} <span className="hidden sm:inline">{l.label}</span>
                </button>
              ))}
            </div>

            {sessionId && (
              <button onClick={newSession} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-text-muted hover:text-primary hover:bg-bg-tertiary transition-colors">
                <RotateCcw size={14} /> New Topic
              </button>
            )}
          </div>

          {!sessionId && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
              <input value={topic} onChange={e => setTopic(e.target.value)} placeholder="What to learn?" className="bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-primary" />
              <select value={subject} onChange={e => setSubject(e.target.value)} className="bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-secondary outline-none focus:border-primary">
                {SUBJECTS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
              <select value={level} onChange={e => setLevel(e.target.value)} className="bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-secondary outline-none focus:border-primary">
                {LEVELS.map(l => <option key={l} value={l}>{l.charAt(0).toUpperCase() + l.slice(1)}</option>)}
              </select>
            </div>
          )}

          {progress > 0 && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-text-muted mb-1.5"><span>Progress</span><span className="text-primary font-medium">{progress.toFixed(0)}%</span></div>
              <div className="h-1.5 bg-bg-tertiary rounded-full overflow-hidden"><div className="h-full bg-primary rounded-full transition-all" style={{ width: `${progress}%` }} /></div>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.length === 0 && (
            <div className="h-[40vh] flex items-center justify-center text-center">
              <div>
                <Target size={48} className="text-text-muted mx-auto mb-4 opacity-30" />
                <h2 className="text-lg font-semibold text-text-primary mb-2">Start Learning</h2>
                <p className="text-text-muted text-sm">Choose a topic, set your level, ask a question, or start Live Teacher mode.</p>
                {localStorage.getItem('learn_session') && <p className="text-text-muted text-xs mt-2">You have a saved session. Start typing to continue.</p>}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i}>
              <ChatMessage role={m.role} content={m.content} />
              {m.role === 'assistant' && (
                <div className="ml-11 mt-1 flex gap-1">
                  {!isSpeaking ? (
                    <button onClick={() => speakText(m.content)} className="p-1 text-text-muted hover:text-primary rounded" title="Read aloud"><Volume2 size={14} /></button>
                  ) : (
                    <button onClick={stopSpeaking} className="p-1 text-text-muted hover:text-danger rounded" title="Stop"><VolumeX size={14} /></button>
                  )}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-1.5 items-center px-4">
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="flex-shrink-0 border-t border-border px-6 py-4">
          <form onSubmit={startSession} className="flex gap-2">
            {!isListening ? (
              <button type="button" onClick={startListening} className="p-2.5 rounded-xl text-text-secondary hover:text-primary bg-bg-tertiary border border-border transition-colors" title="Start listening"><Mic size={18} /></button>
            ) : (
              <button type="button" onClick={stopListening} className="p-2.5 rounded-xl bg-danger text-white animate-pulse transition-colors" title="Stop listening"><MicOff size={18} /></button>
            )}
            <input value={message} onChange={e => setMessage(e.target.value)}
              placeholder={isListening ? 'Listening...' : sessionId ? "Ask a follow-up..." : "Ask your first question..."}
              className="flex-1 bg-bg-tertiary border border-border rounded-xl px-4 py-2.5 text-text-primary placeholder-text-muted text-sm focus:outline-none focus:border-primary" disabled={loading} />
            <Button type="submit" size="sm" loading={loading} disabled={!message.trim()}><Send size={18} /></Button>
          </form>
        </div>

        {showQuiz && quiz && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
            <div className="bg-bg-secondary border border-border rounded-xl w-full max-w-lg p-6 shadow-2xl">
              <div className="flex items-center justify-between mb-4">
                <div><h3 className="text-text-primary font-semibold">Quiz</h3><p className="text-xs text-text-muted">Q {currentQuestion + 1}/{quiz.questions?.length}</p></div>
                <button onClick={() => setShowQuiz(false)} className="text-text-muted hover:text-text-primary"><X size={18} /></button>
              </div>
              <p className="text-text-primary text-sm font-medium mb-4">{quiz.questions?.[currentQuestion]?.question}</p>
              <div className="space-y-2">
                {quiz.questions?.[currentQuestion]?.options?.map((opt, i) => {
                  let cls = 'bg-bg-tertiary border-border hover:border-text-muted text-text-secondary';
                  if (answerResult) {
                    if (i === quiz.questions[currentQuestion].correct_index) cls = 'bg-success/20 border-success text-success';
                    else if (i === selectedAnswer && !answerResult.is_correct) cls = 'bg-danger/20 border-danger text-danger';
                  } else if (i === selectedAnswer) cls = 'bg-primary/20 border-primary text-primary';
                  return <button key={i} onClick={() => submitAnswer(i)} disabled={!!answerResult} className={`w-full text-left px-4 py-3 rounded-lg border text-sm transition-all ${cls}`}><span className="font-medium mr-2">{String.fromCharCode(65 + i)}.</span>{opt}</button>;
                })}
              </div>
              {answerResult && <div className={`mt-4 p-3 rounded-lg text-sm ${answerResult.is_correct ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'}`}>{answerResult.is_correct ? '✓ Correct!' : '✗ Incorrect.'}</div>}
              {answerResult && (
                <div className="flex justify-between mt-4 pt-4 border-t border-border">
                  <span className="text-xs text-text-muted">Score: {answerResult.score?.toFixed(0) || 0}%</span>
                  <Button size="sm" onClick={nextQuestion}>{currentQuestion < (quiz.questions?.length || 0) - 1 ? 'Next' : 'Finish'}<ChevronRight size={14} className="ml-1" /></Button>
                </div>
              )}
            </div>
          </div>
        )}

        {showFlashcards && flashcards && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
            <div className="bg-bg-secondary border border-border rounded-xl w-full max-w-md p-6 shadow-2xl">
              <div className="flex items-center justify-between mb-4">
                <div><h3 className="text-text-primary font-semibold">Flashcards</h3><p className="text-xs text-text-muted">Card {flashcardIndex + 1}/{flashcards.flashcards?.length}</p></div>
                <button onClick={() => setShowFlashcards(false)} className="text-text-muted hover:text-text-primary"><X size={18} /></button>
              </div>
              <div onClick={() => setShowAnswer(!showAnswer)} className="min-h-[200px] bg-bg-tertiary border border-border rounded-xl p-6 flex items-center justify-center text-center cursor-pointer hover:border-text-muted transition-all">
                <div>
                  <p className="text-xs text-text-muted mb-2 uppercase tracking-wider">{showAnswer ? 'Definition' : 'Term'}</p>
                  <p className="text-text-primary text-lg font-medium">{showAnswer ? flashcards.flashcards?.[flashcardIndex]?.definition : flashcards.flashcards?.[flashcardIndex]?.term}</p>
                  {!showAnswer && <p className="text-text-muted text-xs mt-4">Tap to reveal</p>}
                </div>
              </div>
              <div className="flex justify-between mt-4 pt-4 border-t border-border">
                <Button variant="secondary" size="sm" onClick={() => { setFlashcardIndex(Math.max(0, flashcardIndex - 1)); setShowAnswer(false); }} disabled={flashcardIndex === 0}>Previous</Button>
                <span className="text-xs text-text-muted self-center">{flashcardIndex + 1}/{flashcards.flashcards?.length}</span>
                <Button size="sm" onClick={nextFlashcard}>{flashcardIndex < (flashcards.flashcards?.length || 0) - 1 ? 'Next' : 'Done'}<ChevronRight size={14} className="ml-1" /></Button>
              </div>
            </div>
          </div>
        )}
      </div>

      {showAvatar && (
        <div className="w-48 lg:w-56 border-l border-border bg-bg-secondary flex-shrink-0 hidden sm:block">
          <TeacherAvatar speaking={avatarSpeaking} emotion={avatarEmotion} />
        </div>
      )}

      {liveMode && (
        <LiveTeacher language={language} topic={topic} onClose={() => setLiveMode(false)} />
      )}
    </div>
  );
}