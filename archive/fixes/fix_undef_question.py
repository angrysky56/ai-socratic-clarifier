#!/usr/bin/env python3
"""
Quick fix for the 'question' undefined variable in question_generator.py
"""

import os
import shutil

def main():
    """Apply the fix directly."""
    # Get paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_file = os.path.join(base_dir, "socratic_clarifier", "generators", "question_generator.py")
    fixed_file = os.path.join(base_dir, "socratic_clarifier", "generators", "fixed_question_generator.py")
    backup_file = os.path.join(base_dir, "socratic_clarifier", "generators", "question_generator.py.bak")
    
    # Check files
    if not os.path.exists(source_file):
        print(f"Error: Original file not found at {source_file}")
        return 1
    
    if not os.path.exists(fixed_file):
        print(f"Error: Fixed file not found at {fixed_file}")
        return 1
    
    # Create backup
    print(f"Creating backup of original file to {backup_file}")
    shutil.copy2(source_file, backup_file)
    
    # Apply fix by copying fixed file
    print(f"Applying fix...")
    shutil.copy2(fixed_file, source_file)
    
    print("\n✅ Fix applied successfully!")
    print("The undefined 'question' variable has been fixed.")
    print("Restart the server to use the fixed version.")
    
    return 0

if __name__ == "__main__":
    exit(main())
