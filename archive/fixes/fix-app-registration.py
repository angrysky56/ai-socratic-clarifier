#!/usr/bin/env python3
"""
Fix script for the enhanced UI blueprint registration issue.

This script modifies the app.py file to handle the enhanced blueprint correctly.
"""

import os
import sys
import re
from pathlib import Path

def fix_app_py():
    """Fix the app.py file to handle enhanced blueprint registration correctly."""
    app_py_path = Path(__file__).parent / "web_interface" / "app.py"
    
    if not app_py_path.exists():
        print(f"Error: Cannot find app.py at {app_py_path}")
        return False
    
    # Read the current content
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = app_py_path.with_suffix('.py.blueprint_fix_bak')
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup of app.py at {backup_path}")
    
    # Check if enhanced routes registration exists and modify it to be conditional
    enhanced_register_pattern = r'app\.register_blueprint\(enhanced_bp\)\s*logger\.info\("Enhanced routes registered"\)'
    
    # If the pattern exists, replace it with conditional registration
    if re.search(enhanced_register_pattern, content):
        conditional_register = """# Register enhanced routes if not registered already
if 'enhanced' not in app.blueprints:
    app.register_blueprint(enhanced_bp)
    logger.info("Enhanced routes registered")
else:
    logger.info("Enhanced routes already registered")"""
        
        content = re.sub(enhanced_register_pattern, conditional_register, content)
        print("Modified enhanced blueprint registration to be conditional")
    
    # Fix the root route to ensure it redirects to enhanced UI
    root_route_pattern = r'@app\.route\(\'/\', methods=\[\'GET\'\]\)\s*def index\(\):'
    
    if re.search(root_route_pattern, content):
        # Find the whole function
        index_function_match = re.search(
            r'(@app\.route\(\'/\', methods=\[\'GET\'\]\)\s*def index\(\):.*?)(?=@app\.route|$)', 
            content, 
            re.DOTALL
        )
        
        if index_function_match:
            new_root_route = '''@app.route('/', methods=['GET'])
def index():
    """Redirect to enhanced UI if available, otherwise render the main page."""
    if 'enhanced' in app.blueprints:
        return redirect('/enhanced')
    return render_template('index.html', modes=clarifier.available_modes())
'''
            # Replace the whole function
            content = content.replace(index_function_match.group(1), new_root_route)
            print("Modified root route to redirect to enhanced UI")
    
    # Make sure redirect is imported
    if 'from flask import redirect' not in content:
        # Replace the flask import line
        flask_import_pattern = r'from flask import (.*)'
        if re.search(flask_import_pattern, content):
            content = re.sub(
                flask_import_pattern,
                r'from flask import \1, redirect',
                content
            )
            print("Added redirect import to Flask imports")
    
    # Write the modified content
    with open(app_py_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully updated {app_py_path} to fix blueprint registration")
    return True

def main():
    """Main entry point."""
    print("Fixing Enhanced UI blueprint registration issue...")
    
    # Add the parent directory to the Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Fix app.py
    if fix_app_py():
        print("Fix complete! Run 'python start_enhanced_ui.py' to start the enhanced UI.")
    else:
        print("Fix failed. Please check the errors above.")

if __name__ == "__main__":
    main()
