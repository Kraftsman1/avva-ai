#!/bin/bash
# AVVA Local Setup Script - Downloads Piper TTS Binary and Voice Models

echo "🚀 Starting AVVA Local Setup..."

# 1. Create directory structure
mkdir -p bin temp/models

# 2. Download Piper Binary (x86_64)
if [ ! -f "bin/piper" ]; then
    echo "📥 Downloading Piper binary..."
    curl -L https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz -o temp/piper.tar.gz
    tar -xzf temp/piper.tar.gz -C bin
    mv bin/piper/piper bin/piper_bin
    rm -rf bin/piper
    mv bin/piper_bin bin/piper
    chmod +x bin/piper
    rm temp/piper.tar.gz
    echo "✅ Piper binary installed to bin/"
else
    echo "✔ Piper binary already exists."
fi

# 3. Download Voice Model (Lessac Medium)
MODEL_NAME="en_US-lessac-medium"
if [ ! -f "temp/models/$MODEL_NAME.onnx" ]; then
    echo "📥 Downloading voice model ($MODEL_NAME)..."
    curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/$MODEL_NAME.onnx" -o "temp/models/$MODEL_NAME.onnx"
    curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/$MODEL_NAME.onnx.json" -o "temp/models/$MODEL_NAME.onnx.json"
    echo "✅ Voice model installed to temp/models/"
else
    echo "✔ Voice model already exists."
fi

echo "✨ Audio setup complete! You can now run AVVA with piper TTS enabled."
