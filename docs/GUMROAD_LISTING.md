# Gumroad listing copy

Paste directly into the Gumroad product form.

## Title

Jerobeam Fenderson WASM Modules — 8 Native Oscillator Ports

## Price

$10

## Short description

Eight of Jerobeam Fenderson's Gen~/Max motion-oscillator patches
(Blubb, Boing, Kepler-Bouwkamp, Mushroom, Nyquist-Shannon, Radar, Torus,
WirdoSpiral), faithfully ported to compact, dependency-free WebAssembly
modules. Drop them into any web audio/visual project — each one exports
a simple `create -> sample -> x/y -> destroy` interface, no runtime
dependencies, no libm.

Includes a one-click player — open `player.html`, no install, no
server, and you can hear every module immediately.

## What's included

- 8 `.wasm` binaries (one per module)
- `player.html` — self-contained, double-click-to-hear demo of every module
- `manifest.json` describing every export and a SHA-256 checksum per module
- License (commercial use permitted — embed in your own products; no
  reselling as a standalone module pack)

## Product file

`dist/jerobeam-fenderson-wasm-pack-v1.0.0.zip` (run `scripts/build.ps1`
then `scripts/package.py` to regenerate if the source changes)

## Before publishing, still needed

1. Have the `LICENSE` reviewed (ideally by a lawyer) — it currently
   documents a 50% royalty arrangement with Jerobeam Fenderson as an
   informal, not-yet-finalized starting point, and describes proceeds
   owed to him as held in reserve pending that negotiation.
2. Set up Gumroad's Affiliates feature for the royalty split once terms
   with Jerobeam are settled (or keep tracking/holding funds manually
   until then).
