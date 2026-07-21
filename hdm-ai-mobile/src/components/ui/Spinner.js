import React from 'react';
import { ActivityIndicator } from 'react-native';
import { useTheme } from '../../context/ThemeContext';

export default function Spinner({ size = 'md' }) {
  const { colors } = useTheme();
  const sizes = { sm: 20, md: 36, lg: 52 };
  return <ActivityIndicator size={sizes[size] || sizes.md} color={colors.accent} />;
}