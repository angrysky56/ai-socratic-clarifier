#!/usr/bin/env python3
"""
Direct fix for the sidebar duplication issue in the integrated UI.

This script completely overwrites the integrated_ui.html file with a clean version.
"""

import os
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_sidebar_direct():
    # Path to the integrated UI template
    ui_path = "/home/ty/Repositories/ai_workspace/ai-socratic-clarifier/web_interface/templates/integrated_ui.html"
    
    # Create a backup
    backup_path = f"{ui_path}.direct_sidebar_fix_bak"
    logger.info(f"Creating backup to {backup_path}")
    if os.path.exists(ui_path):
        shutil.copy2(ui_path, backup_path)
    
    # Extract the current model value before replacing
    current_model = "{{ current_model }}"
    
    # Here we're being very direct - let's just truncate the file to cut off the duplicated sections
    with open(ui_path, 'r') as f:
        content = f.read()
    
    # Find the Settings pane section
    settings_pane_pos = content.find('<div class="sidebar-pane" id="settings-pane">')
    if settings_pane_pos < 0:
        logger.error("Could not find settings pane section")
        return False
    
    # Find the end of the first section section
    settings_end_pos = content.find('</div>', settings_pane_pos)
    settings_end_pos = content.find('</div>', settings_end_pos + 6)
    
    if settings_end_pos < 0:
        logger.error("Could not find end of settings pane")
        return False
    
    # Find the next section after settings
    content_area_pos = content.find('<!-- Content Area -->')
    
    if content_area_pos < 0:
        logger.error("Could not find content area section")
        return False
    
    # Get everything before and after the duplicate sections
    before_settings = content[:settings_pane_pos]
    
    # This is a fixed, clean settings pane content
    settings_pane = '''                <!-- Settings Sidebar -->
                <div class="sidebar-pane" id="settings-pane">
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
                            <p><strong>LLM:</strong> <span id="currentLLM">''' + current_model + '''</span></p>
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
                </div>
            </div>
        </div>
        
        <!-- Content Area -->'''
    
    after_settings = content[content_area_pos + len('<!-- Content Area -->'):]
    
    # Combine everything into a new file
    new_content = before_settings + settings_pane + after_settings
    
    # Check if there are still duplicate settings panes
    if new_content.count('<div class="sidebar-pane" id="settings-pane">') > 1:
        logger.warning("There are still multiple settings panes in the content!")
    
    # Write the fixed content
    with open(ui_path, 'w') as f:
        f.write(new_content)
    
    logger.info("Directly replaced the integrated UI template")
    return True

if __name__ == "__main__":
    try:
        if fix_sidebar_direct():
            logger.info("✨ Successfully fixed sidebar duplication")
        else:
            logger.error("❌ Failed to fix sidebar duplication")
    except Exception as e:
        logger.error(f"Error: {e}")
