# AI-Socratic-Clarifier

An AI-assisted workflow for bias detection, language clarification, and Socratic questioning, enhanced with Sketch-of-Thought (SoT) reasoning and local LLM integration.

## Introduction

The AI-Socratic-Clarifier is a modular system designed to detect ambiguity, bias, and logical inconsistencies in text, and generate targeted Socratic questions to help clarify and improve communication. It integrates the Sketch-of-Thought framework to provide concise, structured reasoning in its responses and can be enhanced with local LLMs through LM Studio or Ollama.

## Features

- **Multi-agent Architecture**: Specialized modules for ambiguity detection, bias identification, and fact-checking
- **Socratic Question Generation**: Creates thought-provoking questions rather than just corrections
- **Sketch-of-Thought Integration**: Provides compact, structured reasoning using three paradigms:
  - Conceptual Chaining: For connecting key ideas in logical sequences
  - Chunked Symbolism: For numerical and symbolic reasoning
  - Expert Lexicons: For domain-specific terminology and concepts
- **Domain-Specific Modes**: Academic, legal, medical, chat, business, and more
- **Local LLM Integration**: Optional enhancement with models from LM Studio or Ollama
- **Multimodal Capabilities**: Analyze images alongside text (with compatible LLMs)
- **Adaptive Feedback Loops**: System learns from user responses to improve questioning strategies

## Components

The project includes several components:

1. **Core Library**: The main Python package for text analysis and question generation
2. **Web Interface**: A simple Flask-based web UI for interacting with the system
3. **API Server**: FastAPI server to expose the functionality as a service
4. **VS Code Extension**: Integration with the popular code editor
5. **Local LLM Integration**: Optional enhancement with local language models
6. **Examples**: Demonstrating various use cases and features

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/angrysky56/ai-socratic-clarifier.git
cd ai-socratic-clarifier

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package and dependencies
pip install -e .
```

Install [Sketch-of-Thought](https://github.com/SimonAytes/SoT) (should be in the repo already)
```
python install_sot.py
```

### Local LLM Setup (Optional)

For enhanced performance with local LLMs:

1. **LM Studio**:
   - Download from: https://lmstudio.ai/
   - Start the local inference server (default port: 1234)

2. **Ollama**:
   - Download from: https://ollama.com/
   - Pull a model: `ollama pull llama3` (or other model)
   - For embeddings: `ollama pull nomic-embed-text`
   - For multimodal: `ollama pull llava` (or other vision model)

### Configuration

Create a config.json file in the project root:

```bash
cp config.example.json config.json
```

Edit the settings as needed to match your LM Studio or Ollama setup.

### Basic Usage

```python
from socratic_clarifier import SocraticClarifier

# Initialize the clarifier
clarifier = SocraticClarifier(mode="academic")

# Analyze text and generate questions
result = clarifier.analyze("Men are better leaders than women.")
print(result.questions)
print(result.reasoning)
```

### Enhanced Usage with Local LLMs

```python
from socratic_clarifier.examples.local_llm_integration.enhanced_clarifier import EnhancedClarifier

# Initialize the enhanced clarifier
clarifier = EnhancedClarifier(mode="academic")

# Analyze text with local LLM enhancement
result = clarifier.analyze("Men are better leaders than women.")
print(result.questions)
print(result.reasoning)

# Try multimodal analysis if supported
if clarifier.multimodal_available:
    result = clarifier.analyze_multimodal(
        "This graph shows our performance.", 
        "path/to/image.jpg"
    )
    print(result.questions)
```

### Running the Web Interface

```bash
# Install Flask
pip install flask

# Run the web server
cd web_interface
python app.py
```

Then open your browser to http://localhost:5000

### Running the API Server

```bash
# Run the API server
cd examples
python api_server.py
```

The API will be available at http://localhost:8000

## Architecture

The system consists of several interconnected components:

1. **Detectors**: Identify issues in text (ambiguity, bias, unsupported claims)
2. **Reasoning Engine**: Applies Sketch-of-Thought to generate concise reasoning
3. **Question Generators**: Creates Socratic questions based on detected issues
4. **Mode Configurator**: Adjusts sensitivity and style based on domain context
5. **LLM Integration**: Optional enhancement with local language models
6. **Feedback Adapter**: Refines strategies based on user responses

## Examples

Look in the `examples` directory for:

- `basic_usage.py`: Simple demonstration of the core features
- `sot_integration.py`: Advanced examples with different SoT paradigms
- `api_server.py`: FastAPI server to expose the functionality as a service
- `local_llm_integration/`: Examples of enhancing the system with local LLMs

## VS Code Extension

The extension integrates the clarifier into VS Code:

1. Highlights potential issues in your text
2. Shows Socratic questions on hover
3. Displays SoT reasoning for each issue

See the `extensions/vscode` directory for installation and usage instructions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
