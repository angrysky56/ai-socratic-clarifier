#!/usr/bin/env python3
"""
Script to fix settings page issues in AI-Socratic-Clarifier
"""

import os
import sys
import shutil
import logging
import json
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
        backup_path = f"{file_path}.settings_fix_bak"
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    return False

def fix_settings_page():
    """Fix settings page issues by adding multimodal model selection."""
    logger.info("Fixing settings page...")
    
    # Copy the fixed settings routes
    src_file = os.path.join(script_dir, "web_interface", "fixed_settings_routes.py")
    dst_file = os.path.join(script_dir, "web_interface", "fixed_settings_routes.py")
    
    if os.path.exists(src_file):
        logger.info(f"Settings routes already exist")
    else:
        logger.error(f"Fixed settings routes file not found: {src_file}")
        return False
    
    # Create settings page template directory if it doesn't exist
    template_dir = os.path.join(script_dir, "web_interface", "templates")
    os.makedirs(template_dir, exist_ok=True)
    
    # Copy the fixed settings page template
    src_file = os.path.join(script_dir, "web_interface", "templates", "fixed_settings_page.html")
    dst_file = os.path.join(script_dir, "web_interface", "templates", "fixed_settings_page.html")
    
    if os.path.exists(src_file):
        logger.info(f"Settings page template already exists")
    else:
        logger.error(f"Fixed settings page template not found: {src_file}")
        return False
    
    # Copy the fixed app.py with settings routes
    src_file = os.path.join(script_dir, "web_interface", "fixed_app.py")
    dst_file = os.path.join(script_dir, "web_interface", "app.py")
    if os.path.exists(src_file):
        backup_file(dst_file)
        shutil.copy2(src_file, dst_file)
        logger.info(f"Applied app.py fixes for settings routes")
    else:
        logger.error(f"Fixed app file not found: {src_file}")
        return False
    
    # Update the integrated UI template
    src_file = os.path.join(script_dir, "web_interface", "templates", "fixed_integrated_ui.html")
    dst_file = os.path.join(script_dir, "web_interface", "templates", "integrated_ui.html")
    if os.path.exists(src_file):
        backup_file(dst_file)
        shutil.copy2(src_file, dst_file)
        logger.info(f"Applied integrated UI template fixes for settings")
    else:
        logger.error(f"Fixed integrated UI template not found: {src_file}")
        return False
    
    return True

def update_config_with_multimodal():
    """Ensure config has multimodal model setting."""
    logger.info("Updating config with multimodal model setting...")
    
    # Get config file path
    config_path = os.path.join(script_dir, "config.json")
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return False
    
    # Create backup of config file
    backup_file(config_path)
    
    # Load config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check if multimodal model is configured
        if 'integrations' in config and 'ollama' in config['integrations']:
            if 'multimodal_model' not in config['integrations']['ollama']:
                config['integrations']['ollama']['multimodal_model'] = 'llava:latest'
                logger.info("Added default multimodal model 'llava:latest' to config.json")
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info("Config updated successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return False

def main():
    """Apply all settings page fixes."""
    logger.info("Starting to fix settings page issues...")
    
    # Fix settings page
    if fix_settings_page():
        logger.info("Settings page fixed successfully")
    else:
        logger.error("Failed to fix settings page")
    
    # Update config with multimodal model
    if update_config_with_multimodal():
        logger.info("Config updated successfully")
    else:
        logger.error("Failed to update config")
    
    logger.info("All settings page fixes applied. Restart the application to see the changes.")

if __name__ == "__main__":
    main()
