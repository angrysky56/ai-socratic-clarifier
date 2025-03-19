#!/usr/bin/env python3
"""
Manually fix the integrated UI template by completely rewriting it.

This script takes a more direct approach by manually identifying and removing duplicate settings panes.
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
        backup_path = f"{file_path}.manual_fix_bak"
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    return False

def fix_ui_manually():
    """Manually fix the integrated UI template."""
    ui_path = os.path.join("/home/ty/Repositories/ai_workspace/ai-socratic-clarifier", 
                          "web_interface", "templates", "integrated_ui.html")
    
    if not os.path.exists(ui_path):
        logger.error(f"Integrated UI template not found at: {ui_path}")
        return False
    
    # Backup the original file
    backup_file(ui_path)
    
    try:
        with open(ui_path, 'r') as f:
            content = f.readlines()
        
        # Look for lines containing the duplicate settings pane
        fixed_content = []
        settings_pane_found = False
        
        # For counting settings panes and their openings/closings
        settings_pane_count = 0
        in_settings_pane = False
        open_div_count = 0
        
        for line in content:
            if '<div class="sidebar-pane" id="settings-pane">' in line:
                settings_pane_count += 1
                
                # Only include the first occurrence
                if settings_pane_count == 1:
                    in_settings_pane = True
                    open_div_count = 1
                    fixed_content.append(line)
                    settings_pane_found = True
                # Skip the rest
                else:
                    logger.info(f"Skipping duplicate settings pane #{settings_pane_count}")
                    continue
            
            elif in_settings_pane:
                # Count div openings
                open_div_count += line.count('<div')
                
                # Count div closings
                close_count = line.count('</div>')
                open_div_count -= close_count
                
                # If we've closed all divs in the settings pane
                if open_div_count <= 0:
                    fixed_content.append(line)
                    in_settings_pane = False
                    logger.info(f"Reached end of settings pane #{settings_pane_count}")
                else:
                    fixed_content.append(line)
            
            else:
                fixed_content.append(line)
        
        # Write the fixed content back to the file
        with open(ui_path, 'w') as f:
            f.writelines(fixed_content)
        
        logger.info(f"Fixed {settings_pane_count} settings panes, keeping only the first one.")
        
        if not settings_pane_found:
            logger.warning("No settings panes found! This is unexpected.")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"Error manually fixing UI template: {e}")
        return False

if __name__ == "__main__":
    try:
        if fix_ui_manually():
            logger.info("✨ Successfully fixed UI template manually")
        else:
            logger.error("❌ Manual UI fix failed")
    
    except Exception as e:
        logger.error(f"❌ Error while manually fixing UI template: {e}")
