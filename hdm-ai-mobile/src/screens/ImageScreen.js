import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, Image, StyleSheet, Dimensions } from 'react-native';
import api from '../api/axios';
import ScreenWrapper from '../components/ui/ScreenWrapper';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../components/ui/Toast';
import { Image as ImageIcon, Sparkles, Grid, List } from 'lucide-react-native';

const STYLES = [
  { value: 'realistic', label: '📸 Realistic' },
  { value: 'cartoon', label: '🎨 Cartoon' },
  { value: 'anime', label: '🌸 Anime' },
  { value: 'oil-painting', label: '🖼️ Oil' },
  { value: 'watercolor', label: '🎨 Water' },
  { value: 'sketch', label: '✏️ Sketch' },
  { value: '3d-render', label: '🎮 3D' },
  { value: 'pixel-art', label: '👾 Pixel' },
];

const SIZES = ['512x512', '1024x1024'];
const { width } = Dimensions.get('window');

export default function ImageScreen() {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('realistic');
  const [size, setSize] = useState('1024x1024');
  const [numImages, setNumImages] = useState(2);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState('grid');
  const { colors } = useTheme();
  const { addToast } = useToast();

  const generate = async () => {
    if (!prompt.trim() || loading) return;
    setLoading(true);
    setImages([]);
    try {
      const { data } = await api.post('/general/image', { prompt, style, size, num_images: numImages });
      const generated = (data.data.images || []).map((img, i) => ({
        id: Date.now() + i,
        base64: img.base64 || null,
        description: img.description || null,
        prompt: data.data.revised_prompt || prompt,
        style,
      }));
      setImages(generated);
      addToast(generated.length ? 'Generated!' : 'No images returned', generated.length ? 'success' : 'info');
    } catch { addToast('Generation failed', 'error'); }
    setLoading(false);
  };

  return (
    <ScreenWrapper safe style={{ backgroundColor: colors.bg }}>
      {/* Input */}
      <View style={[styles.inputArea, { borderBottomColor: colors.border }]}>
        <TextInput
          value={prompt}
          onChangeText={setPrompt}
          placeholder="Describe the image you want..."
          placeholderTextColor={colors.textMuted}
          style={[styles.promptInput, { backgroundColor: colors.bgTertiary, borderColor: colors.border, color: colors.text }]}
        />
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.styleBar} contentContainerStyle={styles.styleContent}>
          {STYLES.map(s => (
            <TouchableOpacity key={s.value} onPress={() => setStyle(s.value)}
              style={[styles.styleChip, { backgroundColor: style === s.value ? colors.accent : colors.bgTertiary }]}>
              <Text style={[styles.styleText, { color: style === s.value ? '#000' : colors.textSecondary }]}>{s.label}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
        <View style={styles.options}>
          <View style={styles.sizeRow}>
            {SIZES.map(s => (
              <TouchableOpacity key={s} onPress={() => setSize(s)}
                style={[styles.sizeChip, { backgroundColor: size === s ? colors.accent : colors.bgTertiary }]}>
                <Text style={[styles.sizeText, { color: size === s ? '#000' : colors.textSecondary }]}>{s}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <View style={styles.numRow}>
            {[1, 2, 3, 4].map(n => (
              <TouchableOpacity key={n} onPress={() => setNumImages(n)}
                style={[styles.numChip, { backgroundColor: numImages === n ? colors.accent : colors.bgTertiary }]}>
                <Text style={[styles.numText, { color: numImages === n ? '#000' : colors.textSecondary }]}>{n}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
        <Button onPress={generate} loading={loading} disabled={!prompt.trim()} style={styles.genBtn}>
          <Sparkles size={16} color="#000" /> Generate
        </Button>
      </View>

      {/* Gallery */}
      <ScrollView style={styles.gallery} contentContainerStyle={styles.galleryContent}>
        {loading ? (
          <View style={styles.loading}><Spinner size="md" /></View>
        ) : images.length === 0 ? (
          <View style={styles.empty}>
            <ImageIcon size={40} color={colors.textMuted} />
            <Text style={[styles.emptyText, { color: colors.textMuted }]}>Describe an image and generate</Text>
          </View>
        ) : (
          <View style={viewMode === 'grid' ? styles.grid : styles.list}>
            {images.map(img => (
              <View key={img.id} style={[styles.imgCard, { backgroundColor: colors.bgSecondary, borderColor: colors.border }]}>
                {img.base64 ? (
                  <Image source={{ uri: `data:image/png;base64,${img.base64}` }} style={styles.imgPreview} resizeMode="cover" />
                ) : img.description ? (
                  <View style={styles.imgDesc}>
                    <Text style={[styles.descText, { color: colors.textSecondary }]}>"{img.description}"</Text>
                  </View>
                ) : null}
                <Text style={[styles.imgPrompt, { color: colors.textMuted }]} numberOfLines={2}>{img.prompt}</Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  inputArea: { padding: 12, borderBottomWidth: 1 },
  promptInput: { borderRadius: 12, borderWidth: 1, paddingHorizontal: 14, paddingVertical: 10, fontSize: 13, marginBottom: 10 },
  styleBar: { maxHeight: 36, marginBottom: 8 },
  styleContent: { gap: 6 },
  styleChip: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8 },
  styleText: { fontSize: 11, fontWeight: '500' },
  options: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 10 },
  sizeRow: { flexDirection: 'row', gap: 6 },
  sizeChip: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8 },
  sizeText: { fontSize: 11, fontWeight: '500' },
  numRow: { flexDirection: 'row', gap: 6 },
  numChip: { width: 28, height: 28, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  numText: { fontSize: 12, fontWeight: '600' },
  genBtn: { alignSelf: 'flex-end' },
  gallery: { flex: 1 },
  galleryContent: { padding: 12, flexGrow: 1 },
  loading: { alignItems: 'center', paddingTop: 60 },
  empty: { alignItems: 'center', paddingTop: 60 },
  emptyText: { fontSize: 13, marginTop: 10 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  list: { gap: 14 },
  imgCard: { borderRadius: 14, borderWidth: 1, overflow: 'hidden', width: (width - 40) / 2 },
  imgPreview: { width: '100%', height: 180 },
  imgDesc: { padding: 14, minHeight: 100, justifyContent: 'center' },
  descText: { fontSize: 12, fontStyle: 'italic', lineHeight: 18 },
  imgPrompt: { fontSize: 10, padding: 10 },
});