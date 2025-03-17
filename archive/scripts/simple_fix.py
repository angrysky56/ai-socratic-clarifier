#!/usr/bin/env python3
"""
Simple fix for the max_questions parameter issue in AI-Socratic-Clarifier.
"""

import os
import sys
import re

def fix_direct_integration():
    """Patch the direct_integration.py file to accept the max_questions parameter."""
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_interface_dir = os.path.join(base_dir, "web_interface")
    
    # Define file paths
    direct_integration_path = os.path.join(web_interface_dir, "direct_integration.py")
    
    try:
        # Read the original file
        with open(direct_integration_path, "r") as f:
            content = f.read()
        
        # Make the necessary changes
        
        # 1. Update the function definition to include max_questions parameter
        content = content.replace(
            "def direct_analyze_text(text, mode=\"standard\", use_sot=True):",
            "def direct_analyze_text(text, mode=\"standard\", use_sot=True, max_questions=5):"
        )
        
        # 2. Update the generate_socratic_questions function to accept max_questions
        content = content.replace(
            "def generate_socratic_questions(text, issues, sot_paradigm=None):",
            "def generate_socratic_questions(text, issues, sot_paradigm=None, max_questions=5):"
        )
        
        # 3. Modify the call to generate_socratic_questions to include max_questions
        content = content.replace(
            "questions = generate_socratic_questions(text, issues, sot_paradigm) if issues else []",
            "questions = generate_socratic_questions(text, issues, sot_paradigm, max_questions) if issues else []"
        )
        
        # Create a backup of the original file
        backup_path = direct_integration_path + ".backup"
        with open(backup_path, "w") as f:
            f.write(content)
        
        # Write the patched content back to the original file
        with open(direct_integration_path, "w") as f:
            f.write(content)
        
        print(f"Successfully patched {direct_integration_path}")
        print("The max_questions parameter should now work correctly!")
        return True
    
    except Exception as e:
        print(f"Error patching file: {e}")
        return False

if __name__ == "__main__":
    success = fix_direct_integration()
    sys.exit(0 if success else 1)
