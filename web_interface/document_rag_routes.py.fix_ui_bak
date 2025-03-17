"""
Routes for document RAG (Retrieval-Augmented Generation) integration.
This module provides routes for document management, embedding generation,
and retrieval for use in the chat and reflection interfaces.
"""

import os
import sys
import json
import uuid
import tempfile
import shutil
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from flask import Blueprint, request, jsonify, session, current_app, send_file
from werkzeug.utils import secure_filename
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import multimodal integration for document processing
try:
    from multimodal_integration import process_file
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    logger.warning("Multimodal integration not available for document processing")

# Create blueprint
document_rag_bp = Blueprint('document_rag', __name__)

# Configure document storage
DOCUMENT_STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'document_storage'))
DOCUMENT_INDEX_FILE = os.path.join(DOCUMENT_STORAGE_DIR, 'document_index.json')

# Create storage directory if it doesn't exist
os.makedirs(DOCUMENT_STORAGE_DIR, exist_ok=True)

# Initialize document index if it doesn't exist
if not os.path.exists(DOCUMENT_INDEX_FILE):
    with open(DOCUMENT_INDEX_FILE, 'w') as f:
        json.dump({
            "documents": [],
            "last_updated": datetime.datetime.now().isoformat()
        }, f, indent=2)


def initialize_vector_store():
    """
    Initialize the vector store for document embeddings.
    Returns the vector store instance.
    """
    try:
        # Check if ollama is configured for embeddings
        config = current_app.config.get('CLARIFIER_CONFIG', {})
        embedding_model = config.get('integrations', {}).get('ollama', {}).get('default_embedding_model', 'nomic-embed-text')
        
        # For demonstration, just return the model name - in production, would initialize an actual vector store
        return {
            "embedding_model": embedding_model,
            "initialized": True,
            "document_count": len(get_document_index().get("documents", []))
        }
    except Exception as e:
        logger.error(f"Error initializing vector store: {e}")
        return None


def get_document_index() -> Dict[str, Any]:
    """
    Load and return the document index from the index file.
    """
    try:
        with open(DOCUMENT_INDEX_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading document index: {e}")
        return {"documents": [], "last_updated": datetime.datetime.now().isoformat()}


def save_document_index(index_data: Dict[str, Any]) -> bool:
    """
    Save the document index to the index file.
    """
    try:
        with open(DOCUMENT_INDEX_FILE, 'w') as f:
            index_data["last_updated"] = datetime.datetime.now().isoformat()
            json.dump(index_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving document index: {e}")
        return False


def add_document_to_index(
    document_id: str,
    filename: str,
    file_path: str,
    file_type: str,
    file_size: int,
    text_content: str,
    embedding_file: Optional[str] = None
) -> bool:
    """
    Add a document to the document index.
    """
    try:
        # Load current index
        index_data = get_document_index()
        
        # Create document entry
        document = {
            "id": document_id,
            "filename": filename,
            "file_path": file_path,
            "file_type": file_type,
            "file_size": file_size,
            "upload_date": datetime.datetime.now().isoformat(),
            "text_content_length": len(text_content),
            "embedding_file": embedding_file,
            "processed": True
        }
        
        # Add to documents list
        index_data["documents"].append(document)
        
        # Save updated index
        return save_document_index(index_data)
    except Exception as e:
        logger.error(f"Error adding document to index: {e}")
        return False


def process_document_for_rag(file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Process a document for RAG by extracting text and generating embeddings.
    Returns (success, text_content, metadata)
    """
    if not MULTIMODAL_AVAILABLE:
        return False, "", {"error": "Multimodal integration not available"}
    
    try:
        # Use multimodal integration to extract text
        result = process_file(file_path, use_multimodal=False)
        
        if not result.get('success', False):
            return False, "", {"error": result.get('error', 'Unknown error')}
        
        # Get the extracted text
        text_content = result.get('text', '')
        
        if not text_content.strip():
            return False, "", {"error": "No text could be extracted from the document"}
        
        # For now, we'll just return the text content
        # In a production system, we would also generate embeddings here
        
        return True, text_content, {
            "method": result.get('method', 'ocr'),
            "processing_time": result.get('processing_time', 0)
        }
    except Exception as e:
        logger.error(f"Error processing document for RAG: {e}")
        return False, "", {"error": str(e)}


def retrieve_relevant_context(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve relevant document sections based on a query.
    Returns a list of relevant document chunks.
    """
    try:
        # This is a simplified implementation
        # In a real system, this would use vector similarity search
        
        # Get all documents
        index_data = get_document_index()
        documents = index_data.get("documents", [])
        
        # Simple keyword matching (just for demonstration)
        # In production, use actual vector similarity search
        results = []
        for doc in documents:
            doc_path = doc.get("file_path")
            if not doc_path or not os.path.exists(doc_path):
                continue
                
            try:
                # Read text content from file
                with open(f"{doc_path}.txt", 'r') as f:
                    content = f.read()
                
                # Simple keyword matching
                # This should be replaced with actual vector similarity search
                if any(term.lower() in content.lower() for term in query.split()):
                    # Simplified chunking - just grabbing first 1000 chars
                    # In production, use proper chunking and retrieval
                    results.append({
                        "document_id": doc.get("id"),
                        "filename": doc.get("filename"),
                        "content": content[:1000] + "..." if len(content) > 1000 else content,
                        "relevance": 0.85  # Dummy score for demonstration
                    })
                    
                    if len(results) >= limit:
                        break
            except Exception as inner_e:
                logger.error(f"Error processing document {doc.get('filename')}: {inner_e}")
        
        return results
    except Exception as e:
        logger.error(f"Error retrieving relevant context: {e}")
        return []


# Routes
@document_rag_bp.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """
    Upload and process a document for RAG.
    """
    try:
        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file was uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file was selected'
            }), 400
        
        # Get processing options
        generate_embeddings = request.form.get('generate_embeddings', '1') == '1'
        
        # Create a unique ID for the document
        document_id = str(uuid.uuid4())
        
        # Secure the filename and create save path
        filename = secure_filename(file.filename)
        file_type = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
        
        # Create document directory
        document_dir = os.path.join(DOCUMENT_STORAGE_DIR, document_id)
        os.makedirs(document_dir, exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join(document_dir, filename)
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Process the document
        success, text_content, metadata = process_document_for_rag(file_path)
        
        if not success:
            # Clean up and return error
            shutil.rmtree(document_dir)
            return jsonify({
                'success': False,
                'error': metadata.get('error', 'Failed to process document')
            }), 400
        
        # Save extracted text
        text_file_path = f"{file_path}.txt"
        with open(text_file_path, 'w') as f:
            f.write(text_content)
        
        # Add document to index
        embedding_file = f"{file_path}.embeddings" if generate_embeddings else None
        add_document_to_index(
            document_id=document_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            text_content=text_content,
            embedding_file=embedding_file
        )
        
        # Return success response
        return jsonify({
            'success': True,
            'document_id': document_id,
            'filename': filename,
            'file_size': file_size,
            'text_length': len(text_content),
            'metadata': metadata
        })
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@document_rag_bp.route('/api/documents', methods=['GET'])
def list_documents():
    """
    Get a list of all uploaded documents.
    """
    try:
        # Get document index
        index_data = get_document_index()
        documents = index_data.get("documents", [])
        
        # Format response
        formatted_documents = []
        for doc in documents:
            formatted_documents.append({
                "id": doc.get("id"),
                "filename": doc.get("filename"),
                "file_type": doc.get("file_type"),
                "file_size": doc.get("file_size"),
                "upload_date": doc.get("upload_date"),
                "text_content_length": doc.get("text_content_length"),
                "has_embeddings": doc.get("embedding_file") is not None
            })
        
        return jsonify({
            'success': True,
            'documents': formatted_documents,
            'count': len(formatted_documents),
            'last_updated': index_data.get("last_updated")
        })
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@document_rag_bp.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """
    Get information about a specific document.
    """
    try:
        # Get document index
        index_data = get_document_index()
        documents = index_data.get("documents", [])
        
        # Find the document
        document = next((doc for doc in documents if doc.get("id") == document_id), None)
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        # Check if text content file exists
        text_content = ""
        text_file_path = f"{document.get('file_path')}.txt"
        if os.path.exists(text_file_path):
            with open(text_file_path, 'r') as f:
                text_content = f.read()
        
        # Return document information
        return jsonify({
            'success': True,
            'document': {
                "id": document.get("id"),
                "filename": document.get("filename"),
                "file_type": document.get("file_type"),
                "file_size": document.get("file_size"),
                "upload_date": document.get("upload_date"),
                "text_content": text_content,
                "text_content_length": document.get("text_content_length"),
                "has_embeddings": document.get("embedding_file") is not None
            }
        })
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@document_rag_bp.route('/api/documents/<document_id>/download', methods=['GET'])
def download_document(document_id):
    """
    Download a document file.
    """
    try:
        # Get document index
        index_data = get_document_index()
        documents = index_data.get("documents", [])
        
        # Find the document
        document = next((doc for doc in documents if doc.get("id") == document_id), None)
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        file_path = document.get("file_path")
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'Document file not found'
            }), 404
        
        # Send the file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=document.get("filename")
        )
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@document_rag_bp.route('/api/documents/<document_id>/delete', methods=['POST'])
def delete_document(document_id):
    """
    Delete a document and its associated files.
    """
    try:
        # Get document index
        index_data = get_document_index()
        documents = index_data.get("documents", [])
        
        # Find the document
        document = next((doc for doc in documents if doc.get("id") == document_id), None)
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        # Get document directory
        document_dir = os.path.dirname(document.get("file_path"))
        
        # Remove document from index
        index_data["documents"] = [doc for doc in documents if doc.get("id") != document_id]
        save_document_index(index_data)
        
        # Delete document files
        if os.path.exists(document_dir):
            shutil.rmtree(document_dir)
        
        return jsonify({
            'success': True,
            'message': f"Document {document.get('filename')} deleted successfully"
        })
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@document_rag_bp.route('/api/rag/search', methods=['POST'])
def search_documents():
    """
    Search for relevant document sections based on a query.
    """
    try:
        # Get request data
        data = request.get_json()
        query = data.get('query', '')
        limit = int(data.get('limit', 5))
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400
        
        # Retrieve relevant context
        results = retrieve_relevant_context(query, limit)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'query': query
        })
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@document_rag_bp.route('/library', methods=['GET'])
def document_library():
    """
    Render the document library page.
    """
    # This route will be implemented in a separate file with the HTML template
    # For now, just return a placeholder message
    return "Document Library - to be implemented"
