/**
 * Document Manager JavaScript
 * 
 * This script provides functionality for the document panel, handling document uploads,
 * document library management, and RAG integration.
 */

class DocumentManager {
    constructor(options = {}) {
        // Set default options
        this.options = Object.assign({
            documentListId: 'documentList',
            documentSearchId: 'documentSearch',
            uploadBtnId: 'uploadDocBtn',
            refreshBtnId: 'refreshDocsBtn',
            uploadModalId: 'uploadDocumentModal',
            uploadFormId: 'uploadDocumentForm',
            uploadSubmitId: 'uploadDocumentSubmit',
            previewModalId: 'documentPreviewModal',
            enableRagSwitchId: 'enableRagSwitch',
            ragContextId: 'ragContext',
            ragCountId: 'ragCount',
            confirmDeleteModalId: 'confirmDeleteModal'
        }, options);
        
        // Initialize state
        this.documents = [];
        this.selectedDocuments = [];
        this.ragEnabled = true;
        this.currentPreviewDoc = null;
        
        // Initialize when document is ready
        document.addEventListener('DOMContentLoaded', () => this.initialize());
    }
    

    downloadDocument(docId) {
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
    }

    deleteDocument(docId) {
        const doc = this.documents.find(d => d.id === docId);
        
        if (!doc) return;
        
        // Show confirmation dialog
        const confirmModal = new bootstrap.Modal(document.getElementById(this.options.confirmDeleteModalId));
        const confirmModalEl = document.getElementById(this.options.confirmDeleteModalId);
        
        // Set document name in confirmation dialog
        const docNameEl = confirmModalEl.querySelector('.document-name');
        if (docNameEl) {
            docNameEl.textContent = doc.filename || doc.name;
        }
        
        // Set up confirmation button
        const confirmDeleteBtn = confirmModalEl.querySelector('.confirm-delete-btn');
        if (confirmDeleteBtn) {
            // Remove any existing event listeners
            const newConfirmBtn = confirmDeleteBtn.cloneNode(true);
            confirmDeleteBtn.parentNode.replaceChild(newConfirmBtn, confirmDeleteBtn);
            
            // Add new event listener
            newConfirmBtn.addEventListener('click', () => {
                this.performDocumentDeletion(docId);
                confirmModal.hide();
            });
        }
        
        // Show the modal
        confirmModal.show();
    }
    
    performDocumentDeletion(docId) {
        // Set up loading state
        const doc = this.documents.find(d => d.id === docId);
        const card = document.querySelector(`.document-card[data-id="${docId}"]`);
        
        if (card) {
            card.classList.add('deleting');
            card.innerHTML = `
                <div class="d-flex align-items-center justify-content-center p-3">
                    <div class="spinner-border spinner-border-sm text-danger me-2" role="status">
                        <span class="visually-hidden">Deleting...</span>
                    </div>
                    <span>Deleting document...</span>
                </div>
            `;
        }
        
        // Call the API to delete the document
        fetch(`/api/documents/${docId}/delete`, {
            method: 'POST'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Remove from selected documents if it was selected
                if (this.isDocumentSelected(docId)) {
                    this.deselectDocument(docId);
                }
                
                // Remove from documents array
                this.documents = this.documents.filter(d => d.id !== docId);
                
                // Remove card with animation
                if (card) {
                    card.style.height = card.offsetHeight + 'px';
                    card.classList.add('deleted');
                    
                    // Remove after animation
                    setTimeout(() => {
                        card.remove();
                        
                        // Show "no documents" message if no documents left
                        if (this.documents.length === 0) {
                            this.renderDocumentList();
                        }
                    }, 300);
                }
                
                // Show success toast
                this.showToast('Document deleted successfully', 'success');
            } else {
                throw new Error(data.error || 'Failed to delete document');
            }
        })
        .catch(error => {
            console.error('Error deleting document:', error);
            
            // Restore card
            if (card) {
                card.classList.remove('deleting');
                this.renderDocumentList();
            }
            
            // Show error toast
            this.showToast(`Error: ${error.message}`, 'danger');
        });
    }
    
    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.id = toastId;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add to container
        toastContainer.appendChild(toast);
        
        // Initialize and show toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 3000
        });
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    initialize() {
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial documents
        this.loadDocuments();
        
        // Create confirmation delete modal if it doesn't exist
        this.createDeleteConfirmationModal();
    }
    
    createDeleteConfirmationModal() {
        // Check if modal already exists
        if (document.getElementById(this.options.confirmDeleteModalId)) {
            return;
        }
        
        // Create modal element
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = this.options.confirmDeleteModalId;
        modal.tabIndex = -1;
        modal.setAttribute('aria-labelledby', 'confirmDeleteModalLabel');
        modal.setAttribute('aria-hidden', 'true');
        
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="confirmDeleteModalLabel">Confirm Delete</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>Are you sure you want to delete the document: <strong class="document-name"></strong>?</p>
                        <p class="text-danger">This action cannot be undone.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger confirm-delete-btn">Delete</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add to document
        document.body.appendChild(modal);
    }
    
    setupEventListeners() {
        // Download button in preview modal
        const downloadBtn = document.getElementById('downloadDocumentBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                if (this.currentPreviewDoc) {
                    this.downloadDocument(this.currentPreviewDoc.id);
                }
            });
        }
        
        // Delete button in preview modal
        const deleteBtn = document.getElementById('deleteDocumentBtn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                if (this.currentPreviewDoc) {
                    // Close the preview modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById(this.options.previewModalId));
                    if (modal) {
                        modal.hide();
                    }
                    
                    // Show delete confirmation
                    this.deleteDocument(this.currentPreviewDoc.id);
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
            
            const deleteBtn = e.target.closest('.delete-doc-btn');
            if (deleteBtn) {
                const docId = deleteBtn.getAttribute('data-id');
                if (docId) {
                    this.deleteDocument(docId);
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        });
        // Upload button
        const uploadBtn = document.getElementById(this.options.uploadBtnId);
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.openUploadModal());
        }
        
        // Refresh button
        const refreshBtn = document.getElementById(this.options.refreshBtnId);
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadDocuments());
        }
        
        // Upload submit
        const uploadSubmit = document.getElementById(this.options.uploadSubmitId);
        if (uploadSubmit) {
            uploadSubmit.addEventListener('click', () => this.uploadDocument());
        }
        
        // Search input
        const searchInput = document.getElementById(this.options.documentSearchId);
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterDocuments(e.target.value));
        }
        
        // RAG toggle
        const ragSwitch = document.getElementById(this.options.enableRagSwitchId);
        if (ragSwitch) {
            ragSwitch.addEventListener('change', (e) => {
                this.ragEnabled = e.target.checked;
                this.updateRagContext();
            });
        }
        
        // Add to RAG button in preview modal
        const addToRagBtn = document.getElementById('addToRagBtn');
        if (addToRagBtn) {
            addToRagBtn.addEventListener('click', () => {
                if (this.currentPreviewDoc && !this.isDocumentSelected(this.currentPreviewDoc.id)) {
                    this.selectDocument(this.currentPreviewDoc.id);
                }
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById(this.options.previewModalId));
                if (modal) {
                    modal.hide();
                }
            });
        }
    }
    
    openUploadModal() {
        // Reset form
        const form = document.getElementById(this.options.uploadFormId);
        if (form) {
            form.reset();
        }
        
        // Hide progress
        const progress = document.querySelector('.upload-progress');
        if (progress) {
            progress.classList.add('d-none');
        }
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById(this.options.uploadModalId));
        modal.show();
    }
    
    uploadDocument() {
        // Get form and file
        const form = document.getElementById(this.options.uploadFormId);
        const fileInput = document.getElementById('documentFile');
        const generateEmbeddings = document.getElementById('generateEmbeddingsCheck').checked;
        const tagsInput = document.getElementById('documentTags');
        
        if (!form || !fileInput || !fileInput.files || fileInput.files.length === 0) {
            alert('Please select a file to upload');
            return;
        }
        
        const file = fileInput.files[0];
        const tags = tagsInput ? tagsInput.value.split(',').map(tag => tag.trim()).filter(tag => tag) : [];
        
        // Show progress
        const progress = document.querySelector('.upload-progress');
        const progressBar = document.querySelector('.upload-progress .progress-bar');
        const statusText = document.getElementById('uploadStatus');
        
        if (progress) {
            progress.classList.remove('d-none');
        }
        
        if (progressBar) {
            progressBar.style.width = '0%';
        }
        
        if (statusText) {
            statusText.textContent = 'Preparing upload...';
        }
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('generate_embeddings', generateEmbeddings ? '1' : '0');
        formData.append('tags', JSON.stringify(tags));
        
        // Upload file
        fetch('/api/documents/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                if (statusText) {
                    statusText.textContent = 'Document uploaded successfully!';
                }
                
                if (progressBar) {
                    progressBar.style.width = '100%';
                    progressBar.classList.remove('progress-bar-animated');
                }
                
                // Add document to list and refresh
                this.loadDocuments();
                
                // Close modal after 1 second
                setTimeout(() => {
                    const modal = bootstrap.Modal.getInstance(document.getElementById(this.options.uploadModalId));
                    if (modal) {
                        modal.hide();
                    }
                }, 1000);
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        })
        .catch(error => {
            console.error('Error uploading document:', error);
            
            if (statusText) {
                statusText.textContent = `Error: ${error.message}`;
                statusText.classList.add('text-danger');
            }
            
            if (progressBar) {
                progressBar.classList.remove('progress-bar-animated');
                progressBar.classList.remove('bg-primary');
                progressBar.classList.add('bg-danger');
            }
        });
    }
    
    loadDocuments() {
        const listContainer = document.getElementById(this.options.documentListId);
        
        if (!listContainer) return;
        
        // Show loading
        listContainer.innerHTML = `
            <div class="placeholder-text text-muted p-3">
                <div class="d-flex justify-content-center mb-3">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
                <p class="text-center mb-0">Loading documents...</p>
            </div>
        `;
        
        // Fetch documents
        fetch('/api/documents')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    this.documents = data.documents || [];
                    this.renderDocumentList();
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            })
            .catch(error => {
                console.error('Error loading documents:', error);
                listContainer.innerHTML = `
                    <div class="alert alert-danger m-3">
                        <i class="bi bi-exclamation-triangle-fill"></i> Error loading documents: ${error.message}
                    </div>
                `;
            });
    }
    
    renderDocumentList() {
        const listContainer = document.getElementById(this.options.documentListId);
        
        if (!listContainer) return;
        
        if (this.documents.length === 0) {
            listContainer.innerHTML = `
                <div class="placeholder-text text-muted p-3">
                    <p class="text-center mb-0">No documents found</p>
                    <p class="text-center mt-2">
                        <button class="btn btn-sm btn-outline-primary" id="firstUploadBtn">
                            <i class="bi bi-upload"></i> Upload your first document
                        </button>
                    </p>
                </div>
            `;
            
            // Add event listener to upload button
            const firstUploadBtn = document.getElementById('firstUploadBtn');
            if (firstUploadBtn) {
                firstUploadBtn.addEventListener('click', () => this.openUploadModal());
            }
            
            return;
        }
        
        // Create document list
        let html = '';
        
        this.documents.forEach(doc => {
            const iconClass = this.getDocumentIconClass(doc.type || doc.file_type);
            const isSelected = this.isDocumentSelected(doc.id);
            const cardClass = isSelected ? 'document-card selected' : 'document-card';
            const docName = doc.name || doc.filename;
            
            html += `
                <div class="${cardClass}" data-id="${doc.id}">
                    <div class="document-icon">
                        <i class="${iconClass}"></i>
                    </div>
                    <div class="document-info">
                        <div class="document-name" title="${docName}">${docName}</div>
                        <div class="document-meta">
                            <span class="document-size">${this.formatFileSize(doc.size || doc.file_size)}</span>
                            <span class="document-date">${this.formatDate(doc.date_added || doc.upload_date)}</span>
                        </div>
                    </div>
                    <div class="document-actions">
                        <button class="btn btn-sm btn-link preview-doc-btn" data-id="${doc.id}" title="Preview">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-link download-doc-btn" data-id="${doc.id}" title="Download">
                            <i class="bi bi-download"></i>
                        </button>
                        <button class="btn btn-sm btn-link delete-doc-btn" data-id="${doc.id}" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                        <button class="btn btn-sm btn-link ${isSelected ? 'remove-rag-btn' : 'add-rag-btn'}" 
                                data-id="${doc.id}" title="${isSelected ? 'Remove from RAG' : 'Add to RAG'}">
                            <i class="bi bi-${isSelected ? 'dash-circle' : 'plus-circle'}"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        listContainer.innerHTML = html;
        
        // Add event listeners
        this.documents.forEach(doc => {
            // Preview button
            const previewBtn = listContainer.querySelector(`.preview-doc-btn[data-id="${doc.id}"]`);
            if (previewBtn) {
                previewBtn.addEventListener('click', (e) => {
                    this.previewDocument(doc.id);
                    e.stopPropagation();
                });
            }
            
            // Add/remove RAG button
            const ragBtn = listContainer.querySelector(`.add-rag-btn[data-id="${doc.id}"], .remove-rag-btn[data-id="${doc.id}"]`);
            if (ragBtn) {
                ragBtn.addEventListener('click', (e) => {
                    if (this.isDocumentSelected(doc.id)) {
                        this.deselectDocument(doc.id);
                    } else {
                        this.selectDocument(doc.id);
                    }
                    e.stopPropagation();
                });
            }
            
            // Click on card to preview
            const card = listContainer.querySelector(`.document-card[data-id="${doc.id}"]`);
            if (card) {
                card.addEventListener('click', (e) => {
                    // Don't trigger if clicking a button
                    if (!e.target.closest('button')) {
                        this.previewDocument(doc.id);
                    }
                });
            }
        });
    }
    
    filterDocuments(query) {
        const listContainer = document.getElementById(this.options.documentListId);
        
        if (!listContainer) return;
        
        if (!query) {
            // Show all documents
            const cards = listContainer.querySelectorAll('.document-card');
            cards.forEach(card => {
                card.style.display = '';
            });
            
            // If no cards visible, might need to re-render
            if (cards.length === 0) {
                this.renderDocumentList();
            }
            
            return;
        }
        
        query = query.toLowerCase();
        
        // Filter document cards
        const cards = listContainer.querySelectorAll('.document-card');
        
        cards.forEach(card => {
            const docId = card.getAttribute('data-id');
            const doc = this.documents.find(d => d.id === docId);
            
            if (doc) {
                // Check if document name contains query
                const nameMatch = (doc.name || doc.filename).toLowerCase().includes(query);
                
                // Check if tags contain query
                const tagsMatch = (doc.tags || []).some(tag => tag.toLowerCase().includes(query));
                
                if (nameMatch || tagsMatch) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            }
        });
    }
    
    previewDocument(docId) {
        const doc = this.documents.find(d => d.id === docId);
        
        if (!doc) return;
        
        // Store current preview doc
        this.currentPreviewDoc = doc;
        
        // Update preview modal
        const titleEl = document.getElementById('previewDocumentTitle');
        const typeEl = document.getElementById('previewDocumentType');
        const sizeEl = document.getElementById('previewDocumentSize');
        const dateEl = document.getElementById('previewDocumentDate');
        const tagsEl = document.getElementById('previewDocumentTags');
        const contentEl = document.getElementById('documentContentPreview');
        const placeholder = document.querySelector('.content-placeholder');
        const addToRagBtn = document.getElementById('addToRagBtn');
        const deleteBtn = document.getElementById('deleteDocumentBtn');
        
        if (titleEl) titleEl.textContent = doc.name || doc.filename;
        if (typeEl) typeEl.textContent = (doc.type || doc.file_type || "").charAt(0).toUpperCase() + (doc.type || doc.file_type || "").slice(1);
        if (sizeEl) sizeEl.textContent = this.formatFileSize(doc.size || doc.file_size);
        if (dateEl) dateEl.textContent = this.formatDate(doc.date_added || doc.upload_date);
        if (tagsEl) tagsEl.textContent = (doc.tags && doc.tags.length > 0) ? doc.tags.join(', ') : 'None';
        
        // Update Add to RAG button
        if (addToRagBtn) {
            if (this.isDocumentSelected(doc.id)) {
                addToRagBtn.innerHTML = '<i class="bi bi-dash-circle"></i> Remove from RAG Context';
                addToRagBtn.classList.remove('btn-outline-primary');
                addToRagBtn.classList.add('btn-outline-danger');
            } else {
                addToRagBtn.innerHTML = '<i class="bi bi-plus-circle"></i> Add to RAG Context';
                addToRagBtn.classList.remove('btn-outline-danger');
                addToRagBtn.classList.add('btn-outline-primary');
            }
        }
        
        // Ensure delete button is visible
        if (deleteBtn) {
            deleteBtn.classList.remove('d-none');
        }
        
        // Show loading placeholder
        if (contentEl) contentEl.innerHTML = '';
        if (contentEl) contentEl.style.display = 'none';
        if (placeholder) placeholder.classList.remove('d-none');
        
        // Fetch document content
        fetch(`/api/documents/${doc.id}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Hide placeholder
                    if (placeholder) placeholder.classList.add('d-none');
                    
                    // Show content
                    if (contentEl) {
                        contentEl.style.display = '';
                        contentEl.textContent = data.document.text_content || 'No text content available';
                    }
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            })
            .catch(error => {
                console.error('Error loading document content:', error);
                
                // Hide placeholder
                if (placeholder) placeholder.classList.add('d-none');
                
                // Show error
                if (contentEl) {
                    contentEl.style.display = '';
                    contentEl.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="bi bi-exclamation-triangle-fill"></i> Error loading content: ${error.message}
                        </div>
                    `;
                }
            });
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById(this.options.previewModalId));
        modal.show();
    }
    
    selectDocument(docId) {
        const doc = this.documents.find(d => d.id === docId);
        
        if (!doc || this.isDocumentSelected(docId)) return;
        
        // Add to selected documents
        this.selectedDocuments.push(doc);
        
        // Update UI
        this.updateRagContext();
        
        // Update document card
        const card = document.querySelector(`.document-card[data-id="${docId}"]`);
        if (card) {
            card.classList.add('selected');
            
            const ragBtn = card.querySelector('.add-rag-btn');
            if (ragBtn) {
                ragBtn.classList.remove('add-rag-btn');
                ragBtn.classList.add('remove-rag-btn');
                ragBtn.setAttribute('title', 'Remove from RAG');
                ragBtn.querySelector('i').classList.remove('bi-plus-circle');
                ragBtn.querySelector('i').classList.add('bi-dash-circle');
            }
        }
        
        // Update preview modal button if this is the current preview
        if (this.currentPreviewDoc && this.currentPreviewDoc.id === docId) {
            const addToRagBtn = document.getElementById('addToRagBtn');
            if (addToRagBtn) {
                addToRagBtn.innerHTML = '<i class="bi bi-dash-circle"></i> Remove from RAG Context';
                addToRagBtn.classList.remove('btn-outline-primary');
                addToRagBtn.classList.add('btn-outline-danger');
            }
        }
    }
    
    deselectDocument(docId) {
        if (!this.isDocumentSelected(docId)) return;
        
        // Remove from selected documents
        this.selectedDocuments = this.selectedDocuments.filter(doc => doc.id !== docId);
        
        // Update UI
        this.updateRagContext();
        
        // Update document card
        const card = document.querySelector(`.document-card[data-id="${docId}"]`);
        if (card) {
            card.classList.remove('selected');
            
            const ragBtn = card.querySelector('.remove-rag-btn');
            if (ragBtn) {
                ragBtn.classList.remove('remove-rag-btn');
                ragBtn.classList.add('add-rag-btn');
                ragBtn.setAttribute('title', 'Add to RAG');
                ragBtn.querySelector('i').classList.remove('bi-dash-circle');
                ragBtn.querySelector('i').classList.add('bi-plus-circle');
            }
        }
        
        // Update preview modal button if this is the current preview
        if (this.currentPreviewDoc && this.currentPreviewDoc.id === docId) {
            const addToRagBtn = document.getElementById('addToRagBtn');
            if (addToRagBtn) {
                addToRagBtn.innerHTML = '<i class="bi bi-plus-circle"></i> Add to RAG Context';
                addToRagBtn.classList.remove('btn-outline-danger');
                addToRagBtn.classList.add('btn-outline-primary');
            }
        }
    }
    
    isDocumentSelected(docId) {
        return this.selectedDocuments.some(doc => doc.id === docId);
    }
    
    updateRagContext() {
        const ragContext = document.getElementById(this.options.ragContextId);
        const ragCount = document.getElementById(this.options.ragCountId);
        
        if (!ragContext) return;
        
        // Update count
        if (ragCount) {
            ragCount.textContent = this.selectedDocuments.length;
        }
        
        // If RAG is disabled or no documents selected
        if (!this.ragEnabled || this.selectedDocuments.length === 0) {
            ragContext.innerHTML = `
                <div class="placeholder-text text-muted text-center p-2">
                    <small>${!this.ragEnabled ? 'RAG is disabled' : 'No documents selected for context'}</small>
                </div>
            `;
            return;
        }
        
        // Create context list
        let html = '';
        
        this.selectedDocuments.forEach(doc => {
            const iconClass = this.getDocumentIconClass(doc.type || doc.file_type);
            const docName = doc.name || doc.filename;
            
            html += `
                <div class="rag-document" data-id="${doc.id}">
                    <div class="rag-document-info">
                        <i class="${iconClass} me-1"></i>
                        <span class="rag-document-name" title="${docName}">${docName}</span>
                    </div>
                    <button class="btn btn-sm btn-link text-danger remove-rag-doc-btn" data-id="${doc.id}" title="Remove">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            `;
        });
        
        ragContext.innerHTML = html;
        
        // Add event listeners
        this.selectedDocuments.forEach(doc => {
            const removeBtn = ragContext.querySelector(`.remove-rag-doc-btn[data-id="${doc.id}"]`);
            if (removeBtn) {
                removeBtn.addEventListener('click', () => this.deselectDocument(doc.id));
            }
        });
    }
    
    getSelectedDocumentsForRag() {
        if (!this.ragEnabled || this.selectedDocuments.length === 0) {
            return [];
        }
        
        return this.selectedDocuments.map(doc => ({
            document_id: doc.id,
            filename: doc.name || doc.filename
        }));
    }
    
    // Utility methods
    getDocumentIconClass(type) {
        switch (type) {
            case 'pdf':
                return 'bi bi-file-earmark-pdf text-danger';
            case 'image':
                return 'bi bi-file-earmark-image text-primary';
            case 'text':
                return 'bi bi-file-earmark-text text-success';
            case 'word':
                return 'bi bi-file-earmark-word text-primary';
            case 'excel':
                return 'bi bi-file-earmark-excel text-success';
            case 'presentation':
                return 'bi bi-file-earmark-slides text-warning';
            default:
                return 'bi bi-file-earmark text-secondary';
        }
    }
    
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString;
        
        // If today, show time
        const today = new Date();
        if (date.toDateString() === today.toDateString()) {
            return `Today at ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        }
        
        // If this year, show month and day
        if (date.getFullYear() === today.getFullYear()) {
            return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        }
        
        // Otherwise show full date
        return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    }
}

// Create a global instance
let documentManager = null;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    documentManager = new DocumentManager();
    
    // Make manager globally available for API access
    window.documentManager = documentManager;
    
    // Add CSS styles for document deletion
    const style = document.createElement('style');
    style.textContent = `
        .document-card.deleting {
            opacity: 0.6;
            pointer-events: none;
        }
        
        .document-card.deleted {
            animation: fadeOutUp 0.3s forwards;
            overflow: hidden;
        }
        
        @keyframes fadeOutUp {
            from {
                opacity: 1;
                transform: translateY(0);
                max-height: 100px;
            }
            to {
                opacity: 0;
                transform: translateY(-10px);
                max-height: 0;
                margin: 0;
                padding: 0;
                border: 0;
            }
        }
    `;
    document.head.appendChild(style);
});
