/**
 * generate-favicons.js
 * 
 * Creates properly square favicon PNGs from logo.png (which is 2:1 landscape).
 * The logo is placed centered inside a square canvas with transparent padding.
 * 
 * Run: node scripts/generate-favicons.js
 */
const Jimp = require('jimp');
const path = require('path');
const fs = require('fs');

const SOURCE = path.join(__dirname, '..', 'public', 'logo.png');
const OUTPUT_DIR = path.join(__dirname, '..', 'public');

// Favicon sizes to generate
const SIZES = [16, 32, 48, 180, 192];

async function generate() {
  console.log('Loading source logo:', SOURCE);
  
  if (!fs.existsSync(SOURCE)) {
    console.error('ERROR: logo.png not found at', SOURCE);
    process.exit(1);
  }

  const src = await Jimp.read(SOURCE);
  const srcW = src.getWidth();
  const srcH = src.getHeight();
  console.log(`Source dimensions: ${srcW}x${srcH} (ratio: ${(srcW/srcH).toFixed(3)})`);

  for (const size of SIZES) {
    // Scale logo to fit inside the square canvas WITH padding
    // Use 80% of the square for the logo so there's breathing room
    const logoArea = Math.round(size * 0.85);
    
    // Calculate fitted dimensions preserving aspect ratio
    const scale = Math.min(logoArea / srcW, logoArea / srcH);
    const fittedW = Math.round(srcW * scale);
    const fittedH = Math.round(srcH * scale);
    
    // Center the logo in the square canvas
    const offsetX = Math.round((size - fittedW) / 2);
    const offsetY = Math.round((size - fittedH) / 2);

    // Create transparent square canvas
    const canvas = new Jimp(size, size, 0x00000000); // fully transparent

    // Resize source copy to fitted dimensions
    const scaled = src.clone().resize(fittedW, fittedH, Jimp.RESIZE_LANCZOS3);

    // Composite onto canvas
    canvas.composite(scaled, offsetX, offsetY, {
      mode: Jimp.BLEND_SOURCE_OVER,
      opacitySource: 1,
      opacityDest: 1,
    });

    let outName;
    if (size === 16) outName = 'favicon-16x16.png';
    else if (size === 32) outName = 'favicon-32x32.png';
    else if (size === 48) outName = 'favicon-48x48.png';
    else if (size === 180) outName = 'apple-touch-icon.png';
    else if (size === 192) outName = 'favicon-192x192.png';

    const outPath = path.join(OUTPUT_DIR, outName);
    await canvas.writeAsync(outPath);
    console.log(`  ✓ Generated ${outName} (${size}x${size}, logo at ${fittedW}x${fittedH})`);
  }

  console.log('\nAll favicons generated successfully!');
}

generate().catch(err => {
  console.error('Failed:', err);
  process.exit(1);
});
