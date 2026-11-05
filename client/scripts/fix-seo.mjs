import { readFileSync, writeFileSync, existsSync, readdirSync, statSync } from 'fs';
import { resolve, join } from 'path';

const SITE_URL = 'https://ai.hdm.co.ke';

const ROUTES = [
  { path: '/login', priority: '0.80' },
  { path: '/register', priority: '0.80' },
  { path: '/forgot-password', priority: '0.50' },
];

const today = new Date().toISOString().split('T')[0];

const indexPath = resolve('dist/index.html');
if (!existsSync(indexPath)) {
  console.error('❌ dist/index.html not found');
  process.exit(1);
}

let html = readFileSync(indexPath, 'utf-8');

html = html.replace(/<meta name="author" content="[^"]*"\s*\/?>\s*\n?/gi, '');
html = html.replace(/<meta name="keywords" content="[^"]*"\s*\/?>\s*\n?/gi, '');
html = html.replace(/<meta property="og:[^"]*"[^>]*>\s*\n?/gi, '');
html = html.replace(/<meta name="twitter:[^"]*"[^>]*>\s*\n?/gi, '');
html = html.replace(/\n{3,}/g, '\n\n');

const ogBlock = `
    <meta property="og:title" content="HDM AI — Central Intelligence Platform" />
    <meta property="og:description" content="7 AI services — chat, code, image, analysis, learning, and support, built by HDM Technologies." />
    <meta property="og:image" content="https://ai.hdm.co.ke/icon-512.png" />
    <meta property="og:url" content="https://ai.hdm.co.ke/login" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="HDM AI" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="HDM AI — Central Intelligence Platform" />
    <meta name="twitter:description" content="7 AI services — chat, code, image, analysis, learning, and support." />
    <meta name="twitter:image" content="https://ai.hdm.co.ke/icon-512.png" />
`;

html = html.replace('</head>', ogBlock + '</head>');
writeFileSync(indexPath, html, 'utf-8');
console.log('✅ dist/index.html cleaned');

function walk(dir) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      walk(full);
    } else if (entry === 'index.html' && full !== indexPath) {
      let sub = readFileSync(full, 'utf-8');
      sub = sub.replace(/<meta name="author" content="[^"]*"\s*\/?>\s*\n?/gi, '');
      sub = sub.replace(/<meta name="keywords" content="[^"]*"\s*\/?>\s*\n?/gi, '');
      writeFileSync(full, sub, 'utf-8');
    }
  }
}
walk(resolve('dist'));

const urls = ROUTES.map(
  (r) => `    <url>
        <loc>${SITE_URL}${r.path}</loc>
        <lastmod>${today}</lastmod>
        <priority>${r.priority}</priority>
    </url>`
).join('\n');

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>
`;

writeFileSync(resolve('dist/sitemap.xml'), sitemap, 'utf-8');
console.log(`✅ dist/sitemap.xml written (${ROUTES.length} URLs)`);