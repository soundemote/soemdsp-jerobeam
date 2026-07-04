#!/usr/bin/env python3
"""Build the sellable Jerobeam Fenderson WASM pack.

Generates dist/manifest.json (per-module export list, checksum, size,
demo playback args) and dist/jerobeam-fenderson-wasm-pack-vX.Y.Z.zip
containing the compiled .wasm binaries, the manifest, README, LICENSE,
and a self-contained player.html so a buyer can open one file and hear
every module immediately, no coding required -- no C++ source (that
stays in the repo, not the distributable).

Run scripts/build.ps1 first to (re)compile the .wasm files.
"""
import base64
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PLAYER_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Jerobeam Fenderson WASM Modules -- Player</title>
<style>
  body { background: #0b0d10; color: #f3f1ec; font-family: -apple-system, Segoe UI, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 20px; }
  h1 { font-size: 1.3rem; }
  p.sub { color: #9aa0a6; font-size: 0.9rem; }
  .card { border: 1px solid #2a2f36; border-radius: 8px; padding: 14px 18px; margin: 12px 0; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
  .card strong { display: block; font-size: 1rem; }
  .card span { color: #9aa0a6; font-size: 0.85rem; }
  button { background: #1c2128; color: #f3f1ec; border: 1px solid #3a4048; border-radius: 6px; padding: 8px 16px; cursor: pointer; font-size: 0.9rem; }
  button.playing { background: #2f6f4f; border-color: #4a9a6f; }
  button:hover { border-color: #7fc7d9; }
</style>
</head>
<body>
<h1>Jerobeam Fenderson WASM Modules</h1>
<p class="sub">Click a module to hear it (X -> left channel, Y -> right channel). Click again to stop. No install, no server -- this file is self-contained.</p>
<div id="list"></div>
<script>
const MODULES = __MODULES_JSON__;

let audioCtx = null;
let current = null; // { button, node, instance, handle, prefix }

function b64ToBytes(b64) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

async function stopCurrent() {
  if (!current) return;
  current.node.disconnect();
  try { current.instance.exports[current.prefix + "_destroy"](current.handle); } catch (_e) {}
  current.button.textContent = "Play";
  current.button.classList.remove("playing");
  current = null;
}

async function playModule(mod, button) {
  if (current && current.button === button) {
    await stopCurrent();
    return;
  }
  await stopCurrent();
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  if (audioCtx.state === "suspended") await audioCtx.resume();

  const bytes = b64ToBytes(mod.wasmBase64);
  const { instance } = await WebAssembly.instantiate(bytes, {});
  const ex = instance.exports;
  const p = mod.prefix;
  const handle = ex[p + "_create"]();
  const args = mod.demoArgs.length ? mod.demoArgs : [220];

  const node = audioCtx.createScriptProcessor(2048, 0, 2);
  node.onaudioprocess = (event) => {
    const left = event.outputBuffer.getChannelData(0);
    const right = event.outputBuffer.getChannelData(1);
    for (let i = 0; i < left.length; i++) {
      ex[p + "_sample"](handle, ...args, audioCtx.sampleRate);
      const x = ex[p + "_x"](handle);
      const y = ex[p + "_y"](handle);
      left[i] = Number.isFinite(x) ? Math.max(-1, Math.min(1, x)) : 0;
      right[i] = Number.isFinite(y) ? Math.max(-1, Math.min(1, y)) : 0;
    }
  };
  node.connect(audioCtx.destination);

  button.textContent = "Stop";
  button.classList.add("playing");
  current = { button, node, instance, handle, prefix: p };
}

const list = document.getElementById("list");
for (const mod of MODULES) {
  const card = document.createElement("div");
  card.className = "card";
  const info = document.createElement("div");
  info.innerHTML = `<strong>${mod.label}</strong><span>${mod.description}</span>`;
  const button = document.createElement("button");
  button.textContent = "Play";
  button.addEventListener("click", () => playModule(mod, button));
  card.append(info, button);
  list.append(card);
}
</script>
</body>
</html>
"""


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    modules = json.loads((ROOT / "modules.json").read_text(encoding="utf-8"))["modules"]
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)

    entries = []
    missing = []
    for m in modules:
        wasm_path = ROOT / m["dir"] / m["wasm"]
        if not wasm_path.exists():
            missing.append(m["wasm"])
            continue
        entries.append({
            "id": m["id"],
            "label": m["label"],
            "description": m["description"],
            "wasm": m["wasm"],
            "exports": {
                "create": f"{m['prefix']}_create",
                "destroy": f"{m['prefix']}_destroy",
                "reset": f"{m['prefix']}_reset",
                "sample": f"{m['prefix']}_sample",
                "x": f"{m['prefix']}_x",
                "y": f"{m['prefix']}_y",
                "version": f"{m['prefix']}_version",
            },
            "outputs": m["outputs"],
            "demoArgs": m.get("demoArgs", []),
            "sizeBytes": wasm_path.stat().st_size,
            "sha256": sha256_of(wasm_path),
        })

    if missing:
        print(f"ERROR: missing compiled .wasm for: {', '.join(missing)}", file=sys.stderr)
        print("Run scripts/build.ps1 first.", file=sys.stderr)
        return 1

    manifest = {
        "product": "Jerobeam Fenderson WASM Modules",
        "version": version,
        "moduleCount": len(entries),
        "modules": entries,
    }
    manifest_path = dist / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {manifest_path} ({len(entries)} modules)")

    player_modules = [
        {
            "label": e["label"],
            "description": e["description"],
            "prefix": e["exports"]["sample"].rsplit("_sample", 1)[0],
            "demoArgs": e["demoArgs"],
            "wasmBase64": base64.b64encode((ROOT / m["dir"] / m["wasm"]).read_bytes()).decode("ascii"),
        }
        for e, m in zip(entries, modules)
    ]
    player_html = PLAYER_TEMPLATE.replace("__MODULES_JSON__", json.dumps(player_modules))
    player_path = dist / "player.html"
    player_path.write_text(player_html, encoding="utf-8")
    print(f"Wrote {player_path} (self-contained, {len(player_modules)} modules embedded)")

    zip_path = dist / f"jerobeam-fenderson-wasm-pack-v{version}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(manifest_path, "manifest.json")
        zf.write(ROOT / "README.md", "README.md")
        zf.write(player_path, "player.html")
        license_path = ROOT / "LICENSE"
        if license_path.exists():
            zf.write(license_path, "LICENSE")
        for m in modules:
            wasm_path = ROOT / m["dir"] / m["wasm"]
            zf.write(wasm_path, f"wasm/{m['wasm']}")

    print(f"Wrote {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
