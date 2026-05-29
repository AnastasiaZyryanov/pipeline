#!/bin/bash
set -e

echo "Installing zstd (required for Ollama extraction)..."
sudo apt-get update && sudo apt-get install -y zstd

if ! command -v ollama &> /dev/null && ! [ -f /usr/local/bin/ollama ]; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    export PATH=$PATH:/usr/local/bin
else
    echo "Ollama already installed"
fi