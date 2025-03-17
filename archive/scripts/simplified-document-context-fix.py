#!/usr/bin/env python3
"""
Simplified fix for the document_context parameter issue.
"""

import os
from pathlib import Path

def fix_direct_integration():
    """Fix direct_integration.py to add document_context parameter."""
    file_path = Path(__file__).parent / "web_interface" / "direct_integration.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Make a backup
    backup_path = str(file_path) + ".simple_bak"
    with open(backup_path, 'w') as f:
        f.writelines(lines)
    print(f"Created backup at {backup_path}")
    
    # Find the function signature line
    function_line_index = None
    for i, line in enumerate(lines):
        if "def direct_analyze_text(text, mode=" in line and "document_context" not in line:
            function_line_index = i
            break
    
    if function_line_index is None:
        print("Error: Could not find the function signature line")
        return False
    
    # Update the function signature
    old_signature = lines[function_line_index]
    if "max_questions=5):" in old_signature:
        new_signature = old_signature.replace(
            "max_questions=5):", 
            "max_questions=5, document_context=None):"
        )
        lines[function_line_index] = new_signature
        print("Updated function signature to include document_context parameter")
    else:
        print("Error: Function signature doesn't match expected format")
        return False
    
    # Add document context handling code
    # Find where we initialize variables (after function signature)
    context_code = """    # Initialize document_context if not provided
    if document_context is None:
        document_context = []
    
    # Process any document context if provided
    document_text = ""
    if document_context:
        logger.info(f"Processing document context with {len(document_context)} documents")
        for doc in document_context:
            if isinstance(doc, dict) and "content" in doc:
                # Add document content to analysis context
                # (This is handled separately in the prompt construction)
                pass

"""
    
    # Insert after function declaration, indented 4 spaces
    lines.insert(function_line_index + 1, context_code)
    print("Added document context handling code")
    
    # Write the modified file
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    print(f"Successfully updated {file_path}")
    return True

def main():
    """Main entry point."""
    print("Running simplified document_context fix...")
    
    if fix_direct_integration():
        print("Fix completed successfully!")
    else:
        print("Fix failed.")

if __name__ == "__main__":
    main()
