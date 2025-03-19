"""
Enhanced routes for the AI-Socratic-Clarifier.

This module provides routes for the enhanced UI with SRE and document integration.
"""

import os
import json
import traceback
from typing import List, Dict, Any, Optional
from flask import Blueprint, request, jsonify, render_template, current_app, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from loguru import logger

# Create blueprint
enhanced_bp = Blueprint('enhanced', __name__)

# Import enhanced components
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from enhanced_integration.document_manager import get_document_manager
from enhanced_integration.integration import get_enhanced_enhancer

# Enhanced chat route
@enhanced_bp.route('/enhanced', methods=['GET'])
def enhanced_chat():
    """Render the enhanced chat interface."""
    # Get available modes
    from socratic_clarifier import SocraticClarifier
    
    try:
        # Try to get available modes from the app's clarifier
        if hasattr(current_app, 'clarifier') and current_app.clarifier:
            modes = current_app.clarifier.available_modes()
        else:
            # Create a temporary clarifier to get modes
            clarifier = SocraticClarifier()
            modes = clarifier.available_modes()
    except Exception as e:
        logger.error(f"Error getting available modes: {e}")
        # Fallback modes
        modes = ['standard', 'deep', 'reflective']
    
    return render_template('enhanced_chat.html', modes=modes)

# Document library API routes
@enhanced_bp.route('/api/documents', methods=['GET'])
def list_documents():
    """Get a list of all documents in the library."""
    try:
        # Get the document manager
        manager = get_document_manager()
        
        # Get all documents
        documents = manager.get_all_documents()
        
        # Format for response
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                "id": doc.get("id"),
                "name": doc.get("name"),
                "type": doc.get("type", "unknown"),
                "size": doc.get("size", 0),
                "date_added": doc.get("date_added", ""),
                "tags": doc.get("tags", []),
                "has_embeddings": doc.get("has_embeddings", False)
            })
        
        return jsonify({
            "success": True,
            "documents": formatted_docs,
            "count": len(formatted_docs)
        })
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error listing documents: {e}\n{error_traceback}")
        return jsonify({"success": False, "error": str(e)}), 500

@enhanced_bp.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Upload a document to the library."""
    try:
        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No selected file"}), 400
        
        # Get options
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
        manager = get_document_manager()
        
        # Process the document
        doc_metadata = manager.process_document(
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
                "success": True,
                "document": {
                    "id": doc_metadata.get("id"),
                    "name": doc_metadata.get("name"),
                    "type": doc_metadata.get("type", "unknown"),
                    "size": doc_metadata.get("size", 0),
                    "date_added": doc_metadata.get("date_added", "")
                }
            })
        else:
            return jsonify({"success": False, "error": "Failed to process document"}), 500
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error uploading document: {e}\n{error_traceback}")
        return jsonify({"success": False, "error": str(e)}), 500

@enhanced_bp.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get document details and content."""
    try:
        # Get the document manager
        manager = get_document_manager()
        
        # Get document metadata
        doc_metadata = manager.get_document_by_id(doc_id)
        
        if not doc_metadata:
            return jsonify({"success": False, "error": "Document not found"}), 404
        
        # Get document content
        content = manager.get_document_content(doc_id)
        
        return jsonify({
            "success": True,
            "document": {
                "id": doc_metadata.get("id"),
                "name": doc_metadata.get("name"),
                "type": doc_metadata.get("type", "unknown"),
                "size": doc_metadata.get("size", 0),
                "date_added": doc_metadata.get("date_added", ""),
                "tags": doc_metadata.get("tags", []),
                "has_embeddings": doc_metadata.get("has_embeddings", False),
                "text_content": content
            }
        })
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error getting document: {e}\n{error_traceback}")
        return jsonify({"success": False, "error": str(e)}), 500

@enhanced_bp.route('/api/documents/<doc_id>/download', methods=['GET'])
def download_document(doc_id):
    """Download the original document file."""
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
        
        # Send file
        return send_file(
            raw_path,
            as_attachment=True,
            download_name=doc_metadata.get("name", "document")
        )
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error downloading document: {e}\n{error_traceback}")
        return jsonify({"success": False, "error": str(e)}), 500

@enhanced_bp.route('/api/documents/<doc_id>/tag', methods=['POST'])
def tag_document(doc_id):
    """Add tags to a document."""
    try:
        # Get request data
        data = request.get_json()
        tags = data.get('tags', [])
        
        if not tags:
            return jsonify({"success": False, "error": "No tags provided"}), 400
        
        # Get the document manager
        manager = get_document_manager()
        
        # Add tags
        success = manager.tag_document(doc_id, tags)
        
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Failed to add tags"}), 500
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error tagging document: {e}\n{error_traceback}")
        return jsonify({"success": False, "error": str(e)}), 500

# Enhanced analysis routes
@enhanced_bp.route('/api/chat', methods=['POST'])
def chat_message():
    """Process a chat message with enhanced capabilities."""
    try:
        # Get the data from the request
        data = request.get_json()
        message = data.get('message', '')
        mode = data.get('mode', 'standard')
        use_sot = data.get('use_sot', True)
        use_sre = data.get('use_sre', True)
        use_rag = data.get('use_rag', False)
        document_context = data.get('document_context', [])
        
        logger.info(f"Processing chat message with enhanced capabilities: '{message}'")
        
        # Get document content for RAG
        if use_rag and document_context:
            manager = get_document_manager()
            
            # Add content to document context
            for i, doc in enumerate(document_context):
                if "document_id" in doc and "content" not in doc:
                    content = manager.get_document_content(doc["document_id"])
                    if content:
                        document_context[i]["content"] = content
                        document_context[i]["relevance"] = 0.95  # High relevance for manually selected docs
        
        # Use direct integration to analyze the text
        if use_sre:
            # Use enhanced integration
            enhancer = get_enhanced_enhancer()
            
            # Get reasoning context for visualization
            reasoning_context = enhancer.get_reasoning_context(message, [], mode)
            
            # Use the enhancer for question generation
            from web_interface.direct_integration import direct_analyze_text
            try:
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
                    raise
            
            # Add reasoning context to result
            result["reasoning_paths"] = reasoning_context.get("reasoning_paths", [])
            result["meta_meta_stage"] = reasoning_context.get("meta_meta_stage")
            result["advancement"] = reasoning_context.get("advancement")
        else:
            # Use standard integration
            from web_interface.direct_integration import direct_analyze_text
            try:
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
                    raise
        
        # Generate a response based on the analysis
        if result['issues'] and result['questions']:
            # Craft a response that includes one of the Socratic questions
            reply = f"I've analyzed your statement and have some thoughts to share. {result['questions'][0]}"
            
            # If there are more questions, include a followup
            if len(result['questions']) > 1:
                reply += f" I also wonder: {result['questions'][1]}"
                
            # If we used document context, mention that
            if document_context:
                reply += f"\n\n(Analysis included context from {len(document_context)} document(s))"
        else:
            # Default response if no issues detected
            reply = "I've considered your statement. It seems clear and well-formed. Do you have any other thoughts you'd like to explore?"
        
        # Prepare the response data
        response = {
            'reply': reply,
            'text': message,
            'issues': result['issues'],
            'questions': result['questions'],
            'reasoning': result['reasoning'],
            'sot_paradigm': result['sot_paradigm'],
            'confidence': result['confidence'],
            'sot_enabled': result['sot_enabled'],
            'model': result['model'],
            'provider': result['provider'],
            'document_context': document_context,
            'reasoning_paths': result.get('reasoning_paths', []),
            'meta_meta_stage': result.get('meta_meta_stage'),
            'advancement': result.get('advancement')
        }
        
        return jsonify(response)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error processing chat message: {e}\n{error_traceback}")
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

@enhanced_bp.route('/api/sre/status', methods=['GET'])
def get_sre_status():
    """Get the status of the Symbiotic Reflective Ecosystem."""
    try:
        enhancer = get_enhanced_enhancer()
        report = enhancer.get_performance_report()
        
        return jsonify({
            "success": True,
            "report": report
        })
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error getting SRE status: {e}\n{error_traceback}")
        return jsonify({"success": False, "error": str(e)}), 500
