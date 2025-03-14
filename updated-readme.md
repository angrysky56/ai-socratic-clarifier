# AI-Socratic-Clarifier

A tool for generating Socratic questions and clarifications using AI reasoning techniques including Sketch-of-Thought (SoT).

## Overview

AI-Socratic-Clarifier is designed to help create thoughtful Socratic questions based on user inquiries. It leverages modern AI reasoning techniques, particularly Sketch-of-Thought (SoT), to analyze questions and generate appropriate follow-up questions that encourage deeper thinking.

## Features

- **Sketch-of-Thought Integration**: Uses SoT's reasoning paradigms (Conceptual Chaining, Chunked Symbolism, Expert Lexicons) for appropriate question analysis
- **Local LLM Integration**: Connect to Ollama for local processing
- **Web Interface**: User-friendly web UI for interacting with the system
- **Flexible Architecture**: Works with or without local LLM support

## Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai) (optional, for local LLM processing)
- [Sketch-of-Thought](https://github.com/SimonAytes/SoT) package

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-socratic-clarifier.git
   cd ai-socratic-clarifier
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. Install Sketch-of-Thought:
   ```bash
   pip install sketch-of-thought
   ```

5. Run the cleanup script to ensure proper integration:
   ```bash
   python cleanup.py
   ```

## Usage

### Command Line

```bash
# Basic usage
python -m socratic_clarifier.cli "What causes the seasons to change on Earth?"

# With Ollama integration
python examples/local_llm_integration/test_ollama_integration.py
```

### Web Interface

```bash
python web_interface/app.py
```

Then open your browser to http://localhost:5000

### Python API

```python
from socratic_clarifier.clarifier import SocraticClarifier
from examples.local_llm_integration.enhanced_clarifier import EnhancedClarifier

# Basic usage
clarifier = SocraticClarifier()
result = clarifier.process("How does photosynthesis work?")
print(result['socratic_questions'])

# Enhanced usage with Ollama
enhanced = EnhancedClarifier()
result = enhanced.process("What is the relationship between force, mass, and acceleration?")
print(result['socratic_questions'])
```

## Integrations

### Sketch-of-Thought

The system integrates with [Sketch-of-Thought](https://github.com/SimonAytes/SoT), a reasoning framework that uses three paradigms:

- **Conceptual Chaining**: For logical and conceptual reasoning
- **Chunked Symbolism**: For mathematical and symbolic reasoning
- **Expert Lexicons**: For domain-specific technical reasoning

### Ollama

For local LLM processing, the system connects to [Ollama](https://ollama.ai), which should be installed separately. Supported models include:

- Llama3
- Mistral
- Any other model supported by Ollama

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
