#!/bin/bash
# Apply Advanced RAG fixes to AI-Socratic-Clarifier
#
# This script runs the advanced_rag_fix.py script to enhance 
# the system's Retrieval-Augmented Generation capabilities

# Ensure we're in the repository directory
cd "$(dirname "$0")"

# Check if the virtual environment exists
if [ -d ".venv" ]; then
  echo "Activating virtual environment..."
  source .venv/bin/activate
else
  echo "Warning: Virtual environment not found. Running with system Python."
fi

echo "Applying Advanced RAG fixes..."
python advanced_rag_fix.py

# Check if the application was successful
if [ $? -eq 0 ]; then
  echo ""
  echo "Fixes applied successfully. You can now restart the Socratic Clarifier."
  echo "To start with the enhanced RAG capabilities, run:"
  echo "  ./start.py"
  echo ""
  echo "For more information, see ADVANCED_RAG_README.md"
else
  echo ""
  echo "Error: Failed to apply Advanced RAG fixes. Check the error messages above."
  echo ""
fi

# Check if the virtual environment was activated
if [ -n "$VIRTUAL_ENV" ]; then
  deactivate
fi
