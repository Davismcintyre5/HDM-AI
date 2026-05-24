// ====================================================================================================
// client/src/pages/Image.jsx
// ====================================================================================================
import { useState, useRef } from 'react'
import { Image, Sparkles, Copy, Check, RefreshCw, Sliders, Grid, List, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../api/axios'

const STYLES = [
  { value: 'realistic', label: 'Realistic', icon: '📸' },
  { value: 'cartoon', label: 'Cartoon', icon: '🎨' },
  { value: 'anime', label: 'Anime', icon: '🌸' },
  { value: 'oil-painting', label: 'Oil Painting', icon: '🖼️' },
  { value: 'watercolor', label: 'Watercolor', icon: '🎨' },
  { value: 'sketch', label: 'Sketch', icon: '✏️' },
  { value: '3d-render', label: '3D Render', icon: '🎮' },
  { value: 'pixel-art', label: 'Pixel Art', icon: '👾' },
]

const SIZES = ['512x512', '1024x1024', '1792x1024', '1024x1792']

export default function ImagePage() {
  const [prompt, setPrompt] = useState('')
  const [style, setStyle] = useState('realistic')
  const [size, setSize] = useState('1024x1024')
  const [numImages, setNumImages] = useState(2)
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState('grid')
  const [copiedId, setCopiedId] = useState(null)
  const [history, setHistory] = useState([])
  const promptRef = useRef(null)

  const generate = async (e) => {
    e.preventDefault()
    if (!prompt.trim() || loading) return
    setLoading(true)
    setImages([])

    try {
      const { data } = await api.post('/general/image', { prompt, style, size, num_images: numImages })
      const generated = (data.data.images || []).map((img, i) => ({
        id: Date.now() + i,
        base64: img.base64 || null,
        description: img.description || null,
        prompt: data.data.revised_prompt || prompt,
        note: img.note || data.data.note || '',
        style,
      }))
      setImages(generated)
      setHistory(prev => [...generated, ...prev].slice(0, 20))
      
      if (generated[0]?.description && !generated[0]?.base64) {
        toast.success('Image description generated!')
      } else {
        toast.success(`Generated ${generated.length} image(s)!`)
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Generation failed')
    }
    setLoading(false)
  }

  const copyDescription = (text) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied!')
  }

  const copyPrompt = (text) => {
    navigator.clipboard.writeText(text)
    toast.success('Prompt copied!')
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-dark-800 px-6 py-4">
        <h1 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
          <div className="w-8 h-8 bg-gradient-to-br from-pink-500/20 to-purple-500/20 rounded-lg flex items-center justify-center">
            <Image size={18} className="text-pink-400" />
          </div>
          Image Studio
        </h1>

        <form onSubmit={generate} className="space-y-3">
          <div className="flex gap-2">
            <input
              ref={promptRef}
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder="Describe the image you want..."
              className="input-field flex-1 text-sm"
              autoFocus
            />
            <button type="submit" disabled={loading || !prompt.trim()} className="btn-primary flex items-center gap-2 px-6">
              {loading ? <RefreshCw size={18} className="animate-spin" /> : <Sparkles size={18} />}
              Generate
            </button>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-1.5">
              <Sliders size={14} className="text-dark-400" />
              <select value={style} onChange={e => setStyle(e.target.value)} className="bg-dark-800 border border-dark-600 rounded-lg px-2.5 py-1.5 text-xs text-dark-200 outline-none focus:border-primary-500">
                {STYLES.map(s => <option key={s.value} value={s.value}>{s.icon} {s.label}</option>)}
              </select>
            </div>
            <select value={size} onChange={e => setSize(e.target.value)} className="bg-dark-800 border border-dark-600 rounded-lg px-2.5 py-1.5 text-xs text-dark-200 outline-none">
              {SIZES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <div className="flex items-center gap-2">
              <span className="text-xs text-dark-400">Images:</span>
              {[1, 2, 3, 4].map(n => (
                <button key={n} type="button" onClick={() => setNumImages(n)} className={`w-7 h-7 rounded-lg text-xs font-medium transition-all ${numImages === n ? 'bg-primary-600 text-white' : 'bg-dark-800 text-dark-400 hover:text-white'}`}>
                  {n}
                </button>
              ))}
            </div>
            {images.length > 0 && (
              <div className="flex items-center gap-1 ml-auto">
                <button onClick={() => setViewMode('grid')} className={`p-1.5 rounded ${viewMode === 'grid' ? 'bg-dark-700 text-white' : 'text-dark-400 hover:text-white'}`}><Grid size={14} /></button>
                <button onClick={() => setViewMode('single')} className={`p-1.5 rounded ${viewMode === 'single' ? 'bg-dark-700 text-white' : 'text-dark-400 hover:text-white'}`}><List size={14} /></button>
              </div>
            )}
          </div>
        </form>
      </div>

      {/* Gallery */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading && (
          <div className="h-64 flex items-center justify-center">
            <div className="text-center">
              <RefreshCw size={32} className="text-primary-400 animate-spin mx-auto mb-3" />
              <p className="text-dark-400 text-sm">Generating...</p>
            </div>
          </div>
        )}

        {!loading && images.length === 0 && history.length === 0 && (
          <div className="h-[50vh] flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 bg-gradient-to-br from-pink-500/10 to-purple-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Image size={28} className="text-pink-400" />
              </div>
              <h3 className="text-white font-medium mb-2">Create Stunning Images</h3>
              <p className="text-dark-400 text-sm">Describe what you want, choose a style, and let AI bring it to life.</p>
              <p className="text-dark-500 text-xs mt-2">Note: Image generation returns text descriptions on the free tier.</p>
              <div className="flex flex-wrap gap-2 justify-center mt-4">
                {['Sunset over mountains', 'Futuristic city', 'Cute robot', 'Abstract art'].map(s => (
                  <button key={s} onClick={() => setPrompt(s)} className="px-3 py-1.5 bg-dark-800 border border-dark-700 rounded-full text-xs text-dark-300 hover:text-white hover:border-dark-500 transition-all">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Image grid */}
        <div className={`${viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 gap-4' : 'space-y-4'} max-w-5xl mx-auto`}>
          {images.map(img => (
            <div key={img.id} className="group bg-dark-800 border border-dark-700 rounded-xl overflow-hidden hover:border-dark-500 transition-all">
              {/* Base64 image */}
              {img.base64 && (
                <img
                  src={`data:image/png;base64,${img.base64}`}
                  alt={img.prompt}
                  className="w-full object-cover"
                  style={{ maxHeight: viewMode === 'single' ? '60vh' : '300px' }}
                />
              )}

              {/* Text description card */}
              {!img.base64 && img.description && (
                <div className="p-5 bg-gradient-to-br from-dark-800 via-dark-850 to-dark-900 min-h-[200px] flex flex-col justify-center border-b border-dark-700">
                  <div className="flex items-start gap-3 mb-3">
                    <div className="w-8 h-8 bg-pink-500/10 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Sparkles size={14} className="text-pink-400" />
                    </div>
                    <div>
                      <p className="text-sm text-dark-200 leading-relaxed italic">"{img.description}"</p>
                    </div>
                  </div>
                  {img.note && (
                    <p className="text-[10px] text-dark-500 mt-auto ml-11">{img.note}</p>
                  )}
                </div>
              )}

              {/* Card footer */}
              <div className="p-3">
                <p className="text-xs text-dark-400 line-clamp-2 mb-2">{img.prompt}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="px-1.5 py-0.5 bg-dark-700 rounded text-[10px] text-dark-400">{img.style}</span>
                    <span className="px-1.5 py-0.5 bg-dark-700 rounded text-[10px] text-dark-400">{size}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    {img.description && (
                      <button onClick={() => copyDescription(img.description)} className="text-[10px] text-primary-400 hover:text-primary-300">
                        Copy description
                      </button>
                    )}
                    <button onClick={() => copyPrompt(img.prompt)} className="text-[10px] text-dark-500 hover:text-dark-300 ml-2">
                      Copy prompt
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* History */}
        {history.length > images.length && images.length > 0 && (
          <div className="mt-8 max-w-5xl mx-auto">
            <h3 className="text-sm font-medium text-dark-300 mb-3 flex items-center gap-2">
              <RefreshCw size={14} /> Recent
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {history.slice(images.length).slice(0, 4).map(img => (
                <div
                  key={img.id}
                  className="bg-dark-800 border border-dark-700 rounded-lg overflow-hidden cursor-pointer hover:border-dark-500 transition-all"
                  onClick={() => { setPrompt(img.prompt); setStyle(img.style); promptRef.current?.scrollIntoView({ behavior: 'smooth' }) }}
                >
                  {img.base64 ? (
                    <img src={`data:image/png;base64,${img.base64}`} alt={img.prompt} className="w-full h-24 object-cover" />
                  ) : (
                    <div className="w-full h-24 bg-gradient-to-br from-dark-800 to-dark-900 flex items-center justify-center p-2">
                      <FileText size={20} className="text-dark-600" />
                    </div>
                  )}
                  <p className="p-2 text-[10px] text-dark-500 truncate">{img.prompt}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}