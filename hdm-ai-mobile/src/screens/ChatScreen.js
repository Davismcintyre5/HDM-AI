import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View, Text, FlatList, TouchableOpacity, TextInput, StyleSheet,
  Animated, Dimensions
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import api from '../api/axios';
import ChatMessage from '../components/ChatMessage';
import ChatStream from '../components/ChatStream';
import Spinner from '../components/ui/Spinner';
import Button from '../components/ui/Button';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../components/ui/Toast';
import {
  Sparkles, Plus, Trash2, Pencil, Check, X, MessageSquare,
  Send, History
} from 'lucide-react-native';

const { width } = Dimensions.get('window');

export default function ChatScreen() {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const flatListRef = useRef(null);
  const slideAnim = useRef(new Animated.Value(width)).current;
  const { colors } = useTheme();
  const { addToast } = useToast();
  const insets = useSafeAreaInsets();

  useEffect(() => { loadConversations(); }, []);
  useEffect(() => { setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100); }, [messages, streaming]);

  useEffect(() => {
    Animated.timing(slideAnim, { toValue: showHistory ? 0 : width, duration: 250, useNativeDriver: true }).start();
    if (showHistory) loadConversations();
  }, [showHistory]);

  const loadConversations = async () => {
    try { const { data } = await api.get('/conversations'); setConversations(data.data || []); } catch {}
  };

  const loadMessages = async (convId) => {
    try {
      const { data } = await api.get(`/conversations/${convId}`);
      setMessages((data.data?.messages || []).map(m => ({ role: m.role, content: m.content })));
      setConversationId(convId); setShowHistory(false);
    } catch {}
  };

  const newChat = () => { setMessages([]); setConversationId(null); setShowHistory(false); };

  const handleSend = async () => {
    if (!message.trim() || loading) return;
    const msg = message.trim(); setMessage('');
    setMessages(prev => [...prev, { role: 'user', content: msg }]);
    setLoading(true);
    try {
      const { data } = await api.post('/chat/general', { message: msg, conversationId });
      setMessages(prev => [...prev, { role: 'assistant', content: data.data?.reply || 'No response.' }]);
      if (!conversationId) { setConversationId(data.data?.conversationId); loadConversations(); }
    } catch { setMessages(prev => [...prev, { role: 'assistant', content: 'Something went wrong.' }]); }
    setLoading(false);
  };

  const startRename = (conv) => { setEditingId(conv._id); setEditTitle(conv.title || 'New Chat'); };
  const saveRename = (convId) => {
    if (editTitle.trim()) setConversations(prev => prev.map(c => c._id === convId ? { ...c, title: editTitle.trim() } : c));
    setEditingId(null); setEditTitle('');
  };
  const deleteConversation = async (convId) => {
    try { await api.delete(`/conversations/${convId}`); setConversations(prev => prev.filter(c => c._id !== convId)); if (conversationId === convId) newChat(); addToast('Deleted', 'info'); }
    catch { addToast('Failed', 'error'); }
  };

  return (
    <View style={[styles.root, { backgroundColor: colors.bg, paddingTop: insets.top }]}>
      <View style={[styles.header, { borderBottomColor: colors.border }]}>
        <TouchableOpacity onPress={() => setShowHistory(true)}><History size={22} color={colors.textSecondary} /></TouchableOpacity>
        <Text style={[styles.headerTitle, { color: colors.text }]}>Chat</Text>
        <TouchableOpacity onPress={newChat}><Plus size={22} color={colors.accent} /></TouchableOpacity>
      </View>

      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={({ item }) => <ChatMessage role={item.role} content={item.content} />}
        keyExtractor={(_, i) => i.toString()}
        contentContainerStyle={[styles.list, { paddingBottom: insets.bottom + 60 }]}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Sparkles size={48} color={colors.accent} />
            <Text style={[styles.emptyTitle, { color: colors.text }]}>HDM AI Assistant</Text>
            <Text style={[styles.emptyText, { color: colors.textMuted }]}>Ask anything — I'm ready to help.</Text>
          </View>
        }
        ListFooterComponent={
          loading && !streaming ? (
            <View style={styles.loading}><Spinner size="sm" /><Text style={[styles.loadingText, { color: colors.textMuted }]}>Thinking...</Text></View>
          ) : null
        }
      />

      <View style={[styles.inputBar, { borderTopColor: colors.border, backgroundColor: colors.bg, paddingBottom: insets.bottom + 8 }]}>
        <View style={[styles.inputRow, { backgroundColor: colors.bgTertiary, borderColor: colors.border }]}>
          <TextInput value={message} onChangeText={setMessage} placeholder="Type your message..." placeholderTextColor={colors.textMuted}
            style={[styles.input, { color: colors.text }]} multiline editable={!loading} onSubmitEditing={handleSend} returnKeyType="send" />
          <TouchableOpacity onPress={handleSend} disabled={!message.trim() || loading}
            style={[styles.sendBtn, { backgroundColor: colors.accent, opacity: message.trim() ? 1 : 0.5 }]}>
            <Send size={18} color="#000" />
          </TouchableOpacity>
        </View>
      </View>

      {showHistory && <TouchableOpacity style={styles.overlay} activeOpacity={1} onPress={() => setShowHistory(false)} />}

      <Animated.View style={[styles.sidebar, { backgroundColor: colors.bgSecondary, borderLeftColor: colors.border, transform: [{ translateX: slideAnim }], paddingTop: insets.top }]}>
        <View style={[styles.sidebarHeader, { borderBottomColor: colors.border }]}>
          <Text style={[styles.sidebarTitle, { color: colors.text }]}>History</Text>
          <TouchableOpacity onPress={() => setShowHistory(false)}><X size={22} color={colors.textMuted} /></TouchableOpacity>
        </View>
        <TouchableOpacity onPress={newChat} style={[styles.sidebarNewChat, { borderColor: colors.border }]}>
          <Plus size={18} color={colors.accent} /><Text style={[styles.sidebarNewChatText, { color: colors.accent }]}>New Chat</Text>
        </TouchableOpacity>
        <FlatList
          data={conversations} keyExtractor={c => c._id}
          contentContainerStyle={{ paddingBottom: insets.bottom + 20 }}
          renderItem={({ item: conv }) => (
            <TouchableOpacity onPress={() => loadMessages(conv._id)}
              style={[styles.convItem, { backgroundColor: conversationId === conv._id ? colors.bgTertiary : 'transparent' }]}>
              <MessageSquare size={14} color={colors.textMuted} />
              {editingId === conv._id ? (
                <View style={styles.editRow}>
                  <TextInput value={editTitle} onChangeText={setEditTitle} style={[styles.editInput, { backgroundColor: colors.bg, borderColor: colors.border, color: colors.text }]}
                    autoFocus onBlur={() => saveRename(conv._id)} onSubmitEditing={() => saveRename(conv._id)} />
                  <TouchableOpacity onPress={() => saveRename(conv._id)}><Check size={14} color={colors.success} /></TouchableOpacity>
                  <TouchableOpacity onPress={() => setEditingId(null)}><X size={14} color={colors.textMuted} /></TouchableOpacity>
                </View>
              ) : (
                <>
                  <Text style={[styles.convTitle, { color: colors.text }]} numberOfLines={1}>{conv.title || 'New Chat'}</Text>
                  <View style={styles.convActions}>
                    <TouchableOpacity onPress={() => startRename(conv)}><Pencil size={12} color={colors.textMuted} /></TouchableOpacity>
                    <TouchableOpacity onPress={() => deleteConversation(conv._id)}><Trash2 size={12} color={colors.danger} /></TouchableOpacity>
                  </View>
                </>
              )}
            </TouchableOpacity>
          )}
          ListEmptyComponent={<Text style={[styles.emptyHistory, { color: colors.textMuted }]}>No conversations yet</Text>}
        />
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 14, paddingVertical: 10, borderBottomWidth: 1 },
  headerTitle: { fontSize: 17, fontWeight: '600' },
  list: { paddingHorizontal: 14, paddingTop: 10, flexGrow: 1 },
  empty: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingTop: 60 },
  emptyTitle: { fontSize: 20, fontWeight: '700', marginTop: 14 },
  emptyText: { fontSize: 13, marginTop: 4 },
  loading: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingLeft: 42, marginBottom: 16 },
  loadingText: { fontSize: 13 },
  inputBar: { paddingHorizontal: 12, paddingTop: 10, borderTopWidth: 1 },
  inputRow: { flexDirection: 'row', alignItems: 'flex-end', borderRadius: 16, borderWidth: 1, paddingHorizontal: 12, paddingVertical: 4 },
  input: { flex: 1, fontSize: 14, maxHeight: 100, paddingVertical: 8, marginRight: 8 },
  sendBtn: { width: 38, height: 38, borderRadius: 19, alignItems: 'center', justifyContent: 'center', marginBottom: 2 },
  overlay: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.4)', zIndex: 10 },
  sidebar: { position: 'absolute', top: 0, right: 0, bottom: 0, width: Math.min(width * 0.8, 340), borderLeftWidth: 1, zIndex: 20 },
  sidebarHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1 },
  sidebarTitle: { fontSize: 16, fontWeight: '600' },
  sidebarNewChat: { flexDirection: 'row', alignItems: 'center', gap: 8, marginHorizontal: 14, marginVertical: 12, paddingVertical: 10, paddingHorizontal: 14, borderRadius: 12, borderWidth: 1 },
  sidebarNewChatText: { fontSize: 13, fontWeight: '600' },
  convItem: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 10, paddingVertical: 10, borderRadius: 10, marginBottom: 2 },
  convTitle: { flex: 1, fontSize: 13 },
  convActions: { flexDirection: 'row', gap: 4 },
  editRow: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: 6 },
  editInput: { flex: 1, borderWidth: 1, borderRadius: 8, paddingHorizontal: 8, paddingVertical: 4, fontSize: 12 },
  emptyHistory: { textAlign: 'center', paddingTop: 30, fontSize: 13 },
});