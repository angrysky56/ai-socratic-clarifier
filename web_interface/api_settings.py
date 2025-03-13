"""
API endpoints for the web interface settings.
"""

import os
import json
import re
import traceback
from flask import jsonify, request
from loguru import logger

# Function to save updated config to file
def save_config(config_data):
    """Save updated configuration to config.json file."""
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
    try:
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def setup_api_routes(app, config, clarifier):
    """Set up all the API routes for settings."""
    
    @app.route('/api/settings/general', methods=['POST'])
    def api_settings_general():
        """Save general settings."""
        try:
            data = request.get_json()
            
            # Update config
            if 'default_mode' in data:
                app.config['DEFAULT_MODE'] = data['default_mode']
            
            if 'use_sot' in data:
                config['settings']['use_sot'] = data['use_sot']
            
            # Save updated config
            save_config(config)
            
            return jsonify({'success': True})
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error saving general settings: {e}\n{error_traceback}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings/patterns/<pattern_type>', methods=['POST'])
    def api_settings_patterns(pattern_type):
        """Save detection patterns."""
        try:
            data = request.get_json()
            patterns = data.get('patterns', [])
            
            # Validate pattern type
            valid_types = ['vague', 'gender_bias', 'stereotype', 'non_inclusive']
            if pattern_type not in valid_types:
                return jsonify({'error': f'Invalid pattern type: {pattern_type}'}), 400
                
            # Update the appropriate detector
            if pattern_type == 'vague' and 'ambiguity' in clarifier.detectors:
                clarifier.detectors['ambiguity'].vague_terms = patterns
            elif pattern_type == 'gender_bias' and 'bias' in clarifier.detectors:
                clarifier.detectors['bias'].gender_bias = patterns
            elif pattern_type == 'stereotype' and 'bias' in clarifier.detectors:
                clarifier.detectors['bias'].stereotypes = patterns
            elif pattern_type == 'non_inclusive' and 'bias' in clarifier.detectors:
                clarifier.detectors['bias'].non_inclusive = patterns
            
            # Recompile patterns for the detector
            if pattern_type == 'vague' and 'ambiguity' in clarifier.detectors:
                clarifier.detectors['ambiguity'].vague_patterns = [
                    re.compile(pattern, re.IGNORECASE) for pattern in patterns
                ]
            elif 'bias' in clarifier.detectors:
                if pattern_type == 'gender_bias':
                    clarifier.detectors['bias'].gender_patterns = [
                        re.compile(pattern, re.IGNORECASE) for pattern in patterns
                    ]
                elif pattern_type == 'stereotype':
                    clarifier.detectors['bias'].stereotype_patterns = [
                        re.compile(pattern, re.IGNORECASE) for pattern in patterns
                    ]
                elif pattern_type == 'non_inclusive':
                    clarifier.detectors['bias'].non_inclusive_patterns = [
                        re.compile(pattern, re.IGNORECASE) for pattern in patterns
                    ]
            
            # Also save to a custom patterns file for persistence
            patterns_dir = os.path.join(os.path.dirname(__file__), '..', 'custom_patterns')
            os.makedirs(patterns_dir, exist_ok=True)
            
            with open(os.path.join(patterns_dir, f'{pattern_type}.json'), 'w') as f:
                json.dump(patterns, f, indent=2)
            
            return jsonify({'success': True})
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error saving patterns: {e}\n{error_traceback}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings/models', methods=['POST'])
    def api_settings_models():
        """Save model settings."""
        try:
            data = request.get_json()
            
            # Update config
            if 'prefer_provider' in data:
                config['settings']['prefer_provider'] = data['prefer_provider']
            
            if 'ollama_model' in data and 'integrations' in config and 'ollama' in config['integrations']:
                config['integrations']['ollama']['default_model'] = data['ollama_model']
            
            if 'ollama_embedding_model' in data and 'integrations' in config and 'ollama' in config['integrations']:
                config['integrations']['ollama']['default_embedding_model'] = data['ollama_embedding_model']
            
            if 'lm_studio_model' in data and 'integrations' in config and 'lm_studio' in config['integrations']:
                config['integrations']['lm_studio']['default_model'] = data['lm_studio_model']
            
            # Save updated config
            save_config(config)
            
            return jsonify({'success': True})
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error saving model settings: {e}\n{error_traceback}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings/prompts', methods=['POST'])
    def api_settings_prompts():
        """Save system prompts."""
        try:
            data = request.get_json()
            
            # Save prompts to a file
            prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'custom_prompts')
            os.makedirs(prompts_dir, exist_ok=True)
            
            if 'question_prompt' in data:
                with open(os.path.join(prompts_dir, 'question_prompt.txt'), 'w') as f:
                    f.write(data['question_prompt'])
            
            if 'reasoning_prompt' in data:
                with open(os.path.join(prompts_dir, 'reasoning_prompt.txt'), 'w') as f:
                    f.write(data['reasoning_prompt'])
            
            return jsonify({'success': True})
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error saving prompts: {e}\n{error_traceback}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings/sot', methods=['POST'])
    def api_settings_sot():
        """Save SoT settings."""
        try:
            data = request.get_json()
            
            # Update config
            if 'default_paradigm' in data:
                # Store the default paradigm in config
                if 'sot' not in config['settings']:
                    config['settings']['sot'] = {}
                config['settings']['sot']['default_paradigm'] = data['default_paradigm']
                
                # If not 'auto', set the SoT paradigm override
                if data['default_paradigm'] != 'auto':
                    clarifier.set_sot_paradigm(data['default_paradigm'])
                else:
                    clarifier.set_sot_paradigm(None)  # Clear the override
            
            if 'use_llm_questions' in data:
                config['settings']['use_llm_questions'] = data['use_llm_questions']
            
            if 'use_llm_reasoning' in data:
                config['settings']['use_llm_reasoning'] = data['use_llm_reasoning']
            
            # Save updated config
            save_config(config)
            
            return jsonify({'success': True})
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error saving SoT settings: {e}\n{error_traceback}")
            return jsonify({'error': str(e)}), 500
