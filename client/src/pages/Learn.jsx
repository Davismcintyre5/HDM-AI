import { useState, useEffect, useRef } from 'react';
import { BookOpen, Send, Brain, Layers, Target, X, Plus, CheckCircle, Lock, Play, User, Volume2, Headphones, RotateCcw, Mic, MicOff, Square } from 'lucide-react';
import api from '../api/axios';
import ChatMessage from '../components/app/ChatMessage';
import TeacherAvatar from '../components/app/TeacherAvatar';
import LiveTeacher from '../components/app/LiveTeacher';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Modal from '../components/ui/Modal';
import Spinner from '../components/ui/Spinner';
import Badge from '../components/ui/Badge';
import { useToast } from '../components/ui/Toast';
import { useTheme } from '../context/ThemeContext';

const SUBJECTS = [
  { value: 'general', label: 'General' }, { value: 'programming', label: 'Programming' },
  { value: 'math', label: 'Mathematics' }, { value: 'science', label: 'Science' },
  { value: 'history', label: 'History' }, { value: 'language', label: 'Language' },
  { value: 'business', label: 'Business' },
];
const LEVELS = ['beginner', 'intermediate', 'advanced'];
const LANGUAGES = [
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'sw', label: 'Kiswahili', flag: '🇰🇪' },
];

export default function Learn() {
  const { colors } = useTheme();
  const { addToast } = useToast();
  const [curricula, setCurricula] = useState([]);
  const [activeCurriculum, setActiveCurriculum] = useState(null);
  const [activeSubtopic, setActiveSubtopic] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingCurricula, setLoadingCurricula] = useState(true);
  const [showNew, setShowNew] = useState(false);
  const [newTopic, setNewTopic] = useState('');
  const [newSubject, setNewSubject] = useState('general');
  const [newLevel, setNewLevel] = useState('beginner');
  const [creating, setCreating] = useState(false);

  const [showAvatar, setShowAvatar] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [avatarSpeaking, setAvatarSpeaking] = useState(false);
  const [avatarEmotion, setAvatarEmotion] = useState('idle');
  const [isListening, setIsListening] = useState(false);
  const [liveMode, setLiveMode] = useState(false);
  const [language, setLanguage] = useState('en');
  const recognitionRef = useRef(null);

  const [showQuiz, setShowQuiz] = useState(false);
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [quizAnswers, setQuizAnswers] = useState([]);
  const [quizResult, setQuizResult] = useState(null);
  const [generatingQuiz, setGeneratingQuiz] = useState(false);

  const [showFlashcards, setShowFlashcards] = useState(false);
  const [flashcards, setFlashcards] = useState([]);
  const [flashcardIndex, setFlashcardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => { loadCurricula(); }, []);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [activeSubtopic?.messages]);

  const loadCurricula = async () => {
    try {
      const { data } = await api.get('/learn/curriculum');
      setCurricula(data.data || []);
      if (data.data?.length > 0) {
        const active = data.data.find(c => c.status === 'active');
        if (active) {
          setActiveCurriculum(active);
          const currentSub = active.subtopics.find(s => s.status === 'active');
          if (currentSub) setActiveSubtopic(currentSub);
        }
      }
    } catch {}
    setLoadingCurricula(false);
  };

  const createCurriculum = async () => {
    if (!newTopic.trim()) return;
    setCreating(true);
    try {
      const { data } = await api.post('/learn/curriculum', { topic: newTopic, subject: newSubject, level: newLevel });
      setCurricula(prev => [data.data, ...prev]);
      setActiveCurriculum(data.data);
      const firstSub = data.data.subtopics.find(s => s.status === 'active');
      if (firstSub) setActiveSubtopic(firstSub);
      setShowNew(false); setNewTopic('');
      addToast('Curriculum created!', 'success');
    } catch { addToast('Failed', 'error'); }
    setCreating(false);
  };

  const selectCurriculum = async (id) => {
    try {
      const { data } = await api.get(`/learn/curriculum/${id}`);
      setActiveCurriculum(data.data);
      const currentSub = data.data.subtopics.find(s => s.status === 'active');
      setActiveSubtopic(currentSub || null);
    } catch {}
  };

  const selectSubtopic = (sub) => {
    if (sub.status === 'locked') return;
    setActiveSubtopic(sub);
  };

  const speakText = (text) => {
    if (!soundEnabled) return;
    const synth = window.speechSynthesis; synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language; utterance.rate = 0.9;
    utterance.onstart = () => { setIsSpeaking(true); setAvatarSpeaking(true); setAvatarEmotion('speaking'); };
    utterance.onend = () => { setIsSpeaking(false); setAvatarSpeaking(false); setAvatarEmotion('idle'); };
    utterance.onerror = () => { setIsSpeaking(false); setAvatarSpeaking(false); setAvatarEmotion('idle'); };
    synth.speak(utterance);
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false); setAvatarSpeaking(false); setAvatarEmotion('idle');
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) { addToast('Speech not supported', 'error'); return; }
    const langMap = { en: 'en-US', fr: 'fr-FR', sw: 'sw-KE' };
    const recognition = new SpeechRecognition();
    recognition.lang = langMap[language] || 'en-US';
    recognition.continuous = false; recognition.interimResults = true;
    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (e) => {
      const transcript = Array.from(e.results).map(r => r[0].transcript).join('');
      if (e.results[0].isFinal) setMessage(prev => prev + (prev ? ' ' : '') + transcript);
    };
    recognition.onerror = () => { setIsListening(false); addToast('Could not hear you', 'error'); };
    recognition.onend = () => setIsListening(false);
    recognitionRef.current = recognition;
    try { recognition.start(); } catch { setIsListening(false); }
  };

  const stopListening = () => {
    if (recognitionRef.current) { recognitionRef.current.abort(); setIsListening(false); }
  };

  const newSession = () => {
    stopSpeaking(); stopListening();
    setActiveCurriculum(null); setActiveSubtopic(null);
    addToast('Select a topic to start', 'info');
  };

  const sendMessage = async (e) => {
    e?.preventDefault();
    if (!message.trim() || loading || !activeCurriculum || !activeSubtopic) return;
    const msg = message.trim(); setMessage(''); setLoading(true);
    setActiveSubtopic(prev => ({ ...prev, messages: [...(prev.messages || []), { role: 'user', content: msg }] }));
    try {
      const { data } = await api.post(`/learn/curriculum/${activeCurriculum._id}/subtopic/${activeSubtopic._id}/chat`, { message: msg });
      const reply = data.data.reply;
      setActiveSubtopic(prev => ({ ...prev, messages: [...(prev.messages || []), { role: 'assistant', content: reply }] }));
      setAvatarEmotion('happy'); setTimeout(() => setAvatarEmotion('idle'), 2000);
      speakText(reply);
    } catch { addToast('Failed', 'error'); }
    setLoading(false);
  };

  const handleQuiz = async () => {
    setGeneratingQuiz(true);
    try {
      const { data } = await api.post(`/learn/curriculum/${activeCurriculum._id}/subtopic/${activeSubtopic._id}/quiz`);
      setQuizQuestions(data.data.questions); setQuizAnswers([]); setQuizResult(null); setShowQuiz(true);
    } catch { addToast('Failed', 'error'); }
    setGeneratingQuiz(false);
  };

  const submitQuiz = async () => {
    try {
      const { data } = await api.post(`/learn/curriculum/${activeCurriculum._id}/subtopic/${activeSubtopic._id}/quiz/submit`, { answers: quizAnswers });
      setQuizResult(data.data);
      if (data.data.passed) { addToast(`Passed! ${data.data.score}%`, 'success'); loadCurricula(); }
      else addToast(`Score: ${data.data.score}%. Need 60%.`, 'info');
    } catch { addToast('Failed', 'error'); }
  };

  const toggleAnswer = (qIdx, aIdx) => {
    setQuizAnswers(prev => [...prev.filter(a => a.questionIndex !== qIdx), { questionIndex: qIdx, answerIndex: aIdx }]);
  };

  const handleFlashcards = async () => {
    try {
      const { data } = await api.post(`/learn/curriculum/${activeCurriculum._id}/subtopic/${activeSubtopic._id}/flashcards`);
      setFlashcards(data.data.flashcards); setFlashcardIndex(0); setShowAnswer(false); setShowFlashcards(true);
    } catch { addToast('Failed', 'error'); }
  };

  const completeCurriculum = async () => {
    try {
      const { data } = await api.post(`/learn/curriculum/${activeCurriculum._id}/complete`);
      addToast('Curriculum complete! 🎉', 'success'); loadCurricula();
    } catch { addToast('Failed', 'error'); }
  };

  const deleteCurriculum = async (id) => {
    try {
      await api.delete(`/learn/curriculum/${id}`);
      if (activeCurriculum?._id === id) { setActiveCurriculum(null); setActiveSubtopic(null); }
      loadCurricula(); addToast('Deleted', 'info');
    } catch { addToast('Failed', 'error'); }
  };

  if (liveMode) {
    return <LiveTeacher language={language} topic={activeCurriculum?.topic || ''} onClose={() => setLiveMode(false)} onReturn={() => setLiveMode(false)} />;
  }

  if (loadingCurricula) {
    return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;
  }

  return (
    <div className="h-full flex">
      {/* Sidebar */}
      <div className="w-56 lg:w-64 border-r border-border bg-bg-secondary shrink-0 flex flex-col">
        <div className="p-3 border-b border-border">
          <button onClick={() => setShowNew(true)} className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary text-black rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors">
            <Plus size={16} /> New Topic
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {curricula.length === 0 && <p className="text-xs text-text-muted text-center py-8">No learning topics yet</p>}
          {curricula.map(c => (
            <button key={c._id} onClick={() => selectCurriculum(c._id)}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors group ${
                activeCurriculum?._id === c._id ? 'bg-primary/10 text-primary' : 'text-text-secondary hover:bg-bg-tertiary'
              }`}>
              <div className="flex items-center justify-between">
                <span className="font-medium truncate">{c.topic}</span>
                <div className="flex items-center gap-1">
                  {c.status === 'completed' && <CheckCircle size={14} className="text-success" />}
                  <button onClick={(e) => { e.stopPropagation(); deleteCurriculum(c._id); }} className="p-0.5 text-text-muted hover:text-danger rounded opacity-0 group-hover:opacity-100">
                    <X size={12} />
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[10px] text-text-muted">{c.level}</span>
                <div className="flex-1 h-1 bg-bg-tertiary rounded-full overflow-hidden">
                  <div className="h-full bg-primary rounded-full" style={{ width: `${c.overallProgress}%` }} />
                </div>
                <span className="text-[10px] text-text-muted">{c.overallProgress}%</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        {!activeCurriculum ? (
          <div className="flex-1 flex items-center justify-center text-center text-text-muted">
            <div>
              <Target size={48} className="mx-auto mb-4 opacity-30" />
              <h2 className="text-lg font-semibold text-text-primary mb-2">Learning Studio</h2>
              <p className="text-sm">Create a new topic or select one to begin.</p>
            </div>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="border-b border-border px-6 py-3 shrink-0">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-semibold text-text-primary flex items-center gap-2">
                    <BookOpen size={18} className="text-primary" /> {activeCurriculum.topic}
                  </h2>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-text-muted">{activeCurriculum.level} • {activeCurriculum.subject}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
                        <div className="h-full bg-primary rounded-full" style={{ width: `${activeCurriculum.overallProgress}%` }} />
                      </div>
                      <span className="text-xs text-text-muted font-medium">{activeCurriculum.overallProgress}%</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button size="sm" variant="secondary" onClick={handleQuiz} loading={generatingQuiz} disabled={!activeSubtopic}><Brain size={14} className="mr-1" /> Quiz</Button>
                  <Button size="sm" variant="secondary" onClick={handleFlashcards} disabled={!activeSubtopic}><Layers size={14} className="mr-1" /> Cards</Button>
                  {activeCurriculum.status === 'completed' && <Button size="sm" onClick={completeCurriculum}>Finish</Button>}
                </div>
              </div>

              {/* Toggles */}
              <div className="flex items-center gap-3 mt-3 flex-wrap">
                <button onClick={() => setLiveMode(true)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-primary text-black hover:bg-primary-hover transition-colors">
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
                    <button key={l.code} onClick={() => setLanguage(l.code)} className={`px-2 py-1 rounded text-xs transition-colors ${language === l.code ? 'bg-primary text-black' : 'text-text-secondary hover:text-text-primary'}`} title={l.label}>
                      {l.flag} <span className="hidden sm:inline">{l.label}</span>
                    </button>
                  ))}
                </div>
                <button onClick={newSession} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-text-muted hover:text-primary hover:bg-bg-tertiary transition-colors">
                  <RotateCcw size={14} /> New Topic
                </button>
              </div>

              {/* Progress */}
              <div className="mt-3 flex items-center gap-3">
                <div className="flex-1 h-2 bg-bg-tertiary rounded-full overflow-hidden">
                  <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${activeCurriculum.overallProgress}%` }} />
                </div>
                <span className="text-xs text-text-muted font-medium">{activeCurriculum.overallProgress}%</span>
              </div>
            </div>

            {/* Subtopics grid */}
            <div className="border-b border-border px-4 py-3 shrink-0">
              <p className="text-[10px] text-text-muted uppercase tracking-wider mb-2">Curriculum</p>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                {activeCurriculum.subtopics.map((sub) => (
                  <button key={sub._id} onClick={() => selectSubtopic(sub)} disabled={sub.status === 'locked'}
                    className={`flex items-center gap-2 px-3 py-2.5 rounded-lg text-xs font-medium text-left transition-all ${
                      activeSubtopic?._id === sub._id ? 'bg-primary text-black ring-2 ring-primary/30' :
                      sub.status === 'completed' ? 'bg-success/10 text-success border border-success/20' :
                      sub.status === 'locked' ? 'bg-bg-tertiary text-text-muted cursor-not-allowed opacity-50' :
                      'bg-bg-tertiary text-text-secondary hover:text-text-primary border border-border hover:border-text-muted'
                    }`}>
                    <span className="shrink-0">
                      {sub.status === 'completed' ? <CheckCircle size={14} /> : sub.status === 'locked' ? <Lock size={14} /> : <Play size={14} />}
                    </span>
                    <span className="truncate">{sub.title}</span>
                    {sub.score > 0 && <span className="ml-auto text-[10px] opacity-70">{sub.score}%</span>}
                  </button>
                ))}
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
              {activeSubtopic ? (
                <>
                  <div className="text-center mb-4">
                    <Badge variant={activeSubtopic.status === 'completed' ? 'success' : 'primary'}>
                      {activeSubtopic.status === 'completed' ? 'Completed' : 'Learning'}: {activeSubtopic.title}
                    </Badge>
                  </div>
                  {(!activeSubtopic.messages || activeSubtopic.messages.length === 0) && (
                    <div className="text-center text-text-muted py-8">
                      <BookOpen size={32} className="mx-auto mb-2 opacity-30" />
                      <p className="text-sm">Ask a question to start learning about <strong>{activeSubtopic.title}</strong></p>
                    </div>
                  )}
                  {activeSubtopic.messages?.map((m, i) => (
                    <div key={i}>
                      <ChatMessage role={m.role} content={m.content} />
                      {m.role === 'assistant' && soundEnabled && (
                        <button onClick={() => speakText(m.content)} className="ml-11 mt-1 p-1 text-text-muted hover:text-primary rounded">
                          <Volume2 size={14} />
                        </button>
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
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center text-text-muted text-sm">
                  Select a subtopic from the grid above
                </div>
              )}
            </div>

            {/* Input */}
            {activeSubtopic && activeSubtopic.status === 'active' && (
              <div className="border-t border-border px-6 py-4 shrink-0">
                <form onSubmit={sendMessage} className="flex gap-2">
                  {!isListening ? (
                    <button type="button" onClick={startListening} className="p-2.5 rounded-xl text-text-secondary hover:text-primary bg-bg-tertiary border border-border transition-colors">
                      <Mic size={18} />
                    </button>
                  ) : (
                    <button type="button" onClick={stopListening} className="p-2.5 rounded-xl bg-danger text-white animate-pulse">
                      <MicOff size={18} />
                    </button>
                  )}
                  <input value={message} onChange={e => setMessage(e.target.value)}
                    placeholder={isListening ? 'Listening...' : 'Ask about this topic...'}
                    className="flex-1 bg-bg-tertiary border border-border rounded-xl px-4 py-2.5 text-text-primary placeholder-text-muted text-sm focus:outline-none focus:border-primary" disabled={loading} />
                  <Button type="submit" size="sm" loading={loading} disabled={!message.trim()}>Send</Button>
                </form>
              </div>
            )}
          </>
        )}
      </div>

      {/* Mr HDM — far right only */}
      {showAvatar && activeCurriculum && (
        <div className="w-48 lg:w-56 border-l border-border bg-bg-secondary flex-shrink-0 hidden sm:flex items-center justify-center">
          <TeacherAvatar speaking={avatarSpeaking} emotion={avatarEmotion} />
        </div>
      )}

      {liveMode && (
        <LiveTeacher language={language} topic={activeCurriculum?.topic || ''} onClose={() => setLiveMode(false)} onReturn={() => setLiveMode(false)} />
      )}

      {/* New Topic Modal */}
      <Modal open={showNew} onClose={() => setShowNew(false)} title="New Learning Topic">
        <Input label="What do you want to learn?" value={newTopic} onChange={e => setNewTopic(e.target.value)} placeholder="e.g., Digital Marketing" />
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div>
            <label className="block text-xs text-text-secondary mb-1">Subject</label>
            <select value={newSubject} onChange={e => setNewSubject(e.target.value)} className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary">
              {SUBJECTS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-text-secondary mb-1">Level</label>
            <select value={newLevel} onChange={e => setNewLevel(e.target.value)} className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary">
              {LEVELS.map(l => <option key={l} value={l}>{l.charAt(0).toUpperCase() + l.slice(1)}</option>)}
            </select>
          </div>
        </div>
        <Button onClick={createCurriculum} loading={creating} disabled={!newTopic.trim()}>Generate Curriculum</Button>
      </Modal>

   <Modal open={showQuiz} onClose={() => setShowQuiz(false)} title="Quiz">
  {quizResult ? (
    <div className="text-center">
      <p className={`text-2xl font-bold ${quizResult.passed ? 'text-success' : 'text-danger'}`}>{quizResult.score}%</p>
      <p className="text-text-secondary text-sm mt-1">{quizResult.correct}/{quizResult.total} correct</p>
      <p className="text-text-muted text-xs mt-2">{quizResult.passed ? 'You passed! Next subtopic unlocked.' : 'Need 60% to pass. Try again.'}</p>
      <div className="flex gap-2 justify-center mt-4">
        {!quizResult.passed && <Button size="sm" onClick={() => { setQuizResult(null); setQuizAnswers([]); }}>Retry</Button>}
        <Button size="sm" variant="secondary" onClick={() => { setShowQuiz(false); loadCurricula(); }}>Done</Button>
      </div>
    </div>
  ) : (
    <div className="max-h-[55vh] overflow-y-auto pr-2 space-y-4">
      {quizQuestions.map((q, qIdx) => (
        <div key={qIdx}>
          <p className="text-sm font-medium text-text-primary mb-2">{qIdx + 1}. {q.question}</p>
          <div className="space-y-1">
            {q.options.map((opt, aIdx) => (
              <button
                key={aIdx}
                onClick={() => toggleAnswer(qIdx, aIdx)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm border transition-colors ${
                  quizAnswers.find(a => a.questionIndex === qIdx && a.answerIndex === aIdx)
                    ? 'bg-primary/20 border-primary text-primary'
                    : 'bg-bg-tertiary border-border text-text-secondary hover:border-text-muted'
                }`}
              >
                {String.fromCharCode(65 + aIdx)}. {opt}
              </button>
            ))}
          </div>
        </div>
      ))}
      <div className="pt-2 sticky bottom-0 bg-bg-secondary pb-2">
        <Button onClick={submitQuiz} disabled={quizAnswers.length < quizQuestions.length} className="w-full">
          Submit Quiz ({quizAnswers.length}/{quizQuestions.length} answered)
        </Button>
      </div>
    </div>
  )}
</Modal>

      {/* Flashcards Modal */}
      <Modal open={showFlashcards} onClose={() => setShowFlashcards(false)} title="Flashcards">
        {flashcards.length === 0 ? (
          <p className="text-text-muted text-sm text-center py-8">No flashcards yet</p>
        ) : (
          <>
            <div onClick={() => setShowAnswer(!showAnswer)} className="min-h-[180px] bg-bg-tertiary border border-border rounded-xl flex items-center justify-center cursor-pointer p-6 text-center">
              <div>
                <p className="text-[10px] text-text-muted uppercase mb-2">{showAnswer ? 'Definition' : 'Term'}</p>
                <p className="text-text-primary font-medium">{showAnswer ? flashcards[flashcardIndex]?.definition : flashcards[flashcardIndex]?.term}</p>
                {!showAnswer && <p className="text-text-muted text-xs mt-4">Tap to reveal</p>}
              </div>
            </div>
            <div className="flex justify-between mt-4">
              <Button size="sm" variant="secondary" onClick={() => { setFlashcardIndex(Math.max(0, flashcardIndex - 1)); setShowAnswer(false); }} disabled={flashcardIndex === 0}>Prev</Button>
              <span className="text-xs text-text-muted self-center">{flashcardIndex + 1}/{flashcards.length}</span>
              <Button size="sm" onClick={() => { if (flashcardIndex < flashcards.length - 1) { setFlashcardIndex(flashcardIndex + 1); setShowAnswer(false); } else setShowFlashcards(false); }}>
                {flashcardIndex < flashcards.length - 1 ? 'Next' : 'Done'}
              </Button>
            </div>
          </>
        )}
      </Modal>
    </div>
  );
}