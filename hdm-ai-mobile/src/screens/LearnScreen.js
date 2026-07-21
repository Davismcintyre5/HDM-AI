import React, { useState, useRef, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet, Modal as RNModal } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import api from '../api/axios';
import ChatMessage from '../components/ChatMessage';
import TeacherAvatar from '../components/TeacherAvatar';
import Button from '../components/ui/Button';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../components/ui/Toast';
import { BookOpen, Brain, Layers, Target, X, Headphones } from 'lucide-react-native';
import * as Speech from 'expo-speech';
import LiveTeacher from '../components/LiveTeacher';

const SUBJECTS = [
  { value: 'general', label: 'General' }, { value: 'programming', label: 'Programming' },
  { value: 'math', label: 'Mathematics' }, { value: 'science', label: 'Science' },
  { value: 'history', label: 'History' }, { value: 'language', label: 'Language' },
];
const LEVELS = ['beginner', 'intermediate', 'advanced'];
const LANGUAGES = [
  { code: 'en-US', label: 'English', flag: '🇺🇸' },
  { code: 'fr-FR', label: 'Français', flag: '🇫🇷' },
  { code: 'sw-KE', label: 'Kiswahili', flag: '🇰🇪' },
];

export default function LearnScreen() {
  const [sessionId, setSessionId] = useState(null);
  const [topic, setTopic] = useState('');
  const [subject, setSubject] = useState('general');
  const [level, setLevel] = useState('beginner');
  const [language, setLanguage] = useState('en-US');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sessionInfo, setSessionInfo] = useState(null);
  const [liveMode, setLiveMode] = useState(false);
  const [showAvatar, setShowAvatar] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showQuiz, setShowQuiz] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [currentQ, setCurrentQ] = useState(0);
  const [selectedA, setSelectedA] = useState(null);
  const [answerR, setAnswerR] = useState(null);
  const [showCards, setShowCards] = useState(false);
  const [flashcards, setFlashcards] = useState(null);
  const [cardIdx, setCardIdx] = useState(0);
  const [showA, setShowA] = useState(false);
  const flatListRef = useRef(null);
  const { colors } = useTheme();
  const { addToast } = useToast();
  const insets = useSafeAreaInsets();

  useEffect(() => { setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100); }, [messages]);

  const speakText = (text) => {
    if (!soundEnabled) return; Speech.stop(); setIsSpeaking(true);
    Speech.speak(text, { language, rate: 0.9, onDone: () => setIsSpeaking(false), onError: () => setIsSpeaking(false) });
  };
  const stopSpeaking = () => { Speech.stop(); setIsSpeaking(false); };

  const newSession = () => {
    stopSpeaking();
    localStorage?.removeItem('learn_session');
    setSessionId(null); setSessionInfo(null); setMessages([]);
    setProgress(0); setTopic('');
    addToast('New session started', 'info');
  };

  const clearChat = () => {
    stopSpeaking();
    setMessages([]);
    addToast('Chat cleared', 'info');
  };

  const startSession = async () => {
    if (!message.trim() || loading) return;
    setLoading(true); setMessages(prev => [...prev, { role: 'user', content: message }]);
    const msg = message; setMessage('');
    try {
      const { data } = await api.post('/general/learn', { topic: topic || 'General', subject, level, message: msg, session_id: sessionId });
      setMessages(prev => [...prev, { role: 'assistant', content: data.data.reply }]);
      setSessionId(data.data.session_id); setProgress(data.data.progress || 0);
      setSessionInfo({ topic: topic || 'General', subject, level }); speakText(data.data.reply);
    } catch { addToast('Failed', 'error'); }
    setLoading(false);
  };

  const genQuiz = async () => {
    if (!sessionId) return addToast('Start a session first', 'error');
    try { const { data } = await api.post('/general/learn/quiz', { session_id: sessionId, topic: topic || 'General', level, num_questions: 5 }); setQuiz(data.data); setCurrentQ(0); setSelectedA(null); setAnswerR(null); setShowQuiz(true); } catch { addToast('Failed', 'error'); }
  };
  const submitA = async (idx) => {
    if (answerR) return; setSelectedA(idx);
    try { const { data } = await api.post('/general/learn/quiz/submit', { session_id: sessionId, question_index: currentQ, answer_index: idx, quiz_data: quiz.questions, session_data: {} }); setAnswerR(data.data); } catch { addToast('Failed', 'error'); }
  };
  const nextQ = () => { if (currentQ < (quiz?.questions?.length || 0) - 1) { setCurrentQ(p => p + 1); setSelectedA(null); setAnswerR(null); } else { setShowQuiz(false); addToast('Quiz complete!', 'success'); } };
  const genCards = async () => {
    if (!sessionId) return addToast('Start a session first', 'error');
    try { const { data } = await api.post('/general/learn/flashcards', { session_id: sessionId, topic: topic || 'General', level }); setFlashcards(data.data); setCardIdx(0); setShowA(false); setShowCards(true); } catch { addToast('Failed', 'error'); }
  };
  const nextCard = () => { if (cardIdx < (flashcards?.flashcards?.length || 0) - 1) { setCardIdx(p => p + 1); setShowA(false); } else { setShowCards(false); addToast('All reviewed!', 'success'); } };

  if (liveMode) return <LiveTeacher language={language} topic={topic} onClose={() => setLiveMode(false)} onReturn={() => setLiveMode(false)} />;

  return (
    <View style={[styles.root, { backgroundColor: colors.bg, paddingTop: insets.top }]}>
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={({ item }) => <ChatMessage role={item.role} content={item.content} />}
        keyExtractor={(_, i) => i.toString()}
        contentContainerStyle={[styles.list, { paddingBottom: insets.bottom + 100 }]}
        ListHeaderComponent={
          <View style={[styles.header, { borderBottomColor: colors.border }]}>
            <View style={styles.headerRow}>
              <Text style={[styles.title, { color: colors.text }]}><BookOpen size={18} color={colors.accent} />  Learning</Text>
              <View style={styles.headerBtns}>
                <Button size="sm" variant="secondary" onPress={genQuiz}><Brain size={14} color={colors.textSecondary} /> Quiz</Button>
                <Button size="sm" variant="secondary" onPress={genCards}><Layers size={14} color={colors.textSecondary} /> Cards</Button>
              </View>
            </View>
            {sessionInfo && <Text style={[styles.sessionInfo, { color: colors.textSecondary }]}>{sessionInfo.topic} • {sessionInfo.subject} • {sessionInfo.level}</Text>}

            {/* Toggles */}
            <View style={styles.toggles}>
              <TouchableOpacity onPress={() => setLiveMode(true)} style={[styles.toggle, { backgroundColor: colors.accent }]}>
                <Headphones size={14} color="#000" /><Text style={[styles.toggleText, { color: '#000' }]}>Live Teacher</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => setShowAvatar(!showAvatar)} style={[styles.toggle, { backgroundColor: showAvatar ? colors.accent + '20' : colors.bgTertiary, borderColor: showAvatar ? colors.accent : colors.border, borderWidth: 1 }]}>
                <Text style={[styles.toggleText, { color: showAvatar ? colors.accent : colors.textSecondary }]}>{showAvatar ? 'Mr HDM ON' : 'Mr HDM'}</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => { setSoundEnabled(!soundEnabled); if (soundEnabled) stopSpeaking(); }} style={[styles.toggle, { backgroundColor: soundEnabled ? colors.accent + '20' : colors.bgTertiary, borderColor: soundEnabled ? colors.accent : colors.border, borderWidth: 1 }]}>
                <Text style={[styles.toggleText, { color: soundEnabled ? colors.accent : colors.textSecondary }]}>{soundEnabled ? 'Sound ON' : 'Sound'}</Text>
              </TouchableOpacity>
              {isSpeaking && <TouchableOpacity onPress={stopSpeaking} style={[styles.toggle, { backgroundColor: colors.danger + '20', borderColor: colors.danger, borderWidth: 1 }]}><Text style={[styles.toggleText, { color: colors.danger }]}>⏹ Stop</Text></TouchableOpacity>}
              <View style={styles.langRow}>
                {LANGUAGES.map(l => <TouchableOpacity key={l.code} onPress={() => setLanguage(l.code)} style={[styles.langBtn, { backgroundColor: language === l.code ? colors.accent : colors.bgTertiary }]}><Text style={[styles.langText, { color: language === l.code ? '#000' : colors.textSecondary }]}>{l.flag}</Text></TouchableOpacity>)}
              </View>
            </View>

            {/* Session controls */}
            {sessionId && (
              <View style={styles.sessionControls}>
                <TouchableOpacity onPress={newSession} style={[styles.sessionBtn, { backgroundColor: colors.bgTertiary, borderColor: colors.border }]}>
                  <Text style={[styles.sessionBtnText, { color: colors.textSecondary }]}>+ New Session</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={clearChat} style={[styles.sessionBtn, { backgroundColor: colors.bgTertiary, borderColor: colors.border }]}>
                  <Text style={[styles.sessionBtnText, { color: colors.textSecondary }]}>Clear Chat</Text>
                </TouchableOpacity>
              </View>
            )}

            {showAvatar && <View style={styles.avatarContainer}><TeacherAvatar speaking={isSpeaking} emotion="idle" size={100} /></View>}
            {!sessionId && (
              <View style={styles.config}>
                <TextInput value={topic} onChangeText={setTopic} placeholder="What to learn?" placeholderTextColor={colors.textMuted} style={[styles.configInput, { backgroundColor: colors.bgTertiary, borderColor: colors.border, color: colors.text }]} />
                <View style={styles.configSelects}>{SUBJECTS.map(s => <TouchableOpacity key={s.value} onPress={() => setSubject(s.value)} style={[styles.configChip, { backgroundColor: subject === s.value ? colors.accent : colors.bgTertiary }]}><Text style={[styles.configChipText, { color: subject === s.value ? '#000' : colors.textSecondary }]}>{s.label}</Text></TouchableOpacity>)}</View>
                <View style={styles.configSelects}>{LEVELS.map(l => <TouchableOpacity key={l} onPress={() => setLevel(l)} style={[styles.configChip, { backgroundColor: level === l ? colors.accent : colors.bgTertiary }]}><Text style={[styles.configChipText, { color: level === l ? '#000' : colors.textSecondary }]}>{l.charAt(0).toUpperCase() + l.slice(1)}</Text></TouchableOpacity>)}</View>
              </View>
            )}
            {progress > 0 && <View style={styles.progressBar}><View style={[styles.progressFill, { width: `${progress}%`, backgroundColor: colors.accent }]} /></View>}
          </View>
        }
        ListEmptyComponent={
          !sessionId ? <View style={styles.empty}><Target size={40} color={colors.textMuted} /><Text style={[styles.emptyText, { color: colors.textMuted }]}>Choose a topic and ask a question</Text></View> : null
        }
      />
      <View style={[styles.inputBar, { borderTopColor: colors.border, backgroundColor: colors.bg, paddingBottom: insets.bottom + 8 }]}>
        <TextInput value={message} onChangeText={setMessage} placeholder={sessionId ? "Ask a follow-up..." : "Ask your first question..."} placeholderTextColor={colors.textMuted}
          style={[styles.msgInput, { backgroundColor: colors.bgTertiary, borderColor: colors.border, color: colors.text }]} editable={!loading} onSubmitEditing={startSession} returnKeyType="send" />
        <Button size="sm" onPress={startSession} loading={loading} disabled={!message.trim()}>Send</Button>
      </View>

      <RNModal visible={showQuiz} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colors.bgSecondary, borderColor: colors.border }]}>
            <View style={styles.modalHeader}><Text style={[styles.modalTitle, { color: colors.text }]}>Quiz</Text><TouchableOpacity onPress={() => setShowQuiz(false)}><X size={20} color={colors.textMuted} /></TouchableOpacity></View>
            <Text style={[styles.quizQ, { color: colors.text }]}>{quiz?.questions?.[currentQ]?.question}</Text>
            {quiz?.questions?.[currentQ]?.options?.map((opt, i) => {
              let bg = colors.bgTertiary;
              if (answerR) { if (i === quiz.questions[currentQ].correct_index) bg = colors.success + '30'; else if (i === selectedA && !answerR.is_correct) bg = colors.danger + '30'; }
              else if (i === selectedA) bg = colors.accent + '30';
              return <TouchableOpacity key={i} onPress={() => submitA(i)} disabled={!!answerR} style={[styles.quizOpt, { backgroundColor: bg, borderColor: colors.border }]}><Text style={{ color: colors.text }}>{String.fromCharCode(65 + i)}. {opt}</Text></TouchableOpacity>;
            })}
            {answerR && <Text style={{ color: answerR.is_correct ? colors.success : colors.danger, marginTop: 10 }}>{answerR.is_correct ? '✓ Correct!' : '✗ Incorrect'}</Text>}
            {answerR && <Button size="sm" onPress={nextQ} style={{ marginTop: 12 }}>{currentQ < (quiz?.questions?.length || 0) - 1 ? 'Next' : 'Finish'}</Button>}
          </View>
        </View>
      </RNModal>

      <RNModal visible={showCards} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colors.bgSecondary, borderColor: colors.border }]}>
            <View style={styles.modalHeader}><Text style={[styles.modalTitle, { color: colors.text }]}>Flashcards</Text><TouchableOpacity onPress={() => setShowCards(false)}><X size={20} color={colors.textMuted} /></TouchableOpacity></View>
            <TouchableOpacity onPress={() => setShowA(!showA)} style={[styles.cardBody, { backgroundColor: colors.bgTertiary, borderColor: colors.border }]}>
              <Text style={[styles.cardLabel, { color: colors.textMuted }]}>{showA ? 'Definition' : 'Term'}</Text>
              <Text style={[styles.cardText, { color: colors.text }]}>{showA ? flashcards?.flashcards?.[cardIdx]?.definition : flashcards?.flashcards?.[cardIdx]?.term}</Text>
              {!showA && <Text style={[styles.cardHint, { color: colors.textMuted }]}>Tap to reveal</Text>}
            </TouchableOpacity>
            <View style={styles.cardNav}>
              <Button variant="secondary" size="sm" onPress={() => { setCardIdx(Math.max(0, cardIdx - 1)); setShowA(false); }} disabled={cardIdx === 0}>Prev</Button>
              <Text style={{ color: colors.textMuted }}>{cardIdx + 1}/{flashcards?.flashcards?.length}</Text>
              <Button size="sm" onPress={nextCard}>{cardIdx < (flashcards?.flashcards?.length || 0) - 1 ? 'Next' : 'Done'}</Button>
            </View>
          </View>
        </View>
      </RNModal>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  header: { paddingHorizontal: 14, paddingVertical: 10, borderBottomWidth: 1 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  title: { fontSize: 16, fontWeight: '600' },
  headerBtns: { flexDirection: 'row', gap: 8 },
  sessionInfo: { fontSize: 12, marginTop: 4 },
  toggles: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 10, flexWrap: 'wrap' },
  toggle: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 10, paddingVertical: 7, borderRadius: 10 },
  toggleText: { fontSize: 11, fontWeight: '600' },
  langRow: { flexDirection: 'row', gap: 6 },
  langBtn: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8 },
  langText: { fontSize: 12, fontWeight: '500' },
  sessionControls: { flexDirection: 'row', gap: 8, marginTop: 10 },
  sessionBtn: { paddingHorizontal: 14, paddingVertical: 7, borderRadius: 10, borderWidth: 1 },
  sessionBtnText: { fontSize: 11, fontWeight: '600' },
  avatarContainer: { alignItems: 'center', marginTop: 10 },
  config: { marginTop: 10, gap: 8 },
  configInput: { borderWidth: 1, borderRadius: 10, paddingHorizontal: 12, paddingVertical: 10, fontSize: 13 },
  configSelects: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  configChip: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8 },
  configChipText: { fontSize: 12, fontWeight: '500' },
  progressBar: { height: 4, backgroundColor: '#2a2a2a', borderRadius: 2, marginTop: 10, overflow: 'hidden' },
  progressFill: { height: 4, borderRadius: 2 },
  list: { paddingHorizontal: 14, paddingTop: 10, flexGrow: 1 },
  empty: { alignItems: 'center', paddingTop: 60 },
  emptyText: { fontSize: 13, marginTop: 10 },
  inputBar: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingHorizontal: 12, paddingTop: 10, borderTopWidth: 1 },
  msgInput: { flex: 1, borderWidth: 1, borderRadius: 14, paddingHorizontal: 14, paddingVertical: 10, fontSize: 13 },
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.6)', padding: 20 },
  modalContent: { width: '100%', maxWidth: 380, borderRadius: 16, borderWidth: 1, padding: 20 },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  modalTitle: { fontSize: 16, fontWeight: '600' },
  quizQ: { fontSize: 14, fontWeight: '500', marginBottom: 12 },
  quizOpt: { padding: 12, borderRadius: 10, borderWidth: 1, marginBottom: 8 },
  cardBody: { minHeight: 180, justifyContent: 'center', alignItems: 'center', borderRadius: 14, borderWidth: 1, padding: 20 },
  cardLabel: { fontSize: 10, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10 },
  cardText: { fontSize: 17, fontWeight: '500', textAlign: 'center' },
  cardHint: { fontSize: 11, marginTop: 14 },
  cardNav: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 16 },
});