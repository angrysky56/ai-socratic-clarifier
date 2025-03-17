#!/usr/bin/env python3
"""
Fix for document loading issues in the enhanced UI.

This script updates the document_manager.py to fix issues with loading documents
and ensures the directory structure is properly set up.
"""

import os
import sys
import json
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def fix_document_loading():
    """Fix document loading issues."""
    # Ensure document storage directories exist with proper permissions
    from enhanced_integration.document_manager import get_document_manager
    
    manager = get_document_manager()
    
    # Check if directories exist and are writable
    logger.info(f"Checking document storage at: {manager.storage_dir}")
    storage_dirs = [
        manager.storage_dir,
        manager.raw_dir,
        manager.processed_dir, 
        manager.embeddings_dir,
        manager.temp_dir
    ]
    
    for directory in storage_dirs:
        if not os.path.exists(directory):
            logger.info(f"Creating directory: {directory}")
            os.makedirs(directory, exist_ok=True)
        elif not os.access(directory, os.W_OK):
            logger.warning(f"Directory not writable: {directory}")
            # Try to fix permissions
            try:
                os.chmod(directory, 0o755)
                logger.info(f"Fixed permissions for: {directory}")
            except Exception as e:
                logger.error(f"Failed to fix permissions: {e}")
    
    # Check if document index exists and is valid
    if not os.path.exists(manager.index_file):
        logger.info(f"Document index doesn't exist, creating: {manager.index_file}")
        # Create empty index
        with open(manager.index_file, 'w') as f:
            json.dump({
                "documents": [],
                "last_updated": "2025-03-16 17:00:00",
                "version": "1.0"
            }, f, indent=2)
    else:
        # Validate index
        try:
            with open(manager.index_file, 'r') as f:
                index_data = json.load(f)
            
            # Check if it has required fields
            required_fields = ["documents", "last_updated", "version"]
            if not all(field in index_data for field in required_fields):
                logger.warning(f"Document index is missing required fields, recreating")
                
                # Back up the old index
                backup_path = f"{manager.index_file}.bak"
                with open(backup_path, 'w') as f:
                    json.dump(index_data, f, indent=2)
                
                # Create new index
                with open(manager.index_file, 'w') as f:
                    json.dump({
                        "documents": index_data.get("documents", []),
                        "last_updated": "2025-03-16 17:00:00",
                        "version": "1.0"
                    }, f, indent=2)
                
                logger.info(f"Fixed document index and backed up original to: {backup_path}")
        except Exception as e:
            logger.error(f"Error validating document index: {e}")
            
            # Create new index
            with open(manager.index_file, 'w') as f:
                json.dump({
                    "documents": [],
                    "last_updated": "2025-03-16 17:00:00",
                    "version": "1.0"
                }, f, indent=2)
    
    # Add a test document if no documents exist
    try:
        with open(manager.index_file, 'r') as f:
            index_data = json.load(f)
        
        if not index_data.get("documents"):
            logger.info("No documents found, adding a test document")
            
            # Create a test text file
            test_doc_dir = os.path.join(manager.temp_dir, "test")
            os.makedirs(test_doc_dir, exist_ok=True)
            
            test_file_path = os.path.join(test_doc_dir, "welcome.txt")
            with open(test_file_path, 'w') as f:
                f.write("""Welcome to the AI-Socratic-Clarifier!

This is a test document that demonstrates the document management functionality.
You can:
1. Upload your own documents
2. View document content
3. Add documents to RAG context for enhanced AI responses

Try uploading a PDF, text file, or other document to get started.
""")
            
            # Process the document
            manager.process_document(
                test_file_path,
                source="system",
                generate_embeddings=True,
                metadata={"tags": ["welcome", "test", "tutorial"]}
            )
            
            logger.info("Added test document to document library")
    except Exception as e:
        logger.error(f"Error adding test document: {e}")
    
    return True

if __name__ == "__main__":
    try:
        if fix_document_loading():
            logger.info("Successfully fixed document loading issues")
            sys.exit(0)
        else:
            logger.error("Failed to fix document loading issues")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error fixing document loading: {e}")
        sys.exit(1)
