import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';
import api from '../api/axios';
import ScreenWrapper from '../components/ui/ScreenWrapper';
import Button from '../components/ui/Button';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../components/ui/Toast';
import { Play, Copy, Trash2 } from 'lucide-react-native';

const LANGUAGES = [
  { label: 'Python', value: 'python' },
  { label: 'JavaScript', value: 'javascript' },
  { label: 'TypeScript', value: 'typescript' },
  { label: 'Bash', value: 'bash' },
  { label: 'SQL', value: 'sql' },
  { label: 'Java', value: 'java' },
  { label: 'Go', value: 'go' },
  { label: 'Rust', value: 'rust' },
];

const STARTERS = {
  python: 'print("Hello, HDM AI!")',
  javascript: 'console.log("Hello, HDM AI!");',
  bash: 'echo "Hello, HDM AI!"',
  sql: 'SELECT "Hello, HDM AI!" AS greeting;',
};

export default function CodeScreen() {
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState(STARTERS.python);
  const [stdin, setStdin] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const { colors } = useTheme();
  const { addToast } = useToast();

  const run = async () => {
    if (!code.trim()) return addToast('Write some code first', 'error');
    setLoading(true);
    setOutput('Running...');
    try {
      const { data } = await api.post('/general/execute', { language, code, stdin });
      setOutput(data.data?.stdout || data.data?.stderr || 'No output');
    } catch (err) {
      setOutput(`Error: ${err.response?.data?.detail || err.message}`);
    }
    setLoading(false);
  };

  const clear = () => {
    setCode(STARTERS[language] || '');
    setStdin('');
    setOutput('');
  };

  const copy = () => {
    addToast('Copied!', 'success');
  };

  return (
    <ScreenWrapper safe style={{ backgroundColor: colors.bg }}>
      {/* Language selector */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={[styles.langBar, { borderBottomColor: colors.border }]} contentContainerStyle={styles.langContent}>
        {LANGUAGES.map(l => (
          <TouchableOpacity key={l.value} onPress={() => { setLanguage(l.value); setCode(STARTERS[l.value] || ''); }}
            style={[styles.langChip, { backgroundColor: language === l.value ? colors.accent : colors.bgTertiary }]}>
            <Text style={[styles.langText, { color: language === l.value ? '#000' : colors.textSecondary }]}>{l.label}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Code editor */}
      <TextInput
        value={code}
        onChangeText={setCode}
        style={[styles.editor, { backgroundColor: colors.bgSecondary, borderColor: colors.border, color: colors.text }]}
        multiline
        textAlignVertical="top"
        placeholder="Write your code here..."
        placeholderTextColor={colors.textMuted}
        autoCapitalize="none"
        autoCorrect={false}
        spellCheck={false}
        fontFamily="monospace"
      />

      {/* Actions */}
      <View style={styles.actions}>
        <Button size="sm" onPress={run} loading={loading}><Play size={16} color="#000" /> Run</Button>
        <Button size="sm" variant="secondary" onPress={clear}><Trash2 size={16} color={colors.textSecondary} /> Clear</Button>
        <Button size="sm" variant="ghost" onPress={copy}><Copy size={16} color={colors.textSecondary} /> Copy</Button>
      </View>

      {/* Stdin */}
      <TextInput
        value={stdin}
        onChangeText={setStdin}
        placeholder="Input (stdin)..."
        placeholderTextColor={colors.textMuted}
        style={[styles.stdin, { backgroundColor: colors.bgTertiary, borderColor: colors.border, color: colors.text }]}
      />

      {/* Output */}
      <ScrollView style={[styles.output, { backgroundColor: colors.bgSecondary, borderColor: colors.border }]}>
        <Text style={[styles.outputText, { color: output.includes('Error') ? colors.danger : colors.success }]}>
          {output || 'Output will appear here...'}
        </Text>
      </ScrollView>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  langBar: { borderBottomWidth: 1, maxHeight: 44 },
  langContent: { paddingHorizontal: 10, gap: 8, alignItems: 'center' },
  langChip: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 8 },
  langText: { fontSize: 12, fontWeight: '600' },
  editor: { flex: 1, margin: 10, borderRadius: 12, borderWidth: 1, padding: 12, fontSize: 13, fontFamily: 'monospace', lineHeight: 20 },
  actions: { flexDirection: 'row', gap: 10, paddingHorizontal: 10, marginBottom: 8 },
  stdin: { marginHorizontal: 10, borderRadius: 10, borderWidth: 1, paddingHorizontal: 12, paddingVertical: 8, fontSize: 12, fontFamily: 'monospace', marginBottom: 8 },
  output: { flex: 1, marginHorizontal: 10, marginBottom: 10, borderRadius: 12, borderWidth: 1, padding: 12 },
  outputText: { fontSize: 12, fontFamily: 'monospace', lineHeight: 18 },
});