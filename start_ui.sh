#!/bin/bash
# Start script for AI-Socratic-Clarifier with debugging

echo "Starting AI-Socratic-Clarifier on port 5001 (DEBUG MODE)..."
echo "This script includes detailed logging to help troubleshoot any issues."

# Kill any existing processes on port 5001
echo "Checking for existing processes on port 5001..."
PIDS=$(lsof -t -i:5001 2>/dev/null)
if [ ! -z "$PIDS" ]; then
  echo "Killing existing processes on port 5001: $PIDS"
  kill -9 $PIDS
else
  echo "No processes found on port 5001."
fi

# Set environment variables
export FLASK_APP=web_interface/app.py
export FLASK_RUN_PORT=5001
export FLASK_DEBUG=1

# Set path to Python
PYTHON=python3

# Check Ollama connectivity
echo "Checking Ollama connectivity..."
curl -s http://localhost:11434/api/tags > /dev/null
if [ $? -eq 0 ]; then
  echo "✓ Ollama is running."
else
  echo "✗ Ollama is not running. Please start Ollama before continuing."
  exit 1
fi

# Start the application with debug output
echo "Starting web interface..."
cd $(dirname "$0")
$PYTHON -m flask run --host=0.0.0.0 --port=5001
