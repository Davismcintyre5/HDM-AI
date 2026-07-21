import React, { useState, useRef, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Animated } from 'react-native';
import { Mic, MicOff, PhoneOff, FileText, X, ArrowLeft } from 'lucide-react-native';
import TeacherAvatar from './TeacherAvatar';
import * as Speech from 'expo-speech';
import api from '../api/axios';
import { useTheme } from '../context/ThemeContext';
import { useToast } from './ui/Toast';

export default function LiveTeacher({ language = 'en', topic = '', onClose, onReturn }) {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [status, setStatus] = useState('idle');
  const [notes, setNotes] = useState([]);
  const [showNotes, setShowNotes] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const { colors } = useTheme();
  const { addToast } = useToast();

  useEffect(() => {
    if (isListening) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, { toValue: 1.08, duration: 400, useNativeDriver: true }),
          Animated.timing(pulseAnim, { toValue: 1, duration: 400, useNativeDriver: true }),
        ])
      ).start();
    } else {
      pulseAnim.setValue(1);
    }
  }, [isListening]);

  const speak = (text) => {
    setIsSpeaking(true);
    setStatus('speaking');
    Speech.speak(text, {
      language,
      rate: 0.9,
      onDone: () => { setIsSpeaking(false); setStatus('idle'); },
      onError: () => { setIsSpeaking(false); setStatus('idle'); },
    });
  };

  const startListening = async () => {
    if (isSpeaking) {
      Speech.stop();
      setIsSpeaking(false);
    }
    addToast('Tap mic and speak. Speech-to-text on mobile requires native module.', 'info');
    setStatus('idle');
  };

  const endSession = () => {
    Speech.stop();
    if (onClose) onClose();
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.bg }]}>
      {/* Top bar */}
      <View style={styles.topBar}>
        <TouchableOpacity onPress={onReturn} style={styles.topBtn}>
          <ArrowLeft size={22} color={colors.textMuted} />
        </TouchableOpacity>
        <View style={styles.topRight}>
          <TouchableOpacity onPress={() => setShowNotes(true)} style={styles.topBtn}>
            <FileText size={20} color={colors.textMuted} />
          </TouchableOpacity>
          <TouchableOpacity onPress={endSession} style={styles.topBtn}>
            <PhoneOff size={20} color={colors.textMuted} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Status */}
      <Text style={[styles.statusText, { color: colors.textMuted }]}>
        {!hasStarted && 'Tap the microphone to begin'}
        {status === 'listening' && '🎤 Listening...'}
        {status === 'thinking' && '🤔 Thinking...'}
        {status === 'speaking' && '🔊 Speaking...'}
        {status === 'idle' && hasStarted && 'Tap mic to ask a question'}
      </Text>

      {/* Avatar */}
      <Animated.View style={{ transform: [{ scale: isSpeaking ? 1.1 : pulseAnim }] }}>
        <TeacherAvatar speaking={isSpeaking} emotion={status === 'thinking' ? 'thinking' : status === 'speaking' ? 'speaking' : 'idle'} size={160} />
      </Animated.View>

      {/* Mic button */}
      <TouchableOpacity
        onPress={startListening}
        disabled={isSpeaking}
        style={[styles.micBtn, { backgroundColor: colors.accent, opacity: isSpeaking ? 0.5 : 1 }]}
      >
        <Mic size={36} color="#000" />
      </TouchableOpacity>

      {hasStarted && (
        <TouchableOpacity
          onPress={() => { setHasStarted(false); setNotes([]); addToast('New topic started', 'info'); }}
          style={[styles.newTopicBtn, { borderColor: colors.border }]}
        >
          <Text style={[styles.newTopicText, { color: colors.textSecondary }]}>New Topic</Text>
        </TouchableOpacity>
      )}

      <Text style={[styles.hint, { color: colors.textMuted }]}>Mr. HDM only speaks when you tap the mic</Text>

      {/* Notes panel */}
      {showNotes && (
        <View style={[styles.notesPanel, { backgroundColor: colors.bgSecondary, borderLeftColor: colors.border }]}>
          <View style={[styles.notesHeader, { borderBottomColor: colors.border }]}>
            <Text style={[styles.notesTitle, { color: colors.text }]}>Session Notes</Text>
            <TouchableOpacity onPress={() => setShowNotes(false)}>
              <X size={20} color={colors.textMuted} />
            </TouchableOpacity>
          </View>
          <ScrollView style={styles.notesScroll}>
            {notes.length === 0 ? (
              <Text style={[styles.emptyNotes, { color: colors.textMuted }]}>No notes yet.</Text>
            ) : (
              notes.map((n, i) => (
                <View key={i} style={[styles.noteBubble, n.role === 'user' ? styles.noteUser : styles.noteBot, {
                  backgroundColor: n.role === 'user' ? colors.accent + '15' : colors.bgTertiary,
                }]}>
                  <Text style={[styles.noteRole, { color: colors.textMuted }]}>{n.role === 'user' ? 'You' : 'Mr. HDM'}</Text>
                  <Text style={[styles.noteContent, { color: colors.text }]}>{n.content}</Text>
                </View>
              ))
            )}
          </ScrollView>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 20 },
  topBar: { position: 'absolute', top: 50, left: 16, right: 16, flexDirection: 'row', justifyContent: 'space-between' },
  topRight: { flexDirection: 'row', gap: 8 },
  topBtn: { padding: 8 },
  statusText: { fontSize: 11, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 24 },
  micBtn: { width: 80, height: 80, borderRadius: 40, alignItems: 'center', justifyContent: 'center', marginTop: 32 },
  newTopicBtn: { marginTop: 20, borderWidth: 1, borderRadius: 100, paddingHorizontal: 20, paddingVertical: 10 },
  newTopicText: { fontSize: 13, fontWeight: '500' },
  hint: { fontSize: 11, marginTop: 20, textAlign: 'center' },
  notesPanel: { position: 'absolute', top: 0, right: 0, bottom: 0, width: '100%', maxWidth: 360, borderLeftWidth: 1, zIndex: 50 },
  notesHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1 },
  notesTitle: { fontSize: 15, fontWeight: '600' },
  notesScroll: { flex: 1, paddingHorizontal: 14, paddingVertical: 12 },
  emptyNotes: { textAlign: 'center', marginTop: 40, fontSize: 13 },
  noteBubble: { padding: 10, borderRadius: 12, marginBottom: 10 },
  noteUser: { alignSelf: 'flex-end', borderBottomRightRadius: 2 },
  noteBot: { alignSelf: 'flex-start', borderBottomLeftRadius: 2 },
  noteRole: { fontSize: 9, textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 3 },
  noteContent: { fontSize: 13, lineHeight: 18 },
});