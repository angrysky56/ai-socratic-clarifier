"""
Web interface for the enhanced AI-Socratic-Clarifier.
This version fixes the extra top bar issue and integrates the document deletion functionality.
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

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, redirect, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
from socratic_clarifier import SocraticClarifier
from web_interface.api_settings import setup_api_routes
from web_interface import direct_integration
from web_interface.routes_reflective import reflective_bp
from web_interface.document_rag_routes import document_rag_bp

# Import multimodal routes if available
try:
    from web_interface.routes_multimodal import multimodal_bp
    MULTIMODAL_ROUTES_AVAILABLE = True
except ImportError:
    MULTIMODAL_ROUTES_AVAILABLE = False
    logger.warning("Multimodal routes not available")

# Import our fixed direct_integration for document analysis
try:
    from web_interface.direct_integration_fixed import fixed_direct_analyze_text
    FIXED_INTEGRATION_AVAILABLE = True
    logger.info("Fixed direct integration for RAG available")
except ImportError:
    FIXED_INTEGRATION_AVAILABLE = False
    logger.warning("Fixed direct integration not available")

# Import reasoning templates routes
try:
    from web_interface.reasoning_templates_routes import reasoning_templates_bp
    REASONING_TEMPLATES_ROUTES_AVAILABLE = True
    logger.info("Reasoning templates routes available")
except ImportError:
    REASONING_TEMPLATES_ROUTES_AVAILABLE = False
    logger.warning("Reasoning templates routes not available")

# Import enhanced routes
try:
    from web_interface.enhanced_routes import enhanced_bp
    ENHANCED_ROUTES_AVAILABLE = True
except ImportError:
    ENHANCED_ROUTES_AVAILABLE = False
    logger.warning("Enhanced routes not available")

# Import settings routes
try:
    from web_interface.fixed_settings_routes import settings_bp
    SETTINGS_ROUTES_AVAILABLE = True
except ImportError:
    SETTINGS_ROUTES_AVAILABLE = False
    logger.warning("Settings routes not available")

# Import integrated routes
try:
    from web_interface.integrated_routes import integrated_bp
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

# Register the document RAG blueprint
app.register_blueprint(document_rag_bp)
logger.info("Document RAG routes registered")

# Register the enhanced routes blueprint
# Register enhanced routes if not registered already
if 'enhanced' not in app.blueprints and ENHANCED_ROUTES_AVAILABLE:
    app.register_blueprint(enhanced_bp)
    logger.info("Enhanced routes registered")
else:
    logger.info("Enhanced routes already registered")

# Register the reflective ecosystem blueprint
app.register_blueprint(reflective_bp)
logger.info("Reflective ecosystem routes registered")

# Register the multimodal blueprint if available
if MULTIMODAL_ROUTES_AVAILABLE:
    app.register_blueprint(multimodal_bp)
    logger.info("Multimodal routes registered")

# Register the settings routes blueprint
if SETTINGS_ROUTES_AVAILABLE:
    app.register_blueprint(settings_bp)
    logger.info("Settings routes registered")

# Register the reasoning templates routes blueprint
if REASONING_TEMPLATES_ROUTES_AVAILABLE:
    app.register_blueprint(reasoning_templates_bp)
    logger.info("Reasoning templates routes registered")

# Register the integrated blueprint if available
if INTEGRATED_ROUTES_AVAILABLE:
    app.register_blueprint(integrated_bp)
    logger.info("Integrated routes registered")

# Routes
@app.route('/', methods=['GET'])
def index():
    """Redirect to the unified Socratic UI."""
    return redirect('/socratic')

@app.route('/socratic')
def socratic_ui():
    """
    Unified Socratic UI with tabs for all functionality.
    """
    return render_template('socratic_ui.html')
                    
# Redirect old routes to the unified UI
@app.route('/integrated')
@app.route('/integrated_lite')
@app.route('/enhanced')
@app.route('/reflection')
def redirect_to_socratic():
    """
    Redirect old UI routes to the unified Socratic UI.
    """
    return redirect('/socratic')

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
        
        # Use fixed integration for document RAG if available
        if FIXED_INTEGRATION_AVAILABLE and rag_context:
            logger.info("Using fixed direct integration for document analysis")
            result = fixed_direct_analyze_text(
                text, 
                mode, 
                use_sot, 
                document_context=rag_context
            )
        else:
            # Fall back to regular direct integration
            try:
                result = direct_integration.direct_analyze_text(
                    text, 
                    mode, 
                    use_sot, 
                    document_context=rag_context
                )
            except TypeError as e:
                # Handle old version of direct_analyze_text without document_context param
                logger.warning(f"direct_analyze_text may have an incompatible signature: {e}")
                result = direct_integration.direct_analyze_text(text, mode, use_sot)
                # Add document context to the result manually if needed
                if rag_context:
                    result["document_context"] = rag_context
        
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

# Chat message endpoint
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
        
        # Use fixed integration for document RAG if available
        if FIXED_INTEGRATION_AVAILABLE and rag_context:
            logger.info("Using fixed direct integration for document analysis")
            result = fixed_direct_analyze_text(
                message, 
                mode, 
                use_sot, 
                document_context=rag_context
            )
        else:
            # Fall back to regular direct integration
            try:
                result = direct_integration.direct_analyze_text(
                    message, 
                    mode, 
                    use_sot, 
                    document_context=rag_context
                )
            except TypeError as e:
                # Handle old version of direct_analyze_text without document_context param
                logger.warning(f"direct_analyze_text may have an incompatible signature: {e}")
                result = direct_integration.direct_analyze_text(message, mode, use_sot)
                # Add document context to the result manually if needed
                if rag_context:
                    result["document_context"] = rag_context
        
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

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

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

# API endpoint for saving detector settings
@app.route('/api/settings/detectors', methods=['POST'])
def save_detector_settings():
    """Save detector settings to custom pattern files."""
    try:
        data = request.get_json()
        
        # Custom patterns directory
        patterns_dir = os.path.join(os.path.dirname(__file__), '..', 'custom_patterns')
        os.makedirs(patterns_dir, exist_ok=True)
        
        # Save each pattern type
        pattern_types = {
            'vague': data.get('vague', []),
            'gender_bias': data.get('gender_bias', []),
            'stereotype': data.get('stereotype', []),
            'non_inclusive': data.get('non_inclusive', [])
        }
        
        for pattern_type, patterns in pattern_types.items():
            file_name = 'vague.json' if pattern_type == 'vague' else f"{pattern_type.replace('_', '-')}.json"
            file_path = os.path.join(patterns_dir, file_name)
            
            with open(file_path, 'w') as f:
                json.dump(patterns, f, indent=2)
        
        # Apply to current detectors
        if 'ambiguity' in clarifier.detectors and pattern_types['vague']:
            clarifier.detectors['ambiguity'].vague_terms = pattern_types['vague']
            clarifier.detectors['ambiguity'].vague_patterns = [
                re.compile(pattern, re.IGNORECASE) for pattern in pattern_types['vague']
            ]
        
        if 'bias' in clarifier.detectors:
            if pattern_types['gender_bias']:
                clarifier.detectors['bias'].gender_bias = pattern_types['gender_bias']
                clarifier.detectors['bias'].gender_patterns = [
                    re.compile(pattern, re.IGNORECASE) for pattern in pattern_types['gender_bias']
                ]
            
            if pattern_types['stereotype']:
                clarifier.detectors['bias'].stereotypes = pattern_types['stereotype']
                clarifier.detectors['bias'].stereotype_patterns = [
                    re.compile(pattern, re.IGNORECASE) for pattern in pattern_types['stereotype']
                ]
            
            if pattern_types['non_inclusive']:
                clarifier.detectors['bias'].non_inclusive = pattern_types['non_inclusive']
                clarifier.detectors['bias'].non_inclusive_patterns = [
                    re.compile(pattern, re.IGNORECASE) for pattern in pattern_types['non_inclusive']
                ]
        
        return jsonify({
            'success': True,
            'message': 'Detector settings saved successfully'
        })
    except Exception as e:
        logger.error(f"Error saving detector settings: {e}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint for saving socratic reasoning settings
@app.route('/api/settings/socratic', methods=['POST'])
def save_socratic_settings():
    """Save socratic reasoning settings to the config file."""
    try:
        data = request.get_json()
        socratic_settings = data.get('socratic_reasoning', {})
        
        # Load current config
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update socratic reasoning settings
        if 'settings' not in config:
            config['settings'] = {}
            
        if 'socratic_reasoning' not in config['settings']:
            config['settings']['socratic_reasoning'] = {}
            
        # Update individual settings
        if 'enabled' in socratic_settings:
            config['settings']['socratic_reasoning']['enabled'] = socratic_settings['enabled']
            
        if 'reasoning_depth' in socratic_settings:
            config['settings']['socratic_reasoning']['reasoning_depth'] = socratic_settings['reasoning_depth']
            
        if 'system_prompt' in socratic_settings:
            config['settings']['socratic_reasoning']['system_prompt'] = socratic_settings['system_prompt']
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        # Update the app config
        app.config['CLARIFIER_CONFIG'] = config
        
        return jsonify({
            'success': True,
            'message': 'Socratic reasoning settings saved successfully'
        })
    except Exception as e:
        logger.error(f"Error saving socratic reasoning settings: {e}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
    app.run(debug=True, host="0.0.0.0", port=5000)
