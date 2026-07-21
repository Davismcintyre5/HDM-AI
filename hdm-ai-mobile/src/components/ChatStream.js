import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { Bot } from 'lucide-react-native';

export default function ChatStream({ content }) {
  const { colors } = useTheme();

  return (
    <View style={styles.row}>
      <View style={[styles.avatar, { backgroundColor: colors.bgTertiary }]}>
        <Bot size={16} color={colors.textSecondary} />
      </View>
      <View style={[styles.bubble, { backgroundColor: colors.bgSecondary, borderColor: colors.border }]}>
        <Text style={[styles.text, { color: colors.text }]}>
          {content}
          <View style={[styles.cursor, { backgroundColor: colors.accent }]} />
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', gap: 10, marginBottom: 16 },
  avatar: { width: 32, height: 32, borderRadius: 16, alignItems: 'center', justifyContent: 'center' },
  bubble: { maxWidth: '80%', paddingHorizontal: 14, paddingVertical: 10, borderRadius: 16, borderTopLeftRadius: 4, borderWidth: 1 },
  text: { fontSize: 14, lineHeight: 20 },
  cursor: { width: 8, height: 16, marginLeft: 2, alignSelf: 'flex-end' },
});
