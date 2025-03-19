"""
Enhanced Document Manager for AI-Socratic-Clarifier - Simplified Fallback

This is a simplified version that provides basic document management functionality
without full features. It serves as a fallback when the full implementation is unavailable.
"""

import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedDocumentManager:
    """
    Simplified document manager that provides basic document functions.
    """
    
    def __init__(self, storage_dir=None):
        """
        Initialize the simplified document manager.
        
        Args:
            storage_dir: Base directory for document storage
        """
        if storage_dir is None:
            # Default to document_storage in the project root
            storage_dir = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'document_storage'))
        
        self.storage_dir = storage_dir
        self.index_file = os.path.join(storage_dir, 'document_index.json')
        
        # Ensure directories exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize default index structure
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'w') as f:
                json.dump({
                    "documents": [],
                    "last_updated": "2023-01-01T00:00:00"
                }, f, indent=2)
        
        logger.info(f"Simplified Document Manager initialized with storage at: {storage_dir}")
    
    def get_document_by_id(self, doc_id):
        """Get document metadata by ID."""
        try:
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)
            
            for doc in index_data.get("documents", []):
                if doc.get("id") == doc_id:
                    return doc
            
            return None
        except Exception as e:
            logger.error(f"Error getting document by ID: {e}")
            return None
    
    def get_document_content(self, doc_id):
        """Get the text content of a document by ID."""
        try:
            doc = self.get_document_by_id(doc_id)
            if not doc:
                return None
            
            # Check for text_path
            text_path = doc.get("text_path")
            if text_path and os.path.exists(text_path):
                with open(text_path, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            
            # Alternate: check for file_path + .txt
            file_path = doc.get("file_path") or doc.get("raw_path")
            if file_path and os.path.exists(f"{file_path}.txt"):
                with open(f"{file_path}.txt", 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            
            return "Document content not available."
        except Exception as e:
            logger.error(f"Error getting document content: {e}")
            return None

# Create a singleton instance
_document_manager = None

def get_document_manager():
    """Get or create the singleton document manager instance."""
    global _document_manager
    if _document_manager is None:
        _document_manager = EnhancedDocumentManager()
    return _document_manager
