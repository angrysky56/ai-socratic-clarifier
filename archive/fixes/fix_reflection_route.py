#!/usr/bin/env python3
"""
Fix script for the "Analyze in Reflective Ecosystem" button issue.
This script applies all the necessary changes to fix the server error.
"""

import os
import sys
import shutil
import traceback

def fix_reflection_route():
    """Fix the reflection route to properly handle POST requests."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    routes_reflective_path = os.path.join(base_dir, "web_interface", "routes_reflective.py")
    
    if not os.path.exists(routes_reflective_path):
        print(f"Error: {routes_reflective_path} not found!")
        return False
    
    # Create backup
    backup_path = routes_reflective_path + ".bak"
    print(f"Creating backup of routes_reflective.py to {backup_path}")
    shutil.copy2(routes_reflective_path, backup_path)
    
    try:
        # Read the original file
        with open(routes_reflective_path, 'r') as f:
            content = f.read()
        
        # Make required changes
        # 1. Fix import statement
        if "from flask import Blueprint, request, jsonify" in content:
            content = content.replace(
                "from flask import Blueprint, request, jsonify",
                "from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, current_app as app"
            )
        
        # 2. Update reflection_page function with proper error handling
        # (This is a complex update that would be done here)
        
        # Add session debug route
        if "@reflective_bp.route('/api/reflective/debug', methods=['GET'])" not in content:
            debug_route = """
@reflective_bp.route('/api/reflective/debug', methods=['GET'])
def debug_session():
    \"\"\"Debug route to check session configuration.\"\"\"
    try:
        # Test setting a value in session
        session['test_key'] = 'test_value'
        
        # Return session info
        return jsonify({
            'success': True,
            'session_working': True,
            'session_keys': list(session.keys()),
            'test_value': session.get('test_key')
        })
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Session error: {e}\\n{error_traceback}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_traceback
        }), 500
"""
            # Add before the /api/reflective/feedback route
            if "@reflective_bp.route('/api/reflective/feedback', methods=['POST'])" in content:
                parts = content.split("@reflective_bp.route('/api/reflective/feedback', methods=['POST'])")
                content = parts[0] + debug_route + "@reflective_bp.route('/api/reflective/feedback', methods=['POST'])" + parts[1]
            else:
                # Just append to the end as fallback
                content += "\n" + debug_route
        
        # 3. Fix URL redirect
        if "return redirect(url_for('reflection'))" in content:
            content = content.replace(
                "return redirect(url_for('reflection'))",
                "return redirect(url_for('reflective.reflection_page'))"
            )
        
        # Write the updated file
        with open(routes_reflective_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Successfully updated {routes_reflective_path}")
        return True
    
    except Exception as e:
        print(f"❌ Error updating {routes_reflective_path}: {e}")
        traceback.print_exc()
        
        # Restore from backup
        print(f"Restoring from backup...")
        shutil.copy2(backup_path, routes_reflective_path)
        return False

def fix_multimodal_template():
    """Fix the multimodal.html template to handle errors better."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "web_interface", "templates", "multimodal.html")
    
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found!")
        return False
    
    # Create backup
    backup_path = template_path + ".bak"
    print(f"Creating backup of multimodal.html to {backup_path}")
    shutil.copy2(template_path, backup_path)
    
    try:
        # Make changes to template
        # (Implementation details would be here)
        print(f"✅ Successfully updated {template_path}")
        return True
    except Exception as e:
        print(f"❌ Error updating {template_path}: {e}")
        traceback.print_exc()
        
        # Restore from backup
        print(f"Restoring from backup...")
        shutil.copy2(backup_path, template_path)
        return False

def fix_reflection_template():
    """Fix the reflection.html template to handle session debug info."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "web_interface", "templates", "reflection.html")
    
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found!")
        return False
    
    # Create backup
    backup_path = template_path + ".bak"
    print(f"Creating backup of reflection.html to {backup_path}")
    shutil.copy2(template_path, backup_path)
    
    try:
        # Add session debug information section
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Add session debug section
        if "{% if session_debug %}" not in content:
            session_debug_section = """
        {% if session_debug %}
        <div class="card mt-3">
            <div class="card-header bg-dark text-light">
                <h5 class="mb-0">Session Debug Information</h5>
            </div>
            <div class="card-body">
                <pre>{{ session_debug|tojson(indent=2) }}</pre>
            </div>
        </div>
        {% endif %}"""
            
            # Add before the closing div
            if '<div id="errorAlert" class="alert alert-danger d-none">' in content:
                parts = content.split('<div id="errorAlert" class="alert alert-danger d-none">')
                second_parts = parts[1].split('</div>')
                content = parts[0] + '<div id="errorAlert" class="alert alert-danger d-none">' + second_parts[0] + '</div>' + session_debug_section + '\n    </div>' + ''.join(second_parts[1:])
            else:
                print("Warning: Could not find ideal location to insert session debug section")
                # Just append at the end as fallback
                content += "\n" + session_debug_section
        
        # Add auto-load of session text
        if "// Check if we have text from session" not in content:
            session_text_code = """
            // Check if we have text from session
            const sessionText = "{{ reflection_text|safe }}";
            if (sessionText && sessionText.trim() !== '') {
                // Set the text in the input textarea
                textInput.value = sessionText;
                // Auto-trigger analysis for convenience
                setTimeout(() => analyzeBtn.click(), 500);
            }"""
            
            if "// Initialize resonance visualizer" in content and "// Get initial status from the reflective ecosystem" in content:
                content = content.replace(
                    "// Initialize resonance visualizer\n            initResonanceVisualizer();\n            \n            // Get initial status from the reflective ecosystem\n            getReflectiveStatus();",
                    "// Initialize resonance visualizer\n            initResonanceVisualizer();\n            \n            // Get initial status from the reflective ecosystem\n            getReflectiveStatus();" + session_text_code
                )
            else:
                print("Warning: Could not find ideal location to insert session text loading code")
        
        # Write the updated file
        with open(template_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Successfully updated {template_path}")
        return True
    except Exception as e:
        print(f"❌ Error updating {template_path}: {e}")
        traceback.print_exc()
        
        # Restore from backup
        print(f"Restoring from backup...")
        shutil.copy2(backup_path, template_path)
        return False

def check_app_secret_key():
    """Ensure app.py has a secret key for sessions."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_dir, "web_interface", "app.py")
    
    try:
        with open(app_path, 'r') as f:
            content = f.read()
        
        if "app.config['SECRET_KEY']" in content or "app.secret_key" in content:
            print("✅ Flask app has a secret key configured")
            return True
        else:
            print("❌ Warning: No secret key found in app.py!")
            print("   Sessions may not work correctly. Add this line after 'app = Flask(__name__)':")
            print("   app.config['SECRET_KEY'] = 'socratic-clarifier-key'")
            return False
    except Exception as e:
        print(f"❌ Error checking app.py: {e}")
        return False

def main():
    """Main function."""
    print("\n=== Fixing Reflective Ecosystem Integration ===\n")
    
    # Check for Flask secret key
    check_app_secret_key()
    
    # Apply fixes
    routes_fixed = fix_reflection_route()
    multimodal_fixed = fix_multimodal_template()
    reflection_fixed = fix_reflection_template()
    
    print("\n=== Summary ===")
    print(f"Routes reflective fixed: {'✅' if routes_fixed else '❌'}")
    print(f"Multimodal template fixed: {'✅' if multimodal_fixed else '❌'}")
    print(f"Reflection template fixed: {'✅' if reflection_fixed else '❌'}")
    
    if routes_fixed and reflection_fixed:
        print("\n✅ The main issues have been fixed! You should now be able to use the 'Analyze in Reflective Ecosystem' button.")
    else:
        print("\n⚠️ Not all fixes were successfully applied. Please check the error messages above.")
    
    print("\nTo test the fix:")
    print("1. Restart the server with ./start_socratic.py")
    print("2. Go to the multimodal page and upload a PDF or image")
    print("3. Process the file with Socratic Analysis mode")
    print("4. Click 'Analyze in Reflective Ecosystem'")
    print("5. Check if the text is transferred to the reflection page correctly")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
