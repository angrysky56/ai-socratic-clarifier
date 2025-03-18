# AI-Socratic-Clarifier

An advanced system for enhancing critical thinking through AI-assisted questioning and reflection. The AI-Socratic-Clarifier analyzes text and generates Socratic questions that prompt deeper reflection and exploration of ideas.

## Key Features

- **Enhanced UI**: A consolidated single-window interface with document management and reflective visualization
- **Socratic Question Generation**: Analyze text and generate insightful questions to promote critical thinking
- **Symbiotic Reflective Ecosystem (SRE)**: Advanced reflective reasoning system for deeper analysis
- **Sequential of Thought (SoT)**: Structured reasoning approach for complex problem-solving
- **Document Management**: Upload, view, and use documents as context for AI analysis
- **Multimodal Support**: Process images and PDFs using OCR and multimodal AI models
- **RAG Context**: Use uploaded documents as retrieval-augmented generation context for more informed AI responses

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Ollama (for local LLM integration)
- Tesseract OCR (for document processing, optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/angrysky56/ai-socratic-clarifier.git
   cd ai-socratic-clarifier
   ```

2. Install dependencies:
   ```bash
   # Create a venv
   python -m venv venv
   source venv/bin/activate # On Windows, use 'venv\Scripts\activate'
   # Install dependencies
   pip install -r requirements.txt
   python install_dependencies.py

   ```

3. Configure Ollama models:
   
   Ensure Ollama is running and the required models are available:
   ```bash
   ollama pull gemma3:latest    # Default model for text analysis
   ollama pull llava:latest     # Multimodal model for image processing (optional)
   ```

   Copy the configuration file:
   ```bash
   cp config.example.py config.py
   ```
   Edit `config.py` to set the model and other configurations if desired.

4. Start the application:
   ```bash
   python start_ui.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

The AI-Socratic-Clarifier offers several interaction modes:

1. **Enhanced Chat**: The main interface with document management and RAG context
   - Access at: `/enhanced`
   - Upload and manage documents
   - Use documents as context for AI analysis
   - Visualize the AI's reasoning process

2. **Reflective Mode**: Focused on the reflective ecosystem visualization
   - Access at: `/reflection`
   - See the meta-meta framework in action
   - Explore different reasoning paths

3. **Multimodal Analysis**: Process images and PDFs
   - Access at: `/multimodal`
   - Upload images or PDFs for processing
   - Extract text with OCR
   - Analyze visual content with multimodal models

## Configuration

Configuration options are available in `config.json`:

```json
{
    "integrations": {
        "ollama": {
            "enabled": true,
            "base_url": "http://localhost:11434/api",
            "default_model": "gemma3:latest",
            "multimodal_model": "llava:latest"
        }
    },
    "settings": {
        "prefer_provider": "auto",
        "use_llm_questions": true,
        "use_llm_reasoning": true,
        "use_sot": true,
        "use_multimodal": true
    }
}
```

## Troubleshooting

If you encounter issues:

1. Run the UI fix script:
   ```bash
   python fix_all_ui.py
   ```

2. Check the logs for error messages

3. Ensure Ollama is running and the required models are installed

4. Verify that Tesseract OCR is installed for document processing

5. See the `UI_FIXES_README.md` for specific fixes and solutions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the Socratic method of questioning
- Built with Flask, React, and Ollama
- Utilizes state-of-the-art language models for reasoning and analysis
