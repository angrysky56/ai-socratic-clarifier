"""
Enhanced web interface for the AI-Socratic-Clarifier.
This version integrates all components into a unified experience with improved UI.
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

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from socratic_clarifier import SocraticClarifier
from web_interface.api_settings import setup_api_routes
from web_interface import direct_integration

# Import route blueprints
from web_interface.routes_reflective import reflective_bp
from web_interface.document_rag_routes import document_rag_bp

# Import multimodal routes if available
try:
    from web_interface.routes_multimodal import multimodal_bp
    MULTIMODAL_ROUTES_AVAILABLE = True
except ImportError:
    MULTIMODAL_ROUTES_AVAILABLE = False
    logger.warning("Multimodal routes not available")

# Import improved routes if available
try:
    from web_interface.routes_integrated import integrated_bp
    INTEGRATED_ROUTES_AVAILABLE = True
except ImportError:
    INTEGRATED_ROUTES_AVAILABLE = False
    logger.warning("Integrated routes not available")

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

def load_config():
    """Load configuration from ../../../../../../../../config.json."""
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '../../../../../../../../config.json'))
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
            "use_multimodal": True,
            "use_document_rag": True
        }
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        else:
            logger.warning(f"Configuration file not found at {config_path}. Using default configuration.")
            return default_config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}. Using default configuration.")
        return default_config

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'socratic-clarifier-enhanced-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Fix for proxy server setup
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Load configuration
config = load_config()
app.config['CLARIFIER_CONFIG'] = config

# Initialize the clarifier with the loaded configuration
clarifier = SocraticClarifier(config=config)
app.clarifier = clarifier

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

# Register the reflective ecosystem blueprint
app.register_blueprint(reflective_bp)

# Register the document RAG blueprint
app.register_blueprint(document_rag_bp)

# Register the multimodal blueprint if available
if MULTIMODAL_ROUTES_AVAILABLE:
    app.register_blueprint(multimodal_bp)
    logger.info("Multimodal routes registered")

# Register the integrated blueprint if available
if INTEGRATED_ROUTES_AVAILABLE:
    app.register_blueprint(integrated_bp)
    logger.info("Integrated routes registered")

# Redirect root to index page
@app.route('/', methods=['GET'])
def index():
    """Render the main page."""
    return render_template('index.html', modes=clarifier.available_modes())

# Chat interface route
@app.route('/chat', methods=['GET'])
def chat():
    """Render the chat interface."""
    return render_template('chat.html', modes=clarifier.available_modes())

# Route for processing chat messages
@app.route('/chat', methods=['POST'])
def chat_message():
    """Process a chat message and return a response."""
    try:
        # Get the data from the request
        data = request.get_json()
        message = data.get('message', '')
        mode = data.get('mode', 'standard')
        use_sot = data.get('use_sot', True)
        use_rag = data.get('use_rag', False)
        document_context = data.get('document_context', [])
        
        logger.info(f"Received message: '{message}' with mode: {mode}, use_sot: {use_sot}, use_rag: {use_rag}")
        
        # If RAG is enabled, retrieve relevant document context
        rag_context = []
        if use_rag and config.get('settings', {}).get('use_document_rag', False):
            try:
                # Include provided document context
                rag_context = document_context
                
                # If no specific documents were provided, search for relevant context
                if not rag_context and message:
                    from web_interface.document_rag_routes import retrieve_relevant_context
                    results = retrieve_relevant_context(message, limit=3)
                    if results:
                        rag_context = [
                            {
                                "document_id": result.get("document_id"),
                                "filename": result.get("filename"),
                                "content": result.get("content"),
                                "relevance": result.get("relevance", 0.0)
                            }
                            for result in results
                        ]
                        logger.info(f"Retrieved {len(rag_context)} relevant document chunks for RAG")
            except Exception as rag_error:
                logger.error(f"Error retrieving RAG context: {rag_error}")
        
        # Use direct integration to analyze the text
        result = direct_integration.direct_analyze_text(
            message, 
            mode, 
            use_sot, 
            document_context=rag_context
        )
        
        # Generate a response based on the analysis
        if result['issues'] and result['questions']:
            # Craft a response that includes one of the Socratic questions
            reply = f"I've analyzed your statement and have some thoughts to share. {result['questions'][0]}"
            
            # If there are more questions, include a followup
            if len(result['questions']) > 1:
                reply += f" I also wonder: {result['questions'][1]}"
                
            # If we used document context, mention that
            if rag_context:
                reply += f"\n\n(Analysis included context from {len(rag_context)} document(s))"
        else:
            # Default response if no issues detected
            reply = "I've considered your statement. It seems clear and well-formed. Do you have any other thoughts you'd like to explore?"
        
        # Prepare the response data
        response = {
            'reply': reply,
            'text': message,
            'issues': result['issues'],
            'questions': result['questions'],
            'reasoning': result['reasoning'],
            'sot_paradigm': result['sot_paradigm'],
            'confidence': result['confidence'],
            'sot_enabled': result['sot_enabled'],
            'model': result['model'],
            'provider': result['provider'],
            'document_context': rag_context
        }
        
        return jsonify(response)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error processing chat message: {e}\n{error_traceback}")
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

# Settings page route
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
        reasoning_prompt=reasoning_prompt,
        use_document_rag=config.get('settings', {}).get('use_document_rag', True)
    )

# Text analysis endpoint
@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze text and return results."""
    try:
        # Get the data from the request
        data = request.get_json()
        text = data.get('text', '')
        mode = data.get('mode', 'standard')
        use_sot = data.get('use_sot', True)
        use_rag = data.get('use_rag', False)
        document_context = data.get('document_context', [])
        
        logger.info(f"Analyzing text: '{text}' with mode: {mode}, use_sot: {use_sot}, use_rag: {use_rag}")
        
        # If RAG is enabled, retrieve relevant document context
        rag_context = []
        if use_rag and config.get('settings', {}).get('use_document_rag', False):
            try:
                # Include provided document context
                rag_context = document_context
                
                # If no specific documents were provided, search for relevant context
                if not rag_context and text:
                    from web_interface.document_rag_routes import retrieve_relevant_context
                    results = retrieve_relevant_context(text, limit=3)
                    if results:
                        rag_context = [
                            {
                                "document_id": result.get("document_id"),
                                "filename": result.get("filename"),
                                "content": result.get("content"),
                                "relevance": result.get("relevance", 0.0)
                            }
                            for result in results
                        ]
                        logger.info(f"Retrieved {len(rag_context)} relevant document chunks for RAG")
            except Exception as rag_error:
                logger.error(f"Error retrieving RAG context: {rag_error}")
        
        # Use direct integration to analyze the text
        result = direct_integration.direct_analyze_text(
            text, 
            mode, 
            use_sot, 
            document_context=rag_context
        )
        
        # Prepare the response
        response = {
            'text': result['text'],
            'issues': result['issues'],
            'questions': result['questions'],
            'reasoning': result['reasoning'],
            'sot_paradigm': result['sot_paradigm'],
            'confidence': result['confidence'],
            'sot_enabled': result['sot_enabled'],
            'provider': result['provider'],
            'document_context': rag_context
        }
        
        return jsonify(response)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error analyzing text: {e}\n{error_traceback}")
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

# Feedback endpoint
@app.route('/feedback', methods=['POST'])
def feedback():
    """Record feedback on question effectiveness."""
    try:
        # Get the feedback data
        data = request.get_json()
        question = data.get('question', '')
        helpful = data.get('helpful', False)
        issue_type = data.get('issue_type', '')
        paradigm = data.get('paradigm')
        
        # Log the feedback
        logger.info(f"Feedback received: Question '{question}' was {'helpful' if helpful else 'not helpful'}")
        logger.info(f"Issue type: {issue_type}, Paradigm: {paradigm}")
        
        # Log to file
        feedback_dir = Path(__file__).parent / 'feedback'
        feedback_dir.mkdir(exist_ok=True)
        
        with open(feedback_dir / 'feedback_log.txt', 'a') as f:
            f.write(f"Question: {question}\n")
            f.write(f"Helpful: {helpful}\n")
            f.write(f"Issue Type: {issue_type}\n")
            f.write(f"Paradigm: {paradigm}\n")
            f.write("-" * 50 + "\n")
        
        # Process through reflective ecosystem if available
        reflective_success = direct_integration.process_feedback(question, helpful, paradigm)
        
        return jsonify({
            'success': True,
            'reflective_processed': reflective_success
        })
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error processing feedback: {e}\n{error_traceback}")
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

# API test endpoint
@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint to check if the server is working."""
    detectors = list(clarifier.detectors.keys())
    modes = clarifier.available_modes()
    return jsonify({
        'status': 'ok',
        'version': '0.2.0',
        'detectors': detectors,
        'modes': modes,
        'sot_available': clarifier.use_sot,
        'document_rag_available': config.get('settings', {}).get('use_document_rag', False),
        'provider': config.get('settings', {}).get('prefer_provider', 'auto'),
        'model': config.get('integrations', {}).get('ollama', {}).get('default_model', 'llama3')
    })

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

if __name__ == '__main__':
    # Create required directories
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'img'), exist_ok=True)
    
    feedback_dir = os.path.join(os.path.dirname(__file__), 'feedback')
    os.makedirs(feedback_dir, exist_ok=True)
    
    # Start the server
    app.run(debug=True, host='0.0.0.0', port=5000)