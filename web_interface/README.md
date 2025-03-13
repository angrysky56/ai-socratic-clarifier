# AI-Socratic-Clarifier Web Interface

This is a simple web interface for the AI-Socratic-Clarifier system. It allows users to:

1. Enter text for analysis
2. Select the operating mode (academic, casual, etc.)
3. View detected issues, questions, and reasoning
4. Provide feedback on the helpfulness of questions

## Running the Web Interface

```bash
# Install required dependencies
pip install flask

# Run the web server
cd web_interface
python app.py
```

Then open your browser to http://localhost:5000

## Features

- **Text Analysis**: Input text and select a mode
- **Issue Highlighting**: View detected issues with highlighting
- **SoT Reasoning**: See the reasoning process behind the questions
- **Feedback Collection**: Rate questions as helpful or not helpful

## Implementation Details

- Flask web server
- Bootstrap for styling
- JavaScript for dynamic interaction
- Feedback logging to help improve the system
