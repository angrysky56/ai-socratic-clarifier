#!/usr/bin/env python3
"""
Script to fix SRE and SoT settings in the AI-Socratic-Clarifier.

This script updates the settings page to include both SRE and SoT settings
and makes sure they are properly integrated with the UI.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

def backup_file(file_path):
    """Create a backup of a file with .bak extension."""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.sre_sot_fix_bak"
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    return False

def add_sre_settings_to_page():
    """Add SRE settings to the main settings page."""
    settings_path = os.path.join(script_dir, "web_interface", "templates", "settings.html")
    
    if not os.path.exists(settings_path):
        logger.error(f"Settings page not found at: {settings_path}")
        return False
    
    # Backup the original file
    backup_file(settings_path)
    
    try:
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Check if SRE settings tab already exists
        if '<div class="tab-pane fade" id="sre">' in content:
            logger.info("SRE settings tab already exists")
            return True
        
        # Find the SoT settings tab entry in the tab list
        tab_list_entry_pos = content.find('<a href="#sot" class="list-group-item list-group-item-action" data-bs-toggle="list">SoT Settings</a>')
        
        if tab_list_entry_pos == -1:
            logger.warning("Could not find SoT tab list entry")
            return False
        
        # Add SRE tab entry after SoT tab entry
        sre_tab_entry = '<a href="#sre" class="list-group-item list-group-item-action" data-bs-toggle="list">SRE Settings</a>'
        updated_content = content[:tab_list_entry_pos + len('<a href="#sot" class="list-group-item list-group-item-action" data-bs-toggle="list">SoT Settings</a>')] + '\n                    ' + sre_tab_entry + content[tab_list_entry_pos + len('<a href="#sot" class="list-group-item list-group-item-action" data-bs-toggle="list">SoT Settings</a>'):]
        
        # Find the SoT settings tab content
        sot_tab_content_pos = updated_content.find('<div class="tab-pane fade" id="sot">')
        
        if sot_tab_content_pos == -1:
            logger.warning("Could not find SoT tab content")
            return False
        
        # Find the end of the SoT tab content
        sot_tab_content_end = updated_content.find('</div>', sot_tab_content_pos)
        sot_tab_content_end = updated_content.find('</div>', sot_tab_content_end + 1)
        sot_tab_content_end = updated_content.find('</div>', sot_tab_content_end + 1)
        sot_tab_content_end = updated_content.find('</div>', sot_tab_content_end + 1)
        
        if sot_tab_content_end == -1:
            logger.warning("Could not find end of SoT tab content")
            return False
        
        # Add SRE tab content after SoT tab content
        sre_tab_content = '''
                    <!-- SRE Settings Tab -->
                    <div class="tab-pane fade" id="sre">
                        <div class="card">
                            <div class="card-header">
                                <h4>Symbiotic Reflective Ecosystem Settings</h4>
                            </div>
                            <div class="card-body">
                                <form id="sreSettingsForm">
                                    <div class="mb-3">
                                        <label for="sreGlobalResonance" class="form-label">Global Resonance: <span id="sreGlobalResonanceValue">0.8</span></label>
                                        <input type="range" class="form-range" min="0" max="1" step="0.05" value="0.8" id="sreGlobalResonance">
                                        <div class="form-text">Controls how strongly different reasoning approaches resonate with each other.</div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="sreAdaptiveFlexibility" class="form-label">Adaptive Flexibility: <span id="sreAdaptiveFlexibilityValue">0.5</span></label>
                                        <input type="range" class="form-range" min="0" max="1" step="0.05" value="0.5" id="sreAdaptiveFlexibility">
                                        <div class="form-text">Controls how quickly the system adapts to new reasoning approaches.</div>
                                    </div>
                                    
                                    <div class="mb-3 form-check">
                                        <input type="checkbox" class="form-check-input" id="useSREVisualization" checked>
                                        <label class="form-check-label" for="useSREVisualization">Show SRE visualization in reflection mode</label>
                                    </div>
                                    
                                    <div class="mb-3 form-check">
                                        <input type="checkbox" class="form-check-input" id="autoExpandSRE" checked>
                                        <label class="form-check-label" for="autoExpandSRE">Auto-expand SRE visualization when available</label>
                                    </div>
                                    
                                    <button type="submit" class="btn btn-primary">Save SRE Settings</button>
                                </form>
                            </div>
                        </div>
                    </div>
'''
        
        final_content = updated_content[:sot_tab_content_end + 6] + sre_tab_content + updated_content[sot_tab_content_end + 6:]
        
        # Add SRE settings form submission handler
        script_pos = final_content.rfind('</script>')
        
        if script_pos == -1:
            logger.warning("Could not find script end tag")
            return False
        
        sre_settings_script = '''
        document.getElementById('sreSettingsForm').addEventListener('submit', function(e) {
            e.preventDefault();
            saveSreSettings();
        });
        
        document.getElementById('sreGlobalResonance').addEventListener('input', function(e) {
            document.getElementById('sreGlobalResonanceValue').textContent = e.target.value;
        });
        
        document.getElementById('sreAdaptiveFlexibility').addEventListener('input', function(e) {
            document.getElementById('sreAdaptiveFlexibilityValue').textContent = e.target.value;
        });
        
        function saveSreSettings() {
            const settings = {
                global_resonance: parseFloat(document.getElementById('sreGlobalResonance').value),
                adaptive_flexibility: parseFloat(document.getElementById('sreAdaptiveFlexibility').value),
                use_visualization: document.getElementById('useSREVisualization').checked,
                auto_expand: document.getElementById('autoExpandSRE').checked
            };
            
            fetch('/api/settings/sre', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('SRE settings saved successfully!');
                } else {
                    alert('Error saving settings: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        }'''
        
        final_content = final_content[:script_pos] + sre_settings_script + final_content[script_pos:]
        
        # Write back the updated content
        with open(settings_path, 'w') as f:
            f.write(final_content)
        
        logger.info("Added SRE settings to the main settings page")
        return True
    
    except Exception as e:
        logger.error(f"Error adding SRE settings to page: {e}")
        return False

def fix_sidebar_settings_button():
    """Fix the sidebar settings button in the integrated UI."""
    ui_path = os.path.join(script_dir, "web_interface", "templates", "fixed_integrated_ui.html")
    
    if not os.path.exists(ui_path):
        logger.error(f"Integrated UI template not found at: {ui_path}")
        return False
    
    try:
        with open(ui_path, 'r') as f:
            content = f.read()
        
        # Check if the sidebar already has the correct settings pane
        sidebar_pane_pos = content.find('<div class="sidebar-pane" id="settings-pane">')
        
        if sidebar_pane_pos == -1:
            logger.warning("Could not find settings pane in sidebar")
            return False
        
        # Find the end of the settings pane
        sidebar_pane_end = content.find('</div>', sidebar_pane_pos)
        sidebar_pane_end = content.find('</div>', sidebar_pane_end + 1)
        
        if sidebar_pane_end == -1:
            logger.warning("Could not find end of settings pane")
            return False
        
        # Replace the settings pane with the fixed version
        fixed_settings_pane = '''                <div class="sidebar-pane" id="settings-pane">
                    <h5 class="mb-3">Quick Settings</h5>
                    
                    <div class="form-group mb-3">
                        <label for="modeSelect" class="form-label">Operating Mode</label>
                        <select id="modeSelect" class="form-select">
                            <option value="standard">Standard</option>
                            <option value="deep">Deep</option>
                            <option value="technical">Technical</option>
                            <option value="creative">Creative</option>
                        </select>
                        <div class="form-text">Choose the reasoning mode for the assistant.</div>
                    </div>
                    
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="showAnalysisSwitch" checked>
                        <label class="form-check-label" for="showAnalysisSwitch">Show Analysis Details</label>
                    </div>
                    
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="useSoTSwitch" checked>
                        <label class="form-check-label" for="useSoTSwitch">Use Sequential Thinking</label>
                    </div>
                    
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="useRAGSwitch" checked>
                        <label class="form-check-label" for="useRAGSwitch">Use Document Context</label>
                    </div>
                    
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="useSRESwitch" checked>
                        <label class="form-check-label" for="useSRESwitch">Use Reflective Ecosystem</label>
                    </div>
                    
                    <div id="modelInfo" class="mb-3">
                        <h6>Model Information</h6>
                        <div class="small">
                            <p><strong>LLM:</strong> <span id="currentLLM">{{ current_model }}</span></p>
                            <p><strong>SoT Enabled:</strong> <span id="sotEnabled">Yes</span></p>
                            <p><strong>SRE Enabled:</strong> <span id="sreEnabled">Yes</span></p>
                            <p><strong>Provider:</strong> <span id="providerName">ollama</span></p>
                        </div>
                    </div>
                    
                    <div class="d-grid gap-2">
                        <button id="clearChatBtn" class="btn btn-outline-secondary">
                            <i class="bi bi-trash"></i> Clear Chat
                        </button>
                        
                        <a href="/settings" class="btn btn-outline-primary">
                            <i class="bi bi-gear"></i> Advanced Settings
                        </a>
                    </div>
                </div>'''
        
        updated_content = content[:sidebar_pane_pos] + fixed_settings_pane + content[sidebar_pane_end + 6:]
        
        # Write back the updated content
        with open(ui_path, 'w') as f:
            f.write(updated_content)
        
        # Also update the actual integrated_ui.html
        dest_path = os.path.join(script_dir, "web_interface", "templates", "integrated_ui.html")
        if os.path.exists(dest_path):
            # Backup the original file
            backup_file(dest_path)
            
            # Copy the updated fixed file
            shutil.copy2(ui_path, dest_path)
            
            logger.info("Updated integrated_ui.html with fixed sidebar settings")
        
        logger.info("Fixed sidebar settings button in the integrated UI")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing sidebar settings button: {e}")
        return False

def update_sidebar_script():
    """Update the sidebar script to handle SRE and SoT switches."""
    js_dir = os.path.join(script_dir, "web_interface", "static", "js")
    
    # Make sure integrated_ui.js exists
    integrated_ui_path = os.path.join(js_dir, "integrated_ui.js")
    
    if not os.path.exists(integrated_ui_path):
        logger.error(f"Integrated UI JS not found at: {integrated_ui_path}")
        return False
    
    # Backup the original file
    backup_file(integrated_ui_path)
    
    try:
        with open(integrated_ui_path, 'r') as f:
            content = f.read()
        
        # Check if SRE switch handler already exists
        if 'useSRESwitch' in content:
            logger.info("SRE switch handler already exists")
        else:
            # Find the "useRAGSwitch" handler
            rag_switch_pos = content.find('useRAGSwitch')
            
            if rag_switch_pos == -1:
                logger.warning("Could not find RAG switch handler")
                return False
            
            # Find the end of the function
            rag_handler_end = content.find('});', rag_switch_pos)
            
            if rag_handler_end == -1:
                logger.warning("Could not find end of RAG switch handler")
                return False
            
            # Add SRE switch handler after RAG switch handler
            sre_switch_handler = '''
    
    // SRE switch handler
    const useSRESwitch = document.getElementById('useSRESwitch');
    if (useSRESwitch) {
        useSRESwitch.addEventListener('change', function(e) {
            const isEnabled = e.target.checked;
            
            // Update UI
            const sreEnabledEl = document.getElementById('sreEnabled');
            if (sreEnabledEl) {
                sreEnabledEl.textContent = isEnabled ? 'Yes' : 'No';
            }
            
            // Store setting
            localStorage.setItem('useSRE', isEnabled);
            
            // Update visualization
            if (window.sreVisualization) {
                window.sreVisualization.setEnabled(isEnabled);
            }
        });
        
        // Initialize from saved setting
        const savedSRE = localStorage.getItem('useSRE');
        if (savedSRE !== null) {
            useSRESwitch.checked = savedSRE === 'true';
            
            // Update UI
            const sreEnabledEl = document.getElementById('sreEnabled');
            if (sreEnabledEl) {
                sreEnabledEl.textContent = useSRESwitch.checked ? 'Yes' : 'No';
            }
        }
    }'''
            
            updated_content = content[:rag_handler_end + 2] + sre_switch_handler + content[rag_handler_end + 2:]
            
            # Write back the updated content
            with open(integrated_ui_path, 'w') as f:
                f.write(updated_content)
            
            logger.info("Added SRE switch handler to integrated_ui.js")
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating sidebar script: {e}")
        return False

def fix_sre_endpoint():
    """Fix SRE API endpoint for settings."""
    api_settings_path = os.path.join(script_dir, "web_interface", "api_settings.py")
    
    if not os.path.exists(api_settings_path):
        logger.error(f"API settings file not found at: {api_settings_path}")
        return False
    
    # Backup the original file
    backup_file(api_settings_path)
    
    try:
        with open(api_settings_path, 'r') as f:
            content = f.read()
        
        # Check if SRE endpoint already exists
        if "/api/settings/sre" in content:
            logger.info("SRE settings endpoint already exists")
            return True
        
        # Find the SoT settings endpoint
        sot_endpoint_pos = content.find("@app.route('/api/settings/sot', methods=['POST'])")
        
        if sot_endpoint_pos == -1:
            logger.warning("Could not find SoT settings endpoint")
            return False
        
        # Find the end of the SoT settings endpoint function
        sot_endpoint_end = content.find("@app.route", sot_endpoint_pos + 1)
        
        if sot_endpoint_end == -1:
            sot_endpoint_end = content.find("def setup_api_routes", sot_endpoint_pos)
            
            if sot_endpoint_end == -1:
                logger.warning("Could not find end of SoT settings endpoint")
                return False
        
        # Add SRE settings endpoint after SoT settings endpoint
        sre_endpoint = '''
    @app.route('/api/settings/sre', methods=['POST'])
    def save_sre_settings():
        """Save SRE settings to config."""
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
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            # Update clarifier settings
            if clarifier and hasattr(clarifier, 'update_settings'):
                clarifier.update_settings(config['settings'])
            
            return jsonify({
                'success': True,
                'message': 'SRE settings saved successfully'
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
'''
        
        updated_content = content[:sot_endpoint_end] + sre_endpoint + content[sot_endpoint_end:]
        
        # Write back the updated content
        with open(api_settings_path, 'w') as f:
            f.write(updated_content)
        
        logger.info("Added SRE settings endpoint to API settings")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing SRE endpoint: {e}")
        return False

def fix_sre_sot_ui_integration():
    """Apply all SRE and SoT UI fixes."""
    success = True
    
    # Fix sidebar settings button
    if fix_sidebar_settings_button():
        logger.info("✅ Fixed sidebar settings button")
    else:
        logger.warning("❌ Failed to fix sidebar settings button")
        success = False
    
    # Add SRE settings to main settings page
    if add_sre_settings_to_page():
        logger.info("✅ Added SRE settings to main settings page")
    else:
        logger.warning("❌ Failed to add SRE settings to main settings page")
        success = False
    
    # Update sidebar script
    if update_sidebar_script():
        logger.info("✅ Updated sidebar script for SRE switch")
    else:
        logger.warning("❌ Failed to update sidebar script")
        success = False
    
    # Fix SRE endpoint
    if fix_sre_endpoint():
        logger.info("✅ Fixed SRE settings endpoint")
    else:
        logger.warning("❌ Failed to fix SRE settings endpoint")
        success = False
    
    # Also run the previous SRE/SoT fix script
    logger.info("Running SRE/SoT integration fix...")
    try:
        from archive.fixes.fix_sre_sot_integration import fix_sre_sot_integration
        if fix_sre_sot_integration():
            logger.info("✅ Fixed SRE/SoT core integration")
        else:
            logger.warning("❌ Failed to fix SRE/SoT core integration")
            success = False
    except Exception as e:
        logger.error(f"Error running SRE/SoT integration fix: {e}")
        success = False
    
    return success

if __name__ == "__main__":
    try:
        if fix_sre_sot_ui_integration():
            logger.info("✨ Successfully fixed SRE and SoT UI integration")
            sys.exit(0)
        else:
            logger.error("⚠️ Some SRE and SoT UI integration issues could not be fixed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error fixing SRE and SoT UI integration: {e}")
        sys.exit(1)
