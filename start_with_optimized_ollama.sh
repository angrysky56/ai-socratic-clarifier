#!/bin/bash
# Optimized Ollama Configuration Script for AI-Socratic-Clarifier
# This script sets up Ollama with optimized configuration settings for better performance

# Set environment variables for Ollama
export OLLAMA_CONTEXT_LENGTH=8192
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KV_CACHE_TYPE=q8_0

# Optional: Set parallel requests (comment out to use default)
# export OLLAMA_NUM_PARALLEL=4

# Optional: Set maximum queue size (comment out to use default)
# export OLLAMA_MAX_QUEUE=512

echo "Setting up Ollama with optimized configuration:"
echo "- Context Length: $OLLAMA_CONTEXT_LENGTH"
echo "- Flash Attention: Enabled"
echo "- KV Cache Type: $OLLAMA_KV_CACHE_TYPE (8-bit quantization)"

# Update the config.json file to match the new context length
CONFIG_FILE=$(dirname "$0")/config.json

if [ -f "$CONFIG_FILE" ]; then
    echo "Updating context_length in config.json..."
    # Use jq to modify config.json if jq is installed
    if command -v jq >/dev/null 2>&1; then
        # Create a temporary file
        TMP_FILE=$(mktemp)
        # Update the context_length in the config
        jq '.integrations.ollama.context_length = 8192' "$CONFIG_FILE" > "$TMP_FILE"
        # Replace the original file
        mv "$TMP_FILE" "$CONFIG_FILE"
        echo "Config file updated successfully."
    else
        echo "jq is not installed. Please manually set context_length in config.json to $OLLAMA_CONTEXT_LENGTH."
    fi
else
    echo "Warning: config.json not found."
fi

# Apply the advanced settings fix first (if not already applied)
if [ -f "fix_settings_advanced.py" ]; then
    echo "Applying advanced settings fix..."
    python fix_settings_advanced.py
fi

# Start the UI
echo "Starting AI-Socratic-Clarifier..."
python start_ui.py
