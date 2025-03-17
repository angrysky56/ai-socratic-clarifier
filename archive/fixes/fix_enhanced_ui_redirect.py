#!/usr/bin/env python3
"""
Fix script for the enhanced UI redirect issue.

This script modifies the app.py file to:
1. Properly redirect the root route to the enhanced UI
2. Register the enhanced routes blueprint
"""

import os
import sys
import re
from pathlib import Path

def fix_app_py():
    """Fix the app.py file to properly redirect to enhanced UI."""
    app_py_path = Path(__file__).parent / "web_interface" / "app.py"
    
    if not app_py_path.exists():
        print(f"Error: Cannot find app.py at {app_py_path}")
        return False
    
    # Read the current content
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = app_py_path.with_suffix('.py.enhanced_bak')
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup of app.py at {backup_path}")
    
    # Check if enhanced routes are already imported
    enhanced_routes_import = 'from web_interface.enhanced_routes import enhanced_bp'
    if enhanced_routes_import not in content:
        # Add enhanced routes import after the other imports
        try:
            multimodal_import_pattern = r'(try:.*?import.*?multimodal_bp.*?MULTIMODAL_ROUTES_AVAILABLE.*?logger\.warning.*?\n)'
            if re.search(multimodal_import_pattern, content, re.DOTALL):
                content = re.sub(
                    multimodal_import_pattern,
                    r'\1\n# Import enhanced routes\ntry:\n    from web_interface.enhanced_routes import enhanced_bp\n    ENHANCED_ROUTES_AVAILABLE = True\nexcept ImportError:\n    ENHANCED_ROUTES_AVAILABLE = False\n    logger.warning("Enhanced routes not available")\n',
                    content,
                    flags=re.DOTALL
                )
            else:
                # Fallback if the pattern isn't found
                from_web_interface_pattern = r'(from web_interface import.*?\n)'
                content = re.sub(
                    from_web_interface_pattern,
                    r'\1from web_interface.enhanced_routes import enhanced_bp\n',
                    content
                )
        except Exception as e:
            print(f"Error adding enhanced routes import: {e}")
            return False
    
    # Check if enhanced routes blueprint is registered
    register_enhanced_bp = 'app.register_blueprint(enhanced_bp)'
    if register_enhanced_bp not in content:
        # Add registration after the other blueprints
        register_pattern = r'(app\.register_blueprint\(.*?\).*?logger\.info.*?\n)'
        content = re.sub(
            register_pattern,
            r'\1\n# Register the enhanced routes blueprint\napp.register_blueprint(enhanced_bp)\nlogger.info("Enhanced routes registered")\n',
            content,
            flags=re.DOTALL,
            count=1  # Only replace the last occurrence
        )
    
    # Fix the root route
    root_route_pattern = r'@app\.route\(\'/\', methods=\[\'GET\'\]\)\ndef index\(\):\s+""".*?"""\s+return render_template\(\'index\.html\', modes=clarifier\.available_modes\(\)\)'
    new_root_route = """@app.route('/', methods=['GET'])
def index():
    \"\"\"Redirect to enhanced UI if available, otherwise render the main page.\"\"\"
    try:
        # Check if enhanced routes are registered
        if hasattr(app, 'blueprints') and 'enhanced' in app.blueprints:
            return redirect('/enhanced')
        else:
            return render_template('index.html', modes=clarifier.available_modes())
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('index.html', modes=clarifier.available_modes())"""
    
    if re.search(root_route_pattern, content, re.DOTALL):
        content = re.sub(root_route_pattern, new_root_route, content, flags=re.DOTALL)
    else:
        print("Warning: Could not find the root route pattern to replace")
        # Try a simpler pattern
        simple_pattern = r'@app\.route\(\'/\', methods=\[\'GET\'\]\)\ndef index\(\):'
        if re.search(simple_pattern, content):
            # Find the whole function
            index_function_match = re.search(
                r'(@app\.route\(\'/\', methods=\[\'GET\'\]\)\ndef index\(\):.*?)(?=@app\.route|$)', 
                content, 
                re.DOTALL
            )
            if index_function_match:
                # Replace the whole function
                content = content.replace(index_function_match.group(1), new_root_route + "\n\n")
            else:
                print("Error: Could not find the complete index function")
                return False
        else:
            print("Error: Could not find the root route")
            return False
    
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
        else:
            print("Warning: Could not find Flask import to add redirect")
    
    # Write the modified content
    with open(app_py_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully updated {app_py_path} to redirect to enhanced UI")
    return True

def main():
    """Main entry point."""
    print("Fixing Enhanced UI redirect issue...")
    
    # Add the parent directory to the Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Fix app.py
    if fix_app_py():
        print("Fix complete! Run 'python start_enhanced_ui.py' to start the enhanced UI.")
    else:
        print("Fix failed. Please check the errors above.")

if __name__ == "__main__":
    main()
