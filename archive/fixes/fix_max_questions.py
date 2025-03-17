#!/usr/bin/env python3
"""
Fix for the max_questions parameter error in AI-Socratic-Clarifier.

This script replaces the direct_integration.py file with a version that correctly
handles the max_questions parameter that is passed from routes_multimodal.py.

Original error:
Error: Error during Socratic analysis: direct_analyze_text() got an unexpected keyword argument 'max_questions'
"""

import os
import shutil
import sys

def main():
    """Apply the fix for the max_questions parameter."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_interface_dir = os.path.join(base_dir, "web_interface")
    
    direct_integration_path = os.path.join(web_interface_dir, "direct_integration.py")
    fixed_direct_integration_path = os.path.join(web_interface_dir, "fixed_direct_integration.py")
    
    if not os.path.exists(fixed_direct_integration_path):
        print("Error: fixed_direct_integration.py not found!")
        print("Make sure the file exists before running this script.")
        return 1
    
    # Create a backup of the original file
    backup_path = os.path.join(web_interface_dir, "direct_integration.py.bak")
    
    try:
        # Create backup if it doesn't exist
        if not os.path.exists(backup_path):
            print(f"Creating backup of original file: {backup_path}")
            shutil.copy2(direct_integration_path, backup_path)
        
        # Replace the original file with the fixed version
        print(f"Replacing {direct_integration_path} with fixed version")
        shutil.copy2(fixed_direct_integration_path, direct_integration_path)
        
        print("\nFix applied successfully!")
        print("\nThe following changes were made:")
        print("1. Added max_questions parameter to direct_analyze_text() function")
        print("2. Updated generate_socratic_questions() to accept max_questions parameter")
        print("3. Made the function pass the max_questions value to the reflective ecosystem")
        print("4. Added proper docstrings to all functions")
        print("\nPlease restart the application for the changes to take effect.")
        
        return 0
    except Exception as e:
        print(f"Error applying fix: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
