import React, { useState, useRef, useEffect } from 'react';
import { View, TextInput, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { Send, Paperclip } from 'lucide-react-native';
import { useTheme } from '../context/ThemeContext';

export default function ChatInput({ onSend, loading }) {
  const [message, setMessage] = useState('');
  const inputRef = useRef(null);
  const { colors } = useTheme();

  const handleSend = () => {
    if (!message.trim() || loading) return;
    onSend({ message: message.trim(), files: [] });
    setMessage('');
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.bg, borderTopColor: colors.border }]}>
      <View style={[styles.inputRow, { backgroundColor: colors.bgTertiary, borderColor: colors.border }]}>
        <TextInput
          ref={inputRef}
          value={message}
          onChangeText={setMessage}
          placeholder="Type your message..."
          placeholderTextColor={colors.textMuted}
          style={[styles.input, { color: colors.text }]}
          multiline
          maxLength={4000}
          editable={!loading}
          onSubmitEditing={handleSend}
          returnKeyType="send"
          blurOnSubmit={false}
        />
        <TouchableOpacity
          onPress={handleSend}
          disabled={!message.trim() || loading}
          style={[styles.sendBtn, { backgroundColor: colors.accent, opacity: message.trim() ? 1 : 0.5 }]}
        >
          <Send size={18} color="#000" />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { paddingHorizontal: 12, paddingVertical: 10, borderTopWidth: 1 },
  inputRow: { flexDirection: 'row', alignItems: 'flex-end', borderRadius: 16, borderWidth: 1, paddingHorizontal: 12, paddingVertical: Platform.OS === 'ios' ? 10 : 4 },
  input: { flex: 1, fontSize: 14, maxHeight: 100, paddingVertical: 6, marginRight: 8 },
  sendBtn: { width: 38, height: 38, borderRadius: 19, alignItems: 'center', justifyContent: 'center', marginBottom: 2 },
});
