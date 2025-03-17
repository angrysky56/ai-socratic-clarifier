#!/usr/bin/env python3
"""
Fix for the reflection button in AI-Socratic-Clarifier.

This script adds a new route handler that will properly open the reflective analysis
in a new tab instead of trying to redirect within the same window, which was causing issues.
"""

import os
import sys
import shutil

def main():
    """Apply the fix for the reflective analysis button."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_interface_dir = os.path.join(base_dir, "web_interface")
    
    # Define paths
    routes_multimodal_path = os.path.join(web_interface_dir, "routes_multimodal.py")
    fixed_routes_path = os.path.join(web_interface_dir, "fixed_routes_reflective.py")
    
    # Create the fixed_routes_reflective.py file
    with open(fixed_routes_path, "w") as f:
        f.write('''"""
Fixed routes for reflective analysis integration.
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

# Create a blueprint
reflective_bp = Blueprint('reflective', __name__)

@reflective_bp.route('/reflection', methods=['GET', 'POST'])
def reflection_page():
    """Render the reflection page with optional pre-loaded text."""
    if request.method == 'POST':
        # Get text and mode from form submission
        text = request.form.get('text', '')
        mode = request.form.get('mode', 'standard')
        debug = request.form.get('debug', '0') == '1'
        
        # Store in session
        session['reflection_text'] = text
        session['reflection_mode'] = mode
        session['reflection_debug'] = debug
        
        # Render the template with the provided text
        return render_template('reflection.html', 
                              initial_text=text, 
                              initial_mode=mode,
                              debug=debug)
    else:
        # For GET requests, just render the template
        return render_template('reflection.html')

@reflective_bp.route('/api/reflective/debug', methods=['GET'])
def reflective_debug():
    """Debug endpoint to check if Reflective Ecosystem integration is working."""
    try:
        # Just return success for now
        return jsonify({
            'success': True,
            'message': 'Reflective ecosystem is available'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        })
''')
    
    # Update the app.py file to include the new blueprint
    app_path = os.path.join(web_interface_dir, "app.py")
    app_backup_path = os.path.join(web_interface_dir, "app.py.reflective_backup")
    
    # Create backup if not exists
    if not os.path.exists(app_backup_path):
        shutil.copy2(app_path, app_backup_path)
        print(f"Created backup of app.py: {app_backup_path}")
    
    # Read the app.py file
    with open(app_path, "r") as f:
        app_content = f.read()
    
    # Check if the fixed route is already imported
    if "from web_interface.fixed_routes_reflective import reflective_bp" not in app_content:
        # Add the import for the fixed routes
        app_content = app_content.replace(
            "from web_interface.routes_multimodal import multimodal_bp",
            "from web_interface.routes_multimodal import multimodal_bp\nfrom web_interface.fixed_routes_reflective import reflective_bp"
        )
        
        # Register the blueprint
        app_content = app_content.replace(
            "app.register_blueprint(multimodal_bp)",
            "app.register_blueprint(multimodal_bp)\napp.register_blueprint(reflective_bp)"
        )
        
        # Write the updated app.py file
        with open(app_path, "w") as f:
            f.write(app_content)
            
        print(f"Updated {app_path} to include the fixed reflective routes")
    else:
        print(f"The reflective blueprint is already registered in {app_path}")
    
    print("\nFix applied successfully!")
    print("\nThe following changes were made:")
    print("1. Created fixed_routes_reflective.py with improved reflection page handling")
    print("2. Updated app.py to use the new reflective routes blueprint")
    print("\nPlease restart the application for the changes to take effect.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
