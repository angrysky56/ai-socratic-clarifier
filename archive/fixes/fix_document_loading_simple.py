#!/usr/bin/env python3
"""
Simple fix for document loading issues in the enhanced UI.

This script ensures the document storage directories exist and creates a test document
to verify functionality.
"""

import os
import sys
import json
import time
import uuid
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def fix_document_loading_simple():
    """Fix document loading issues with a simpler approach."""
    # Define base storage directory
    storage_dir = os.path.join(
        os.path.dirname(__file__),
        'document_storage'
    )
    
    # Define subdirectories
    raw_dir = os.path.join(storage_dir, 'raw')
    processed_dir = os.path.join(storage_dir, 'processed')
    embeddings_dir = os.path.join(storage_dir, 'embeddings')
    temp_dir = os.path.join(storage_dir, 'temp')
    
    # Ensure all directories exist
    for directory in [storage_dir, raw_dir, processed_dir, embeddings_dir, temp_dir]:
        if not os.path.exists(directory):
            logger.info(f"Creating directory: {directory}")
            os.makedirs(directory, exist_ok=True)
    
    # Check if document index exists
    index_file = os.path.join(storage_dir, 'document_index.json')
    
    if not os.path.exists(index_file):
        logger.info(f"Creating document index: {index_file}")
        with open(index_file, 'w') as f:
            json.dump({
                "documents": [],
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0"
            }, f, indent=2)
    
    # Create a test document
    test_doc_dir = os.path.join(temp_dir, "test")
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
    
    # Generate document ID and metadata
    doc_id = str(uuid.uuid4())
    file_name = os.path.basename(test_file_path)
    file_size = os.path.getsize(test_file_path)
    
    # Create document directory structure
    target_dir = os.path.join(raw_dir, doc_id)
    os.makedirs(target_dir, exist_ok=True)
    
    # Copy test file to raw directory
    raw_path = os.path.join(target_dir, file_name)
    with open(test_file_path, 'r') as src, open(raw_path, 'w') as dst:
        dst.write(src.read())
    
    # Save text content to processed directory
    processed_dir_doc = os.path.join(processed_dir, doc_id)
    os.makedirs(processed_dir_doc, exist_ok=True)
    text_path = os.path.join(processed_dir_doc, f"{file_name}.txt")
    
    with open(test_file_path, 'r') as src, open(text_path, 'w') as dst:
        text_content = src.read()
        dst.write(text_content)
    
    # Create document metadata
    doc_metadata = {
        "id": doc_id,
        "name": file_name,
        "raw_path": raw_path,
        "text_path": text_path,
        "embedding_path": None,
        "type": "text",
        "size": file_size,
        "page_count": 1,
        "text_length": len(text_content),
        "source": "system",
        "date_added": time.strftime("%Y-%m-%d %H:%M:%S"),
        "last_accessed": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tags": ["welcome", "test", "tutorial"],
        "has_embeddings": False
    }
    
    # Add to index if not already present
    try:
        with open(index_file, 'r') as f:
            index_data = json.load(f)
        
        # Check if we already have a test document
        has_test_doc = False
        for doc in index_data.get("documents", []):
            if "test" in doc.get("tags", []) and "welcome" in doc.get("tags", []):
                has_test_doc = True
                break
        
        if not has_test_doc:
            # Add test document to index
            index_data["documents"].append(doc_metadata)
            index_data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            logger.info(f"Added test document to index: {file_name}")
        else:
            logger.info("Test document already exists in index")
    except Exception as e:
        logger.error(f"Error updating document index: {e}")
    
    return True

if __name__ == "__main__":
    try:
        if fix_document_loading_simple():
            logger.info("Successfully fixed document loading issues")
            sys.exit(0)
        else:
            logger.error("Failed to fix document loading issues")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error fixing document loading: {e}")
        sys.exit(1)
