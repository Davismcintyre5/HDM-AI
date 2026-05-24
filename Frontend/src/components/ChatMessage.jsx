// ====================================================================================================
// client/src/components/ChatMessage.jsx — FINAL COMPLETE
// Smart code parsing, exact filename download, HTML run preview, 50+ languages
// ====================================================================================================
import { useState } from 'react'
import { Bot, Download, Copy, Check } from 'lucide-react'
import toast from 'react-hot-toast'

// ================================================================================================
// LANGUAGE MAP
// ================================================================================================
const LANG_MAP = {
  js: 'JavaScript', javascript: 'JavaScript',
  jsx: 'React JSX', 'jsx': 'React JSX',
  ts: 'TypeScript', typescript: 'TypeScript',
  tsx: 'React TSX', 'tsx': 'React TSX',
  mjs: 'ES Module', cjs: 'CommonJS',
  py: 'Python', python: 'Python', ipynb: 'Jupyter Notebook',
  html: 'HTML', htm: 'HTML',
  css: 'CSS', scss: 'SCSS', sass: 'Sass', less: 'Less',
  vue: 'Vue SFC', svelte: 'Svelte', astro: 'Astro',
  java: 'Java', go: 'Go', rust: 'Rust', rs: 'Rust',
  php: 'PHP', rb: 'Ruby', ruby: 'Ruby',
  pl: 'Perl', perl: 'Perl', ex: 'Elixir', exs: 'Elixir Script',
  bash: 'Bash', sh: 'Bash', shell: 'Shell', zsh: 'Zsh',
  ps1: 'PowerShell', powershell: 'PowerShell', pwsh: 'PowerShell',
  bat: 'Batch', cmd: 'CMD', batch: 'Batch', fish: 'Fish',
  json: 'JSON', jsonc: 'JSONC',
  yaml: 'YAML', yml: 'YAML', xml: 'XML', svg: 'SVG',
  toml: 'TOML', ini: 'INI', cfg: 'Config', conf: 'Config',
  env: 'Env File', dotenv: 'Env', properties: 'Properties',
  sql: 'SQL', pgsql: 'PostgreSQL', mysql: 'MySQL',
  graphql: 'GraphQL', gql: 'GraphQL', prisma: 'Prisma Schema',
  md: 'Markdown', markdown: 'Markdown', mdx: 'MDX',
  txt: 'Plain Text', text: 'Plain Text', rst: 'reStructuredText',
  c: 'C', cpp: 'C++', 'c++': 'C++', cxx: 'C++',
  csharp: 'C#', cs: 'C#', h: 'C Header', hpp: 'C++ Header',
  swift: 'Swift', kt: 'Kotlin', kotlin: 'Kotlin',
  dart: 'Dart', scala: 'Scala',
  r: 'R', lua: 'Lua', zig: 'Zig', nim: 'Nim',
  dockerfile: 'Dockerfile', docker: 'Dockerfile',
  makefile: 'Makefile', make: 'Makefile', nix: 'Nix',
  lock: 'Lock File',
}

const EXT_MAP = {
  javascript: '.js', js: '.js',
  'react jsx': '.jsx', jsx: '.jsx',
  typescript: '.ts', ts: '.ts',
  'react tsx': '.tsx', tsx: '.tsx',
  'es module': '.mjs', 'commonjs': '.cjs',
  python: '.py', 'jupyter notebook': '.ipynb',
  html: '.html', css: '.css', scss: '.scss', sass: '.sass', less: '.less',
  'vue sfc': '.vue', svelte: '.svelte', astro: '.astro',
  java: '.java', go: '.go', rust: '.rs', php: '.php', ruby: '.rb',
  perl: '.pl', elixir: '.ex', 'elixir script': '.exs',
  bash: '.sh', shell: '.sh', zsh: '.sh',
  powershell: '.ps1', pwsh: '.ps1',
  batch: '.bat', cmd: '.bat', fish: '.fish',
  json: '.json', jsonc: '.jsonc',
  yaml: '.yml', yml: '.yml', xml: '.xml', svg: '.svg',
  toml: '.toml', ini: '.ini', config: '.cfg', conf: '.cfg',
  'env file': '.env', env: '.env', properties: '.properties',
  sql: '.sql', postgresql: '.sql', mysql: '.sql',
  graphql: '.graphql', gql: '.graphql', 'prisma schema': '.prisma',
  markdown: '.md', md: '.md', mdx: '.mdx',
  'plain text': '.txt', txt: '.txt', restructuredtext: '.rst',
  c: '.c', 'c++': '.cpp', cpp: '.cpp', 'c#': '.cs', cs: '.cs',
  'c header': '.h', 'c++ header': '.hpp',
  swift: '.swift', kotlin: '.kt', dart: '.dart', scala: '.scala',
  r: '.r', lua: '.lua', zig: '.zig', nim: '.nim',
  dockerfile: '.dockerfile', makefile: '.makefile', nix: '.nix',
  'lock file': '.lock',
}

const COLOR_MAP = {
  javascript: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  'react jsx': 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  typescript: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'react tsx': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  python: 'bg-green-500/20 text-green-400 border-green-500/30',
  html: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  css: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  scss: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
  java: 'bg-red-500/20 text-red-400 border-red-500/30',
  go: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  rust: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  bash: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  powershell: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  batch: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  json: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  sql: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  markdown: 'bg-primary-500/20 text-primary-400 border-primary-500/30',
  'plain text': 'bg-dark-500/20 text-dark-400 border-dark-500/30',
  c: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'c++': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  'c#': 'bg-green-500/20 text-green-400 border-green-500/30',
}

function getLanguage(fence) {
  const raw = fence?.trim().toLowerCase() || ''
  return LANG_MAP[raw] || (raw ? raw.charAt(0).toUpperCase() + raw.slice(1) : 'Code')
}

function getExtension(lang) {
  const l = lang.toLowerCase()
  if (EXT_MAP[l]) return EXT_MAP[l]
  if (l.includes('python')) return '.py'
  if (l.includes('javascript') || l.includes('js')) return '.js'
  if (l.includes('typescript') || l.includes('ts')) return '.ts'
  if (l.includes('html')) return '.html'
  if (l.includes('css')) return '.css'
  if (l.includes('sql')) return '.sql'
  if (l.includes('json')) return '.json'
  if (l.includes('markdown') || l.includes('md')) return '.md'
  if (l.includes('bash') || l.includes('shell') || l.includes('sh')) return '.sh'
  if (l.includes('powershell') || l.includes('ps')) return '.ps1'
  if (l.includes('cmd') || l.includes('batch')) return '.bat'
  if (l.includes('text') || l.includes('txt')) return '.txt'
  if (l.includes('yaml') || l.includes('yml')) return '.yml'
  if (l.includes('xml')) return '.xml'
  if (l.includes('java')) return '.java'
  if (l.includes('go')) return '.go'
  if (l.includes('rust')) return '.rs'
  if (l.includes('c++') || l.includes('cpp')) return '.cpp'
  if (l.includes('c#')) return '.cs'
  if (l.includes('ruby')) return '.rb'
  if (l.includes('php')) return '.php'
  if (l.includes('swift')) return '.swift'
  if (l.includes('kotlin')) return '.kt'
  if (l.includes('dart')) return '.dart'
  if (l.includes('docker')) return '.dockerfile'
  return '.txt'
}

function getColor(lang) {
  const l = lang.toLowerCase()
  if (COLOR_MAP[l]) return COLOR_MAP[l]
  if (l.includes('python')) return 'bg-green-500/20 text-green-400 border-green-500/30'
  if (l.includes('javascript') || l.includes('js')) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
  if (l.includes('typescript') || l.includes('ts')) return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
  if (l.includes('react')) return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30'
  if (l.includes('html')) return 'bg-orange-500/20 text-orange-400 border-orange-500/30'
  if (l.includes('css') || l.includes('scss')) return 'bg-pink-500/20 text-pink-400 border-pink-500/30'
  if (l.includes('sql')) return 'bg-purple-500/20 text-purple-400 border-purple-500/30'
  if (l.includes('bash') || l.includes('shell') || l.includes('cmd') || l.includes('powershell')) return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  if (l.includes('json') || l.includes('yaml') || l.includes('xml') || l.includes('toml')) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
  if (l.includes('java')) return 'bg-red-500/20 text-red-400 border-red-500/30'
  if (l.includes('go')) return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30'
  if (l.includes('rust')) return 'bg-orange-500/20 text-orange-400 border-orange-500/30'
  if (l.includes('c++') || l.includes('cpp')) return 'bg-purple-500/20 text-purple-400 border-purple-500/30'
  if (l.includes('c#') || l.includes('csharp')) return 'bg-green-500/20 text-green-400 border-green-500/30'
  return 'bg-primary-500/20 text-primary-400 border-primary-500/30'
}

// ================================================================================================
// DOWNLOAD
// ================================================================================================
const downloadCode = (text, filename) => {
  const blob = new Blob([text], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

// ================================================================================================
// MESSAGE PARSER — Extracts code blocks with filename detection
// ================================================================================================
function parseMessageContent(text) {
  if (!text) return [{ type: 'text', content: '' }]
  const segments = []
  const regex = /```(\S*)\n?([\s\S]*?)```/g
  let lastIndex = 0
  let match

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      const textBefore = text.slice(lastIndex, match.index).trim()
      if (textBefore) segments.push({ type: 'text', content: textBefore })
    }

    const fenceLang = match[1]?.trim() || ''
    const beforeText = text.slice(Math.max(0, match.index - 200), match.index)

    let filename = null
    let filenameExt = null

    const boldFileMatch = beforeText.match(/\*\*(\w+\.\w+)\*\*/)
    if (boldFileMatch) {
      filename = boldFileMatch[1]
      filenameExt = filename.split('.').pop()?.toLowerCase()
    }

    if (!filename) {
      const lineFileMatch = beforeText.match(/(\w+\.\w+)\s*$/)
      if (lineFileMatch) {
        filename = lineFileMatch[1]
        filenameExt = filename.split('.').pop()?.toLowerCase()
      }
    }

    if (!filename) {
      const codeFileMatch = beforeText.match(/`(\w+\.\w+)`/)
      if (codeFileMatch) {
        filename = codeFileMatch[1]
        filenameExt = filename.split('.').pop()?.toLowerCase()
      }
    }

    let finalLang, finalExt
    if (filenameExt && LANG_MAP[filenameExt]) {
      finalLang = LANG_MAP[filenameExt]
      finalExt = `.${filenameExt}`
    } else if (fenceLang && LANG_MAP[fenceLang.toLowerCase()]) {
      finalLang = LANG_MAP[fenceLang.toLowerCase()]
      finalExt = EXT_MAP[finalLang.toLowerCase()] || '.txt'
    } else if (fenceLang) {
      finalLang = fenceLang.charAt(0).toUpperCase() + fenceLang.slice(1)
      finalExt = '.txt'
    } else {
      finalLang = 'Code'
      finalExt = '.txt'
    }

    const code = match[2].trim()
    if (code) {
      segments.push({
        type: 'code',
        language: finalLang,
        extension: finalExt,
        filename: filename || `code${finalExt}`,
        color: getColor(finalLang),
        content: code,
      })
    }

    lastIndex = match.index + match[0].length
  }

  if (lastIndex < text.length) {
    const textAfter = text.slice(lastIndex).trim()
    if (textAfter) segments.push({ type: 'text', content: textAfter })
  }

  if (segments.length === 0) {
    segments.push({ type: 'text', content: text.trim() })
  }

  return segments
}

// ================================================================================================
// TEXT SEGMENT
// ================================================================================================
function TextSegment({ content }) {
  const processed = content
    .replace(/^### (.*$)/gim, '<h4 class="text-white font-semibold text-sm mt-3 mb-1">$1</h4>')
    .replace(/^## (.*$)/gim, '<h3 class="text-white font-semibold text-base mt-4 mb-2">$1</h3>')
    .replace(/^# (.*$)/gim, '<h2 class="text-white font-bold text-lg mt-4 mb-2">$1</h2>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^\- (.*$)/gim, '<li class="ml-4 list-disc text-dark-300">$1</li>')
    .replace(/^\* (.*$)/gim, '<li class="ml-4 list-disc text-dark-300">$1</li>')
    .replace(/\n/g, '<br/>')

  return (
    <div
      className="text-sm leading-relaxed text-dark-200"
      dangerouslySetInnerHTML={{ __html: processed }}
    />
  )
}

// ================================================================================================
// CODE SEGMENT — With Run button for HTML
// ================================================================================================
function CodeSegment({ language, extension, filename, color, content }) {
  const [copied, setCopied] = useState(false)
  const [showPreview, setShowPreview] = useState(false)

  const canRun = ['html', 'htm'].includes(extension?.toLowerCase().replace('.', ''))

  return (
    <div className="bg-dark-800 border border-dark-700/50 rounded-xl overflow-hidden my-2">
      {/* Top bar */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-dark-900/50 border-b border-dark-700/30">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 rounded text-[10px] font-medium border ${color}`}>
            {language}
          </span>
          <span className="text-[10px] text-dark-500 font-mono">{filename}</span>
        </div>
        <div className="flex items-center gap-1">
          {/* Copy */}
          <button
            onClick={() => {
              navigator.clipboard.writeText(content)
              setCopied(true)
              setTimeout(() => setCopied(false), 2000)
              toast.success('Copied')
            }}
            className="p-1 text-dark-500 hover:text-white rounded transition-colors"
            title="Copy code"
          >
            {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
          </button>
          {/* Run (HTML only) */}
          {canRun && (
            <button
              onClick={() => setShowPreview(!showPreview)}
              className={`p-1 rounded transition-colors ${showPreview ? 'text-green-400 bg-green-500/10' : 'text-dark-500 hover:text-green-400'}`}
              title={showPreview ? 'Hide preview' : 'Run HTML'}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="5 3 19 12 5 21 5 3"/>
              </svg>
            </button>
          )}
          {/* Download */}
          <button
            onClick={() => downloadCode(content, filename)}
            className="p-1 text-dark-500 hover:text-white rounded transition-colors"
            title={`Download ${filename}`}
          >
            <Download size={14} />
          </button>
        </div>
      </div>
      {/* Code */}
      <pre className="p-4 text-xs font-mono text-dark-200 overflow-x-auto whitespace-pre-wrap leading-relaxed">
        {content}
      </pre>
      {/* HTML Preview */}
      {showPreview && canRun && (
        <div className="border-t border-dark-700/30">
          <iframe
            srcDoc={content}
            className="w-full h-64 bg-white"
            sandbox="allow-scripts allow-same-origin"
            title="HTML Preview"
          />
        </div>
      )}
    </div>
  )
}

// ================================================================================================
// CHAT MESSAGE COMPONENT
// ================================================================================================
export default function ChatMessage({ message, isUser, onLike, onDislike, likedMessages }) {
  const segments = isUser ? [{ type: 'text', content: message }] : parseMessageContent(message)

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? 'bg-primary-600' : 'bg-dark-700 ring-1 ring-dark-600'}`}>
        {isUser ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-white"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        ) : (
          <Bot size={16} className="text-primary-400" />
        )}
      </div>

      {/* Content */}
      <div className={`max-w-[80%] group ${isUser ? 'items-end' : 'items-start'}`}>
        {isUser ? (
          <div className="px-4 py-3 rounded-2xl rounded-tr-md bg-primary-600 text-white text-sm leading-relaxed">
            <p className="whitespace-pre-wrap">{message}</p>
          </div>
        ) : (
          <div className="space-y-3">
            {segments.map((seg, i) => (
              seg.type === 'code' ? (
                <CodeSegment
                  key={i}
                  language={seg.language}
                  extension={seg.extension}
                  filename={seg.filename}
                  color={seg.color}
                  content={seg.content}
                />
              ) : (
                <div key={i} className="px-4 py-3 rounded-2xl rounded-tl-md bg-dark-800 text-dark-100 border border-dark-700/50">
                  <TextSegment content={seg.content} />
                </div>
              )
            ))}
          </div>
        )}

        {/* Action buttons */}
        {!isUser && (
          <div className="flex items-center gap-0.5 mt-1 px-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={onLike} className={`p-1 rounded ${likedMessages === 'liked' ? 'text-green-400' : 'text-dark-500 hover:text-green-400'}`}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>
            </button>
            <button onClick={onDislike} className={`p-1 rounded ${likedMessages === 'disliked' ? 'text-red-400' : 'text-dark-500 hover:text-red-400'}`}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3H10zM17 2h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"/></svg>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}