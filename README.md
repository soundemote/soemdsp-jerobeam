# soemdsp-jerobeam

Native WebAssembly ports of 8 Jerobeam Fenderson Gen~/Max oscillator
patches, plus the original JS-only Spiral module. Source: this repo's
`native_modules/jerobeam_*/*.cpp`, ported from
`soemdsp/include/soemdsp/oscillator/Jerobeam*.{h,cpp}` in the
[soemdsp-sandbox](https://github.com/soundemote/soemdsp-sandbox) codebase.

## Build target

`--target=wasm32 -O3 -nostdlib -fno-exceptions -fno-rtti`. No libm:
`sin`/`cos` implemented via a 7-term minimax polynomial with quadrant
range reduction; `pow` (where used) via IEEE-754 exponent-field
manipulation. Compiled with clang++.

## Export convention

Every module exposes the same 7 functions, prefixed per module (see
table):

```
int    {prefix}_create()                          // allocate an instance, returns handle (0 = pool exhausted)
void   {prefix}_destroy(int handle)
void   {prefix}_reset(int handle)                  // zero internal phase accumulators
void   {prefix}_sample(int handle, ...params, double sampleRate)
double {prefix}_x(int handle)                      // read X output after _sample
double {prefix}_y(int handle)                      // read Y output after _sample
double {prefix}_version()
```

Instance pool: 16 concurrent handles per module (`kMaxInstances`).

## Modules

| Module | Prefix | Params | Source |
|---|---|---|---|
| WirdoSpiral | `soemdsp_jbwirdo` | frequency, sharp, cross, density, length, rotate, splashDepth, splashDensity, cut, scrap, ringCut, splashSpeed, syncCut (13) | `native_modules/jerobeam_wirdo_spiral/` |
| Blubb | `soemdsp_jbblubb` | frequency, shape, rotX, rotY, zDepth (5) | `native_modules/jerobeam_blubb/` |
| Boing | `soemdsp_jbboing` | frequency, density, sharpness, rotX, rotY, zDepth, zAmount, ends, boing, boingStrength, dir, shape, volume, volumePreJump (14) | `native_modules/jerobeam_boing/` |
| Kepler-Bouwkamp | `soemdsp_jbkepler` | frequency, start, length, circles, zoom, rotation, tri (7) | `native_modules/jerobeam_kepler_bouwkamp/` |
| Mushroom | `soemdsp_jbmushroom` | frequency, phaseOffset, numMushrooms, grow, density, capRotation, stemRotationSpeed, head, spread, wobble, clusterRotation, clusterRotationSpeed, sharp, width, stem, apart, capStemTransition (17) | `native_modules/jerobeam_mushroom/` |
| Nyquist-Shannon | `soemdsp_jbnyquist` | frequencyA, midiNoteRaw, rate, sampleDots, phaseOffset, frequencyB, subPhase, subPhaseRotationSpeed, tone, toneSmoothTime, artifact, enableToneModPitch, enableToneModFreq, enableToneModNote (14) | `native_modules/jerobeam_nyquist_shannon/` |
| Radar | `soemdsp_jbradar` | frequency, phaseOffset, density, sharp, fade, rotation, direction, shade, lap, ringcut, pow1Up, pow1Down, pow2Bend, phaseInv, tunnelInv, spiralReturn, length, ratio, frontring, zoom, zDepth, inner, x, y (24) | `native_modules/jerobeam_radar/` |
| Torus | `soemdsp_jbtorus` | frequency, density, quantizeDensity, subdensity, quantizeSubDensity, sharp, size, length, balance, wander, darkAngle, darkIntensity, rotX, rotY, rotZ, zAngleX, zAngleY, zDepth (18) | `native_modules/jerobeam_torus/` |
| Spiral | (JS only) | — | `public/node-graph-jerobeam-spiral.js` |

Each module outputs a continuous (X, Y) pair per call to `_sample`,
suitable for direct audio-rate use (X → left, Y → right) or 2D/3D
motion-graphics use.

## Files

- `native_modules/jerobeam_*/` — C++ source and compiled `.wasm` per module.
- `public/node-graph-jerobeam-*.js` — JS reference implementation per
  module, used during development to numerically cross-check the native
  build (verified to agree within floating-point tolerance over
  20,000+ sample runs).
- `player.html`, `modules.json`, `scripts/build.ps1`, `scripts/package.py`
  — self-contained demo player and build/packaging pipeline.
- `docs/` — distribution research and announcement drafts.
- `BEAMING_RADAR_SIGNAL_TO_JEROBEAM.md` — dedication document.
