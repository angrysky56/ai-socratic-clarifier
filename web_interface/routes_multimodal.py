"""
Routes for the multimodal analysis integration.
"""

import os
import sys
import json
import tempfile
from flask import Blueprint, request, jsonify, render_template, current_app
import traceback
from loguru import logger
from werkzeug.utils import secure_filename

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import multimodal integration
try:
    from socratic_clarifier.multimodal_integration import process_file
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    logger.warning("Multimodal integration not available")

# Import direct integration for Socratic analysis
from web_interface import direct_integration

# Create a blueprint
multimodal_bp = Blueprint('multimodal', __name__)

@multimodal_bp.route('/multimodal', methods=['GET'])
def multimodal_page():
    """Render the multimodal analysis page."""
    return render_template('multimodal.html')

@multimodal_bp.route('/api/multimodal/process', methods=['POST'])
def process_document():
    """Process a document (image or PDF) with OCR and optional analysis."""
    if not MULTIMODAL_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Multimodal integration is not available. Please install the required dependencies.'
        }), 400
    
    try:
        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file was uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file was selected'
            }), 400
        
        # Get processing mode
        mode = request.form.get('mode', 'ocr')
        
        # Save the uploaded file to a temporary location
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(file_path)
        
        # Process the file based on the selected mode
        if mode == 'ocr':
            # OCR only mode
            result = process_file(file_path, use_multimodal=False)
            
            if result.get('success', False):
                return jsonify({
                    'success': True,
                    'text': result.get('text', ''),
                    'method': result.get('method', 'ocr')
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error during OCR processing')
                })
                
        elif mode == 'multimodal':
            # Multimodal analysis mode
            result = process_file(file_path, use_multimodal=True)
            
            if result.get('success', False):
                text = result.get('text', '') or result.get('content', '')
                analysis = result.get('content', '')
                
                return jsonify({
                    'success': True,
                    'text': text,
                    'analysis': analysis,
                    'method': result.get('method', 'multimodal'),
                    'model': result.get('model', 'Unknown')
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error during multimodal analysis')
                })
        
        elif mode == 'socratic':
            # Socratic analysis mode - first extract text, then analyze
            # Get socratic options from request
            max_questions = int(request.form.get('max_questions', '5'))
            use_sre = request.form.get('use_sre', '1') == '1'
            
            logger.info(f"Socratic analysis with max_questions={max_questions}, use_sre={use_sre}")
            
            result = process_file(file_path, use_multimodal=(mode=='multimodal'))
            
            if not result.get('success', False):
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error extracting text')
                })
            
            # Get the text from OCR or multimodal analysis
            text = result.get('text', '') or result.get('content', '')
            
            if not text.strip():
                return jsonify({
                    'success': False,
                    'error': 'No text could be extracted from the document'
                })
            
            # Analyze the extracted text with Socratic analysis
            try:
                # Pass max_questions and use_sre to direct_analyze_text
                analysis_result = direct_integration.direct_analyze_text(
                    text, 
                    'reflective' if use_sre else 'standard', 
                    use_sre,
                    max_questions=max_questions
                )
                
                return jsonify({
                    'success': True,
                    'text': text,
                    'method': result.get('method', 'ocr+socratic'),
                    'issues': analysis_result.get('issues', []),
                    'questions': analysis_result.get('questions', []),
                    'reasoning': analysis_result.get('reasoning'),
                    'sre_used': use_sre
                })
            except Exception as e:
                logger.error(f"Error in Socratic analysis: {e}")
                return jsonify({
                    'success': False,
                    'text': text,  # Still return the text even if analysis failed
                    'error': f"Error during Socratic analysis: {str(e)}"
                })
        else:
            return jsonify({
                'success': False,
                'error': f"Invalid processing mode: {mode}"
            }), 400
            
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f"Error processing document: {str(e)}"
        }), 500
    finally:
        # Clean up temporary files
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {e}")

@multimodal_bp.route('/api/multimodal/status', methods=['GET'])
def multimodal_status():
    """Get the status of multimodal integration."""
    status = {
        'available': MULTIMODAL_AVAILABLE
    }
    
    if MULTIMODAL_AVAILABLE:
        try:
            # Check for required dependencies
            from multimodal_integration import check_dependencies
            deps_status = check_dependencies()
            
            status['dependencies_installed'] = deps_status
            
            # Check for multimodal models
            try:
                # Load config
                config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                multimodal_model = config.get('integrations', {}).get('ollama', {}).get('multimodal_model', 'llava:latest')
                status['multimodal_model'] = multimodal_model
                
                # Check if model is available
                import requests
                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_names = [m.get('name') for m in models]
                    
                    status['available_models'] = model_names
                    status['configured_model_available'] = multimodal_model in model_names
            except Exception as e:
                logger.warning(f"Error checking multimodal models: {e}")
                status['model_check_error'] = str(e)
                
        except Exception as e:
            logger.error(f"Error checking multimodal status: {e}")
            status['error'] = str(e)
    
    return jsonify(status)
