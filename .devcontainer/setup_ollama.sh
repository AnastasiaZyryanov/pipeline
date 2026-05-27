#!/bin/bash

set -e

echo "Installing zstd (required for Ollama extraction)..."
sudo apt-get update && sudo apt-get install -y zstd

if ! command -v ollama &> /dev/null
then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed"
fi

if ! pgrep -x "ollama" > /dev/null
then
    echo "Starting Ollama server..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
else
    echo "Ollama server already running"
fi