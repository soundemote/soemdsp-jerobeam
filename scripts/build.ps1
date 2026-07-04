$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$clang = "C:\Program Files\LLVM\bin\clang++.exe"

if (!(Test-Path -LiteralPath $clang)) {
  throw "clang++ not found at $clang"
}

$modules = (Get-Content -Raw "$root\modules.json" | ConvertFrom-Json).modules

foreach ($m in $modules) {
  $cppPath = Join-Path $root (Join-Path $m.dir $m.cpp)
  $wasmPath = Join-Path $root (Join-Path $m.dir $m.wasm)
  $exportFlags = @(
    "-Wl,--export=$($m.prefix)_create",
    "-Wl,--export=$($m.prefix)_destroy",
    "-Wl,--export=$($m.prefix)_reset",
    "-Wl,--export=$($m.prefix)_sample",
    "-Wl,--export=$($m.prefix)_x",
    "-Wl,--export=$($m.prefix)_y",
    "-Wl,--export=$($m.prefix)_version"
  )
  Write-Host "Building $($m.label) -> $($m.wasm)"
  & $clang `
    --target=wasm32 `
    -O3 `
    -nostdlib `
    -fno-exceptions `
    -fno-rtti `
    "-Wl,--no-entry" `
    @exportFlags `
    "-Wl,--export-memory" `
    -o $wasmPath `
    $cppPath
  if ($LASTEXITCODE -ne 0) {
    throw "Build failed for $($m.label)"
  }
}

Write-Host "Built $($modules.Count) modules."
