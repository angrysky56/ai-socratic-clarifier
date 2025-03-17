#!/usr/bin/env python3
"""
Direct fix for the enhanced routes to handle document_context correctly.
"""

import os
from pathlib import Path

def fix_enhanced_routes():
    """Fix enhanced_routes.py to handle document_context parameter error."""
    file_path = Path(__file__).parent / "web_interface" / "enhanced_routes.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(file_path) + ".simple_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Find the direct_analyze_text calls
    if "result = direct_analyze_text(message, mode, use_sot, document_context=document_context)" in content:
        # Add error handling for the document_context parameter
        updated_content = content.replace(
            "result = direct_analyze_text(message, mode, use_sot, document_context=document_context)",
            """try:
                # Try with document_context parameter
                result = direct_analyze_text(message, mode, use_sot, document_context=document_context)
            except TypeError as e:
                if "document_context" in str(e):
                    # Fallback to call without document_context
                    logger.warning("direct_analyze_text() doesn't support document_context, falling back")
                    result = direct_analyze_text(message, mode, use_sot)
                    
                    # Add document context to the result manually
                    if document_context:
                        result["document_context"] = document_context
                else:
                    # Re-raise any other errors
                    raise"""
        )
        
        # Write the modified content
        with open(file_path, 'w') as f:
            f.write(updated_content)
        
        print("Added error handling for document_context parameter")
        return True
    else:
        print("Could not find the direct_analyze_text call with document_context parameter")
        return False

def main():
    """Main entry point."""
    print("Running enhanced routes fix...")
    
    if fix_enhanced_routes():
        print("Fix completed successfully!")
    else:
        print("Fix failed.")

if __name__ == "__main__":
    main()
