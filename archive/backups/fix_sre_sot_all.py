#!/usr/bin/env python3
"""
Comprehensive fix for SRE and SoT settings and integration in the AI-Socratic-Clarifier.

This script:
1. Fixes the SRE endpoint in api_settings.py
2. Ensures ecosystem state file exists and is valid in the correct location
3. Corrects path references in the integration scripts
4. Verifies all frontend SRE visualization files exist
5. Makes sure SoT and SRE integrations are working properly
"""

import os
import sys
import json
import shutil
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = script_dir

def backup_file(file_path):
    """Create a backup of a file with .bak extension."""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.sre_sot_all_fix_bak"
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    return False

def fix_sre_endpoint():
    """Fix SRE API endpoint for settings."""
    api_settings_path = os.path.join(project_root, "web_interface", "api_settings.py")
    
    if not os.path.exists(api_settings_path):
        logger.error(f"API settings file not found at: {api_settings_path}")
        return False
    
    # Backup the original file
    backup_file(api_settings_path)
    
    try:
        with open(api_settings_path, 'r') as f:
            content = f.read()
        
        # Check if SRE endpoint already exists
        if "@app.route('/api/settings/sre', methods=['POST'])" in content:
            logger.info("SRE settings endpoint already exists")
            return True
        
        # Find the SoT settings endpoint
        sot_endpoint_pos = content.find("@app.route('/api/settings/sot', methods=['POST'])")
        
        if sot_endpoint_pos == -1:
            logger.warning("Could not find SoT settings endpoint")
            return False
        
        # Find function definition
        sot_def_pos = content.find("def api_settings_sot():", sot_endpoint_pos)
        if sot_def_pos == -1:
            logger.warning("Could not find SoT settings function definition")
            return False
        
        # Find the end of the SoT settings function
        # Look for the closing of the try-except block
        except_pos = content.find("except Exception as e:", sot_def_pos)
        if except_pos == -1:
            logger.warning("Could not find except block in SoT settings function")
            return False
        
        # Find the last line of the except block
        last_line_match = re.search(r'return jsonify\({.+}\), \d+\s*$', content[except_pos:], re.MULTILINE)
        if not last_line_match:
            logger.warning("Could not find the last line of the except block")
            return False
        
        end_pos = except_pos + last_line_match.end()
        
        # Add SRE settings endpoint after SoT settings endpoint
        sre_endpoint = '''
            
    @app.route('/api/settings/sre', methods=['POST'])
    def api_settings_sre():
        """Save SRE settings."""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Update config
            if 'global_resonance' in data:
                config['settings']['sre_global_resonance'] = float(data['global_resonance'])
            
            if 'adaptive_flexibility' in data:
                config['settings']['sre_adaptive_flexibility'] = float(data['adaptive_flexibility'])
            
            if 'use_visualization' in data:
                config['settings']['use_sre_visualization'] = data['use_visualization']
            
            if 'auto_expand' in data:
                config['settings']['auto_expand_sre'] = data['auto_expand']
            
            # Save updated config
            save_config(config)
            
            # Update clarifier settings
            if clarifier and hasattr(clarifier, 'update_settings'):
                clarifier.update_settings(config['settings'])
            
            return jsonify({
                'success': True,
                'message': 'SRE settings saved successfully'
            })
        
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"Error saving SRE settings: {e}\\n{error_traceback}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500'''
        
        updated_content = content[:end_pos] + sre_endpoint + content[end_pos:]
        
        # Check if traceback is imported
        if 'import traceback' not in content:
            # Add the import
            import_pos = content.find('import')
            import_end_pos = content.find('\n\n', import_pos)
            updated_content = updated_content[:import_end_pos] + '\nimport traceback' + updated_content[import_end_pos:]
        
        # Write back the updated content
        with open(api_settings_path, 'w') as f:
            f.write(updated_content)
        
        logger.info("Added SRE settings endpoint to API settings")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing SRE endpoint: {e}")
        return False

def fix_ecosystem_state():
    """Ensure that the ecosystem state file exists and is valid."""
    state_path = os.path.join(project_root, 'sequential_thinking', 'ecosystem_state.json')
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    
    try:
        # Check if the file already exists
        if os.path.exists(state_path):
            # Try to load it to make sure it's valid
            try:
                with open(state_path, 'r') as f:
                    json.load(f)
                logger.info(f"Ecosystem state file exists and is valid: {state_path}")
                return True
            except json.JSONDecodeError:
                # Invalid JSON, back it up and create a new one
                backup_path = f"{state_path}.invalid_bak"
                logger.warning(f"Ecosystem state file is invalid JSON, backing up to {backup_path}")
                shutil.copy2(state_path, backup_path)
                # Will create a new one below
        
        # Create a minimal state file
        default_state = {
            "nodes": {
                "conceptual_chaining": {
                    "id": "conceptual_chaining",
                    "name": "Conceptual Chaining",
                    "count": 0,
                    "success_count": 0
                },
                "chunked_symbolism": {
                    "id": "chunked_symbolism",
                    "name": "Chunked Symbolism",
                    "count": 0,
                    "success_count": 0
                },
                "expert_lexicons": {
                    "id": "expert_lexicons",
                    "name": "Expert Lexicons",
                    "count": 0,
                    "success_count": 0
                }
            },
            "global_coherence": 0.8,
            "question_history": [],
            "meta_meta_framework": {
                "principle_of_inquiry": "Improve critical thinking through effective Socratic questioning",
                "dimensional_axes": {
                    "reasoning_approach": {
                        "description": "Reasoning approach to use",
                        "values": ["conceptual_chaining", "chunked_symbolism", "expert_lexicons", "socratic_questioning"]
                    },
                    "question_focus": {
                        "description": "Focus area for generated questions",
                        "values": ["definitions", "evidence", "assumptions", "implications", "alternatives"]
                    },
                    "complexity_level": {
                        "description": "Complexity level of exploration",
                        "values": ["simple", "moderate", "complex"]
                    }
                },
                "constraints": [
                    {"constraint": "Questions must be genuinely helpful", "purpose": "Ensure practical value"},
                    {"constraint": "Questions must address specific issues", "purpose": "Maintain relevance"},
                    {"constraint": "Questions should be open-ended", "purpose": "Encourage deeper thinking"}
                ],
                "controlled_emergence": 0.3,
                "feedback_loops": [
                    {
                        "name": "Question effectiveness",
                        "metric": "user_feedback",
                        "current_value": 0.5,
                        "target_value": 0.8
                    },
                    {
                        "name": "Reasoning coherence",
                        "metric": "global_coherence",
                        "current_value": 0.8,
                        "target_value": 0.9
                    },
                    {
                        "name": "Paradigm selection accuracy",
                        "metric": "paradigm_accuracy",
                        "current_value": 0.5,
                        "target_value": 0.85
                    }
                ],
                "adaptive_flexibility": 0.5
            },
            "intellisynth": {
                "truth_value": 0.7,
                "scrutiny_value": 0.0,
                "improvement_value": 0.0,
                "advancement": 0.0,
                "alpha": 0.5,
                "beta": 0.5
            }
        }
        
        # Save the default state
        with open(state_path, 'w') as f:
            json.dump(default_state, f, indent=2)
        
        logger.info(f"Created ecosystem state file at: {state_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing ecosystem state: {e}")
        return False

def fix_archive_path_references():
    """Fix any archive path references in the integration scripts."""
    integration_fix_path = os.path.join(project_root, 'archive', 'fixes', 'fix_sre_sot_integration.py')
    
    if not os.path.exists(integration_fix_path):
        logger.warning(f"Integration fix script not found at: {integration_fix_path}")
        return False
    
    # Backup the original file
    backup_file(integration_fix_path)
    
    try:
        with open(integration_fix_path, 'r') as f:
            content = f.read()
        
        # Fix the ecosystem state path
        old_path = "os.path.join(os.path.dirname(__file__), 'sequential_thinking', 'ecosystem_state.json')"
        new_path = "os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')), 'sequential_thinking', 'ecosystem_state.json')"
        
        content = content.replace(old_path, new_path)
        
        # Also fix the config path reference
        config_ref = "sequential_thinking.reflective_ecosystem - WARNING - Configuration file not found at"
        if config_ref in content:
            old_config_path = "config.json"
            new_config_path = "/home/ty/Repositories/ai_workspace/ai-socratic-clarifier/config.json"
            content = content.replace(old_config_path, new_config_path)
        
        # Write back the updated content
        with open(integration_fix_path, 'w') as f:
            f.write(content)
        
        logger.info("Fixed archive path references in the integration fix script")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing archive path references: {e}")
        return False

def ensure_sre_visualization_files():
    """Ensure the SRE visualization files exist in the correct location."""
    js_dir = os.path.join(project_root, 'web_interface', 'static', 'js', 'enhanced')
    css_dir = os.path.join(project_root, 'web_interface', 'static', 'css', 'enhanced')
    
    # Make sure directories exist
    os.makedirs(js_dir, exist_ok=True)
    os.makedirs(css_dir, exist_ok=True)
    
    js_path = os.path.join(js_dir, 'sre_visualization.js')
    css_path = os.path.join(css_dir, 'sre_visualization.css')
    
    # Check if files exist
    js_exists = os.path.exists(js_path)
    css_exists = os.path.exists(css_path)
    
    if js_exists and css_exists:
        logger.info("SRE visualization files already exist")
        return True
    
    # Try to copy from archive if exists
    archive_js = os.path.join(project_root, 'archive', 'fixes', 'web_interface', 'static', 'js', 'enhanced', 'sre_visualization.js')
    archive_css = os.path.join(project_root, 'archive', 'fixes', 'web_interface', 'static', 'css', 'enhanced', 'sre_visualization.css')
    
    success = True
    
    if not js_exists:
        if os.path.exists(archive_js):
            shutil.copy2(archive_js, js_path)
            logger.info(f"Copied SRE visualization JS from archive to: {js_path}")
        else:
            logger.warning(f"SRE visualization JS not found in archive or main location")
            success = False
    
    if not css_exists:
        if os.path.exists(archive_css):
            shutil.copy2(archive_css, css_path)
            logger.info(f"Copied SRE visualization CSS from archive to: {css_path}")
        else:
            logger.warning(f"SRE visualization CSS not found in archive or main location")
            success = False
    
    return success

def fix_config_defaults():
    """Ensure that the config.json has all the necessary SRE and SoT settings."""
    config_path = os.path.join(project_root, 'config.json')
    
    if not os.path.exists(config_path):
        logger.error(f"Config file not found at: {config_path}")
        # Try to use config.example.json as a template
        example_path = os.path.join(project_root, 'config.example.json')
        if os.path.exists(example_path):
            logger.info(f"Using config.example.json as template")
            shutil.copy2(example_path, config_path)
        else:
            logger.error(f"Config example file not found either")
            return False
    
    # Backup the original file
    backup_file(config_path)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Make sure settings section exists
        if 'settings' not in config:
            config['settings'] = {}
        
        # Add SRE settings if missing
        if 'sre_global_resonance' not in config['settings']:
            config['settings']['sre_global_resonance'] = 0.8
        
        if 'sre_adaptive_flexibility' not in config['settings']:
            config['settings']['sre_adaptive_flexibility'] = 0.5
        
        if 'use_sre_visualization' not in config['settings']:
            config['settings']['use_sre_visualization'] = True
        
        if 'auto_expand_sre' not in config['settings']:
            config['settings']['auto_expand_sre'] = True
        
        # Add SoT settings if missing
        if 'sot' not in config['settings']:
            config['settings']['sot'] = {
                'default_paradigm': 'auto'
            }
        
        if 'use_sot' not in config['settings']:
            config['settings']['use_sot'] = True
        
        if 'use_llm_questions' not in config['settings']:
            config['settings']['use_llm_questions'] = True
        
        if 'use_llm_reasoning' not in config['settings']:
            config['settings']['use_llm_reasoning'] = True
        
        # Write back the updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info("Updated config.json with SRE and SoT defaults")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing config defaults: {e}")
        return False

def run_original_fix_script():
    """Run the original fix_sre_sot_settings.py script with modifications for paths."""
    fix_script_path = os.path.join(project_root, 'fix_sre_sot_settings.py')
    
    if not os.path.exists(fix_script_path):
        logger.error(f"Original fix script not found at: {fix_script_path}")
        return False
    
    try:
        # Import the script and run the main function
        logger.info("Running original fix_sre_sot_settings.py script...")
        
        # Add project root to path
        sys.path.insert(0, project_root)
        
        # Create a copy of the script with fixed paths
        temp_script_path = os.path.join(project_root, 'fix_sre_sot_settings_temp.py')
        
        with open(fix_script_path, 'r') as f:
            content = f.read()
        
        # Modify path references if needed
        if 'archive/fixes' in content:
            content = content.replace('archive/fixes', '')
        
        with open(temp_script_path, 'w') as f:
            f.write(content)
        
        # Execute the modified script
        exec(compile(content, fix_script_path, 'exec'))
        
        # Clean up temp file
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)
        
        logger.info("Successfully ran original fix script")
        return True
    
    except Exception as e:
        logger.error(f"Error running original fix script: {e}")
        return False

def sync_ecosystem_state_files():
    """Sync ecosystem state files between main and archive locations."""
    main_path = os.path.join(project_root, 'sequential_thinking', 'ecosystem_state.json')
    archive_path = os.path.join(project_root, 'archive', 'fixes', 'sequential_thinking', 'ecosystem_state.json')
    
    # Create archive directory if it doesn't exist
    os.makedirs(os.path.dirname(archive_path), exist_ok=True)
    
    try:
        # Check if main file exists
        if os.path.exists(main_path):
            # Copy to archive
            shutil.copy2(main_path, archive_path)
            logger.info(f"Synced ecosystem state from main to archive location")
            return True
        elif os.path.exists(archive_path):
            # Copy from archive to main
            shutil.copy2(archive_path, main_path)
            logger.info(f"Synced ecosystem state from archive to main location")
            return True
        else:
            logger.warning("Ecosystem state file not found in either location")
            return False
    
    except Exception as e:
        logger.error(f"Error syncing ecosystem state files: {e}")
        return False

def fix_ui_integrated():
    """Fix the integrated UI template issues."""
    ui_path = os.path.join(project_root, 'web_interface', 'templates', 'integrated_ui.html')
    
    if not os.path.exists(ui_path):
        logger.error(f"Integrated UI template not found at: {ui_path}")
        return False
    
    # Backup the original file
    backup_file(ui_path)
    
    try:
        with open(ui_path, 'r') as f:
            content = f.read()
        
        # Check for common UI issues
        issues_fixed = False
        
        # Fix duplicate settings panes
        settings_pane_count = content.count('<div class="sidebar-pane" id="settings-pane">')
        if settings_pane_count > 1:
            logger.warning(f"Found {settings_pane_count} settings panes in UI template")
            
            # Find first settings pane
            first_pane_pos = content.find('<div class="sidebar-pane" id="settings-pane">')
            first_pane_end = content.find('</div>', first_pane_pos)
            first_pane_end = content.find('</div>', first_pane_end + 1)
            
            # Find second pane
            second_pane_pos = content.find('<div class="sidebar-pane" id="settings-pane">', first_pane_end)
            
            if second_pane_pos > 0:
                # Remove the second one
                second_pane_end = content.find('</div>', second_pane_pos)
                second_pane_end = content.find('</div>', second_pane_end + 1)
                
                updated_content = content[:second_pane_pos] + content[second_pane_end+6:]
                content = updated_content
                issues_fixed = True
                logger.info("Fixed duplicate settings pane issue")
        
        # Fix CSS and JS imports
        if 'sre_visualization.css' not in content:
            # Find the CSS imports section
            css_import_pos = content.find('<link rel="stylesheet" href="/static/css/')
            if css_import_pos > 0:
                end_of_line = content.find('\n', css_import_pos)
                if end_of_line > 0:
                    # Add our import after this line
                    new_import = '\n    <link rel="stylesheet" href="/static/css/enhanced/sre_visualization.css">'
                    updated_content = content[:end_of_line] + new_import + content[end_of_line:]
                    content = updated_content
                    issues_fixed = True
                    logger.info("Fixed missing SRE CSS import")
        
        if 'sre_visualization.js' not in content:
            # Find the JS imports section
            js_import_pos = content.find('<script src="/static/js/')
            if js_import_pos > 0:
                end_of_line = content.find('\n', js_import_pos)
                if end_of_line > 0:
                    # Add our import after this line
                    new_import = '\n    <script src="/static/js/enhanced/sre_visualization.js"></script>'
                    updated_content = content[:end_of_line] + new_import + content[end_of_line:]
                    content = updated_content
                    issues_fixed = True
                    logger.info("Fixed missing SRE JS import")
        
        # Make sure SRE switch is present
        if 'useSRESwitch' not in content:
            # Find the SoT switch
            sot_switch_pos = content.find('useSoTSwitch')
            if sot_switch_pos > 0:
                # Find the end of the div
                div_end = content.find('</div>', sot_switch_pos)
                if div_end > 0:
                    # Add SRE switch after this div
                    sre_switch = '''
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="useSRESwitch" checked>
                        <label class="form-check-label" for="useSRESwitch">Use Reflective Ecosystem</label>
                    </div>'''
                    updated_content = content[:div_end+6] + sre_switch + content[div_end+6:]
                    content = updated_content
                    issues_fixed = True
                    logger.info("Fixed missing SRE switch")
        
        # Fix SRE enabled indicator
        if 'sreEnabled' not in content:
            # Find the model info section
            model_info_pos = content.find('<div id="modelInfo"')
            if model_info_pos > 0:
                # Find the SoT enabled line
                sot_enabled_pos = content.find('<p><strong>SoT Enabled:</strong>', model_info_pos)
                if sot_enabled_pos > 0:
                    # Find the end of this line
                    line_end = content.find('</p>', sot_enabled_pos)
                    if line_end > 0:
                        # Add SRE enabled after this line
                        sre_enabled = '<p><strong>SRE Enabled:</strong> <span id="sreEnabled">Yes</span></p>'
                        updated_content = content[:line_end+4] + '\n                            ' + sre_enabled + content[line_end+4:]
                        content = updated_content
                        issues_fixed = True
                        logger.info("Fixed missing SRE enabled indicator")
        
        # Write back changes if any issues were fixed
        if issues_fixed:
            with open(ui_path, 'w') as f:
                f.write(content)
            
            logger.info("Successfully fixed UI issues in integrated_ui.html")
        else:
            logger.info("No UI issues found in integrated_ui.html")
        
        return True
    
    except Exception as e:
        logger.error(f"Error fixing integrated UI: {e}")
        return False

def fix_sre_sot_all():
    """Apply all SRE and SoT fixes."""
    success = True
    
    # Fix the SRE endpoint in api_settings.py
    if fix_sre_endpoint():
        logger.info("✅ Fixed SRE settings endpoint")
    else:
        logger.warning("❌ Failed to fix SRE settings endpoint")
        success = False
    
    # Make sure ecosystem state file exists and is valid
    if fix_ecosystem_state():
        logger.info("✅ Fixed ecosystem state file")
    else:
        logger.warning("❌ Failed to fix ecosystem state file")
        success = False
    
    # Fix archive path references
    if fix_archive_path_references():
        logger.info("✅ Fixed archive path references")
    else:
        logger.warning("❌ Failed to fix archive path references")
        success = False
    
    # Ensure SRE visualization files exist
    if ensure_sre_visualization_files():
        logger.info("✅ Ensured SRE visualization files exist")
    else:
        logger.warning("❌ Failed to ensure SRE visualization files")
        success = False
    
    # Fix config defaults
    if fix_config_defaults():
        logger.info("✅ Fixed config defaults")
    else:
        logger.warning("❌ Failed to fix config defaults")
        success = False
    
    # Sync ecosystem state files
    if sync_ecosystem_state_files():
        logger.info("✅ Synced ecosystem state files")
    else:
        logger.warning("❌ Failed to sync ecosystem state files")
        success = False
    
    # Fix integrated UI
    if fix_ui_integrated():
        logger.info("✅ Fixed integrated UI")
    else:
        logger.warning("❌ Failed to fix integrated UI")
        success = False
    
    return success

if __name__ == "__main__":
    try:
        if fix_sre_sot_all():
            logger.info("✨ Successfully fixed SRE and SoT integration issues")
            sys.exit(0)
        else:
            logger.error("⚠️ Some SRE and SoT integration issues could not be fixed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error fixing SRE and SoT integration: {e}")
        sys.exit(1)
