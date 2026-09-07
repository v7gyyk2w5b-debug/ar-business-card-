// Converts a raw 3D Gaussian Splatting PLY export into a compressed .ksplat
// file using @mkkellogg/gaussian-splats-3d's own PLY parser + generator —
// the same library the AR page renders with, so the output is guaranteed
// compatible.
//
// Why: the source PLY is a full-quality training checkpoint (1.68M splats,
// full spherical harmonics, ~397MB) — completely impractical to download
// over a phone connection or render smoothly on a mobile GPU. This produces
// a much smaller, quantized version suitable for a WebAR business card.

globalThis.window = globalThis; // the library calls window.setTimeout internally

import * as GaussianSplats3D from '@mkkellogg/gaussian-splats-3d';
import fs from 'fs';

const [,, inPath, outPath, minAlphaArg, compressionArg, shDegreeArg] = process.argv;
const minimumAlpha = minAlphaArg ? parseFloat(minAlphaArg) : 1;
const compressionLevel = compressionArg ? parseInt(compressionArg) : 1;
const shDegree = shDegreeArg ? parseInt(shDegreeArg) : 0; // 0 = drop spherical harmonics detail, big size win

console.log(`Reading ${inPath} ...`);
const fileBuffer = fs.readFileSync(inPath);
// PLY parser expects an ArrayBuffer, not a Node Buffer
const arrayBuffer = fileBuffer.buffer.slice(fileBuffer.byteOffset, fileBuffer.byteOffset + fileBuffer.byteLength);

console.log(`Parsing PLY + generating compressed SplatBuffer (compressionLevel=${compressionLevel}, shDegree=${shDegree}, minimumAlpha=${minimumAlpha}) ...`);
const t0 = Date.now();

GaussianSplats3D.PlyLoader.loadFromFileData(arrayBuffer, minimumAlpha, compressionLevel, shDegree)
  .then((splatBuffer) => {
    const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
    console.log(`Done in ${elapsed}s. Splat count: ${splatBuffer.getSplatCount ? splatBuffer.getSplatCount() : '(unknown)'}`);
    const outBuffer = Buffer.from(splatBuffer.bufferData);
    fs.writeFileSync(outPath, outBuffer);
    console.log(`Wrote ${outPath} (${(outBuffer.length / 1024 / 1024).toFixed(2)} MB)`);
  })
  .catch((err) => {
    console.error('Conversion failed:', err);
    process.exit(1);
  });
