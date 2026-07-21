import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '../../context/ThemeContext';

export default function Badge({ children, variant = 'primary' }) {
  const { colors } = useTheme();

  const variants = {
    primary: { bg: colors.accent + '20', text: colors.accent },
    success: { bg: colors.success + '20', text: colors.success },
    danger: { bg: colors.danger + '20', text: colors.danger },
    muted: { bg: colors.bgTertiary, text: colors.textMuted },
  };

  const v = variants[variant];

  return (
    <View style={[styles.badge, { backgroundColor: v.bg }]}>
      <Text style={[styles.text, { color: v.text }]}>{children}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 100, alignSelf: 'flex-start' },
  text: { fontSize: 11, fontWeight: '600' },
});