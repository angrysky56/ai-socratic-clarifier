#!/usr/bin/env python3
"""
Fix configuration file paths in the AI-Socratic-Clarifier.

This script ensures that the modules are looking for config.json in the correct location (project root)
instead of inside the archive directory or other incorrect locations.
"""

import os
import sys
import glob
import re
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = script_dir

def backup_file(file_path):
    """Create a backup of a file with .bak extension."""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.config_path_fix_bak"
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    return False

def find_py_files(directory):
    """Find all Python files in the given directory and its subdirectories."""
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files

def fix_config_paths_in_file(file_path):
    """Fix config paths in the given file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Fix hardcoded paths to config.json
        hardcoded_paths = [
            "config.json",
            "config.json",
            "config.json",
            "config.json",
        ]
        
        for path in hardcoded_paths:
            if path in content:
                content = content.replace(path, "../config.json" if "archive" in file_path else "config.json")
                changes_made = True
                logger.info(f"Fixed hardcoded config path in {file_path}")
        
        # Fix complex path constructions
        config_expressions = [
            r"os\.path\.join\(\s*os\.path\.dirname\(__file__\),\s*['\"]archive['\"],\s*['\"]fixes['\"],\s*['\"]config\.json['\"]\s*\)",
            r"os\.path\.join\(\s*os\.path\.dirname\(__file__\),\s*['\"]archive['\"],\s*['\"]config\.json['\"]\s*\)",
            r"os\.path\.join\(\s*os\.path\.dirname\(__file__\),\s*['\"]fixes['\"],\s*['\"]config\.json['\"]\s*\)",
        ]
        
        for expr in config_expressions:
            matches = re.findall(expr, content)
            for match in matches:
                # Replace with a reference to config.json in project root
                if "archive" in file_path:
                    # If the file is in archive, go back to project root
                    replacement = "os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')"
                else:
                    # If the file is already in project root
                    replacement = "os.path.join(os.path.dirname(__file__), 'config.json')"
                
                content = content.replace(match, replacement)
                changes_made = True
                logger.info(f"Fixed config path expression in {file_path}")
        
        # Fix loading ecosystem state
        ecosystem_state_paths = [
            "sequential_thinking/ecosystem_state.json",
            "sequential_thinking/ecosystem_state.json"
        ]
        
        for path in ecosystem_state_paths:
            if path in content:
                content = content.replace(path, "sequential_thinking/ecosystem_state.json")
                changes_made = True
                logger.info(f"Fixed ecosystem state path in {file_path}")
        
        # Write back if changes were made
        if changes_made:
            # Backup the original file
            backup_file(file_path)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error fixing config paths in {file_path}: {e}")
        return False

def copy_config_to_needed_locations():
    """Copy config.json to locations where it might be needed."""
    config_path = os.path.join(project_root, 'config.json')
    
    if not os.path.exists(config_path):
        logger.error(f"Config file not found at: {config_path}")
        return False
    
    # Copy to archive directory
    archive_config = os.path.join(project_root, 'archive', 'config.json')
    archive_fixes_config = os.path.join(project_root, 'archive', 'fixes', 'config.json')
    
    os.makedirs(os.path.dirname(archive_config), exist_ok=True)
    os.makedirs(os.path.dirname(archive_fixes_config), exist_ok=True)
    
    shutil.copy2(config_path, archive_config)
    shutil.copy2(config_path, archive_fixes_config)
    
    logger.info(f"Copied config.json to archive directories")
    return True

def fix_all_config_paths():
    """Fix config paths in all Python files."""
    # Get all Python files
    py_files = find_py_files(project_root)
    
    total_files = len(py_files)
    fixed_files = 0
    
    for file_path in py_files:
        # Skip the venv directory
        if 'venv/' in file_path:
            continue
        
        # Fix config paths in the file
        if fix_config_paths_in_file(file_path):
            fixed_files += 1
    
    # Copy config.json to needed locations
    copy_config_to_needed_locations()
    
    logger.info(f"Fixed config paths in {fixed_files}/{total_files} Python files")
    return True

if __name__ == "__main__":
    try:
        if fix_all_config_paths():
            logger.info("✨ Successfully fixed config file paths")
            sys.exit(0)
        else:
            logger.error("⚠️ Some config file paths could not be fixed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error fixing config file paths: {e}")
        sys.exit(1)
