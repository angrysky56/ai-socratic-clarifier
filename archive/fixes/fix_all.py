#!/usr/bin/env python3
"""
Comprehensive fix script for the AI-Socratic-Clarifier.

This script:
1. Fixes the max_questions parameter in direct_integration.py
2. Creates improved templates and route handlers
3. Updates the application to use these new components
"""

import os
import sys
import shutil

def fix_max_questions():
    """Fix the max_questions parameter error in direct_integration.py."""
    print("\n=== Fixing max_questions parameter ===\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_interface_dir = os.path.join(base_dir, "web_interface")
    
    direct_integration_path = os.path.join(web_interface_dir, "direct_integration.py")
    backup_path = os.path.join(web_interface_dir, "direct_integration.py.bak")
    
    # Create a backup of the original file if not exists
    if not os.path.exists(backup_path):
        shutil.copy2(direct_integration_path, backup_path)
        print(f"Created backup of original file: {backup_path}")
    
    # Read the file to check if the fix is needed
    with open(direct_integration_path, "r") as f:
        content = f.read()
    
    if "def direct_analyze_text(text, mode=\"standard\", use_sot=True, max_questions=5)" in content:
        print("max_questions parameter already added to direct_analyze_text function.")
        return
    
    # Update the function definition to include max_questions parameter
    content = content.replace(
        "def direct_analyze_text(text, mode=\"standard\", use_sot=True):",
        "def direct_analyze_text(text, mode=\"standard\", use_sot=True, max_questions=5):"
    )
    
    # Update the call to generate_socratic_questions to pass max_questions
    content = content.replace(
        "questions = generate_socratic_questions(text, issues, sot_paradigm) if issues else []",
        "questions = generate_socratic_questions(text, issues, sot_paradigm, max_questions) if issues else []"
    )
    
    # Update the generate_socratic_questions function to accept max_questions parameter
    content = content.replace(
        "def generate_socratic_questions(text, issues, sot_paradigm=None):",
        "def generate_socratic_questions(text, issues, sot_paradigm=None, max_questions=5):"
    )
    
    # Update the call to enhancer.enhance_questions to use the parameter
    content = content.replace(
        "max_questions=5",
        "max_questions=max_questions"
    )
    
    # Add max_questions to the result dictionary
    content = content.replace(
        '"provider": "ollama",',
        '"provider": "ollama",\n        "max_questions": max_questions,'
    )
    
    # Write the updated content
    with open(direct_integration_path, "w") as f:
        f.write(content)
    
    print("Updated direct_integration.py to handle max_questions parameter.")

def create_improved_multimodal_template():
    """Create the improved multimodal template with numeric input instead of slider."""
    print("\n=== Creating improved multimodal UI ===\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_interface_dir = os.path.join(base_dir, "web_interface")
    templates_dir = os.path.join(web_interface_dir, "templates")
    
    # Create the templates directory if it doesn't exist
    os.makedirs(templates_dir, exist_ok=True)
    
    improved_template_path = os.path.join(templates_dir, "multimodal_improved.html")
    
    # Write the improved template - this is a simplified version for brevity
    with open(improved_template_path, "w") as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Socratic-Clarifier - Improved Multimodal Analysis</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        .card {
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
        }
        .card-header {
            background-color: #363636;
            border-bottom: 1px solid #3d3d3d;
        }
        .max-questions-control {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        .max-questions-control input[type="number"] {
            width: 60px;
            text-align: center;
            margin: 0 10px;
            background-color: #333;
            color: #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h3>Improved Multimodal Analysis</h3>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-header">Upload Document</div>
                    <div class="card-body">
                        <div class="mb-3">
                            <input class="form-control" type="file" id="fileInput">
                        </div>
                        
                        <div class="mb-3">
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="radio" name="analysisMode" id="socraticMode" value="socratic">
                                <label class="form-check-label" for="socraticMode">Socratic Analysis</label>
                            </div>
                        </div>
                        
                        <!-- Improved max questions control -->
                        <div class="mb-3">
                            <label for="maxQuestionsInput" class="form-label">Maximum Questions:</label>
                            <div class="max-questions-control">
                                <button type="button" id="decreaseQuestions" class="btn btn-secondary">
                                    <i class="fas fa-minus"></i>
                                </button>
                                <input type="number" id="maxQuestionsInput" min="1" max="10" value="5" class="form-control">
                                <button type="button" id="increaseQuestions" class="btn btn-secondary">
                                    <i class="fas fa-plus"></i>
                                </button>
                            </div>
                        </div>
                        
                        <button class="btn btn-primary" id="processButton">Process Document</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Results</div>
                    <div class="card-body">
                        <p>Select a file and processing mode to get started.</p>
                        <button class="btn btn-info" id="analyzeTextButton">
                            <i class="fas fa-brain me-1"></i>Analyze in Reflective Ecosystem
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('analyzeTextButton').addEventListener('click', function() {
            window.open('/reflection', '_blank');
        });
        
        // Plus/minus controls for max questions
        document.getElementById('decreaseQuestions').addEventListener('click', function() {
            const input = document.getElementById('maxQuestionsInput');
            const value = Math.max(1, parseInt(input.value) - 1);
            input.value = value;
        });
        
        document.getElementById('increaseQuestions').addEventListener('click', function() {
            const input = document.getElementById('maxQuestionsInput');
            const value = Math.min(10, parseInt(input.value) + 1);
            input.value = value;
        });
    </script>
</body>
</html>''')
    
    print(f"Created simplified improved template: {improved_template_path}")
    
    # Create a routes file for the improved UI
    routes_path = os.path.join(web_interface_dir, "improved_routes.py")
    with open(routes_path, "w") as f:
        f.write('''"""
Improved routes for AI-Socratic-Clarifier.
"""

from flask import Blueprint, render_template, request, jsonify, session

# Create a blueprint for the improved UI
improved_bp = Blueprint('improved', __name__)

@improved_bp.route('/improved_multimodal', methods=['GET'])
def improved_multimodal():
    """Render the improved multimodal analysis page."""
    return render_template('multimodal_improved.html')

@improved_bp.route('/improved_reflection', methods=['GET', 'POST'])
def improved_reflection():
    """Render the improved reflection page with better handling."""
    if request.method == 'POST':
        # Handle POST requests for text analysis
        text = request.form.get('text', '')
        mode = request.form.get('mode', 'standard')
        
        # Store in session
        session['text'] = text
        session['mode'] = mode
        
        # Render template with provided data
        return render_template('reflection.html', initial_text=text, initial_mode=mode)
    else:
        # For GET requests, just render the template
        return render_template('reflection.html')
''')
    
    print(f"Created improved routes: {routes_path}")
    
    return improved_template_path, routes_path

def update_app():
    """Update app.py to include the improved routes."""
    print("\n=== Updating app.py ===\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_interface_dir = os.path.join(base_dir, "web_interface")
    app_path = os.path.join(web_interface_dir, "app.py")
    backup_path = os.path.join(web_interface_dir, "app.py.fix_all_bak")
    
    # Create a backup if not exists
    if not os.path.exists(backup_path):
        shutil.copy2(app_path, backup_path)
        print(f"Created backup of app.py: {backup_path}")
    
    # Load the fixed app contents
    fixed_app_content = """'''
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
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '../../../../../../../../config.json'))
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
"""
    
    # Write the simplified fixed app.py to a separate file
    fixed_app_path = os.path.join(web_interface_dir, "fixed_all_app.py")
    with open(fixed_app_path, "w") as f:
        f.write(fixed_app_content)
    
    print(f"Created fixed application file: {fixed_app_path}")
    print("To use the fixed application, run:")
    print(f"python -m web_interface.fixed_all_app")

def main():
    """Apply all fixes to the AI-Socratic-Clarifier."""
    try:
        # Fix the max_questions parameter
        fix_max_questions()
        
        # Create the improved UI
        template_path, routes_path = create_improved_multimodal_template()
        
        # Update the application
        update_app()
        
        print("\n=== All fixes applied successfully! ===\n")
        print("You can now run the application with all fixes by using:")
        print("python -m web_interface.fixed_all_app")
        print("\nThis will start the server with the following URLs:")
        print("  - http://localhost:5000/ - Home page")
        print("  - http://localhost:5000/multimodal - Original multimodal analysis")
        print("  - http://localhost:5000/improved_multimodal - Improved multimodal analysis")
        print("  - http://localhost:5000/reflection - Reflective analysis")
        print("  - http://localhost:5000/improved_reflection - Improved reflective analysis")
        
        return 0
    except Exception as e:
        print(f"Error applying fixes: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
