"""
Routes for document RAG (Retrieval-Augmented Generation) integration.
This module provides routes for document management, embedding generation,
and retrieval for use in the chat and reflection interfaces.

This improved version consolidates document handling through the enhanced_integration.document_manager
to eliminate duplication and improve consistency.
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

# Import the enhanced document manager
from enhanced_integration.document_manager import get_document_manager

# Import multimodal integration for document processing if available
try:
    from multimodal_integration import process_file
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    logger.warning("Multimodal integration not available for document processing")

# Create blueprint
document_rag_bp = Blueprint('document_rag', __name__)

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
        
        # Get tags if provided
        tags = []
        if 'tags' in request.form:
            try:
                tags = json.loads(request.form['tags'])
            except Exception as e:
                logger.error(f"Error parsing tags: {e}")
        
        # Create a temporary file
        filename = secure_filename(file.filename)
        temp_dir = os.path.join(current_app.root_path, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        # Get the document manager
        document_manager = get_document_manager()
        
        # Process the document
        doc_metadata = document_manager.process_document(
            file_path=temp_path,
            source="upload",
            generate_embeddings=generate_embeddings,
            metadata={"tags": tags}
        )
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if doc_metadata:
            return jsonify({
                'success': True,
                'document_id': doc_metadata.get("id"),
                'filename': doc_metadata.get("name"),
                'file_size': doc_metadata.get("size", 0),
                'text_length': doc_metadata.get("text_length", 0),
                'metadata': {
                    'type': doc_metadata.get("type", "unknown"),
                    'page_count': doc_metadata.get("page_count", 1),
                    'has_embeddings': doc_metadata.get("has_embeddings", False),
                    'date_added': doc_metadata.get("date_added", "")
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to process document'
            }), 500
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
        # Get document manager
        document_manager = get_document_manager()
        
        # Get all documents
        documents = document_manager.get_all_documents()
        
        # Format response
        formatted_documents = []
        for doc in documents:
            formatted_documents.append({
                "id": doc.get("id"),
                "filename": doc.get("name"),
                "file_type": doc.get("type"),
                "file_size": doc.get("size", 0),
                "upload_date": doc.get("date_added", ""),
                "text_content_length": doc.get("text_length", 0),
                "has_embeddings": doc.get("has_embeddings", False),
                "tags": doc.get("tags", [])
            })
        
        # Get document stats
        stats = document_manager.get_document_stats()
        
        return jsonify({
            'success': True,
            'documents': formatted_documents,
            'count': len(formatted_documents),
            'stats': stats,
            'last_updated': stats.get("last_updated", "")
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
        # Get document manager
        document_manager = get_document_manager()
        
        # Get document metadata
        doc_metadata = document_manager.get_document_by_id(document_id)
        
        if not doc_metadata:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        # Get document content
        text_content = document_manager.get_document_content(document_id)
        
        # Return document information
        return jsonify({
            'success': True,
            'document': {
                "id": doc_metadata.get("id"),
                "filename": doc_metadata.get("name"),
                "file_type": doc_metadata.get("type"),
                "file_size": doc_metadata.get("size", 0),
                "upload_date": doc_metadata.get("date_added", ""),
                "text_content": text_content,
                "text_content_length": len(text_content) if text_content else 0,
                "has_embeddings": doc_metadata.get("has_embeddings", False),
                "tags": doc_metadata.get("tags", [])
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
        # Get document manager
        document_manager = get_document_manager()
        
        # Get document metadata
        doc_metadata = document_manager.get_document_by_id(document_id)
        
        if not doc_metadata:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        # Check if raw file exists
        raw_path = doc_metadata.get("raw_path")
        if not raw_path or not os.path.exists(raw_path):
            return jsonify({
                'success': False,
                'error': 'Document file not found'
            }), 404
        
        # Get filename for download
        filename = doc_metadata.get("name", "document")
        
        # Use simple approach that works across Flask versions
        directory = os.path.dirname(raw_path)
        basename = os.path.basename(raw_path)
        
        try:
            # Try send_from_directory which is more reliable
            from flask import send_from_directory
            return send_from_directory(
                directory=directory,
                path=basename,
                as_attachment=True,
                download_name=filename
            )
        except TypeError:
            # Older Flask version
            try:
                from flask import send_from_directory
                return send_from_directory(
                    directory=directory,
                    filename=basename,
                    as_attachment=True,
                    attachment_filename=filename
                )
            except Exception as inner_e:
                logger.error(f"Error with send_from_directory: {inner_e}")
                
                # Last resort fallback
                from flask import Response
                with open(raw_path, 'rb') as f:
                    data = f.read()
                
                response = Response(data, mimetype='application/octet-stream')
                response.headers.set('Content-Disposition', f'attachment; filename={filename}')
                return response
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
        # This is a placeholder for actual implementation
        # In the enhanced implementation, we would need to add a delete method to the DocumentManager
        
        # Get document manager
        document_manager = get_document_manager()
        
        # Get document metadata
        doc_metadata = document_manager.get_document_by_id(document_id)
        
        if not doc_metadata:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        # TODO: Add delete_document method to DocumentManager
        # For now, just return a not implemented error
        return jsonify({
            'success': False,
            'error': 'Delete functionality not yet implemented in DocumentManager'
        }), 501
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@document_rag_bp.route('/api/documents/<document_id>/tag', methods=['POST'])
def tag_document(document_id):
    """
    Add tags to a document.
    """
    try:
        # Get request data
        data = request.get_json()
        tags = data.get('tags', [])
        
        if not tags:
            return jsonify({
                'success': False,
                'error': 'No tags provided'
            }), 400
        
        # Get document manager
        document_manager = get_document_manager()
        
        # Add tags
        success = document_manager.tag_document(document_id, tags)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Tags added successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add tags'
            }), 500
    except Exception as e:
        logger.error(f"Error adding tags to document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@document_rag_bp.route('/api/rag/search', methods=['POST'])
def search_documents():
    """
    Search for relevant document sections based on a query.
    Uses the document manager to provide vector-based similarity search.
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
        
        # Get document manager
        document_manager = get_document_manager()
        
        # Use the enhanced document manager to get relevant documents for RAG
        # This uses the search_documents method which provides vector-based similarity when available
        results = document_manager.get_documents_for_rag(query, limit=limit)
        
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
