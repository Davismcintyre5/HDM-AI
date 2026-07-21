const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const SVG_PATH = path.join(__dirname, '..', 'assets', 'icon.svg');
const OUTPUT_DIR = path.join(__dirname, '..', 'assets');

const SIZES = {
  icon: [48, 72, 96, 144, 192],
  adaptive: [48, 72, 96, 144, 192, 512],
  splash: { width: 1284, height: 2778 },
};

async function generate() {
  console.log('Generating assets...\n');

  const svg = fs.readFileSync(SVG_PATH, 'utf-8');

  // Icon
  for (const size of SIZES.icon) {
    await sharp(Buffer.from(svg))
      .resize(size, size)
      .png()
      .toFile(path.join(OUTPUT_DIR, `icon-${size}.png`));
    console.log(`✓ icon-${size}.png`);
  }

  // Main icon
  await sharp(Buffer.from(svg))
    .resize(1024, 1024)
    .png()
    .toFile(path.join(OUTPUT_DIR, 'icon.png'));
  console.log('✓ icon.png');

  // Adaptive icon (Android)
  for (const size of SIZES.adaptive) {
    await sharp(Buffer.from(svg))
      .resize(size, size)
      .png()
      .toFile(path.join(OUTPUT_DIR, `adaptive-icon-${size}.png`));
    console.log(`✓ adaptive-icon-${size}.png`);
  }

  await sharp(Buffer.from(svg))
    .resize(1024, 1024)
    .png()
    .toFile(path.join(OUTPUT_DIR, 'adaptive-icon.png'));
  console.log('✓ adaptive-icon.png');

  // Splash screen
  await sharp({
    create: {
      width: SIZES.splash.width,
      height: SIZES.splash.height,
      channels: 4,
      background: { r: 10, g: 10, b: 10, alpha: 1 },
    },
  })
    .composite([
      {
        input: await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer(),
        gravity: 'center',
      },
    ])
    .png()
    .toFile(path.join(OUTPUT_DIR, 'splash.png'));
  console.log('✓ splash.png');

  // Favicon
  await sharp(Buffer.from(svg))
    .resize(48, 48)
    .png()
    .toFile(path.join(OUTPUT_DIR, 'favicon.png'));
  console.log('✓ favicon.png');

  console.log('\nAll assets generated!');
}

generate().catch(console.error);