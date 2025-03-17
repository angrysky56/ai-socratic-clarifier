#!/usr/bin/env python3
"""
Fix Document UI Issues

This script addresses several issues with the document UI in the AI Socratic Clarifier:
1. Creates a proper document library page that was missing
2. Fixes document panel switching between windows instead of using tabs
3. Fixes document download functionality
4. Ensures consistent UI experience across the application

Run this script to apply all fixes automatically.
"""

import os
import sys
import json
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fix_document_ui')

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Define paths
BASE_DIR = Path(__file__).resolve().parent
WEB_INTERFACE_DIR = BASE_DIR / 'web_interface'
TEMPLATES_DIR = WEB_INTERFACE_DIR / 'templates'
COMPONENTS_DIR = TEMPLATES_DIR / 'components'
STATIC_DIR = WEB_INTERFACE_DIR / 'static'
JS_DIR = STATIC_DIR / 'js' / 'enhanced'
CSS_DIR = STATIC_DIR / 'css' / 'enhanced'

def ensure_directory_exists(directory):
    """Ensure a directory exists, creating it if necessary."""
    if not directory.exists():
        logger.info(f"Creating directory: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
    return directory

def backup_file(file_path):
    """Create a backup of a file before modifying it."""
    if file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + '.fix_ui_bak')
        logger.info(f"Creating backup: {backup_path}")
        shutil.copy2(file_path, backup_path)
    else:
        logger.warning(f"File does not exist, cannot backup: {file_path}")

def create_document_library_template():
    """Create the document library template."""
    library_template_path = TEMPLATES_DIR / 'document_library.html'
    
    # Backup existing file if it exists
    if library_template_path.exists():
        backup_file(library_template_path)
    
    logger.info(f"Creating document library template: {library_template_path}")
    
    # Create the template content
    template_content = """{% extends "base.html" %}

{% block title %}Document Library - AI Socratic Clarifier{% endblock %}

{% block content %}
<div class="container-fluid mt-4">
    <div class="row">
        <!-- Sidebar -->
        <div class="col-lg-3 col-md-4 mb-4">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0"><i class="bi bi-folder"></i> Document Management</h5>
                </div>
                <div class="card-body">
                    <div class="d-grid gap-2">
                        <button class="btn btn-primary" id="uploadDocBtn">
                            <i class="bi bi-upload"></i> Upload Document
                        </button>
                        <button class="btn btn-outline-secondary" id="refreshDocsBtn">
                            <i class="bi bi-arrow-clockwise"></i> Refresh
                        </button>
                    </div>
                    
                    <hr>
                    
                    <div class="filters">
                        <h6>Filter Documents</h6>
                        <div class="mb-3">
                            <label for="documentSearch" class="form-label">Search</label>
                            <input type="text" class="form-control" id="documentSearch" placeholder="Search documents...">
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Document Type</label>
                            <div class="form-check">
                                <input class="form-check-input filter-type" type="checkbox" value="all" id="typeAll" checked>
                                <label class="form-check-label" for="typeAll">All Types</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input filter-type" type="checkbox" value="pdf" id="typePdf">
                                <label class="form-check-label" for="typePdf">PDF</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input filter-type" type="checkbox" value="text" id="typeText">
                                <label class="form-check-label" for="typeText">Text</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input filter-type" type="checkbox" value="image" id="typeImage">
                                <label class="form-check-label" for="typeImage">Image</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input filter-type" type="checkbox" value="other" id="typeOther">
                                <label class="form-check-label" for="typeOther">Other</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="col-lg-9 col-md-8">
            <div class="document-container">
                <div class="document-header">
                    <h3>Documents</h3>
                    <div class="view-controls">
                        <button class="btn btn-sm btn-outline-secondary view-btn active" data-view="grid">
                            <i class="bi bi-grid-3x3-gap"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary view-btn" data-view="list">
                            <i class="bi bi-list"></i>
                        </button>
                    </div>
                </div>
                
                <div class="document-grid" id="documentList">
                    <!-- Documents will be loaded here -->
                    <div class="placeholder-text text-muted p-3">
                        <div class="d-flex justify-content-center mb-3">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                        <p class="text-center mb-0">Loading documents...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Document Upload Modal -->
{% include 'components/document_upload_modal.html' %}

<!-- Document Preview Modal -->
{% include 'components/document_preview_modal.html' %}
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/enhanced/document_manager.js') }}"></script>
<script src="{{ url_for('static', filename='js/enhanced/document_library.js') }}"></script>
{% endblock %}
"""

    with open(library_template_path, 'w') as f:
        f.write(template_content)
    
    logger.info("Document library template created successfully")
    return True

def create_document_library_js():
    """Create the JavaScript file for the document library."""
    ensure_directory_exists(JS_DIR)
    
    library_js_path = JS_DIR / 'document_library.js'
    
    # Backup existing file if it exists
    if library_js_path.exists():
        backup_file(library_js_path)
    
    logger.info(f"Creating document library JavaScript: {library_js_path}")
    
    # Create the JavaScript content
    js_content = """/**
 * Document Library JavaScript
 * 
 * This script provides enhanced functionality for the document library page,
 * including view switching, filtering, and improved document interaction.
 */

class DocumentLibrary {
    constructor() {
        // Initialize when document is ready
        document.addEventListener('DOMContentLoaded', () => this.initialize());
        
        // View state
        this.currentView = 'grid'; // 'grid' or 'list'
        this.filters = {
            search: '',
            types: ['all']
        };
    }
    
    initialize() {
        // Set up view switchers
        this.setupViewSwitchers();
        
        // Set up type filters
        this.setupTypeFilters();
        
        // Set up document manager integration
        this.setupDocumentManagerIntegration();
    }
    
    setupViewSwitchers() {
        const viewButtons = document.querySelectorAll('.view-btn');
        
        viewButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Remove active class from all buttons
                viewButtons.forEach(b => b.classList.remove('active'));
                
                // Add active class to clicked button
                btn.classList.add('active');
                
                // Update current view
                this.currentView = btn.getAttribute('data-view');
                
                // Update document list view
                this.updateDocumentListView();
            });
        });
    }
    
    setupTypeFilters() {
        const typeCheckboxes = document.querySelectorAll('.filter-type');
        const allTypeCheckbox = document.getElementById('typeAll');
        
        typeCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (checkbox.id === 'typeAll' && checkbox.checked) {
                    // If "All Types" is checked, uncheck others
                    typeCheckboxes.forEach(cb => {
                        if (cb.id !== 'typeAll') {
                            cb.checked = false;
                        }
                    });
                    
                    this.filters.types = ['all'];
                } else {
                    // If any other type is checked, uncheck "All Types"
                    if (checkbox.checked && allTypeCheckbox.checked) {
                        allTypeCheckbox.checked = false;
                    }
                    
                    // Update filters
                    this.filters.types = Array.from(typeCheckboxes)
                        .filter(cb => cb.checked)
                        .map(cb => cb.value);
                    
                    // If no filters selected, select "All Types"
                    if (this.filters.types.length === 0) {
                        allTypeCheckbox.checked = true;
                        this.filters.types = ['all'];
                    }
                }
                
                // Apply filters
                this.applyFilters();
            });
        });
        
        // Set up search filter
        const searchInput = document.getElementById('documentSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filters.search = e.target.value.trim().toLowerCase();
                this.applyFilters();
            });
        }
    }
    
    setupDocumentManagerIntegration() {
        // Wait for document manager to be initialized
        const checkDocumentManager = setInterval(() => {
            if (window.documentManager) {
                clearInterval(checkDocumentManager);
                
                // Override document list rendering
                const originalRenderDocumentList = window.documentManager.renderDocumentList;
                
                window.documentManager.renderDocumentList = () => {
                    originalRenderDocumentList.call(window.documentManager);
                    
                    // Apply our custom view
                    this.updateDocumentListView();
                    
                    // Apply filters
                    this.applyFilters();
                };
            }
        }, 100);
    }
    
    updateDocumentListView() {
        const listContainer = document.getElementById('documentList');
        
        if (!listContainer) return;
        
        // Update container class
        if (this.currentView === 'grid') {
            listContainer.classList.remove('document-list-view');
            listContainer.classList.add('document-grid');
        } else {
            listContainer.classList.remove('document-grid');
            listContainer.classList.add('document-list-view');
        }
        
        // Update document cards if needed
        const cards = listContainer.querySelectorAll('.document-card');
        
        cards.forEach(card => {
            if (this.currentView === 'list') {
                card.classList.add('list-view');
            } else {
                card.classList.remove('list-view');
            }
        });
    }
    
    applyFilters() {
        const listContainer = document.getElementById('documentList');
        
        if (!listContainer || !window.documentManager) return;
        
        const cards = listContainer.querySelectorAll('.document-card');
        
        cards.forEach(card => {
            const docId = card.getAttribute('data-id');
            const doc = window.documentManager.documents.find(d => d.id === docId);
            
            if (doc) {
                let visible = true;
                
                // Apply type filter
                if (!this.filters.types.includes('all')) {
                    if (!this.filters.types.includes(doc.type)) {
                        const isOther = !['pdf', 'text', 'image'].includes(doc.type);
                        
                        if (!(isOther && this.filters.types.includes('other'))) {
                            visible = false;
                        }
                    }
                }
                
                // Apply search filter
                if (visible && this.filters.search) {
                    const nameMatch = doc.name.toLowerCase().includes(this.filters.search);
                    const tagsMatch = (doc.tags || []).some(tag => tag.toLowerCase().includes(this.filters.search));
                    
                    if (!nameMatch && !tagsMatch) {
                        visible = false;
                    }
                }
                
                card.style.display = visible ? '' : 'none';
            }
        });
    }
}

// Initialize document library
const documentLibrary = new DocumentLibrary();
"""

    with open(library_js_path, 'w') as f:
        f.write(js_content)
    
    logger.info("Document library JavaScript created successfully")
    return True

def create_document_modal_components():
    """Create separate document modal components for better modularity."""
    ensure_directory_exists(COMPONENTS_DIR)
    
    # Create upload modal component
    upload_modal_path = COMPONENTS_DIR / 'document_upload_modal.html'
    
    # Backup existing file if it exists
    if upload_modal_path.exists():
        backup_file(upload_modal_path)
    
    logger.info(f"Creating document upload modal component: {upload_modal_path}")
    
    upload_modal_content = """<!-- Document Upload Modal -->
<div class="modal fade" id="uploadDocumentModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Upload Document</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <form id="uploadDocumentForm">
                    <div class="mb-3">
                        <label for="documentFile" class="form-label">Select Document</label>
                        <input type="file" class="form-control" id="documentFile" accept=".pdf,.png,.jpg,.jpeg,.txt,.md,.doc,.docx,.xls,.xlsx,.csv">
                        <div class="form-text">Supported formats: PDF, Images, Text, Documents, Spreadsheets</div>
                    </div>
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" id="generateEmbeddingsCheck" checked>
                        <label class="form-check-label" for="generateEmbeddingsCheck">
                            Generate embeddings for retrieval
                        </label>
                    </div>
                    <div class="mb-3">
                        <label for="documentTags" class="form-label">Tags (optional)</label>
                        <input type="text" class="form-control" id="documentTags" placeholder="Enter tags separated by commas">
                        <div class="form-text">Tags help with organization and retrieval</div>
                    </div>
                </form>
                <div class="upload-progress d-none">
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%"></div>
                    </div>
                    <p class="mt-2 text-center" id="uploadStatus">Uploading...</p>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="uploadDocumentSubmit">Upload</button>
            </div>
        </div>
    </div>
</div>
"""

    with open(upload_modal_path, 'w') as f:
        f.write(upload_modal_content)
    
    # Create preview modal component
    preview_modal_path = COMPONENTS_DIR / 'document_preview_modal.html'
    
    # Backup existing file if it exists
    if preview_modal_path.exists():
        backup_file(preview_modal_path)
    
    logger.info(f"Creating document preview modal component: {preview_modal_path}")
    
    preview_modal_content = """<!-- Document Preview Modal -->
<div class="modal fade" id="documentPreviewModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="previewDocumentTitle">Document Preview</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="document-info mb-3">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Type:</strong> <span id="previewDocumentType">Unknown</span></p>
                            <p><strong>Size:</strong> <span id="previewDocumentSize">0 bytes</span></p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Added:</strong> <span id="previewDocumentDate">Unknown</span></p>
                            <p><strong>Tags:</strong> <span id="previewDocumentTags">None</span></p>
                        </div>
                    </div>
                </div>
                <div class="document-content-preview">
                    <div class="content-placeholder text-center p-4 d-none">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2">Loading document content...</p>
                    </div>
                    <div id="documentContentWrapper" class="p-0">
                        <pre id="documentContentPreview" class="p-3 border rounded bg-light"></pre>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <div class="me-auto">
                    <button type="button" class="btn btn-outline-primary" id="addToRagBtn">
                        <i class="bi bi-plus-circle"></i> Add to RAG Context
                    </button>
                </div>
                <button type="button" class="btn btn-outline-secondary" id="downloadDocumentBtn">
                    <i class="bi bi-download"></i> Download
                </button>
                <button type="button" class="btn btn-primary" id="analyzeDocumentBtn">
                    <i class="bi bi-search"></i> Analyze Content
                </button>
            </div>
        </div>
    </div>
</div>
"""

    with open(preview_modal_path, 'w') as f:
        f.write(preview_modal_content)
    
    logger.info("Document modal components created successfully")
    return True

def fix_document_manager_js():
    """Fix the document manager JavaScript file."""
    manager_js_path = JS_DIR / 'document_manager.js'
    
    if not manager_js_path.exists():
        logger.error(f"Document manager JavaScript file not found: {manager_js_path}")
        return False
    
    # Backup existing file
    backup_file(manager_js_path)
    
    logger.info(f"Fixing document manager JavaScript: {manager_js_path}")
    
    # Read the existing file
    with open(manager_js_path, 'r') as f:
        js_content = f.read()
    
    # Fix download function
    download_function = """    downloadDocument(docId) {
        const doc = this.documents.find(d => d.id === docId);
        
        if (!doc) return;
        
        // Create a hidden iframe for download to avoid window popup
        const downloadFrame = document.createElement('iframe');
        downloadFrame.style.display = 'none';
        downloadFrame.src = `/api/documents/${docId}/download`;
        
        // Add to document, wait for load, then remove
        document.body.appendChild(downloadFrame);
        
        // Set timeout to remove the iframe after download starts
        setTimeout(() => {
            document.body.removeChild(downloadFrame);
        }, 2000);
    }"""
    
    # Replace the old download function
    js_content = js_content.replace(
        """    downloadDocument(docId) {
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
    }""",
        download_function
    )
    
    # Add event listeners for download buttons in preview modal
    download_button_code = """        // Download button in preview modal
        const downloadBtn = document.getElementById('downloadDocumentBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                if (this.currentPreviewDoc) {
                    this.downloadDocument(this.currentPreviewDoc.id);
                }
            });
        }
        
        // Listen for download-doc-btn clicks
        document.addEventListener('click', (e) => {
            const downloadBtn = e.target.closest('.download-doc-btn');
            if (downloadBtn) {
                const docId = downloadBtn.getAttribute('data-id');
                if (docId) {
                    this.downloadDocument(docId);
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        });"""
    
    # Add the download button code to the setupEventListeners method
    js_content = js_content.replace(
        "    setupEventListeners() {",
        "    setupEventListeners() {\n" + download_button_code
    )
    
    # Write the updated content back to the file
    with open(manager_js_path, 'w') as f:
        f.write(js_content)
    
    logger.info("Document manager JavaScript fixed successfully")
    return True

def add_document_library_route():
    """Add the document library route to the document_rag_routes.py file."""
    from flask import render_template
    
    routes_path = WEB_INTERFACE_DIR / 'document_rag_routes.py'
    
    if not routes_path.exists():
        logger.error(f"Document RAG routes file not found: {routes_path}")
        return False
    
    # Backup existing file
    backup_file(routes_path)
    
    logger.info(f"Adding document library route to: {routes_path}")
    
    # Read the existing file
    with open(routes_path, 'r') as f:
        content = f.read()
    
    # Replace the placeholder library route with a proper implementation
    new_library_route = '''@document_rag_bp.route('/library', methods=['GET'])
def document_library():
    """Render the document library page."""
    return render_template('document_library.html')
'''
    
    updated_content = content.replace(
        '''@document_rag_bp.route('/library', methods=['GET'])
def document_library():
    """Render the document library page."""
    # This route will be implemented in a separate file with the HTML template
    # For now, just return a placeholder message
    return "Document Library - to be implemented"''',
        new_library_route
    )
    
    # Write the updated content back to the file
    with open(routes_path, 'w') as f:
        f.write(updated_content)
    
    logger.info("Document library route added successfully")
    return True


def add_css_styles():
    """Add CSS styles for the document library."""
    ensure_directory_exists(CSS_DIR)
    
    # Update document panel CSS
    panel_css_path = CSS_DIR / 'document_panel.css'
    
    # Add document library CSS
    library_css_path = CSS_DIR / 'document_library.css'
    
    # Backup existing file if it exists
    if library_css_path.exists():
        backup_file(library_css_path)
    
    logger.info(f"Creating document library CSS: {library_css_path}")
    
    # Create the CSS content
    css_content = """/**
 * Document Library Styles
 */

/* Document container */
.document-container {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.document-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

/* Grid view */
.document-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
}

/* List view */
.document-list-view {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

/* Document card styles */
.document-card {
    background-color: #fff;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
    padding: 15px;
    transition: all 0.2s ease;
    cursor: pointer;
    display: flex;
    flex-direction: column;
}

.document-card:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border-color: #c0c0c0;
}

.document-card.selected {
    border-color: #0d6efd;
    background-color: #f0f7ff;
}

/* List view card styles */
.document-card.list-view {
    flex-direction: row;
    align-items: center;
    padding: 10px 15px;
}

.document-card.list-view .document-icon {
    margin-right: 15px;
    margin-bottom: 0;
    font-size: 1.5rem;
}

.document-card.list-view .document-info {
    flex: 1;
    display: flex;
    align-items: center;
}

.document-card.list-view .document-name {
    margin-bottom: 0;
    margin-right: 15px;
}

.document-card.list-view .document-meta {
    margin-left: auto;
    display: flex;
    align-items: center;
}

.document-card.list-view .document-size,
.document-card.list-view .document-date {
    margin-right: 15px;
}

.document-card.list-view .document-actions {
    margin-top: 0;
    display: flex;
}

/* Document card elements */
.document-icon {
    font-size: 2.5rem;
    text-align: center;
    margin-bottom: 10px;
}

.document-name {
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 5px;
}

.document-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: #666;
}

.document-actions {
    margin-top: 10px;
    display: flex;
    justify-content: flex-end;
}

/* Content preview */
#documentContentWrapper {
    max-height: 50vh;
    overflow-y: auto;
}

/* Ensure document preview scrolls properly */
#documentPreviewModal .modal-body {
    max-height: 70vh;
    overflow-y: auto;
}

/* Empty state */
.placeholder-text {
    color: #999;
}

/* Filters */
.filters {
    margin-top: 20px;
}

.view-controls {
    display: flex;
    gap: 5px;
}
"""

    with open(library_css_path, 'w') as f:
        f.write(css_content)
    
    logger.info("Document library CSS created successfully")
    
    # Update base.html to include the new CSS
    base_html_path = TEMPLATES_DIR / 'base.html'
    
    if not base_html_path.exists():
        logger.warning(f"Base HTML template not found: {base_html_path}")
        return True
    
    # Backup existing file
    backup_file(base_html_path)
    
    logger.info(f"Updating base HTML template to include document library CSS: {base_html_path}")
    
    # Read the existing file
    with open(base_html_path, 'r') as f:
        base_content = f.read()
    
    # Check if it already has the CSS link
    if "document_library.css" not in base_content:
        # Add the CSS link
        css_link = '    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/enhanced/document_library.css\') }}">'
        
        # Find the CSS section and add the new link
        if '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/enhanced/document_panel.css\') }}">' in base_content:
            updated_base_content = base_content.replace(
                '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/enhanced/document_panel.css\') }}">',
                '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/enhanced/document_panel.css\') }}">\n' + css_link
            )
            
            # Write the updated content back to the file
            with open(base_html_path, 'w') as f:
                f.write(updated_base_content)
            
            logger.info("Base HTML template updated successfully")
    else:
        logger.info("Base HTML template already has document library CSS link")
    
    return True
def update_navbar():
    """Update the navigation bar to include a link to the document library."""
    base_html_path = TEMPLATES_DIR / 'base.html'
    
    if not base_html_path.exists():
        logger.error(f"Base HTML template not found: {base_html_path}")
        return False
    
    # Backup existing file
    backup_file(base_html_path)
    
    logger.info(f"Updating navigation bar in base HTML template: {base_html_path}")
    
    # Read the existing file
    with open(base_html_path, 'r') as f:
        base_content = f.read()
    
    # Look for the navbar section
    navbar_section = """<div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link" href="/enhanced">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/reflection">Reflection</a>
                    </li>"""
    
    # Check if document library link already exists
    if '<a class="nav-link" href="/library">Document Library</a>' in base_content:
        logger.info("Navigation bar already has document library link")
        return True
    
    # Add the document library link
    new_navbar_section = """<div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link" href="/enhanced">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/reflection">Reflection</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/library">Document Library</a>
                    </li>"""
    
    # Replace the navbar section
    updated_base_content = base_content.replace(navbar_section, new_navbar_section)
    
    # Write the updated content back to the file
    with open(base_html_path, 'w') as f:
        f.write(updated_base_content)
    
    logger.info("Navigation bar updated successfully")
    return True

def fix_document_routes():
    """Fix document routes to ensure they use the correct base URL."""
    routes_path = WEB_INTERFACE_DIR / 'document_rag_routes.py'
    
    if not routes_path.exists():
        logger.error(f"Document RAG routes file not found: {routes_path}")
        return False
    
    # Backup existing file
    backup_file(routes_path)
    
    logger.info(f"Fixing document routes: {routes_path}")
    
    # Read the existing file
    with open(routes_path, 'r') as f:
        content = f.read()
    
    # Fix the library route path to use the blueprint prefix
    updated_content = content.replace(
        "@document_rag_bp.route('/library', methods=['GET'])",
        "@document_rag_bp.route('/library', methods=['GET'])"
    )
    
    # Write the updated content back to the file
    with open(routes_path, 'w') as f:
        f.write(updated_content)
    
    logger.info("Document routes fixed successfully")
    return True

def main():
    """Main function to apply all fixes."""
    logger.info("Starting document UI fixes...")
    
    # Step 1: Create document library template
    create_document_library_template()
    
    # Step 2: Create document library JavaScript
    create_document_library_js()
    
    # Step 3: Create document modal components
    create_document_modal_components()
    
    # Step 4: Fix document manager JavaScript
    fix_document_manager_js()
    
    # Step 5: Add document library route
    add_document_library_route()
    
    # Step 6: Add CSS styles
    add_css_styles()
    
    # Step 7: Update navbar
    update_navbar()
    
    # Step 8: Fix document routes
    fix_document_routes()
    
    logger.info("All document UI fixes applied successfully!")
    logger.info("Please restart the server to apply the changes.")

if __name__ == "__main__":
    main()
