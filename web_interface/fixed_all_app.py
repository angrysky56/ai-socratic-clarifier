'''
Web interface for the AI-Socratic-Clarifier with all fixes applied.
'''

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
from web_interface import direct_integration
from web_interface.routes_reflective import reflective_bp
from web_interface.improved_routes import improved_bp

# Import multimodal routes if available
try:
    from web_interface.routes_multimodal import multimodal_bp
    MULTIMODAL_ROUTES_AVAILABLE = True
except ImportError:
    MULTIMODAL_ROUTES_AVAILABLE = False
    logger.warning("Multimodal routes not available")

# Load configuration - shortened for brevity
def load_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

# Load configuration
config = load_config()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'socratic-clarifier-key'

# Initialize the clarifier with the loaded configuration
clarifier = SocraticClarifier(config=config)

# Set up the API routes for settings
setup_api_routes(app, config, clarifier)

# Register the reflective ecosystem blueprint
app.register_blueprint(reflective_bp)

# Register the improved routes blueprint
app.register_blueprint(improved_bp)

# Register the multimodal blueprint if available
if MULTIMODAL_ROUTES_AVAILABLE:
    app.register_blueprint(multimodal_bp)
    logger.info("Multimodal routes registered")

# Routes - only keeping the essential routes for brevity
@app.route('/', methods=['GET'])
def index():
    # Render the main page.
    return render_template('index.html', modes=clarifier.available_modes())

@app.route('/chat', methods=['GET'])
def chat():
    # Render the chat interface.
    return render_template('chat.html', modes=clarifier.available_modes())

@app.route('/settings', methods=['GET'])
def settings():
    # Render the settings page.
    return render_template('settings.html', modes=clarifier.available_modes())

if __name__ == '__main__':
    # Create the templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create the feedback directory if it doesn't exist
    feedback_dir = os.path.join(os.path.dirname(__file__), 'feedback')
    os.makedirs(feedback_dir, exist_ok=True)
    
    # Start the application
    print("Starting AI-Socratic-Clarifier with all fixes applied")
    print("Access URLs:")
    print("  - http://localhost:5000/ - Home page")
    print("  - http://localhost:5000/multimodal - Original multimodal analysis")
    print("  - http://localhost:5000/improved_multimodal - Improved multimodal analysis")
    print("  - http://localhost:5000/reflection - Reflective analysis")
    print("  - http://localhost:5000/improved_reflection - Improved reflective analysis")
    app.run(debug=True, port=5000)
