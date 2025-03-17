#!/usr/bin/env python3
"""
Fix for document download issues in the enhanced UI.

This script updates the download functionality in enhanced_routes.py to work
with different Flask versions and ensures proper file handling.
"""

import os
import sys
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def fix_document_download():
    """Fix document download functionality."""
    # Path to the enhanced_routes.py file
    routes_path = os.path.join(
        os.path.dirname(__file__),
        'web_interface',
        'enhanced_routes.py'
    )
    
    if not os.path.exists(routes_path):
        logger.error(f"Enhanced routes file not found at: {routes_path}")
        return False
    
    # Read the current file
    with open(routes_path, 'r') as f:
        content = f.read()
    
    # Replace the problematic download_document function
    old_function = """@enhanced_bp.route('/api/documents/<doc_id>/download', methods=['GET'])
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
        logger.error(f"Error downloading document: {e}\n{error_traceback}")
        return jsonify({"success": False, "error": str(e)}), 500"""
    
    new_function = """@enhanced_bp.route('/api/documents/<doc_id>/download', methods=['GET'])
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
        
        # Get file name from metadata
        file_name = doc_metadata.get("name", "document")
        
        # Use simple approach that works across Flask versions
        from flask import send_from_directory, Response
        
        directory = os.path.dirname(raw_path)
        filename = os.path.basename(raw_path)
        
        try:
            # Try send_from_directory which is more reliable
            return send_from_directory(
                directory=directory,
                path=filename,
                as_attachment=True,
                download_name=file_name
            )
        except TypeError:
            # Older Flask version
            try:
                return send_from_directory(
                    directory=directory,
                    filename=filename,
                    as_attachment=True,
                    attachment_filename=file_name
                )
            except Exception as e2:
                logger.error(f"Error with send_from_directory: {e2}")
                
                # Last resort fallback
                with open(raw_path, 'rb') as f:
                    data = f.read()
                
                response = Response(data, mimetype='application/octet-stream')
                response.headers.set('Content-Disposition', f'attachment; filename={file_name}')
                return response
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error downloading document: {e}\n{error_traceback}")
        return jsonify({"success": False, "error": str(e)}), 500"""
    
    # Update the file content
    updated_content = content.replace(old_function, new_function)
    
    # Write the updated content back to the file
    with open(routes_path, 'w') as f:
        f.write(updated_content)
    
    logger.info(f"Updated download_document function in: {routes_path}")
    
    # Also fix the JavaScript for document downloads
    js_file_path = os.path.join(
        os.path.dirname(__file__),
        'web_interface',
        'static',
        'js',
        'enhanced',
        'document_manager.js'
    )
    
    if os.path.exists(js_file_path):
        with open(js_file_path, 'r') as f:
            js_content = f.read()
        
        # Check if download functionality is missing
        if "downloadDocument" not in js_content:
            # Add download function
            download_function = """
    downloadDocument(docId) {
        const doc = this.documents.find(d => d.id === docId);
        
        if (!doc) return;
        
        // Create a hidden anchor element for download
        const downloadLink = document.createElement('a');
        downloadLink.href = `/api/documents/${docId}/download`;
        downloadLink.target = '_blank';
        downloadLink.download = doc.name;
        
        // Add to document and click
        document.body.appendChild(downloadLink);
        downloadLink.click();
        
        // Clean up
        document.body.removeChild(downloadLink);
    }"""
            
            # Find constructor method and insert after it
            constructor_end = js_content.indexOf("    initialize() {")
            if constructor_end !== -1:
                js_content = js_content.slice(0, constructor_end) + download_function + "\n" + js_content.slice(constructor_end);
                
                # Also add download button to document card
                js_content = js_content.replace(
                    '<button class="btn btn-sm btn-link preview-doc-btn" data-id="${doc.id}" title="Preview">',
                    '<button class="btn btn-sm btn-link preview-doc-btn" data-id="${doc.id}" title="Preview">'
                )
                
                js_content = js_content.replace(
                    '<button class="btn btn-sm btn-link ${isSelected ? \'remove-rag-btn\' : \'add-rag-btn\'}" ',
                    '<button class="btn btn-sm btn-link download-doc-btn" data-id="${doc.id}" title="Download">\n' +
                    '                            <i class="bi bi-download"></i>\n' +
                    '                        </button>\n' +
                    '                        <button class="btn btn-sm btn-link ${isSelected ? \'remove-rag-btn\' : \'add-rag-btn\'}" '
                )
                
                # Add event listener for download button
                js_content = js_content.replace(
                    "            // Add event listeners",
                    "            // Add event listeners\n" +
                    "            // Download button\n" +
                    "            const downloadBtn = listContainer.querySelector(`.download-doc-btn[data-id=\"${doc.id}\"]`);\n" +
                    "            if (downloadBtn) {\n" +
                    "                downloadBtn.addEventListener('click', (e) => {\n" +
                    "                    e.stopPropagation();\n" +
                    "                    this.downloadDocument(doc.id);\n" +
                    "                });\n" +
                    "            }"
                )
                
                with open(js_file_path, 'w') as f:
                    f.write(js_content)
                
                logger.info(f"Added download functionality to document manager JS: {js_file_path}")
        
    return True

if __name__ == "__main__":
    try:
        if fix_document_download():
            logger.info("Successfully fixed document download functionality")
            sys.exit(0)
        else:
            logger.error("Failed to fix document download functionality")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error fixing document download: {e}")
        sys.exit(1)
