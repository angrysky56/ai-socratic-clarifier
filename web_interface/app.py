def load_custom_patterns():
    """Load custom patterns from the custom_patterns directory if available."""
    patterns = {
        'vague': [],
        'gender_bias': [],
        'stereotype': [],
        'non_inclusive': []
    }
    
    patterns_dir = os.path.join(os.path.dirname(__file__), '..', 'custom_patterns')
    if not os.path.exists(patterns_dir):
        os.makedirs(patterns_dir, exist_ok=True)
        return patterns
    
    for pattern_type in patterns.keys():
        pattern_file = os.path.join(patterns_dir, f'{pattern_type}.json')
        if os.path.exists(pattern_file):
            try:
                with open(pattern_file, 'r') as f:
                    patterns[pattern_type] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading custom patterns for {pattern_type}: {e}")
    
    return patterns

"""
Web interface for the AI-Socratic-Clarifier.
"""

import sys
import os
import json
import re
from pathlib import Path
import traceback
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify
from socratic_clarifier import SocraticClarifier
from web_interface.api_settings import setup_api_routes

def load_config():
    """Load configuration from config.json."""
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
    default_config = {
        "integrations": {
            "lm_studio": {
                "enabled": True,
                "base_url": "http://localhost:1234/v1",
                "api_key": None,
                "default_model": "default",
                "timeout": 60
            },
            "ollama": {
                "enabled": True,
                "base_url": "http://localhost:11434/api",
                "api_key": None,
                "default_model": "llama3",
                "default_embedding_model": "nomic-embed-text",
                "timeout": 60
            }
        },
        "settings": {
            "prefer_provider": "auto",
            "use_llm_questions": True,
            "use_llm_reasoning": True,
            "use_sot": True,
            "use_multimodal": True
        }
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"Configuration loaded from {config_path}")
            return config
        else:
            print(f"Configuration file not found at {config_path}. Using default configuration.")
            return default_config
    except Exception as e:
        print(f"Error loading configuration: {e}. Using default configuration.")
        return default_config

# Load configuration
config = load_config()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'socratic-clarifier-key'

# Initialize the clarifier with the loaded configuration
clarifier = SocraticClarifier(config=config)

# Load and apply custom patterns to detectors
custom_patterns = load_custom_patterns()
if custom_patterns:
    logger.info("Loading custom detection patterns...")
    
    # Apply vague patterns
    if custom_patterns['vague'] and 'ambiguity' in clarifier.detectors:
        clarifier.detectors['ambiguity'].vague_terms = custom_patterns['vague']
        clarifier.detectors['ambiguity'].vague_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in custom_patterns['vague']
        ]
        logger.info(f"Loaded {len(custom_patterns['vague'])} custom vague term patterns")
    
    # Apply bias patterns
    if 'bias' in clarifier.detectors:
        if custom_patterns['gender_bias']:
            clarifier.detectors['bias'].gender_bias = custom_patterns['gender_bias']
            clarifier.detectors['bias'].gender_patterns = [
                re.compile(pattern, re.IGNORECASE) for pattern in custom_patterns['gender_bias']
            ]
            logger.info(f"Loaded {len(custom_patterns['gender_bias'])} custom gender bias patterns")
        
        if custom_patterns['stereotype']:
            clarifier.detectors['bias'].stereotypes = custom_patterns['stereotype']
            clarifier.detectors['bias'].stereotype_patterns = [
                re.compile(pattern, re.IGNORECASE) for pattern in custom_patterns['stereotype']
            ]
            logger.info(f"Loaded {len(custom_patterns['stereotype'])} custom stereotype patterns")
        
        if custom_patterns['non_inclusive']:
            clarifier.detectors['bias'].non_inclusive = custom_patterns['non_inclusive']
            clarifier.detectors['bias'].non_inclusive_patterns = [
                re.compile(pattern, re.IGNORECASE) for pattern in custom_patterns['non_inclusive']
            ]
            logger.info(f"Loaded {len(custom_patterns['non_inclusive'])} custom non-inclusive patterns")

# Set up the API routes for settings
setup_api_routes(app, config, clarifier)

# Add a navbar to the index page with a link to the settings page
@app.route('/', methods=['GET'])
def index():
    """Render the main page."""
    return render_template('index.html', modes=clarifier.available_modes())

@app.route('/settings', methods=['GET'])
def settings():
    """Render the settings page."""
    # Get current patterns from detectors
    vague_patterns = []
    gender_bias_patterns = []
    stereotype_patterns = []
    non_inclusive_patterns = []
    
    # Try to load from custom patterns first
    custom_patterns = load_custom_patterns()
    
    # Use custom patterns if available, otherwise get from detectors
    if custom_patterns['vague']:
        vague_patterns = custom_patterns['vague']
    elif 'ambiguity' in clarifier.detectors:
        vague_patterns = clarifier.detectors['ambiguity'].vague_terms
    
    if custom_patterns['gender_bias']:
        gender_bias_patterns = custom_patterns['gender_bias']
    elif 'bias' in clarifier.detectors:
        gender_bias_patterns = clarifier.detectors['bias'].gender_bias
    
    if custom_patterns['stereotype']:
        stereotype_patterns = custom_patterns['stereotype']
    elif 'bias' in clarifier.detectors:
        stereotype_patterns = clarifier.detectors['bias'].stereotypes
    
    if custom_patterns['non_inclusive']:
        non_inclusive_patterns = custom_patterns['non_inclusive']
    elif 'bias' in clarifier.detectors:
        non_inclusive_patterns = clarifier.detectors['bias'].non_inclusive
    
    # Get model settings from config
    ollama_model = config.get('integrations', {}).get('ollama', {}).get('default_model', 'llama3')
    ollama_embedding_model = config.get('integrations', {}).get('ollama', {}).get('default_embedding_model', 'nomic-embed-text')
    lm_studio_model = config.get('integrations', {}).get('lm_studio', {}).get('default_model', 'default')
    
    # Get system prompts
    question_prompt = """
You are an expert at creating Socratic questions to help improve communication clarity and reduce bias.
Based on the text and detected issues, generate thought-provoking questions that will help the author clarify their meaning, 
consider potential biases, and strengthen their reasoning.

Focus on questions that:
- Ask for clarification of ambiguous terms
- Challenge biased assumptions
- Request evidence for unsupported claims
- Identify logical inconsistencies
- Encourage deeper reflection

Your questions should be specific to the issues detected and should help improve the text.
"""
    
    reasoning_prompt = """
You are an expert at creating structured reasoning in the {paradigm} format.
Analyze the text and issues to create a concise reasoning diagram.

Use the following format for your response:

<think>
# Your structured reasoning here
</think>
"""
    
    return render_template(
        'settings.html',
        modes=clarifier.available_modes(),
        vague_patterns=vague_patterns,
        gender_bias_patterns=gender_bias_patterns,
        stereotype_patterns=stereotype_patterns,
        non_inclusive_patterns=non_inclusive_patterns,
        ollama_model=ollama_model,
        ollama_embedding_model=ollama_embedding_model,
        lm_studio_model=lm_studio_model,
        question_prompt=question_prompt,
        reasoning_prompt=reasoning_prompt
    )

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze text and return results."""
    try:
        # Get the data from the request
        data = request.get_json()
        text = data.get('text', '')
        mode = data.get('mode', 'standard')
        
        print(f"Analyzing text: '{text}' with mode: {mode}")
        
        # Set the mode and analyze
        clarifier.set_mode(mode)
        result = clarifier.analyze(text)
        
        # Debug output
        print(f"Detected {len(result.issues)} issues")
        for issue in result.issues:
            print(f"  - {issue.get('issue', 'Unknown')} - '{issue.get('term', '')}' ({issue.get('confidence', 0):.2f})")
        
        print(f"Generated {len(result.questions)} questions")
        for question in result.questions:
            print(f"  - {question}")
        
        # Prepare the response
        response = {
            'text': result.text,
            'issues': [
                {
                    'term': issue.get('term', ''),
                    'issue': issue.get('issue', ''),
                    'description': issue.get('description', ''),
                    'confidence': issue.get('confidence', 0)
                }
                for issue in result.issues
            ],
            'questions': result.questions,
            'reasoning': result.reasoning,
            'sot_paradigm': result.sot_paradigm,
            'confidence': result.confidence,
            'sot_enabled': config.get('settings', {}).get('use_sot', True),
            'provider': config.get('settings', {}).get('prefer_provider', 'auto')
        }
        
        return jsonify(response)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error analyzing text: {e}\n{error_traceback}")
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    """Record feedback on question effectiveness."""
    try:
        # Get the feedback data
        data = request.get_json()
        question = data.get('question', '')
        helpful = data.get('helpful', False)
        issue_type = data.get('issue_type', '')
        
        # In a real implementation, this would store feedback in a database
        # For this example, we'll just print it
        print(f"Feedback received: Question '{question}' was {'helpful' if helpful else 'not helpful'}")
        print(f"Issue type: {issue_type}")
        
        # Log the feedback (in a real app, save to database)
        feedback_dir = Path(__file__).parent / 'feedback'
        feedback_dir.mkdir(exist_ok=True)
        
        with open(feedback_dir / 'feedback_log.txt', 'a') as f:
            f.write(f"Question: {question}\n")
            f.write(f"Helpful: {helpful}\n")
            f.write(f"Issue Type: {issue_type}\n")
            f.write("-" * 50 + "\n")
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint to check if the server is working."""
    detectors = list(clarifier.detectors.keys())
    modes = clarifier.available_modes()
    return jsonify({
        'status': 'ok',
        'version': '0.1.0',
        'detectors': detectors,
        'modes': modes,
        'sot_available': clarifier.use_sot
    })

if __name__ == '__main__':
    # Create the templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create the feedback directory if it doesn't exist
    feedback_dir = os.path.join(os.path.dirname(__file__), 'feedback')
    os.makedirs(feedback_dir, exist_ok=True)
    
    app.run(debug=True, port=5000)
