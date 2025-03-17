#!/usr/bin/env python3
"""
Fix specific UI elements in the integrated UI template.

This script focuses on fixing specific UI elements that may be causing issues with the layout.
"""

import os
import logging
import shutil
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Create a backup of a file."""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.elements_fix_bak"
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    return False

def fix_ui_elements():
    """Fix specific UI elements in the integrated UI template."""
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
        
        # Track if we made any changes
        changes_made = False
        
        # 1. Fix settings-pane closing tags
        if content.count('<div class="sidebar-pane" id="settings-pane">') > 1:
            # Find all occurrences
            settings_panes = re.finditer(r'<div class="sidebar-pane" id="settings-pane">', content)
            positions = [m.start() for m in settings_panes]
            
            if len(positions) > 1:
                # Keep only the first occurrence, remove the rest
                start_pos = positions[1]  # Start from the second occurrence
                
                # Find where to cut
                cut_end = content.find('<!-- Content Area -->')
                if cut_end > 0:
                    # Cut out the repeated sections
                    fixed_content = content[:start_pos] + content[cut_end:]
                    content = fixed_content
                    changes_made = True
                    logger.info("Removed duplicate settings pane sections")
        
        # 2. Fix sidebar-content structure
        sidebar_content_count = content.count('<div class="sidebar-content">')
        if sidebar_content_count > 1:
            # Find all occurrences
            sidebar_contents = re.finditer(r'<div class="sidebar-content">', content)
            positions = [m.start() for m in sidebar_contents]
            
            if len(positions) > 1:
                # Keep only the first occurrence
                start_pos = positions[1]  # Start from the second occurrence
                
                # Find where to cut
                next_major_section = content.find('<!-- Content Area -->', start_pos)
                if next_major_section > 0:
                    # Cut out the section with the duplicate sidebar-content
                    fixed_content = content[:start_pos] + content[next_major_section:]
                    content = fixed_content
                    changes_made = True
                    logger.info("Fixed duplicate sidebar-content sections")
        
        # 3. Fix any mismatched div tags
        open_divs = content.count('<div')
        close_divs = content.count('</div>')
        
        if open_divs != close_divs:
            logger.warning(f"Mismatched div tags: {open_divs} opening vs {close_divs} closing")
            
            # Check if there are too many closing divs
            if close_divs > open_divs:
                # Try to find sequences of multiple closing divs and reduce them
                extra_closings = close_divs - open_divs
                pattern = r'(</div>\s*){3,}'  # Find 3 or more consecutive closing divs
                
                # Replace with appropriate number of closing divs
                def replace_closings(match):
                    count = match.group(0).count('</div>')
                    if count > extra_closings + 2:  # Keep at least 2 closing divs
                        return '</div></div>'
                    return match.group(0)
                
                fixed_content = re.sub(pattern, replace_closings, content)
                if fixed_content != content:
                    content = fixed_content
                    changes_made = True
                    logger.info("Fixed excessive closing div tags")
        
        # 4. Ensure sidebar structure is correct
        if '<!-- Content Area -->' in content:
            # Find sidebar end and content area start
            sidebar_end_markers = [
                '</div>\n        </div>\n        \n        <!-- Content Area -->',
                '</div>\n            </div>\n        </div>\n        \n        <!-- Content Area -->'
            ]
            
            for marker in sidebar_end_markers:
                if marker not in content:
                    proper_end = '</div>\n            </div>\n        </div>\n        \n        <!-- Content Area -->'
                    fixed_content = content.replace('</div>\n        \n        <!-- Content Area -->', proper_end)
                    
                    if fixed_content != content:
                        content = fixed_content
                        changes_made = True
                        logger.info("Fixed sidebar closing structure")
        
        # Write back the fixed content if changes were made
        if changes_made:
            with open(ui_path, 'w') as f:
                f.write(content)
            logger.info("Successfully saved UI fixes")
        else:
            logger.info("No UI fixes required")
        
        return True
    
    except Exception as e:
        logger.error(f"Error fixing UI elements: {e}")
        return False

if __name__ == "__main__":
    try:
        if fix_ui_elements():
            logger.info("✨ Successfully fixed UI elements")
        else:
            logger.error("❌ Failed to fix UI elements")
    
    except Exception as e:
        logger.error(f"❌ Error while fixing UI elements: {e}")
