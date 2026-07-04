#!/usr/bin/env python3
"""Build the sellable Jerobeam Fenderson WASM pack.

Generates dist/manifest.json (per-module export list, checksum, size) and
dist/jerobeam-fenderson-wasm-pack-vX.Y.Z.zip containing only the compiled
.wasm binaries, the manifest, README, and LICENSE -- no C++ source (that
stays in the repo, not the distributable).

Run scripts/build.ps1 first to (re)compile the .wasm files.
"""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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

    zip_path = dist / f"jerobeam-fenderson-wasm-pack-v{version}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(manifest_path, "manifest.json")
        zf.write(ROOT / "README.md", "README.md")
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
