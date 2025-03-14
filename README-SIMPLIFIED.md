# AI-Socratic-Clarifier - Simplified Startup

This document explains the simplified startup process for the AI-Socratic-Clarifier. I've created a clean, consolidated script that makes it easy to start the application.

## Quick Start

Simply run the following command from the repository root:

```bash
./start_socratic.py
```

This script will:

1. Check your environment (virtual environment, config file)
2. Verify that Ollama is running and the configured model is available
3. Start the web interface on port 5000

## Available Interfaces

Once started, you can access the following interfaces:

- **Main interface**: http://localhost:5000/
- **Chat interface**: http://localhost:5000/chat
- **Reflection interface**: http://localhost:5000/reflection

## Configuration

The script uses `config.json` in the repository root. If this file doesn't exist, a default configuration will be created automatically.

## Requirements

- Python 3.8 or higher
- Ollama running locally with at least one model available
- Flask (will be installed automatically if missing)

## Troubleshooting

If you encounter issues:

1. Make sure Ollama is running with `ollama serve`
2. Check that you have the model specified in your `config.json`
3. Look for error messages in the script output

## Cleaning Up

To stop the server, simply press `Ctrl+C` in the terminal where the script is running.

## Notes

This simplified script replaces the multiple start scripts that were previously available. If you find any issues with this new approach, please let me know.
