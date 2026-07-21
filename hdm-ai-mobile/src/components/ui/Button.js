import React from 'react';
import { TouchableOpacity, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { useTheme } from '../../context/ThemeContext';

export default function Button({ children, variant = 'primary', size = 'md', loading, disabled, onPress, style }) {
  const { colors } = useTheme();

  const variants = {
    primary: { bg: colors.accent, text: '#000' },
    secondary: { bg: colors.bgTertiary, text: colors.text, border: colors.border },
    danger: { bg: colors.danger, text: '#fff' },
    ghost: { bg: 'transparent', text: colors.textSecondary },
  };

  const sizes = {
    sm: { py: 8, px: 14, fontSize: 13 },
    md: { py: 12, px: 20, fontSize: 14 },
    lg: { py: 16, px: 28, fontSize: 16 },
  };

  const v = variants[variant];
  const s = sizes[size];

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
      style={[
        styles.base,
        {
          backgroundColor: v.bg,
          paddingVertical: s.py,
          paddingHorizontal: s.px,
          opacity: disabled ? 0.5 : 1,
          borderWidth: v.border ? 1 : 0,
          borderColor: v.border || 'transparent',
        },
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator size="small" color={v.text} />
      ) : (
        <Text style={[styles.text, { color: v.text, fontSize: s.fontSize }]}>{children}</Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: { borderRadius: 10, alignItems: 'center', justifyContent: 'center', flexDirection: 'row', gap: 6 },
  text: { fontWeight: '600' },
});