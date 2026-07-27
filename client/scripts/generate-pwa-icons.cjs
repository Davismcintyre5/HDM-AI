const sharp = require('sharp');
const path = require('path');

const svgPath = path.join(__dirname, '..', 'public', 'hdm.svg');
const outDir = path.join(__dirname, '..', 'public');

async function generate() {
  await sharp(svgPath).resize(192, 192).png().toFile(path.join(outDir, 'icon-192.png'));
  await sharp(svgPath).resize(512, 512).png().toFile(path.join(outDir, 'icon-512.png'));
  console.log('PWA icons generated');
}

generate();