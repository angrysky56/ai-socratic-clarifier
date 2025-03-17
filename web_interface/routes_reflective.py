"""
Routes for the reflective ecosystem integration.
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, current_app as app
import traceback
from loguru import logger
from web_interface import direct_integration

# Create a blueprint
reflective_bp = Blueprint('reflective', __name__)

@reflective_bp.route('/reflection', methods=['GET', 'POST'])
def reflection_page():
    """Render the reflective ecosystem interface."""
    try:
        # Handle POST request from multimodal analysis to receive text
        if request.method == 'POST':
            logger.info("Received POST request to /reflection")
            text = request.form.get('text', '')
            is_debug = request.form.get('debug', '0') == '1'
            
            if is_debug:
                logger.info(f"Debug mode: text length = {len(text)}")
                
            # Get mode if present
            mode = request.form.get('mode', '')
            if mode:
                # Store the mode in session
                try:
                    session['preferred_mode'] = mode
                    logger.info(f"Stored preferred mode in session: {mode}")
                except Exception as e:
                    logger.error(f"Error storing mode in session: {e}")
                    
            if text:
                # Store the text in session for the template to use
                try:
                    session['reflection_text'] = text
                    logger.info("Successfully stored text in session")
                except Exception as e:
                    logger.error(f"Error storing text in session: {e}")
                    if is_debug:
                        return jsonify({
                            'success': False, 
                            'error': f"Session error: {str(e)}"
                        }), 500
                    raise
                
                # Redirect to GET to avoid form resubmission issues
                redirect_url = url_for('reflective.reflection_page')
                if mode:
                    redirect_url += f"?mode={mode}"
                return redirect(redirect_url)
        
        # For GET requests, check if we have text in the URL parameters
        text_param = request.args.get('text', '')
        if text_param and len(text_param) < 2000:  # Only use if reasonable length
            session['reflection_text'] = text_param
        
        # Check if the reflective ecosystem is available
        status = direct_integration.get_reflective_ecosystem_status()
        
        # Get any text from session
        try:
            reflection_text = session.get('reflection_text', '')
            logger.info(f"Retrieved text from session: {len(reflection_text)} characters")
        except Exception as e:
            logger.error(f"Error retrieving text from session: {e}")
            reflection_text = ''
        
        # Clear the session if requested
        if request.args.get('clear') == '1':
            try:
                session.pop('reflection_text', None)
                reflection_text = ''
                logger.info("Cleared reflection_text from session")
            except Exception as e:
                logger.error(f"Error clearing session: {e}")
        
        # Get available modes from the clarifier
        from socratic_clarifier import SocraticClarifier
        modes = []
        try:
            # Try to get available modes from the app's clarifier
            if hasattr(app, 'clarifier') and app.clarifier:
                modes = app.clarifier.available_modes()
            else:
                # Create a temporary clarifier to get modes
                clarifier = SocraticClarifier()
                modes = clarifier.available_modes()
        except Exception as e:
            logger.error(f"Error getting available modes: {e}")
            # Fallback modes
            modes = ['standard', 'deep', 'reflective']
        
        # Show session debug info in development
        session_debug = {}
        if app.debug:
            try:
                session_debug = dict(session)
            except Exception as e:
                session_debug = {"error": str(e)}
        
        return render_template('reflection.html', 
                            reflective_ecosystem=status,
                            reflection_text=reflection_text,
                            session_debug=session_debug,
                            modes=modes)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error in reflection_page: {e}\n{error_traceback}")
        return f"<h1>Error</h1><p>An error occurred: {e}</p><pre>{error_traceback}</pre>", 500

@reflective_bp.route('/api/reflective/status', methods=['GET'])
def reflective_status():
    """Get the status of the reflective ecosystem."""
    try:
        status = direct_integration.get_reflective_ecosystem_status()
        return jsonify(status)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error getting reflective ecosystem status: {e}\n{error_traceback}")
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

@reflective_bp.route('/api/reflective/analyze', methods=['POST'])
def reflective_analyze():
    """Analyze text using the reflective ecosystem."""
    try:
        # Get the data from the request
        data = request.get_json()
        text = data.get('text', '')
        mode = data.get('mode', 'standard')
        use_sot = data.get('use_sot', True)
        
        logger.info(f"Analyzing text with reflective ecosystem: '{text}' (mode: {mode}, use_sot: {use_sot})")
        
        # Use direct integration to analyze the text
        result = direct_integration.direct_analyze_text(text, mode, use_sot)
        
        return jsonify(result)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error analyzing with reflective ecosystem: {e}\n{error_traceback}")
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

@reflective_bp.route('/api/reflective/debug', methods=['GET'])
def debug_session():
    """Debug route to check session configuration."""
    try:
        # Test setting a value in session
        session['test_key'] = 'test_value'
        
        # Return session info
        return jsonify({
            'success': True,
            'session_working': True,
            'session_keys': list(session.keys()),
            'test_value': session.get('test_key')
        })
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Session error: {e}\n{error_traceback}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_traceback
        }), 500

@reflective_bp.route('/api/reflective/feedback', methods=['POST'])
def reflective_feedback():
    """Process feedback through the reflective ecosystem."""
    try:
        # Get the feedback data
        data = request.get_json()
        question = data.get('question', '')
        helpful = data.get('helpful', False)
        paradigm = data.get('paradigm')
        
        logger.info(f"Processing feedback for question: '{question}' (helpful: {helpful}, paradigm: {paradigm})")
        
        # Process the feedback
        success = direct_integration.process_feedback(question, helpful, paradigm)
        
        return jsonify({'success': success})
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error processing reflective feedback: {e}\n{error_traceback}")
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500
