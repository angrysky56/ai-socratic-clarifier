#!/usr/bin/env python3
"""
Apply all fixes for the AI-Socratic-Clarifier at once.

This script runs all the individual fix scripts to address:
1. max_questions parameter error
2. Reflective analysis button issues
3. UI improvements
"""

import os
import sys
import subprocess
import time

def run_script(script_name):
    """Run a Python script and return its exit code."""
    print(f"\n=== Running {script_name} ===\n")
    result = subprocess.run([sys.executable, script_name])
    return result.returncode

def main():
    """Apply all fixes in sequence."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of scripts to run
    scripts = [
        os.path.join(base_dir, "fix_max_questions.py"),
        os.path.join(base_dir, "fix_reflection_button.py"),
        os.path.join(base_dir, "improved_multimodal_ui.py")
    ]
    
    # Check if all scripts exist
    for script in scripts:
        if not os.path.exists(script):
            print(f"Error: Script {script} not found!")
            return 1
    
    # Run each script
    success = True
    for script in scripts:
        exit_code = run_script(script)
        if exit_code != 0:
            print(f"Error: Script {script} failed with exit code {exit_code}")
            success = False
    
    if success:
        print("\n=== All fixes applied successfully! ===")
        print("\nPlease restart the application for all changes to take effect.")
        print("\nYou can access the application at:")
        print("  - Original UI (with fixes): /multimodal")
        print("  - Improved UI: /improved_multimodal")
        return 0
    else:
        print("\n=== Some fixes failed to apply ===")
        print("Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
