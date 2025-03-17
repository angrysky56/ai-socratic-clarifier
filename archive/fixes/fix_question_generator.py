#!/usr/bin/env python3
"""
Fix for the question_generator.py file to address the undefined 'question' variable.
"""

import os
import sys
import shutil
import re
import traceback

def fix_question_generator():
    """Fix the error in question_generator.py."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "socratic_clarifier", "generators", "question_generator.py")
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Create backup
    backup_path = file_path + ".bak"
    print(f"Creating backup of {file_path} to {backup_path}")
    shutil.copy2(file_path, backup_path)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if 'questions.append(question)' line exists and fix it
        if "questions.append(question)" in content:
            # We need to fix this line, which is referencing an undefined variable
            # This is in the else clause where no templates are found for the issue type
            
            # Pattern to find the problematic section
            pattern = r'(\s+else:\s+)(\s+questions\.append\(question\))'
            
            # Replace with a default question for unknown issue types
            replacement = r'\1\tquestions.append(f"Can you clarify what you mean by \'{term}\'?")'
            
            # Apply the fix
            new_content = re.sub(pattern, replacement, content)
            
            # Write the fixed content
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            print(f"✅ Fixed question_generator.py")
            return True
        else:
            print(f"⚠️ Could not find the error pattern in {file_path}")
            return False
    
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        traceback.print_exc()
        
        # Restore from backup
        print(f"Restoring {file_path} from backup")
        shutil.copy2(backup_path, file_path)
        return False

def main():
    """Main function."""
    print("\n=== Fixing Question Generator Error ===\n")
    
    if fix_question_generator():
        print("\n✅ Successfully fixed the question generator!")
        print("You should now be able to generate questions without errors.")
        print("Please restart the server with ./start_socratic.py to apply the fix.")
    else:
        print("\n❌ Failed to fix the question generator.")
        print("Please check the error messages above.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
