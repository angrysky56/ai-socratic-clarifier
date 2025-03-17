#!/usr/bin/env python3
"""
Fix for syntax error in enhanced_routes.py
"""
import os
from pathlib import Path

def fix_syntax_error():
    """Fix the syntax error in enhanced_routes.py"""
    file_path = Path(__file__).parent / "web_interface" / "enhanced_routes.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Make a backup
    backup_path = str(file_path) + ".syntax_fix_bak"
    with open(backup_path, 'w') as f:
        f.writelines(lines)
    print(f"Created backup at {backup_path}")
    
    # Find the problematic section and fix it
    # Based on the error, there seems to be an unmatched parenthesis around line 224
    
    # Write a completely fixed version of the download_document function
    fixed_function = """@enhanced_bp.route('/api/documents/<doc_id>/download', methods=['GET'])
def download_document(doc_id):
    \"\"\"Download the original document file.\"\"\"
    try:
        # Get the document manager
        manager = get_document_manager()
        
        # Get document metadata
        doc_metadata = manager.get_document_by_id(doc_id)
        
        if not doc_metadata or "raw_path" not in doc_metadata:
            return jsonify({"success": False, "error": "Document not found"}), 404
        
        # Check if file exists
        raw_path = doc_metadata.get("raw_path")
        if not os.path.exists(raw_path):
            return jsonify({"success": False, "error": "Document file not found"}), 404
        
        # Send file with better error handling
        try:
            # For newer Flask versions
            return send_file(
                raw_path,
                as_attachment=True,
                download_name=doc_metadata.get("name", "document")
            )
        except TypeError:
            # For older Flask versions
            return send_file(
                raw_path,
                as_attachment=True,
                attachment_filename=doc_metadata.get("name", "document")
            )
        except Exception as e:
            # Last resort fallback
            logger.error(f"Error using send_file: {e}")
            from flask import Response
            with open(raw_path, 'rb') as f:
                data = f.read()
            
            response = Response(data, mimetype='application/octet-stream')
            response.headers.set('Content-Disposition', f'attachment; filename={doc_metadata.get("name", "document")}')
            return response
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error downloading document: {e}\\n{error_traceback}")
        return jsonify({"success": False, "error": str(e)}), 500
"""
    
    # Find the download_document function
    start_line = -1
    end_line = -1
    
    for i, line in enumerate(lines):
        if 'def download_document(doc_id):' in line:
            start_line = i
        elif start_line != -1 and '@enhanced_bp.route' in line:
            end_line = i
            break
    
    if start_line == -1:
        print("Could not find download_document function")
        return False
    
    if end_line == -1:
        end_line = len(lines)  # If no next route, go to end of file
    
    # Replace the function
    original_function = ''.join(lines[start_line-1:end_line])
    print(f"Found function from line {start_line} to {end_line-1}")
    
    # Split fixed function into lines
    fixed_lines = fixed_function.split('\n')
    fixed_lines = [line + '\n' for line in fixed_lines]
    
    # Replace the function in the original file
    new_lines = lines[:start_line-1] + fixed_lines + lines[end_line:]
    
    # Write the fixed content
    with open(file_path, 'w') as f:
        f.writelines(new_lines)
    
    print("Fixed syntax error in download_document function")
    return True

def main():
    """Main function."""
    print("Fixing syntax error in enhanced_routes.py...")
    
    if fix_syntax_error():
        print("✅ Syntax error fixed")
    else:
        print("❌ Failed to fix syntax error")
    
    print("\nDone! Please restart the application with:")
    print("python start_enhanced_ui.py")

if __name__ == "__main__":
    main()
