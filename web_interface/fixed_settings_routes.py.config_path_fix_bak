"""
Settings routes for AI-Socratic-Clarifier.
This module provides API endpoints for managing application settings.
"""

import os
import sys
import json
from flask import Blueprint, request, jsonify, render_template, current_app
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create blueprint
settings_bp = Blueprint('settings', __name__)

def get_config_path():
    """Get the path to the config file."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))

def load_config():
    """Load configuration from config.json."""
    config_path = get_config_path()
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Configuration file not found at {config_path}. Using default configuration.")
            return {}
    except Exception as e:
        logger.error(f"Error loading configuration: {e}. Using default configuration.")
        return {}

def save_config(config):
    """Save configuration to config.json."""
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False

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

@settings_bp.route('/settings', methods=['GET'])
def settings_page():
    """Render the settings page."""
    # Get current patterns from detectors for settings page
    custom_patterns = load_custom_patterns()
    
    # Get model information from config
    config = load_config()
    
    ollama_model = config.get('integrations', {}).get('ollama', {}).get('default_model', 'gemma3:latest')
    multimodal_model = config.get('integrations', {}).get('ollama', {}).get('multimodal_model', 'llava:latest')
    embedding_model = config.get('integrations', {}).get('ollama', {}).get('default_embedding_model', 'nomic-embed-text:latest')
    
    return render_template(
        'fixed_settings_page.html',
        vague_patterns=custom_patterns['vague'],
        gender_bias_patterns=custom_patterns['gender_bias'],
        stereotype_patterns=custom_patterns['stereotype'],
        non_inclusive_patterns=custom_patterns['non_inclusive'],
        ollama_model=ollama_model,
        multimodal_model=multimodal_model,
        embedding_model=embedding_model,
        use_document_rag=config.get('settings', {}).get('use_document_rag', True)
    )

@settings_bp.route('/api/settings/detectors', methods=['POST'])
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
        
        # Update current app if available
        try:
            clarifier = current_app.clarifier
            if clarifier:
                # Apply vague patterns
                if 'ambiguity' in clarifier.detectors and pattern_types['vague']:
                    clarifier.detectors['ambiguity'].vague_terms = pattern_types['vague']
                
                # Apply bias patterns
                if 'bias' in clarifier.detectors:
                    if pattern_types['gender_bias']:
                        clarifier.detectors['bias'].gender_bias = pattern_types['gender_bias']
                    
                    if pattern_types['stereotype']:
                        clarifier.detectors['bias'].stereotypes = pattern_types['stereotype']
                    
                    if pattern_types['non_inclusive']:
                        clarifier.detectors['bias'].non_inclusive = pattern_types['non_inclusive']
        except Exception as e:
            logger.error(f"Error updating clarifier detectors: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Detector settings saved successfully'
        })
    except Exception as e:
        logger.error(f"Error saving detector settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/models', methods=['POST'])
def save_model_settings():
    """Save model settings to config.json."""
    try:
        data = request.get_json()
        
        # Load current config
        config = load_config()
        
        # Update model settings
        if 'integrations' not in config:
            config['integrations'] = {}
        if 'ollama' not in config['integrations']:
            config['integrations']['ollama'] = {}
        
        # Update ollama model settings
        if 'ollama_model' in data:
            config['integrations']['ollama']['default_model'] = data['ollama_model']
        
        if 'multimodal_model' in data:
            config['integrations']['ollama']['multimodal_model'] = data['multimodal_model']
        
        if 'embedding_model' in data:
            config['integrations']['ollama']['default_embedding_model'] = data['embedding_model']
        
        # Update provider preference
        if 'preferred_provider' in data:
            if 'settings' not in config:
                config['settings'] = {}
            config['settings']['prefer_provider'] = data['preferred_provider']
        
        # Update temperature
        if 'temperature' in data:
            if 'settings' not in config:
                config['settings'] = {}
            config['settings']['temperature'] = float(data['temperature'])
        
        # Save updated config
        if save_config(config):
            return jsonify({
                'success': True,
                'message': 'Model settings saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error saving configuration'
            }), 500
    except Exception as e:
        logger.error(f"Error saving model settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/general', methods=['POST'])
def save_general_settings():
    """Save general settings to config.json."""
    try:
        data = request.get_json()
        
        # Load current config
        config = load_config()
        
        # Ensure settings section exists
        if 'settings' not in config:
            config['settings'] = {}
        
        # Update settings
        if 'default_mode' in data:
            config['settings']['default_mode'] = data['default_mode']
        
        if 'enable_sot' in data:
            config['settings']['use_sot'] = data['enable_sot']
        
        if 'enable_rag' in data:
            config['settings']['use_document_rag'] = data['enable_rag']
        
        if 'enable_sre' in data:
            config['settings']['use_reflective_ecosystem'] = data['enable_sre']
        
        if 'show_analysis' in data:
            config['settings']['show_analysis_details'] = data['show_analysis']
        
        if 'dark_mode' in data:
            config['settings']['dark_mode'] = data['dark_mode']
        
        # Save updated config
        if save_config(config):
            return jsonify({
                'success': True,
                'message': 'General settings saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error saving configuration'
            }), 500
    except Exception as e:
        logger.error(f"Error saving general settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/settings/system', methods=['POST'])
def save_system_settings():
    """Save system settings to config.json."""
    try:
        data = request.get_json()
        
        # Load current config
        config = load_config()
        
        # Ensure settings section exists
        if 'settings' not in config:
            config['settings'] = {}
        
        # Update settings
        if 'max_context_size' in data:
            config['settings']['max_context_size'] = int(data['max_context_size'])
        
        if 'system_prompt' in data:
            config['settings']['system_prompt'] = data['system_prompt']
        
        # Save updated config
        if save_config(config):
            return jsonify({
                'success': True,
                'message': 'System settings saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error saving configuration'
            }), 500
    except Exception as e:
        logger.error(f"Error saving system settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history."""
    try:
        # This is a placeholder - in a real application, you would clear the chat history
        return jsonify({
            'success': True,
            'message': 'Chat history cleared successfully'
        })
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
