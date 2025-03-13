# Local LLM Integration Example

This example demonstrates how to enhance the AI-Socratic-Clarifier with local LLMs using LM Studio and Ollama.

## Features

- **Automatic Provider Detection**: Automatically discovers and uses available local LLM providers
- **Enhanced Questions**: Uses local LLMs to generate more insightful Socratic questions
- **Improved Reasoning**: Enhances SoT reasoning with LLM-generated insights
- **Multimodal Capabilities**: Adds image analysis when using multimodal models

## Requirements

To use the local LLM integration, you'll need at least one of:

1. **LM Studio** - A desktop application for running local LLMs
   - Download from: https://lmstudio.ai/
   - Start the local inference server (runs on port 1234 by default)

2. **Ollama** - A command-line tool for running local LLMs
   - Download from: https://ollama.com/
   - Pull a model: `ollama pull llama3` or any other model
   - For embeddings: `ollama pull nomic-embed-text`
   - For multimodal: `ollama pull llava` or other vision models

## Usage

```bash
# Basic usage with examples
python enhanced_clarifier.py

# Provide your own text
python enhanced_clarifier.py --text "The study shows significant results that prove our theory."

# Use a specific mode
python enhanced_clarifier.py --mode academic

# Multimodal analysis (requires a vision model in Ollama/LM Studio)
python enhanced_clarifier.py --text "This graph shows a clear trend." --image "path/to/image.jpg"

# Use only base SoT functionality (no local LLM enhancement)
python enhanced_clarifier.py --base-only
```

## How It Works

1. The `EnhancedClarifier` extends the base `SocraticClarifier` class
2. It uses the `IntegrationManager` to discover and manage local LLM providers
3. The base SoT functionality is used for issue detection and initial reasoning
4. Local LLMs enhance the questions and reasoning when available
5. Multimodal capabilities are used when available and an image is provided

## Benefits

- **Preserves Core SoT Functionality**: The base system still works even without local LLMs
- **Enhanced Questions**: Local LLMs can generate more contextually relevant questions
- **Richer Reasoning**: Combines structured SoT reasoning with LLM insights
- **Multimodal Analysis**: Adds image understanding capabilities
