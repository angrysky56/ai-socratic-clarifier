"""
Routes for the reflective ecosystem integration.
"""

from flask import Blueprint, request, jsonify
import traceback
from loguru import logger
from web_interface import direct_integration

# Create a blueprint
reflective_bp = Blueprint('reflective', __name__)

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
