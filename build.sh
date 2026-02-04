#!/bin/bash
set -e

echo "🚀 Starting AVVA AI Build Pipeline..."

# 1. Build Python Core Sidecar
echo "📦 [1/4] Compiling Python Core..."
./venv/bin/pyinstaller --onefile --name avva-core-x86_64-unknown-linux-gnu avva_core.py
mkdir -p ui-web/src-tauri/sidecars
mv dist/avva-core-x86_64-unknown-linux-gnu ui-web/src-tauri/sidecars/

# 2. Build Nuxt Frontend
echo "🌐 [2/4] Building Web UI..."
cd ui-web
npm run generate

# 3. Build Tauri Native App
echo "🦀 [3/4] Building Tauri Shell..."
rm -rf src-tauri/target
npx tauri build

# 4. Finalize
echo "✨ [4/4] Build Complete!"
echo "Binary location: ui-web/src-tauri/target/release/avva"
