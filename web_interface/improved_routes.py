"""
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
