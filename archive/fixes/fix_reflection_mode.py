#!/usr/bin/env python3
"""
Fix script for issues with the reflection page mode selection when using the 
'Analyze in Reflective Ecosystem' button.

This script:
1. Updates routes_reflective.py to pass the modes to the template
2. Updates routes_reflective.py to handle mode parameter from forms
3. Updates multimodal.html to include the mode in the form submission
4. Updates reflection.html to use the mode from the URL parameter

This ensures that when you analyze a document in the multimodal interface and
then click "Analyze in Reflective Ecosystem", it will transfer both the text
and the appropriate mode to the reflection page.
"""

import os
import sys
import shutil
import re
import traceback

def fix_routes_reflective():
    """Update routes_reflective.py to handle modes properly."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "web_interface", "routes_reflective.py")
    backup_path = file_path + ".bak"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Create backup
    print(f"Creating backup of {file_path} to {backup_path}")
    try:
        shutil.copy2(file_path, backup_path)
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
    try:
        # Read file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Make changes
        
        # 1. Add modes import and retrieval
        if "# Get available modes from the clarifier" not in content:
            content = content.replace(
                "# Show session debug info in development",
                """# Get available modes from the clarifier
        from socratic_clarifier import SocraticClarifier
        modes = []
        try:
            # Try to get available modes from the app's clarifier
            if hasattr(app, 'clarifier') and app.clarifier:
                modes = app.clarifier.available_modes()
            else:
                # Create a temporary clarifier to get modes
                clarifier = SocraticClarifier()
                modes = clarifier.available_modes()
        except Exception as e:
            logger.error(f"Error getting available modes: {e}")
            # Fallback modes
            modes = ['standard', 'deep', 'reflective']
        
        # Show session debug info in development"""
            )
        
        # 2. Pass modes to template
        if "modes=modes" not in content:
            content = content.replace(
                "reflection_text=reflection_text,\n                            session_debug=session_debug",
                "reflection_text=reflection_text,\n                            session_debug=session_debug,\n                            modes=modes"
            )
        
        # 3. Add mode handling in POST request
        if "# Get mode if present" not in content:
            content = content.replace(
                "if text:",
                """# Get mode if present
            mode = request.form.get('mode', '')
            if mode:
                # Store the mode in session
                try:
                    session['preferred_mode'] = mode
                    logger.info(f"Stored preferred mode in session: {mode}")
                except Exception as e:
                    logger.error(f"Error storing mode in session: {e}")
                    
            if text:"""
            )
        
        # 4. Update redirect to include mode
        if "redirect_url = url_for" not in content:
            content = content.replace(
                "# Redirect to GET to avoid form resubmission issues\n                return redirect(url_for('reflective.reflection_page'))",
                """# Redirect to GET to avoid form resubmission issues
                redirect_url = url_for('reflective.reflection_page')
                if mode:
                    redirect_url += f"?mode={mode}"
                return redirect(redirect_url)"""
            )
        
        # Write changes
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Successfully updated {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        traceback.print_exc()
        
        # Restore from backup
        try:
            print("Restoring from backup...")
            shutil.copy2(backup_path, file_path)
        except Exception as restore_error:
            print(f"Error restoring from backup: {restore_error}")
        
        return False

def fix_multimodal_template():
    """Update multimodal.html to pass the mode to the reflection page."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "web_interface", "templates", "multimodal.html")
    backup_path = file_path + ".bak"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Create backup
    print(f"Creating backup of {file_path} to {backup_path}")
    try:
        shutil.copy2(file_path, backup_path)
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
    try:
        # Read file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if we already have the targetMode code
        if "targetMode" not in content:
            # Find the analyze button click handler
            analyze_button_code = re.search(r'analyzeTextButton\.addEventListener\(\'click\', function\(\) \{.*?try \{.*?}\)', content, re.DOTALL)
            
            if analyze_button_code:
                old_code = analyze_button_code.group(0)
                
                # Create new code with mode handling
                new_code = old_code.replace(
                    "try {",
                    """try {
                    console.log('Submitting text to reflection page...');
                    
                    // Get the current mode (OCR, Multimodal, or Socratic)
                    const currentMode = document.querySelector('input[name="analysisMode"]:checked').value;
                    let targetMode = 'standard'; // Default mode for reflection page
                    
                    // Map the multimodal mode to reflection page mode
                    if (currentMode === 'socratic') {
                        targetMode = 'reflective'; // Use reflective mode for socratic analysis
                    } else if (currentMode === 'multimodal') {
                        targetMode = 'deep'; // Use deep mode for multimodal analysis
                    }"""
                ).replace(
                    "// Add the text as a form field",
                    """// Add the text as a form field"""
                ).replace(
                    "form.appendChild(textField);",
                    """form.appendChild(textField);
                    
                    // Add the mode as a form field
                    const modeField = document.createElement('input');
                    modeField.type = 'hidden';
                    modeField.name = 'mode';
                    modeField.value = targetMode;
                    form.appendChild(modeField);"""
                )
                
                # Replace the old code with the new code
                content = content.replace(old_code, new_code)
                
                # Write changes
                with open(file_path, 'w') as f:
                    f.write(content)
                
                print(f"✅ Successfully updated {file_path}")
                return True
            else:
                print(f"❌ Could not find analyze button click handler in {file_path}")
                return False
        else:
            print(f"✅ {file_path} already has the necessary changes")
            return True
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        traceback.print_exc()
        
        # Restore from backup
        try:
            print("Restoring from backup...")
            shutil.copy2(backup_path, file_path)
        except Exception as restore_error:
            print(f"Error restoring from backup: {restore_error}")
        
        return False

def fix_reflection_template():
    """Update reflection.html to use the mode parameter."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "web_interface", "templates", "reflection.html")
    backup_path = file_path + ".bak"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Create backup
    print(f"Creating backup of {file_path} to {backup_path}")
    try:
        shutil.copy2(file_path, backup_path)
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
    try:
        # Read file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if we already have the urlParams code
        if "urlParams" not in content and "// Check if we have text from session" in content:
            # Add URL parameter handling for mode
            content = content.replace(
                """// Check if we have text from session
            const sessionText = "{{ reflection_text|safe }}";
            if (sessionText && sessionText.trim() !== '') {
                // Set the text in the input textarea
                textInput.value = sessionText;
                // Auto-trigger analysis for convenience
                setTimeout(() => analyzeBtn.click(), 500);
            }""",
                """// Check if we have text from session
            const sessionText = "{{ reflection_text|safe }}";
            if (sessionText && sessionText.trim() !== '') {
                // Set the text in the input textarea
                textInput.value = sessionText;
                // Check if we have a preferred mode
                const urlParams = new URLSearchParams(window.location.search);
                const preferredMode = urlParams.get('mode');
                if (preferredMode && modeSelect.querySelector(`option[value="${preferredMode}"]`)) {
                    modeSelect.value = preferredMode;
                }
                // Auto-trigger analysis for convenience
                setTimeout(() => analyzeBtn.click(), 500);
            }"""
            )
            
            # Write changes
            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Successfully updated {file_path}")
            return True
        else:
            print(f"✅ {file_path} already has the necessary changes")
            return True
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        traceback.print_exc()
        
        # Restore from backup
        try:
            print("Restoring from backup...")
            shutil.copy2(backup_path, file_path)
        except Exception as restore_error:
            print(f"Error restoring from backup: {restore_error}")
        
        return False

def main():
    """Main function."""
    print("\n=== Fixing Mode Selection in Reflection Ecosystem ===\n")
    
    # Apply the fixes
    reflective_fixed = fix_routes_reflective()
    multimodal_fixed = fix_multimodal_template()
    reflection_fixed = fix_reflection_template()
    
    print("\n=== Summary ===")
    print(f"Routes reflective fixed: {'✅' if reflective_fixed else '❌'}")
    print(f"Multimodal template fixed: {'✅' if multimodal_fixed else '❌'}")
    print(f"Reflection template fixed: {'✅' if reflection_fixed else '❌'}")
    
    if reflective_fixed and multimodal_fixed and reflection_fixed:
        print("\n✅ All fixes successfully applied!")
        print("When you click 'Analyze in Reflective Ecosystem', the mode will now be preserved.")
    else:
        print("\n⚠️ Not all fixes were successfully applied. Please check the error messages above.")
    
    print("\nTo test the fix:")
    print("1. Restart the server with ./start_socratic.py")
    print("2. Go to the multimodal page and upload a PDF or image")
    print("3. Select a specific processing mode (OCR, Multimodal, or Socratic)")
    print("4. Process the file")
    print("5. Click 'Analyze in Reflective Ecosystem'")
    print("6. Check if the text is transferred and the appropriate mode is selected")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
