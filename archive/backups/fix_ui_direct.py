#!/usr/bin/env python3
"""
Fix duplicate settings panes in the integrated UI by directly replacing the entire file.

This script takes a direct approach by completely replacing the HTML file with a
clean version without duplicated settings panes.
"""

import os
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Create a backup of a file."""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.direct_fix_bak"
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    return False

def fix_integrated_ui():
    """Fix the integrated UI template directly by focusing only on the settings pane section."""
    ui_path = os.path.join("/home/ty/Repositories/ai_workspace/ai-socratic-clarifier", 
                          "web_interface", "templates", "integrated_ui.html")
    
    if not os.path.exists(ui_path):
        logger.error(f"Integrated UI template not found at: {ui_path}")
        return False
    
    # Backup the original file
    backup_file(ui_path)
    
    try:
        with open(ui_path, 'r') as f:
            content = f.read()
        
        # First, identify the settings pane section
        settings_panes = content.count('<div class="sidebar-pane" id="settings-pane">')
        logger.info(f"Found {settings_panes} settings pane definitions")
        
        if settings_panes <= 1:
            logger.info("No duplicate settings panes found")
            return True
        
        # Find the starting position of the first settings pane
        first_pane_pos = content.find('<div class="sidebar-pane" id="settings-pane">')
        if first_pane_pos == -1:
            logger.error("Could not find any settings pane")
            return False
        
        # Find the starting position of the questions pane (comes before settings)
        questions_pane_pos = content.find('<div class="sidebar-pane" id="questions-pane">')
        if questions_pane_pos == -1:
            logger.warning("Could not find questions pane position")
        
        # Find the content area (comes after the sidebar)
        content_area_pos = content.find('<!-- Content Area -->')
        if content_area_pos == -1:
            logger.error("Could not find content area position")
            return False
        
        # Extract the single settings pane properly
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
        
        # Construct the fixed content
        if questions_pane_pos != -1:
            # Find the end of the questions pane
            questions_pane_end = content.find('</div>', questions_pane_pos)
            if questions_pane_end == -1:
                logger.warning("Could not properly find end of questions pane")
                questions_pane_end = questions_pane_pos + 100  # Rough estimate
            else:
                # Find the enclosing div end
                questions_pane_end = content.find('</div>', questions_pane_end + 6)
            
            # Build content with known good structure
            before_content = content[:questions_pane_end + 6]  # Include the closing div
            after_content = content[content_area_pos:]  # Start from content area
            
            # Assemble the fixed content
            fixed_content = before_content + '\n' + settings_pane + '\n            </div>\n        </div>\n        \n' + after_content
        else:
            # If we can't find the questions pane, do a direct search and replace
            # Find all occurrences of settings pane
            parts = content.split('<div class="sidebar-pane" id="settings-pane">')
            
            # Keep only the first occurrence
            fixed_content = parts[0] + settings_pane
            
            # Find where to continue after the last settings pane
            content_after_settings = content[content_area_pos:]
            fixed_content = fixed_content + '\n            </div>\n        </div>\n        \n' + content_after_settings
        
        # Write the fixed content back to the file
        with open(ui_path, 'w') as f:
            f.write(fixed_content)
        
        logger.info("Fixed UI template with clean settings pane")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing UI template: {e}")
        return False

if __name__ == "__main__":
    try:
        if fix_integrated_ui():
            logger.info("✨ Successfully fixed integrated UI template")
        else:
            logger.error("❌ Failed to fix integrated UI template")
    
    except Exception as e:
        logger.error(f"❌ Error while fixing UI template: {e}")
