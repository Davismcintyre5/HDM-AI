import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';
import api from '../api/axios';
import ScreenWrapper from '../components/ui/ScreenWrapper';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../components/ui/Toast';
import { FileSearch, Smile, Hash, Users, Database, Layers, Copy } from 'lucide-react-native';

const TYPES = [
  { value: 'summary', label: 'Summary', icon: FileSearch, color: '#60a5fa' },
  { value: 'sentiment', label: 'Sentiment', icon: Smile, color: '#facc15' },
  { value: 'keywords', label: 'Keywords', icon: Hash, color: '#4ade80' },
  { value: 'entities', label: 'Entities', icon: Users, color: '#c084fc' },
  { value: 'data', label: 'Data Extraction', icon: Database, color: '#fb923c' },
  { value: 'full', label: 'Full Analysis', icon: Layers, color: '#f472b6' },
];

export default function AnalyzeScreen() {
  const [content, setContent] = useState('');
  const [type, setType] = useState('summary');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const { colors } = useTheme();
  const { addToast } = useToast();

  const analyze = async () => {
    if (!content.trim() || loading) return;
    setLoading(true);
    setResult(null);
    try {
      const { data } = await api.post('/general/analyze', { content, analysis_type: type });
      setResult(data.data);
    } catch {
      addToast('Analysis failed', 'error');
    }
    setLoading(false);
  };

  return (
    <ScreenWrapper safe style={{ backgroundColor: colors.bg }}>
      {/* Input */}
      <View style={[styles.inputArea, { borderBottomColor: colors.border }]}>
        <TextInput
          value={content}
          onChangeText={setContent}
          placeholder="Paste text to analyze..."
          placeholderTextColor={colors.textMuted}
          style={[styles.textArea, { backgroundColor: colors.bgTertiary, borderColor: colors.border, color: colors.text }]}
          multiline
          textAlignVertical="top"
        />
        <Button onPress={analyze} loading={loading} disabled={!content.trim()} style={styles.analyzeBtn}>Analyze</Button>
      </View>

      {/* Type selector */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.typeBar} contentContainerStyle={styles.typeContent}>
        {TYPES.map(t => (
          <TouchableOpacity key={t.value} onPress={() => { setType(t.value); setResult(null); }}
            style={[styles.typeChip, { backgroundColor: type === t.value ? t.color + '20' : colors.bgTertiary, borderColor: type === t.value ? t.color : colors.border }]}>
            <t.icon size={14} color={type === t.value ? t.color : colors.textMuted} />
            <Text style={[styles.typeText, { color: type === t.value ? t.color : colors.textSecondary }]}>{t.label}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Result */}
      <ScrollView style={styles.resultArea} contentContainerStyle={styles.resultContent}>
        {loading ? (
          <View style={styles.loading}><Spinner size="md" /><Text style={[styles.loadingText, { color: colors.textMuted }]}>Analyzing...</Text></View>
        ) : result ? (
          <View style={[styles.resultCard, { backgroundColor: colors.bgSecondary, borderColor: colors.border }]}>
            <Text style={[styles.resultTitle, { color: colors.text }]}>
              {TYPES.find(t => t.value === type)?.label} Results
            </Text>

            {type === 'sentiment' && result.result && (
              <View style={styles.sentimentRow}>
                <Text style={{ fontSize: 40 }}>{result.result.score > 0 ? '😊' : result.result.score < 0 ? '😞' : '😐'}</Text>
                <View>
                  <Text style={[styles.sentimentLabel, { color: colors.text }]}>{result.result.sentiment}</Text>
                  <Text style={[styles.sentimentScore, { color: colors.textSecondary }]}>Score: {result.result.score}</Text>
                </View>
              </View>
            )}

            {type === 'keywords' && result.result && (
              <View style={styles.tagRow}>
                {(Array.isArray(result.result) ? result.result : []).map((kw, i) => (
                  <View key={i} style={[styles.tag, { backgroundColor: colors.bgTertiary, borderColor: colors.border }]}>
                    <Text style={[styles.tagText, { color: colors.textSecondary }]}>#{kw}</Text>
                  </View>
                ))}
              </View>
            )}

            {type === 'entities' && result.result && (
              <View>
                {(Array.isArray(result.result) ? result.result : []).map((e, i) => (
                  <View key={i} style={[styles.entityRow, { borderBottomColor: colors.border }]}>
                    <Text style={[styles.entityName, { color: colors.text }]}>{e.name}</Text>
                    <Text style={[styles.entityType, { color: colors.textMuted }]}>{e.type}</Text>
                  </View>
                ))}
              </View>
            )}

            {!['sentiment', 'keywords', 'entities'].includes(type) && (
              <Text style={[styles.resultText, { color: colors.textSecondary }]}>
                {typeof result.result === 'string' ? result.result : JSON.stringify(result.result, null, 2)}
              </Text>
            )}
          </View>
        ) : (
          <View style={styles.empty}>
            <FileSearch size={36} color={colors.textMuted} />
            <Text style={[styles.emptyText, { color: colors.textMuted }]}>Select a type and paste content to analyze</Text>
          </View>
        )}
      </ScrollView>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  inputArea: { padding: 12, borderBottomWidth: 1 },
  textArea: { height: 100, borderRadius: 12, borderWidth: 1, padding: 12, fontSize: 13, lineHeight: 20, marginBottom: 10 },
  analyzeBtn: { alignSelf: 'flex-end' },
  typeBar: { maxHeight: 48, borderBottomWidth: 0 },
  typeContent: { paddingHorizontal: 10, gap: 8, alignItems: 'center' },
  typeChip: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 12, paddingVertical: 8, borderRadius: 10, borderWidth: 1 },
  typeText: { fontSize: 12, fontWeight: '600' },
  resultArea: { flex: 1 },
  resultContent: { padding: 12, flexGrow: 1 },
  loading: { alignItems: 'center', paddingTop: 40, gap: 10 },
  loadingText: { fontSize: 13 },
  resultCard: { borderRadius: 14, borderWidth: 1, padding: 16 },
  resultTitle: { fontSize: 15, fontWeight: '600', marginBottom: 12 },
  sentimentRow: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  sentimentLabel: { fontSize: 16, fontWeight: '600', textTransform: 'capitalize' },
  sentimentScore: { fontSize: 13 },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  tag: { paddingHorizontal: 10, paddingVertical: 5, borderRadius: 100, borderWidth: 1 },
  tagText: { fontSize: 12 },
  entityRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10, borderBottomWidth: 0.5 },
  entityName: { fontSize: 13, fontWeight: '500' },
  entityType: { fontSize: 11, textTransform: 'capitalize' },
  resultText: { fontSize: 12, lineHeight: 20 },
  empty: { alignItems: 'center', paddingTop: 50 },
  emptyText: { fontSize: 13, marginTop: 10 },
});