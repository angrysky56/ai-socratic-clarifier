#!/usr/bin/env python3
"""
Script to fix document deletion issues in AI-Socratic-Clarifier
"""

import os
import sys
import shutil
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

def backup_file(file_path):
    """Create a backup of a file with .bak extension."""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.deletion_fix_bak"
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    return False

def fix_document_deletion():
    """Fix document deletion functionality in document_rag_routes.py."""
    logger.info("Fixing document deletion functionality...")
    
    # Copy the fixed document_rag_routes.py
    src_file = os.path.join(script_dir, "web_interface", "fixed_document_rag_routes.py")
    dst_file = os.path.join(script_dir, "web_interface", "document_rag_routes.py")
    if os.path.exists(src_file):
        backup_file(dst_file)
        shutil.copy2(src_file, dst_file)
        logger.info(f"Applied document_rag_routes.py fixes")
    else:
        logger.error(f"Fixed document routes file not found: {src_file}")

def cleanup_document_index():
    """Clean up the document index by removing entries with invalid file paths."""
    logger.info("Cleaning up document index...")
    
    # Get document index file path
    index_file = os.path.join(script_dir, "document_storage", "document_index.json")
    if not os.path.exists(index_file):
        logger.error(f"Document index file not found: {index_file}")
        return False
    
    # Create backup of index file
    backup_file(index_file)
    
    # Load document index
    try:
        with open(index_file, 'r') as f:
            index_data = json.load(f)
        
        documents = index_data.get("documents", [])
        original_count = len(documents)
        valid_documents = []
        
        # Check each document
        for doc in documents:
            file_path = doc.get("file_path")
            # Skip documents with None or invalid file paths
            if file_path and os.path.exists(file_path):
                valid_documents.append(doc)
            else:
                logger.info(f"Removing invalid document entry: {doc.get('id')} - {doc.get('filename', 'unknown')}")
        
        # Update index with valid documents only
        index_data["documents"] = valid_documents
        
        # Save updated index
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        logger.info(f"Cleaned up document index - removed {original_count - len(valid_documents)} invalid entries")
        return True
    
    except Exception as e:
        logger.error(f"Error cleaning up document index: {e}")
        return False

def check_document_directories():
    """Check that all document directories exist and are properly structured."""
    logger.info("Checking document directories...")
    
    # Document storage directory
    storage_dir = os.path.join(script_dir, "document_storage")
    if not os.path.exists(storage_dir):
        logger.error(f"Document storage directory not found: {storage_dir}")
        return False
    
    # Get document index
    index_file = os.path.join(storage_dir, "document_index.json")
    if not os.path.exists(index_file):
        logger.error(f"Document index file not found: {index_file}")
        return False
    
    try:
        with open(index_file, 'r') as f:
            index_data = json.load(f)
        
        documents = index_data.get("documents", [])
        
        # Check each document
        for doc in documents:
            doc_id = doc.get("id")
            file_path = doc.get("file_path")
            
            if not file_path:
                logger.warning(f"Document {doc_id} has no file path")
                continue
            
            # Check if document directory exists
            doc_dir = os.path.dirname(file_path)
            if not os.path.exists(doc_dir):
                logger.warning(f"Document directory does not exist: {doc_dir}")
                # Optionally create the directory
                # os.makedirs(doc_dir, exist_ok=True)
                # logger.info(f"Created document directory: {doc_dir}")
            
            # Check if document file exists
            if not os.path.exists(file_path):
                logger.warning(f"Document file does not exist: {file_path}")
        
        logger.info(f"Checked {len(documents)} document entries")
        return True
    
    except Exception as e:
        logger.error(f"Error checking document directories: {e}")
        return False

def main():
    """Apply all fixes."""
    logger.info("Starting to fix document deletion issues...")
    
    # Fix document deletion functionality
    fix_document_deletion()
    
    # Clean up document index
    cleanup_document_index()
    
    # Check document directories
    check_document_directories()
    
    logger.info("Fixes applied successfully. Restart the application to see the changes.")

if __name__ == "__main__":
    main()
