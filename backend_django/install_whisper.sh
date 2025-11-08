#!/bin/bash

# Whisper.cpp Installation Script for Render
# ============================================
# This script downloads, compiles and sets up whisper.cpp
# with the medium model for audio transcription.

set -e  # Exit on error

echo "========================================"
echo "🎙️  Installing Whisper.cpp"
echo "========================================"

# Configuration
WHISPER_DIR="/opt/whisper.cpp"
MODEL_SIZE="medium"
THREADS=4

# Install dependencies
echo "📦 Installing build dependencies..."
apt-get update -qq
apt-get install -y -qq build-essential cmake curl git > /dev/null 2>&1
echo "✅ Dependencies installed"

# Clone whisper.cpp repository
if [ -d "$WHISPER_DIR" ]; then
    echo "♻️  Whisper.cpp directory exists, removing..."
    rm -rf "$WHISPER_DIR"
fi

echo "📥 Cloning whisper.cpp repository..."
git clone --quiet https://github.com/ggerganov/whisper.cpp.git "$WHISPER_DIR"
cd "$WHISPER_DIR"
echo "✅ Repository cloned"

# Compile whisper.cpp
echo "🔨 Compiling whisper.cpp..."
make -j${THREADS} > /dev/null 2>&1
echo "✅ Compilation complete"

# Download model
echo "📥 Downloading ${MODEL_SIZE} model..."
cd "$WHISPER_DIR/models"
bash ./download-ggml-model.sh "$MODEL_SIZE" > /dev/null 2>&1
echo "✅ Model downloaded: ggml-${MODEL_SIZE}.bin"

# Verify installation
echo ""
echo "🔍 Verifying installation..."
EXECUTABLE="${WHISPER_DIR}/main"
MODEL_FILE="${WHISPER_DIR}/models/ggml-${MODEL_SIZE}.bin"

if [ -f "$EXECUTABLE" ]; then
    echo "✅ Executable found: $EXECUTABLE"
else
    echo "❌ ERROR: Executable not found!"
    exit 1
fi

if [ -f "$MODEL_FILE" ]; then
    echo "✅ Model found: $MODEL_FILE"
    MODEL_SIZE_MB=$(du -m "$MODEL_FILE" | cut -f1)
    echo "   Size: ${MODEL_SIZE_MB}MB"
else
    echo "❌ ERROR: Model not found!"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ Whisper.cpp installation complete!"
echo "========================================"
echo "Directory: $WHISPER_DIR"
echo "Executable: $EXECUTABLE"
echo "Model: $MODEL_FILE"
echo "========================================"
