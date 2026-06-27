import { useState, useRef, useEffect } from 'react';
import { BookOpen, Send, Brain, Layers, Sparkles, Target, Zap, ChevronRight, X } from 'lucide-react';
import api from '../api/axios';
import ChatMessage from '../components/app/ChatMessage';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
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

export default function Learn() {
  const [sessionId, setSessionId] = useState(null);
  const [topic, setTopic] = useState('');
  const [subject, setSubject] = useState('general');
  const [level, setLevel] = useState('beginner');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sessionInfo, setSessionInfo] = useState(null);
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

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const startSession = async (e) => {
    e?.preventDefault();
    if (!message.trim() || loading) return;
    setLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    const msg = message;
    setMessage('');
    try {
      const { data } = await api.post('/general/learn', { topic: topic || 'General', subject, level, message: msg, session_id: sessionId });
      setMessages(prev => [...prev, { role: 'assistant', content: data.data.reply }]);
      setSessionId(data.data.session_id);
      setProgress(data.data.progress || 0);
      setSessionInfo({ topic: topic || 'General', subject, level });
    } catch {
      addToast('Failed', 'error');
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong.' }]);
    }
    setLoading(false);
  };

  const generateQuiz = async () => {
    if (!sessionId) return addToast('Start a session first', 'error');
    try {
      const { data } = await api.post('/general/learn/quiz', { session_id: sessionId, topic: topic || 'General', level, num_questions: 5 });
      setQuiz(data.data);
      setCurrentQuestion(0);
      setSelectedAnswer(null);
      setAnswerResult(null);
      setShowQuiz(true);
      addToast(`Quiz ready!`, 'success');
    } catch { addToast('Failed to generate quiz', 'error'); }
  };

  const submitAnswer = async (answerIndex) => {
    if (answerResult) return;
    setSelectedAnswer(answerIndex);
    try {
      const { data } = await api.post('/general/learn/quiz/submit', { session_id: sessionId, question_index: currentQuestion, answer_index: answerIndex, quiz_data: quiz.questions, session_data: { correct_answers: answerResult?.is_correct ? 1 : 0 } });
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
      setFlashcards(data.data);
      setFlashcardIndex(0);
      setShowAnswer(false);
      setShowFlashcards(true);
    } catch { addToast('Failed', 'error'); }
  };

  const nextFlashcard = () => {
    if (flashcardIndex < (flashcards?.flashcards?.length || 0) - 1) { setFlashcardIndex(p => p + 1); setShowAnswer(false); }
    else { setShowFlashcards(false); addToast('All reviewed!', 'success'); }
  };

  return (
    <div className="h-full flex flex-col max-w-3xl mx-auto">
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

        {!sessionId && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
            <input value={topic} onChange={e => setTopic(e.target.value)} placeholder="What do you want to learn?" className="bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-primary" />
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
          <div className="h-[50vh] flex items-center justify-center text-center">
            <div>
              <Target size={48} className="text-text-muted mx-auto mb-4 opacity-30" />
              <h2 className="text-lg font-semibold text-text-primary mb-2">Start Learning</h2>
              <p className="text-text-muted text-sm">Choose a topic, set your level, and ask a question.</p>
            </div>
          </div>
        )}
        {messages.map((m, i) => <ChatMessage key={i} role={m.role} content={m.content} />)}
        {loading && <div className="flex gap-1.5 items-center px-4"><div className="w-2 h-2 bg-primary rounded-full animate-bounce" /><div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} /><div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} /></div>}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex-shrink-0 border-t border-border px-6 py-4">
        <form onSubmit={startSession} className="flex gap-2">
          <input value={message} onChange={e => setMessage(e.target.value)} placeholder={sessionId ? "Ask a follow-up..." : "Ask your first question..."} className="flex-1 bg-bg-tertiary border border-border rounded-xl px-4 py-2.5 text-text-primary placeholder-text-muted text-sm focus:outline-none focus:border-primary" disabled={loading} />
          <Button type="submit" size="sm" loading={loading} disabled={!message.trim()}><Send size={18} /></Button>
        </form>
      </div>

      {showQuiz && quiz && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <Card className="w-full max-w-lg">
            <div className="flex items-center justify-between mb-4">
              <div><h3 className="text-text-primary font-semibold">Quiz</h3><p className="text-xs text-text-muted">Question {currentQuestion + 1} of {quiz.questions?.length}</p></div>
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
            {answerResult && (
              <div className={`mt-4 p-3 rounded-lg text-sm ${answerResult.is_correct ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'}`}>
                {answerResult.is_correct ? '✓ Correct!' : `✗ Incorrect.`}
              </div>
            )}
            {answerResult && (
              <div className="flex justify-between mt-4 pt-4 border-t border-border">
                <span className="text-xs text-text-muted">Score: {answerResult.score?.toFixed(0) || 0}%</span>
                <Button size="sm" onClick={nextQuestion}>{currentQuestion < (quiz.questions?.length || 0) - 1 ? 'Next' : 'Finish'}<ChevronRight size={14} className="ml-1" /></Button>
              </div>
            )}
          </Card>
        </div>
      )}

      {showFlashcards && flashcards && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <Card className="w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <div><h3 className="text-text-primary font-semibold">Flashcards</h3><p className="text-xs text-text-muted">Card {flashcardIndex + 1} of {flashcards.flashcards?.length}</p></div>
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
          </Card>
        </div>
      )}
    </div>
  );
}