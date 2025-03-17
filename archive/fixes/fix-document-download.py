#!/usr/bin/env python3
"""
Fix for document download functionality.
"""
import os
from pathlib import Path

def ensure_proper_document_structure():
    """Ensure document storage directories exist with proper permissions."""
    # Create main directory if it doesn't exist
    storage_dir = Path(__file__).parent / "document_storage"
    storage_dir.mkdir(exist_ok=True)
    print(f"Ensured document storage directory exists at {storage_dir}")
    
    # Create subdirectories
    for subdir in ["raw", "processed", "embeddings", "temp"]:
        (storage_dir / subdir).mkdir(exist_ok=True)
        print(f"Created directory: {storage_dir / subdir}")
    
    # Fix the send_file usage in enhanced_routes.py
    file_path = Path(__file__).parent / "web_interface" / "enhanced_routes.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(file_path) + ".download_fix_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Update the send_file usage (remove download_name if it's causing issues)
    if "download_name" in content:
        # Replace with a version that doesn't specify download_name
        old_send_file = """        # Send file
        return send_file(
            raw_path,
            as_attachment=True,
            download_name=doc_metadata.get("name", "document")
        )"""
        
        new_send_file = """        # Send file
        try:
            return send_file(
                raw_path,
                as_attachment=True,
                download_name=doc_metadata.get("name", "document")
            )
        except TypeError:
            # For older Flask versions that don't support download_name
            return send_file(
                raw_path,
                as_attachment=True,
                attachment_filename=doc_metadata.get("name", "document")
            )"""
        
        content = content.replace(old_send_file, new_send_file)
        print("Updated send_file usage for compatibility")
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed enhanced_routes.py for document download")
    return True

def main():
    """Main function."""
    print("Fixing document download functionality...")
    ensure_proper_document_structure()
    print("Done!")

if __name__ == "__main__":
    main()
