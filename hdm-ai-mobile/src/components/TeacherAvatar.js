import React, { useEffect, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import Svg, { Circle, Ellipse, Path, Line, Rect } from 'react-native-svg';
import { useTheme } from '../context/ThemeContext';

export default function TeacherAvatar({ speaking = false, emotion = 'idle', size = 140 }) {
  const [blink, setBlink] = useState(false);
  const { colors } = useTheme();

  useEffect(() => {
    if (!speaking) {
      const interval = setInterval(() => { setBlink(true); setTimeout(() => setBlink(false), 150); }, 3000);
      return () => clearInterval(interval);
    }
  }, [speaking]);

  const mouthD = speaking ? 'M38 72 Q48 80 58 72' : 'M40 72 Q48 74 56 72';
  const eyeScale = blink ? 0.1 : 1;

  return (
    <View style={styles.container}>
      <Svg viewBox="0 0 96 140" width={size} height={size * 1.45}>
        {/* Head */}
        <Ellipse cx="48" cy="34" rx="18" ry="20" fill="#f4c29a" />
        {/* Hair */}
        <Path d="M30 28 Q30 8 48 8 Q66 8 66 28" fill="#1a1a1a" />
        <Path d="M28 30 Q48 5 68 30 Q62 14 48 14 Q34 14 28 30" fill="#2a2a2a" />
        {/* Eyes */}
        <Ellipse cx="40" cy="30" rx="3" ry="4" fill="#1a1a1a" scaleY={eyeScale} origin="40,30" />
        <Ellipse cx="56" cy="30" rx="3" ry="4" fill="#1a1a1a" scaleY={eyeScale} origin="56,30" />
        <Circle cx="41" cy="28" r="1.2" fill="#fff" />
        <Circle cx="57" cy="28" r="1.2" fill="#fff" />
        {/* Eyebrows */}
        <Path d="M34 25 Q40 22 44 25" stroke="#1a1a1a" strokeWidth="1.2" fill="none" />
        <Path d="M52 25 Q56 22 62 25" stroke="#1a1a1a" strokeWidth="1.2" fill="none" />
        {/* Nose */}
        <Path d="M46 36 Q48 41 50 36" stroke="#999" strokeWidth="0.8" fill="none" />
        {/* Mouth */}
        <Path d={mouthD} stroke="#555" strokeWidth="1.5" fill="none" strokeLinecap="round" />
        {/* Glasses */}
        <Rect x="34" y="26" width="12" height="8" rx="3" stroke="#555" strokeWidth="1.2" fill="none" />
        <Rect x="50" y="26" width="12" height="8" rx="3" stroke="#555" strokeWidth="1.2" fill="none" />
        <Line x1="46" y1="30" x2="50" y2="30" stroke="#555" strokeWidth="1.2" />
        {/* Suit */}
        <Path d="M30 54 L30 115 Q48 128 66 115 L66 54 Z" fill="#1a1a1a" />
        {/* Shirt */}
        <Path d="M36 54 L36 90 L60 90 L60 54 Z" fill="#fff" />
        {/* Tie */}
        <Path d="M42 54 L48 80 L54 54 Z" fill={colors.accent} />
        {/* Lapels */}
        <Path d="M36 54 L48 72 L48 54" fill="#2a2a2a" />
        <Path d="M60 54 L48 72 L48 54" fill="#2a2a2a" />
        {/* Arms */}
        <Path d="M30 58 Q18 72 22 100 Q24 106 30 102" stroke="#1a1a1a" strokeWidth="7" fill="none" strokeLinecap="round" />
        <Path d="M66 58 Q78 72 74 100 Q72 106 66 102" stroke="#1a1a1a" strokeWidth="7" fill="none" strokeLinecap="round" />
        {/* Hands */}
        <Circle cx="24" cy="102" r="4" fill="#f4c29a" />
        <Circle cx="72" cy="102" r="4" fill="#f4c29a" />
        {/* Pocket square */}
        <Rect x="44" y="58" width="8" height="6" fill={colors.accent} opacity={0.6} />
      </Svg>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center', justifyContent: 'center' },
});
