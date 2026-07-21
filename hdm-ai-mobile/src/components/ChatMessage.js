import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { Bot, User } from 'lucide-react-native';

export default function ChatMessage({ role, content }) {
  const { colors } = useTheme();
  const isUser = role === 'user';

  return (
    <View style={[styles.row, isUser && styles.rowReverse]}>
      <View style={[styles.avatar, { backgroundColor: isUser ? colors.accent : colors.bgTertiary }]}>
        {isUser ? <User size={16} color="#000" /> : <Bot size={16} color={colors.textSecondary} />}
      </View>
      <View style={[styles.bubble, isUser ? styles.bubbleUser : styles.bubbleBot, {
        backgroundColor: isUser ? colors.accent : colors.bgSecondary,
        borderColor: isUser ? 'transparent' : colors.border,
      }]}>
        <Text style={[styles.text, { color: isUser ? '#000' : colors.text }]}>{content}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', gap: 10, marginBottom: 16 },
  rowReverse: { flexDirection: 'row-reverse' },
  avatar: { width: 32, height: 32, borderRadius: 16, alignItems: 'center', justifyContent: 'center' },
  bubble: { maxWidth: '80%', paddingHorizontal: 14, paddingVertical: 10, borderRadius: 16, borderWidth: 1 },
  bubbleUser: { borderTopRightRadius: 4 },
  bubbleBot: { borderTopLeftRadius: 4 },
  text: { fontSize: 14, lineHeight: 20 },
});