import { useState, useRef, useEffect } from 'react'
import { BookOpen, Send, Brain, Layers, Sparkles, Target, Zap, TrendingUp, ChevronRight, X, Check, RotateCcw } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/axios'
import ChatMessage from '../components/ChatMessage'

const SUBJECTS = [
  { value: 'general', label: 'General', icon: BookOpen },
  { value: 'programming', label: 'Programming', icon: Code },
  { value: 'math', label: 'Mathematics', icon: Target },
  { value: 'science', label: 'Science', icon: Zap },
  { value: 'history', label: 'History', icon: BookOpen },
  { value: 'language', label: 'Language', icon: Sparkles },
]

const LEVELS = ['beginner', 'intermediate', 'advanced']

// Fix missing import
import { Code } from 'lucide-react'

export default function Learn() {
  const [sessionId, setSessionId] = useState(null)
  const [topic, setTopic] = useState('')
  const [subject, setSubject] = useState('general')
  const [level, setLevel] = useState('beginner')
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [progress, setProgress] = useState(0)
  const [loading, setLoading] = useState(false)
  const [sessionInfo, setSessionInfo] = useState(null)
  const [showQuiz, setShowQuiz] = useState(false)
  const [quiz, setQuiz] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [answerResult, setAnswerResult] = useState(null)
  const [flashcards, setFlashcards] = useState(null)
  const [showFlashcards, setShowFlashcards] = useState(false)
  const [flashcardIndex, setFlashcardIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startSession = async (e) => {
    e?.preventDefault()
    if (!message.trim() || loading) return
    setLoading(true)
    setMessages((prev) => [...prev, { content: message, isUser: true }])
    const msg = message
    setMessage('')

    try {
      const { data } = await api.post('/general/learn', {
        topic: topic || 'General',
        subject,
        level,
        message: msg,
        session_id: sessionId,
      })
      setMessages((prev) => [...prev, { content: data.data.reply, isUser: false }])
      setSessionId(data.data.session_id)
      setProgress(data.data.progress || 0)
      setSessionInfo({ topic: topic || 'General', subject, level })
    } catch (err) {
      toast.error('Failed to get response')
      setMessages((prev) => [...prev, { content: 'Sorry, something went wrong.', isUser: false }])
    }
    setLoading(false)
  }

  const generateQuiz = async () => {
    if (!sessionId) return toast.error('Start a session first')
    try {
      const { data } = await api.get(`/general/learn/${sessionId}/quiz`)
      setQuiz(data.data)
      setCurrentQuestion(0)
      setSelectedAnswer(null)
      setAnswerResult(null)
      setShowQuiz(true)
      toast.success(`Quiz with ${data.data.questions?.length || 0} questions ready!`)
    } catch (err) {
      toast.error('Failed to generate quiz')
    }
  }

  const submitAnswer = async (answerIndex) => {
    if (answerResult) return
    setSelectedAnswer(answerIndex)
    try {
      const { data } = await api.post(`/general/learn/${sessionId}/quiz`, {
        question_index: currentQuestion,
        answer_index: answerIndex,
      })
      setAnswerResult(data.data)
    } catch (err) {
      toast.error('Failed to submit answer')
    }
  }

  const nextQuestion = () => {
    if (currentQuestion < (quiz?.questions?.length || 0) - 1) {
      setCurrentQuestion((prev) => prev + 1)
      setSelectedAnswer(null)
      setAnswerResult(null)
    } else {
      setShowQuiz(false)
      toast.success('Quiz complete!')
    }
  }

  const generateFlashcards = async () => {
    if (!sessionId) return toast.error('Start a session first')
    try {
      const { data } = await api.get(`/general/learn/${sessionId}/flashcards`)
      setFlashcards(data.data)
      setFlashcardIndex(0)
      setShowAnswer(false)
      setShowFlashcards(true)
      toast.success(`Generated ${data.data.flashcards?.length || 0} flashcards!`)
    } catch (err) {
      toast.error('Failed to generate flashcards')
    }
  }

  const nextFlashcard = () => {
    if (flashcardIndex < (flashcards?.flashcards?.length || 0) - 1) {
      setFlashcardIndex((prev) => prev + 1)
      setShowAnswer(false)
    } else {
      setShowFlashcards(false)
      toast.success('All flashcards reviewed!')
    }
  }

  return (
    <div className="h-full flex">
      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex-shrink-0 border-b border-dark-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-lg font-semibold text-white flex items-center gap-2">
                <BookOpen size={20} className="text-primary-400" />
                Learning Studio
              </h1>
              {sessionInfo && (
                <p className="text-sm text-dark-400 mt-0.5">
                  {sessionInfo.topic} • {sessionInfo.subject} • {sessionInfo.level}
                </p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button onClick={generateQuiz} className="btn-secondary text-sm flex items-center gap-1.5">
                <Brain size={15} /> Quiz
              </button>
              <button onClick={generateFlashcards} className="btn-secondary text-sm flex items-center gap-1.5">
                <Layers size={15} /> Flashcards
              </button>
            </div>
          </div>

          {/* Session config */}
          {!sessionId && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
              <input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="What do you want to learn?"
                className="input-field text-sm"
              />
              <select value={subject} onChange={(e) => setSubject(e.target.value)} className="input-field text-sm">
                {SUBJECTS.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
              <select value={level} onChange={(e) => setLevel(e.target.value)} className="input-field text-sm">
                {LEVELS.map((l) => (
                  <option key={l} value={l}>{l.charAt(0).toUpperCase() + l.slice(1)}</option>
                ))}
              </select>
            </div>
          )}

          {/* Progress bar */}
          {progress > 0 && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-dark-400 mb-1.5">
                <span>Learning Progress</span>
                <span className="text-primary-400 font-medium">{progress.toFixed(0)}%</span>
              </div>
              <div className="h-1.5 bg-dark-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primary-600 to-primary-400 rounded-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-6 py-4 space-y-4">
            {messages.length === 0 && !quiz && (
              <div className="h-[50vh] flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 bg-primary-600/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Target size={28} className="text-primary-400" />
                  </div>
                  <h2 className="text-lg font-semibold text-white mb-2">Start Learning</h2>
                  <p className="text-dark-400 text-sm max-w-sm">
                    Choose a topic, set your level, and ask a question to begin your personalized learning session.
                  </p>
                </div>
              </div>
            )}
            {messages.map((msg, i) => (
              <ChatMessage key={i} message={msg.content} isUser={msg.isUser} />
            ))}
            {loading && (
              <div className="flex gap-1.5 items-center px-4">
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="flex-shrink-0 border-t border-dark-800 bg-dark-950/80 backdrop-blur">
          <div className="max-w-3xl mx-auto px-6 py-4">
            <form onSubmit={startSession} className="flex gap-2">
              <input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder={sessionId ? "Ask a follow-up question..." : "Ask your first question..."}
                className="input-field flex-1 text-sm"
                disabled={loading}
              />
              <button type="submit" disabled={loading || !message.trim()} className="btn-primary px-4">
                <Send size={18} />
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Quiz modal */}
      {showQuiz && quiz && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-dark-900 border border-dark-700 rounded-2xl w-full max-w-lg shadow-2xl">
            <div className="flex items-center justify-between p-5 border-b border-dark-800">
              <div>
                <h3 className="text-white font-semibold">Quiz</h3>
                <p className="text-xs text-dark-400 mt-0.5">
                  Question {currentQuestion + 1} of {quiz.questions?.length}
                </p>
              </div>
              <button onClick={() => setShowQuiz(false)} className="p-1.5 text-dark-400 hover:text-white rounded-lg hover:bg-dark-800">
                <X size={18} />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <p className="text-white text-sm font-medium">{quiz.questions?.[currentQuestion]?.question}</p>
              <div className="space-y-2">
                {quiz.questions?.[currentQuestion]?.options?.map((option, i) => {
                  let buttonClass = 'bg-dark-800 border-dark-700 hover:border-dark-500 text-dark-200'
                  if (answerResult) {
                    if (i === quiz.questions[currentQuestion].correct_index) {
                      buttonClass = 'bg-green-600/20 border-green-600 text-green-400'
                    } else if (i === selectedAnswer && !answerResult.is_correct) {
                      buttonClass = 'bg-red-600/20 border-red-600 text-red-400'
                    }
                  } else if (i === selectedAnswer) {
                    buttonClass = 'bg-primary-600/20 border-primary-600 text-primary-400'
                  }
                  return (
                    <button
                      key={i}
                      onClick={() => submitAnswer(i)}
                      disabled={!!answerResult}
                      className={`w-full text-left px-4 py-3 rounded-lg border text-sm transition-all ${buttonClass}`}
                    >
                      <span className="font-medium mr-2">{String.fromCharCode(65 + i)}.</span>
                      {option}
                    </button>
                  )
                })}
              </div>
              {answerResult && (
                <div className={`p-3 rounded-lg text-sm ${answerResult.is_correct ? 'bg-green-600/10 text-green-400' : 'bg-red-600/10 text-red-400'}`}>
                  {answerResult.is_correct ? '✓ Correct!' : `✗ Incorrect. The correct answer is ${String.fromCharCode(65 + answerResult.correct_answer)}.`}
                </div>
              )}
            </div>
            <div className="flex justify-between p-5 border-t border-dark-800">
              <span className="text-xs text-dark-400">
                Score: {answerResult?.score?.toFixed(0) || 0}%
              </span>
              {answerResult && (
                <button onClick={nextQuestion} className="btn-primary text-sm flex items-center gap-1.5">
                  {currentQuestion < (quiz.questions?.length || 0) - 1 ? 'Next' : 'Finish'}
                  <ChevronRight size={14} />
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Flashcards modal */}
      {showFlashcards && flashcards && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-dark-900 border border-dark-700 rounded-2xl w-full max-w-md shadow-2xl">
            <div className="flex items-center justify-between p-5 border-b border-dark-800">
              <div>
                <h3 className="text-white font-semibold">Flashcards</h3>
                <p className="text-xs text-dark-400 mt-0.5">
                  Card {flashcardIndex + 1} of {flashcards.flashcards?.length}
                </p>
              </div>
              <button onClick={() => setShowFlashcards(false)} className="p-1.5 text-dark-400 hover:text-white rounded-lg hover:bg-dark-800">
                <X size={18} />
              </button>
            </div>
            <div className="p-8">
              <div
                onClick={() => setShowAnswer(!showAnswer)}
                className="min-h-[200px] bg-dark-800 border border-dark-700 rounded-xl p-6 flex items-center justify-center text-center cursor-pointer hover:border-dark-500 transition-all"
              >
                <div>
                  <p className="text-xs text-dark-500 mb-2 uppercase tracking-wider">
                    {showAnswer ? 'Definition' : 'Term'}
                  </p>
                  <p className="text-white text-lg font-medium">
                    {showAnswer
                      ? flashcards.flashcards?.[flashcardIndex]?.definition
                      : flashcards.flashcards?.[flashcardIndex]?.term
                    }
                  </p>
                  {!showAnswer && (
                    <p className="text-dark-500 text-xs mt-4">Tap to reveal answer</p>
                  )}
                </div>
              </div>
            </div>
            <div className="flex justify-between p-5 border-t border-dark-800">
              <button
                onClick={() => { setFlashcardIndex(Math.max(0, flashcardIndex - 1)); setShowAnswer(false) }}
                disabled={flashcardIndex === 0}
                className="btn-secondary text-sm"
              >
                Previous
              </button>
              <span className="text-xs text-dark-400 self-center">
                {flashcardIndex + 1} / {flashcards.flashcards?.length}
              </span>
              <button onClick={nextFlashcard} className="btn-primary text-sm flex items-center gap-1.5">
                {flashcardIndex < (flashcards.flashcards?.length || 0) - 1 ? 'Next' : 'Done'}
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}