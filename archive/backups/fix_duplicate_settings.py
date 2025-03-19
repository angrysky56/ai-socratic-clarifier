#!/usr/bin/env python3
"""
Fix duplicate settings pane in the AI-Socratic-Clarifier integrated UI.

This script specifically targets the issue where the settings pane is duplicated
multiple times in the HTML template, causing UI rendering problems.
"""

import os
import re
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Create a backup of a file."""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.duplicate_fix_bak"
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    return False

def fix_duplicate_settings_pane():
    """Fix the duplicate settings pane in the integrated UI template."""
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
        
        # Find all occurrences of the settings pane
        settings_pane_pattern = r'<div class="sidebar-pane" id="settings-pane">.*?</div>\s*</div>\s*</div>'
        settings_panes = re.findall(settings_pane_pattern, content, re.DOTALL)
        
        if len(settings_panes) <= 1:
            logger.info("No duplicate settings panes found.")
            return True
        
        logger.info(f"Found {len(settings_panes)} settings panes, keeping only the first one.")
        
        # Get the first complete settings pane with all its content
        first_pane = settings_panes[0]
        
        # Find all occurrences and replace all but the first one
        first_occurrence = True
        updated_content = content
        
        for pane in settings_panes:
            if first_occurrence:
                first_occurrence = False
                continue
            
            # Replace this occurrence with nothing
            updated_content = updated_content.replace(pane, '')
        
        # Clean up any potential artifacts (multiple closing divs)
        updated_content = re.sub(r'</div>\s*</div>\s*</div>\s*</div>\s*</div>', '</div>\n                </div>\n            </div>', updated_content)
        
        # Write the fixed content back to the file
        with open(ui_path, 'w') as f:
            f.write(updated_content)
        
        logger.info("Successfully fixed duplicate settings panes.")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing duplicate settings panes: {e}")
        return False

def completely_rewrite_ui():
    """Complete rewrite of the integrated UI if other fixes fail."""
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
        
        # Find the beginning and end of the settings pane section
        sidebar_content_start = content.find('<div class="sidebar-content">')
        if sidebar_content_start == -1:
            logger.error("Could not find sidebar content start.")
            return False
        
        # Find all settings panes
        settings_pane_markers = [m.start() for m in re.finditer(r'<div class="sidebar-pane" id="settings-pane">', content)]
        
        if not settings_pane_markers:
            logger.error("Could not find settings pane markers.")
            return False
        
        # Take only the first settings pane
        first_pane_pos = settings_pane_markers[0]
        
        # Find the end of the entire sidebar content section
        sidebar_content_end = content.find('</div>', content.find('</div>', content.find('</div>', first_pane_pos + 500)))
        
        if sidebar_content_end == -1:
            logger.error("Could not find sidebar content end.")
            return False
        
        # Extract sections
        before_sidebar = content[:sidebar_content_start + len('<div class="sidebar-content">')]
        
        # Find the last tab pane before settings
        questions_pane_end = content.find('</div>', content.find('<div class="sidebar-pane" id="questions-pane">'))
        
        if questions_pane_end == -1:
            logger.error("Could not find questions pane end.")
            return False
        
        # Extract just the first occurrence of the settings pane
        first_settings_pane_end = content.find('</div>', content.find('</div>', content.find('</div>', first_pane_pos)))
        
        if first_settings_pane_end == -1:
            logger.error("Could not find end of first settings pane.")
            return False
        
        # +6 for the length of "</div>"
        first_settings_pane = content[first_pane_pos:first_settings_pane_end + 6]
        
        # Combine everything
        fixed_content = before_sidebar
        fixed_content += '\n                <!-- Documents Sidebar -->\n'
        fixed_content += content[before_sidebar.find('<div class="sidebar-content">') + len('<div class="sidebar-content">'):questions_pane_end + 6]
        fixed_content += '\n                \n                <!-- Settings Sidebar -->\n'
        fixed_content += first_settings_pane
        fixed_content += '\n            </div>\n        </div>\n        \n        <!-- Content Area -->'
        fixed_content += content[content.find('<!-- Content Area -->'):]
        
        # Write the fixed content back to the file
        with open(ui_path, 'w') as f:
            f.write(fixed_content)
        
        logger.info("Successfully reconstructed the UI template.")
        return True
    
    except Exception as e:
        logger.error(f"Error reconstructing UI template: {e}")
        return False

if __name__ == "__main__":
    try:
        if fix_duplicate_settings_pane():
            logger.info("✨ Successfully fixed duplicate settings panes")
        else:
            logger.error("⚠️ Could not fix duplicate settings panes with primary method")
            logger.info("Attempting complete UI reconstruction...")
            
            if completely_rewrite_ui():
                logger.info("✨ Successfully reconstructed the UI template")
            else:
                logger.error("❌ All fix attempts failed. Manual intervention required.")
    
    except Exception as e:
        logger.error(f"❌ Error while fixing duplicate settings panes: {e}")
