#!/usr/bin/env python3
"""
Simplified fix for UI issues in the AI-Socratic-Clarifier.

This script focuses on removing duplicate settings panes and fixing div structure.
"""

import os
import logging
import shutil
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_ui_issues():
    """Fix UI issues in the integrated template."""
    ui_path = os.path.join("/home/ty/Repositories/ai_workspace/ai-socratic-clarifier", 
                          "web_interface", "templates", "integrated_ui.html")
    
    if not os.path.exists(ui_path):
        logger.error(f"UI template not found at: {ui_path}")
        return False
    
    # Backup the file
    backup_path = f"{ui_path}.simplified_fix_bak"
    logger.info(f"Creating backup to {backup_path}")
    shutil.copy2(ui_path, backup_path)
    
    # Read the file content
    with open(ui_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Remove duplicate settings panes
    # First, find all settings pane sections
    settings_pattern = r'<div class="sidebar-pane" id="settings-pane">[\s\S]*?<a href="/settings" class="btn btn-outline-primary">[\s\S]*?</a>[\s\S]*?</div>[\s\S]*?</div>'
    settings_matches = list(re.finditer(settings_pattern, content))
    
    if len(settings_matches) > 1:
        logger.info(f"Found {len(settings_matches)} settings pane sections")
        
        # Keep only the first match, remove others
        for i in range(1, len(settings_matches)):
            match = settings_matches[i]
            content = content[:match.start()] + content[match.end():]
            logger.info(f"Removed duplicate settings pane #{i+1}")
    else:
        logger.info("No duplicate settings pane sections found")
    
    # Fix 2: Correct any mismatched div tags
    # Count opening and closing div tags
    open_count = content.count('<div')
    close_count = content.count('</div>')
    
    if open_count != close_count:
        logger.info(f"Found mismatched div tags: {open_count} opening vs {close_count} closing")
        
        # If we have more closing tags than opening tags, remove some
        if close_count > open_count:
            excess = close_count - open_count
            pattern = r'(</div>\s*){3,}'  # Find sequences of 3+ consecutive closing divs
            
            def replace_divs(match):
                divs = match.group(0)
                count = divs.count('</div>')
                if count > 3 and count - 2 <= excess:  # Only reduce if it won't remove too many
                    return '</div></div>'
                return divs
            
            fixed_content = re.sub(pattern, replace_divs, content)
            if fixed_content != content:
                content = fixed_content
                logger.info("Fixed excessive closing div tags")
    
    # Fix 3: Ensure properly structured sidebar-content area
    # Structure should be: sidebar-content > sidebar-pane > settings, then close properly
    content = re.sub(r'</div>\s*</div>\s*</div>\s*</div>\s*</div>', '</div>\n            </div>\n        </div>', content)
    
    # Write the fixed content
    with open(ui_path, 'w') as f:
        f.write(content)
    
    logger.info("Completed UI fixes")
    return True

if __name__ == "__main__":
    try:
        if fix_ui_issues():
            logger.info("✨ Successfully fixed UI issues")
        else:
            logger.error("❌ Failed to fix UI issues")
    except Exception as e:
        logger.error(f"Error: {e}")
