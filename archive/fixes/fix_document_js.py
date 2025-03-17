#!/usr/bin/env python3
"""
Fix for document download JavaScript.

This script adds download functionality to the document manager JS file.
"""

import os
import sys
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def fix_document_js():
    """Fix document manager JavaScript."""
    js_file_path = os.path.join(
        os.path.dirname(__file__),
        'web_interface',
        'static',
        'js',
        'enhanced',
        'document_manager.js'
    )
    
    if not os.path.exists(js_file_path):
        logger.error(f"Document manager JS file not found at: {js_file_path}")
        return False
    
    # Read the current file
    with open(js_file_path, 'r') as f:
        js_content = f.read()
    
    # Check if download functionality is missing
    if "downloadDocument" not in js_content:
        logger.info("Adding download functionality to document manager JS")
        
        # Create download function
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
        
        # Find position to insert function - after constructor but before initialize
        parts = js_content.split('    initialize() {')
        if len(parts) < 2:
            logger.error("Couldn't find initialize method in the JS file")
            return False
        
        # Reassemble with the new function added
        js_content = parts[0] + download_function + "\n\n    initialize() {" + parts[1]
        
        # Add download button to renderDocumentList method
        if '<button class="btn btn-sm btn-link preview-doc-btn"' in js_content:
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
        if '            // Add event listeners' in js_content:
            js_content = js_content.replace(
                '            // Add event listeners',
                '            // Add event listeners\n' +
                '            // Download button\n' +
                '            const downloadBtn = listContainer.querySelector(`.download-doc-btn[data-id="${doc.id}"]`);\n' +
                '            if (downloadBtn) {\n' +
                '                downloadBtn.addEventListener(\'click\', (e) => {\n' +
                '                    e.stopPropagation();\n' +
                '                    this.downloadDocument(doc.id);\n' +
                '                });\n' +
                '            }'
            )
        
        # Write updated content back to file
        with open(js_file_path, 'w') as f:
            f.write(js_content)
        
        logger.info(f"Added download functionality to document manager JS: {js_file_path}")
    else:
        logger.info("Download functionality already exists in document manager JS")
    
    return True

if __name__ == "__main__":
    try:
        if fix_document_js():
            logger.info("Successfully fixed document manager JavaScript")
            sys.exit(0)
        else:
            logger.error("Failed to fix document manager JavaScript")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error fixing document manager JavaScript: {e}")
        sys.exit(1)
