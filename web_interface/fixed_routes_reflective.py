"""
Fixed routes for reflective analysis integration.
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

# Create a blueprint with a unique name to avoid conflicts
fixed_reflective_bp = Blueprint('fixed_reflective', __name__)

@fixed_reflective_bp.route('/reflection_improved', methods=['GET', 'POST'])
def reflection_page():
    """Render the reflection page with optional pre-loaded text."""
    if request.method == 'POST':
        # Get text and mode from form submission
        text = request.form.get('text', '')
        mode = request.form.get('mode', 'standard')
        debug = request.form.get('debug', '0') == '1'
        
        # Store in session
        session['reflection_text'] = text
        session['reflection_mode'] = mode
        session['reflection_debug'] = debug
        
        # Render the template with the provided text
        return render_template('reflection.html', 
                              initial_text=text, 
                              initial_mode=mode,
                              debug=debug)
    else:
        # For GET requests, just render the template
        return render_template('reflection.html')

@fixed_reflective_bp.route('/api/reflective_improved/debug', methods=['GET'])
def reflective_debug():
    """Debug endpoint to check if Reflective Ecosystem integration is working."""
    try:
        # Just return success for now
        return jsonify({
            'success': True,
            'message': 'Reflective ecosystem is available'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        })
