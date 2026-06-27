import { useState } from 'react';
import { Image, Sparkles, RefreshCw, Grid, List, FileText } from 'lucide-react';
import api from '../api/axios';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { useToast } from '../components/ui/Toast';

const STYLES = [
  { value: 'realistic', label: 'Realistic', icon: '📸' },
  { value: 'cartoon', label: 'Cartoon', icon: '🎨' },
  { value: 'anime', label: 'Anime', icon: '🌸' },
  { value: 'oil-painting', label: 'Oil Painting', icon: '🖼️' },
  { value: 'watercolor', label: 'Watercolor', icon: '🎨' },
  { value: 'sketch', label: 'Sketch', icon: '✏️' },
  { value: '3d-render', label: '3D Render', icon: '🎮' },
  { value: 'pixel-art', label: 'Pixel Art', icon: '👾' },
];

const SIZES = ['512x512', '1024x1024', '1792x1024', '1024x1792'];

export default function ImagePage() {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('realistic');
  const [size, setSize] = useState('1024x1024');
  const [numImages, setNumImages] = useState(2);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState('grid');
  const [history, setHistory] = useState([]);
  const { addToast } = useToast();

  const generate = async (e) => {
    e.preventDefault();
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
        note: data.data.note || '',
        style,
      }));
      setImages(generated);
      setHistory(prev => [...generated, ...prev].slice(0, 20));
      addToast(generated[0]?.description ? 'Description generated' : `Generated ${generated.length} image(s)`, 'success');
    } catch {
      addToast('Generation failed', 'error');
    }
    setLoading(false);
  };

  return (
    <div className="h-full flex flex-col max-w-5xl mx-auto">
      <div className="flex-shrink-0 border-b border-border px-6 py-4">
        <h1 className="text-lg font-semibold text-text-primary flex items-center gap-2 mb-4">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center"><Image size={18} className="text-primary" /></div>
          Image Studio
        </h1>
        <form onSubmit={generate} className="space-y-3">
          <div className="flex gap-2">
            <input value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Describe the image you want..." className="flex-1 bg-bg-tertiary border border-border rounded-xl px-4 py-2.5 text-text-primary placeholder-text-muted text-sm focus:outline-none focus:border-primary" />
            <Button type="submit" disabled={loading || !prompt.trim()} loading={loading} size="sm">{loading ? 'Generating' : 'Generate'}</Button>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            <select value={style} onChange={e => setStyle(e.target.value)} className="bg-bg-tertiary border border-border rounded-lg px-2.5 py-1.5 text-xs text-text-secondary outline-none focus:border-primary">
              {STYLES.map(s => <option key={s.value} value={s.value}>{s.icon} {s.label}</option>)}
            </select>
            <select value={size} onChange={e => setSize(e.target.value)} className="bg-bg-tertiary border border-border rounded-lg px-2.5 py-1.5 text-xs text-text-secondary outline-none">
              {SIZES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <div className="flex items-center gap-2">
              <span className="text-xs text-text-muted">Images:</span>
              {[1, 2, 3, 4].map(n => (
                <button key={n} type="button" onClick={() => setNumImages(n)} className={`w-7 h-7 rounded-lg text-xs font-medium transition-all ${numImages === n ? 'bg-primary text-black' : 'bg-bg-tertiary text-text-secondary hover:text-text-primary'}`}>{n}</button>
              ))}
            </div>
            {images.length > 0 && (
              <div className="flex items-center gap-1 ml-auto">
                <button onClick={() => setViewMode('grid')} className={`p-1.5 rounded ${viewMode === 'grid' ? 'bg-bg-tertiary text-text-primary' : 'text-text-muted hover:text-text-primary'}`}><Grid size={14} /></button>
                <button onClick={() => setViewMode('single')} className={`p-1.5 rounded ${viewMode === 'single' ? 'bg-bg-tertiary text-text-primary' : 'text-text-muted hover:text-text-primary'}`}><List size={14} /></button>
              </div>
            )}
          </div>
        </form>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {loading && <div className="h-64 flex items-center justify-center"><RefreshCw size={32} className="text-primary animate-spin" /></div>}

        {!loading && images.length === 0 && history.length === 0 && (
          <div className="h-[50vh] flex items-center justify-center text-center">
            <div>
              <Image size={48} className="text-text-muted mx-auto mb-4 opacity-30" />
              <h3 className="text-text-primary font-medium mb-2">Create Stunning Images</h3>
              <p className="text-text-muted text-sm mb-4">Describe what you want and let AI bring it to life.</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {['Sunset over mountains', 'Futuristic city', 'Cute robot', 'Abstract art'].map(s => (
                  <button key={s} onClick={() => setPrompt(s)} className="px-3 py-1.5 bg-bg-tertiary border border-border rounded-full text-xs text-text-secondary hover:text-text-primary hover:border-text-muted transition-all">{s}</button>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className={`${viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 gap-4' : 'space-y-4'}`}>
          {images.map(img => (
            <Card key={img.id} className="overflow-hidden">
              {img.base64 && <img src={`data:image/png;base64,${img.base64}`} alt={img.prompt} className="w-full object-cover" style={{ maxHeight: viewMode === 'single' ? '60vh' : '300px' }} />}
              {!img.base64 && img.description && (
                <div className="p-5 min-h-[200px] flex flex-col justify-center">
                  <div className="flex items-start gap-3 mb-3">
                    <Sparkles size={14} className="text-primary mt-0.5" />
                    <p className="text-sm text-text-secondary italic">"{img.description}"</p>
                  </div>
                  {img.note && <p className="text-[10px] text-text-muted">{img.note}</p>}
                </div>
              )}
              <div className="p-3 border-t border-border">
                <p className="text-xs text-text-muted line-clamp-2 mb-2">{img.prompt}</p>
                <div className="flex items-center justify-between">
                  <span className="px-1.5 py-0.5 bg-bg-tertiary rounded text-[10px] text-text-muted">{img.style} • {size}</span>
                  <Button variant="ghost" size="sm" onClick={() => { navigator.clipboard.writeText(img.description || img.prompt); addToast('Copied!', 'success'); }}>Copy</Button>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {history.length > images.length && images.length > 0 && (
          <div className="mt-8">
            <h3 className="text-sm font-medium text-text-secondary mb-3">Recent</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {history.slice(images.length, images.length + 4).map(img => (
                <div key={img.id} className="bg-bg-secondary border border-border rounded-lg overflow-hidden cursor-pointer hover:border-text-muted transition-all" onClick={() => { setPrompt(img.prompt); setStyle(img.style); }}>
                  {img.base64 ? <img src={`data:image/png;base64,${img.base64}`} alt="" className="w-full h-24 object-cover" /> : <div className="w-full h-24 bg-bg-tertiary flex items-center justify-center"><FileText size={20} className="text-text-muted opacity-30" /></div>}
                  <p className="p-2 text-[10px] text-text-muted truncate">{img.prompt}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}