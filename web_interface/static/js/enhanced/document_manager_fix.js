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
            ragCountId: 'ragCount'
        }, options);
        
        // Initialize state
        this.documents = [];
        this.selectedDocuments = [];
        this.ragEnabled = true;
        this.currentPreviewDoc = null;
        this.initialized = false;
    }
    
    initialize() {
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial documents
        this.loadDocuments();
        
        // Set initialization flag
        this.initialized = true;
        console.log("Document Manager initialized");
    }
    
    downloadDocument(docId) {
        const doc = this.documents.find(d => d.id === docId);
        
        if (!doc) return;
        
        console.log("Downloading document:", docId);
        
        // Create a hidden link for download to avoid window popup
        const downloadLink = document.createElement('a');
        downloadLink.style.display = 'none';
        downloadLink.href = `/api/documents/${docId}/download`;
        downloadLink.target = '_blank';
        
        // Add to document, trigger click, then remove
        document.body.appendChild(downloadLink);
        downloadLink.click();
        
        // Remove after a short delay
        setTimeout(() => {
            document.body.removeChild(downloadLink);
        }, 100);
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
                } else if (this.currentPreviewDoc && this.isDocumentSelected(this.currentPreviewDoc.id)) {
                    this.deselectDocument(this.currentPreviewDoc.id);
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
            // Get the file extension from the filename to determine type
            const filename = doc.filename || doc.name || 'unknown';
            const fileExt = filename.split('.').pop().toLowerCase();
            const docType = this.getDocumentType(fileExt);
            
            const iconClass = this.getDocumentIconClass(docType);
            const isSelected = this.isDocumentSelected(doc.id);
            const cardClass = isSelected ? 'document-card selected' : 'document-card';
            
            html += `
                <div class="${cardClass}" data-id="${doc.id}">
                    <div class="document-icon">
                        <i class="${iconClass}"></i>
                    </div>
                    <div class="document-info">
                        <div class="document-name" title="${filename}">${filename}</div>
                        <div class="document-meta">
                            <span class="document-size">${this.formatFileSize(doc.file_size || doc.size || 0)}</span>
                            <span class="document-date">${this.formatDate(doc.upload_date || doc.date_added || '')}</span>
                        </div>
                    </div>
                    <div class="document-actions">
                        <button class="btn btn-sm btn-link preview-doc-btn" data-id="${doc.id}" title="Preview">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-link download-doc-btn" data-id="${doc.id}" title="Download">
                            <i class="bi bi-download"></i>
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
                previewBtn.addEventListener('click', () => this.previewDocument(doc.id));
            }
            
            // Add/remove RAG button
            const ragBtn = listContainer.querySelector(`.add-rag-btn[data-id="${doc.id}"], .remove-rag-btn[data-id="${doc.id}"]`);
            if (ragBtn) {
                ragBtn.addEventListener('click', () => {
                    if (this.isDocumentSelected(doc.id)) {
                        this.deselectDocument(doc.id);
                    } else {
                        this.selectDocument(doc.id);
                    }
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
                const nameMatch = (doc.name || doc.filename || '').toLowerCase().includes(query);
                
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
        
        // Get the file extension from the filename to determine type
        const filename = doc.filename || doc.name || 'unknown';
        const fileExt = filename.split('.').pop().toLowerCase();
        const docType = this.getDocumentType(fileExt);
        
        if (titleEl) titleEl.textContent = filename;
        if (typeEl) typeEl.textContent = docType.charAt(0).toUpperCase() + docType.slice(1);
        if (sizeEl) sizeEl.textContent = this.formatFileSize(doc.file_size || doc.size || 0);
        if (dateEl) dateEl.textContent = this.formatDate(doc.upload_date || doc.date_added || '');
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
                        const textContent = data.document.text_content || '';
                        contentEl.textContent = textContent || 'No text content available';
                        
                        // Store text content in the document object for later use
                        this.currentPreviewDoc.text_content = textContent;
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
        
        // Dispatch event for other components to listen for
        document.dispatchEvent(new CustomEvent('rag-document-selected', { 
            detail: { 
                documentId: docId,
                selectedDocuments: this.selectedDocuments
            } 
        }));
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
        
        // Dispatch event for other components to listen for
        document.dispatchEvent(new CustomEvent('rag-document-deselected', { 
            detail: { 
                documentId: docId,
                selectedDocuments: this.selectedDocuments
            } 
        }));
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
            // Get the file extension from the filename to determine type
            const filename = doc.filename || doc.name || 'unknown';
            const fileExt = filename.split('.').pop().toLowerCase();
            const docType = this.getDocumentType(fileExt);
            
            const iconClass = this.getDocumentIconClass(docType);
            
            html += `
                <div class="rag-document" data-id="${doc.id}">
                    <div class="rag-document-info">
                        <i class="${iconClass} me-1"></i>
                        <span class="rag-document-name" title="${filename}">${filename}</span>
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
        
        // Format each document for RAG context
        return this.selectedDocuments.map(doc => {
            const filename = doc.filename || doc.name || 'unknown';
            return {
                document_id: doc.id,
                filename: filename,
                content: doc.text_content || '' // Include content if available
            };
        });
    }
    
    // Utility methods
    getDocumentType(fileExt) {
        const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp'];
        const textExts = ['txt', 'md', 'rtf', 'log', 'csv', 'json', 'xml', 'html', 'htm'];
        const wordExts = ['doc', 'docx', 'odt'];
        const excelExts = ['xls', 'xlsx', 'ods', 'csv'];
        const presentationExts = ['ppt', 'pptx', 'odp'];
        
        if (fileExt === 'pdf') return 'pdf';
        if (imageExts.includes(fileExt)) return 'image';
        if (textExts.includes(fileExt)) return 'text';
        if (wordExts.includes(fileExt)) return 'word';
        if (excelExts.includes(fileExt)) return 'excel';
        if (presentationExts.includes(fileExt)) return 'presentation';
        
        return 'unknown';
    }
    
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
        if (bytes === undefined || bytes === null) return '0 bytes';
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
window.documentManager = null;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    window.documentManager = new DocumentManager();
    window.documentManager.initialize();
    
    console.log("Document manager registered globally");
});
