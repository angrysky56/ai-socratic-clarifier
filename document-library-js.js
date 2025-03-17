/**
 * Document Library Management
 * 
 * Manages the document library UI for the AI-Socratic-Clarifier enhanced interface.
 * Provides functionality for document upload, viewing, tagging, and RAG integration.
 */

// Global state
let documents = [];
let currentPage = 1;
let pageSize = 10;
let currentDocumentId = null;
let searchQuery = '';

// Document ready handler
document.addEventListener('DOMContentLoaded', function() {
  // Initialize event handlers
  initializeEventHandlers();
  
  // Load documents
  loadDocuments();
  
  // Load document stats
  loadDocumentStats();
});

/**
 * Initialize all event handlers for the document library interface
 */
function initializeEventHandlers() {
  // Document upload form submission
  const uploadForm = document.getElementById('documentUploadForm');
  if (uploadForm) {
    uploadForm.addEventListener('submit', function(event) {
      event.preventDefault();
      uploadDocument();
    });
  }
  
  // Document search
  const searchButton = document.getElementById('searchButton');
  const searchInput = document.getElementById('documentSearch');
  
  if (searchButton && searchInput) {
    searchButton.addEventListener('click', function() {
      searchQuery = searchInput.value.trim();
      currentPage = 1;
      loadDocuments();
    });
    
    searchInput.addEventListener('keypress', function(event) {
      if (event.key === 'Enter') {
        searchQuery = searchInput.value.trim();
        currentPage = 1;
        loadDocuments();
      }
    });
  }
  
  // Pagination
  const prevButton = document.getElementById('prevPage');
  const nextButton = document.getElementById('nextPage');
  
  if (prevButton) {
    prevButton.addEventListener('click', function() {
      if (currentPage > 1) {
        currentPage--;
        loadDocuments();
      }
    });
  }
  
  if (nextButton) {
    nextButton.addEventListener('click', function() {
      const totalPages = Math.ceil(documents.length / pageSize);
      if (currentPage < totalPages) {
        currentPage++;
        loadDocuments();
      }
    });
  }
  
  // Document preview modal buttons
  const documentDownload = document.getElementById('documentDownload');
  const documentUseRag = document.getElementById('documentUseRag');
  const documentAddTags = document.getElementById('documentAddTags');
  const documentDelete = document.getElementById('documentDelete');
  
  if (documentDownload) {
    documentDownload.addEventListener('click', function() {
      if (currentDocumentId) {
        downloadDocument(currentDocumentId);
      }
    });
  }
  
  if (documentUseRag) {
    documentUseRag.addEventListener('click', function() {
      if (currentDocumentId) {
        useDocumentInRag(currentDocumentId);
      }
    });
  }
  
  if (documentAddTags) {
    documentAddTags.addEventListener('click', function() {
      if (currentDocumentId) {
        showAddTagsModal(currentDocumentId);
      }
    });
  }
  
  if (documentDelete) {
    documentDelete.addEventListener('click', function() {
      if (currentDocumentId) {
        showDeleteConfirmation(currentDocumentId);
      }
    });
  }
  
  // Add tags modal
  const saveTagsButton = document.getElementById('saveTagsButton');
  if (saveTagsButton) {
    saveTagsButton.addEventListener('click', function() {
      saveDocumentTags();
    });
  }
  
  // Delete confirmation modal
  const confirmDeleteButton = document.getElementById('confirmDeleteButton');
  if (confirmDeleteButton) {
    confirmDeleteButton.addEventListener('click', function() {
      deleteDocument();
    });
  }
}

/**
 * Load documents from the API
 */
function loadDocuments() {
  // Show loading state
  const documentsList = document.getElementById('documentsList');
  if (documentsList) {
    documentsList.innerHTML = '<tr><td colspan="5" class="text-center">Loading documents...</td></tr>';
  }
  
  // Make API request
  fetch('/api/documents')
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        documents = data.documents;
        
        // Filter by search query if needed
        if (searchQuery) {
          const query = searchQuery.toLowerCase();
          documents = documents.filter(doc => 
            doc.filename.toLowerCase().includes(query) || 
            (doc.tags && doc.tags.some(tag => tag.toLowerCase().includes(query)))
          );
        }
        
        // Update document count
        const documentCount = document.getElementById('documentCount');
        if (documentCount) {
          documentCount.textContent = documents.length;
        }
        
        // Update pagination
        updatePagination();
        
        // Display documents for current page
        displayDocuments();
      } else {
        // Show error
        if (documentsList) {
          documentsList.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error loading documents: ${data.error || 'Unknown error'}</td></tr>`;
        }
      }
    })
    .catch(error => {
      console.error('Error loading documents:', error);
      if (documentsList) {
        documentsList.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error loading documents: ${error.message || 'Network error'}</td></tr>`;
      }
    });
}

/**
 * Display documents for the current page
 */
function displayDocuments() {
  const documentsList = document.getElementById('documentsList');
  if (!documentsList) return;
  
  // Calculate page range
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, documents.length);
  
  // No documents to display
  if (documents.length === 0) {
    documentsList.innerHTML = '<tr><td colspan="5" class="text-center">No documents found</td></tr>';
    return;
  }
  
  // Build HTML for document list
  let html = '';
  for (let i = startIndex; i < endIndex; i++) {
    const doc = documents[i];
    const date = new Date(doc.upload_date).toLocaleDateString();
    const size = formatFileSize(doc.file_size);
    
    html += `
      <tr>
        <td>${doc.filename}</td>
        <td>${doc.file_type || 'Unknown'}</td>
        <td>${size}</td>
        <td>${date}</td>
        <td>
          <div class="btn-group btn-group-sm" role="group">
            <button type="button" class="btn btn-outline-primary" onclick="previewDocument('${doc.id}')">
              <i class="fas fa-eye"></i>
            </button>
            <button type="button" class="btn btn-outline-success" onclick="useDocumentInRag('${doc.id}')">
              <i class="fas fa-brain"></i>
            </button>
            <button type="button" class="btn btn-outline-secondary" onclick="downloadDocument('${doc.id}')">
              <i class="fas fa-download"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }
  
  documentsList.innerHTML = html;
}

/**
 * Update pagination controls
 */
function updatePagination() {
  const prevButton = document.getElementById('prevPage');
  const nextButton = document.getElementById('nextPage');
  
  if (!prevButton || !nextButton) return;
  
  const totalPages = Math.ceil(documents.length / pageSize);
  
  // Update buttons state
  prevButton.disabled = currentPage <= 1;
  nextButton.disabled = currentPage >= totalPages;
}

/**
 * Load document library statistics
 */
function loadDocumentStats() {
  const statsElement = document.getElementById('documentStats');
  if (!statsElement) return;
  
  fetch('/api/documents')
    .then(response => response.json())
    .then(data => {
      if (data.success && data.stats) {
        const stats = data.stats;
        
        // Format stats
        let statsHtml = `
          <div class="d-flex justify-content-between mb-2">
            <span>Total Documents:</span>
            <span class="fw-bold">${stats.total_documents}</span>
          </div>
          <div class="d-flex justify-content-between mb-2">
            <span>With Embeddings:</span>
            <span class="fw-bold">${stats.with_embeddings}</span>
          </div>
          <div class="d-flex justify-content-between mb-2">
            <span>Total Size:</span>
            <span class="fw-bold">${formatFileSize(stats.total_size_bytes)}</span>
          </div>
          <div class="mt-3">
            <h6>Document Types:</h6>
            <ul class="list-unstyled">
        `;
        
        // Add document types
        for (const [type, count] of Object.entries(stats.document_types)) {
          statsHtml += `<li><span class="badge bg-secondary">${type}</span> <span class="fw-bold">${count}</span></li>`;
        }
        
        statsHtml += `
            </ul>
          </div>
          <div class="mt-2 small text-muted">
            Last updated: ${new Date(stats.last_updated).toLocaleString()}
          </div>
        `;
        
        statsElement.innerHTML = statsHtml;
      } else {
        statsElement.innerHTML = '<p class="text-danger">Error loading statistics</p>';
      }
    })
    .catch(error => {
      console.error('Error loading document stats:', error);
      statsElement.innerHTML = '<p class="text-danger">Error loading statistics</p>';
    });
}

/**
 * Upload a document to the library
 */
function uploadDocument() {
  // Get form elements
  const fileInput = document.getElementById('documentFile');
  const tagsInput = document.getElementById('documentTags');
  const generateEmbeddings = document.getElementById('generateEmbeddings');
  const uploadButton = document.getElementById('uploadButton');
  const uploadSpinner = document.getElementById('uploadSpinner');
  
  if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
    alert('Please select a file to upload');
    return;
  }
  
  // Create form data
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  
  // Add tags if provided
  if (tagsInput && tagsInput.value.trim()) {
    const tags = tagsInput.value.split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0);
    
    formData.append('tags', JSON.stringify(tags));
  }
  
  // Add embeddings option
  if (generateEmbeddings) {
    formData.append('generate_embeddings', generateEmbeddings.checked ? '1' : '0');
  }
  
  // Show loading state
  if (uploadButton && uploadSpinner) {
    uploadButton.disabled = true;
    uploadSpinner.classList.remove('d-none');
  }
  
  // Upload the document
  fetch('/api/documents/upload', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      // Reset loading state
      if (uploadButton && uploadSpinner) {
        uploadButton.disabled = false;
        uploadSpinner.classList.add('d-none');
      }
      
      if (data.success) {
        // Reset form
        if (fileInput) fileInput.value = '';
        if (tagsInput) tagsInput.value = '';
        
        // Show success message
        alert('Document uploaded successfully');
        
        // Reload documents and stats
        loadDocuments();
        loadDocumentStats();
      } else {
        alert(`Error uploading document: ${data.error || 'Unknown error'}`);
      }
    })
    .catch(error => {
      console.error('Error uploading document:', error);
      
      // Reset loading state
      if (uploadButton && uploadSpinner) {
        uploadButton.disabled = false;
        uploadSpinner.classList.add('d-none');
      }
      
      alert(`Error uploading document: ${error.message || 'Network error'}`);
    });
}

/**
 * Preview a document
 * @param {string} documentId - ID of the document to preview
 */
function previewDocument(documentId) {
  if (!documentId) return;
  
  // Set current document ID
  currentDocumentId = documentId;
  
  // Get modal elements
  const modalTitle = document.getElementById('documentPreviewModalLabel');
  const documentInfo = document.getElementById('documentInfo');
  const documentContent = document.getElementById('documentContent');
  const documentTagsDisplay = document.getElementById('documentTagsDisplay');
  
  // Show loading state
  if (modalTitle) modalTitle.textContent = 'Loading Document...';
  if (documentInfo) documentInfo.innerHTML = '<p>Loading document information...</p>';
  if (documentContent) documentContent.innerHTML = '<p>Loading document content...</p>';
  if (documentTagsDisplay) documentTagsDisplay.innerHTML = 'Loading tags...';
  
  // Show the modal
  const modal = new bootstrap.Modal(document.getElementById('documentPreviewModal'));
  modal.show();
  
  // Fetch document details
  fetch(`/api/documents/${documentId}`)
    .then(response => response.json())
    .then(data => {
      if (data.success && data.document) {
        const doc = data.document;
        
        // Update modal title
        if (modalTitle) modalTitle.textContent = doc.filename;
        
        // Update document info
        if (documentInfo) {
          const date = new Date(doc.upload_date).toLocaleString();
          const size = formatFileSize(doc.file_size);
          
          documentInfo.innerHTML = `
            <div class="d-flex justify-content-between mb-1">
              <span>File Type:</span>
              <span class="fw-bold">${doc.file_type || 'Unknown'}</span>
            </div>
            <div class="d-flex justify-content-between mb-1">
              <span>Size:</span>
              <span class="fw-bold">${size}</span>
            </div>
            <div class="d-flex justify-content-between mb-1">
              <span>Uploaded:</span>
              <span class="fw-bold">${date}</span>
            </div>
            <div class="d-flex justify-content-between mb-1">
              <span>Has Embeddings:</span>
              <span class="fw-bold">${doc.has_embeddings ? 'Yes' : 'No'}</span>
            </div>
          `;
        }
        
        // Update document content
        if (documentContent) {
          if (doc.text_content) {
            // Escape HTML content
            const escapedContent = doc.text_content
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
            
            documentContent.innerHTML = `<pre>${escapedContent}</pre>`;
          } else {
            documentContent.innerHTML = '<p class="text-muted">No text content available</p>';
          }
        }
        
        // Update tags
        if (documentTagsDisplay) {
          if (doc.tags && doc.tags.length > 0) {
            const tagsHtml = doc.tags.map(tag => 
              `<span class="badge bg-info me-1">${tag}</span>`
            ).join(' ');
            
            documentTagsDisplay.innerHTML = tagsHtml;
          } else {
            documentTagsDisplay.innerHTML = '<span class="text-muted">No tags</span>';
          }
        }
      } else {
        alert(`Error loading document: ${data.error || 'Unknown error'}`);
        
        // Hide the modal
        modal.hide();
      }
    })
    .catch(error => {
      console.error('Error loading document:', error);
      alert(`Error loading document: ${error.message || 'Network error'}`);
      
      // Hide the modal
      modal.hide();
    });
}

/**
 * Download a document
 * @param {string} documentId - ID of the document to download
 */
function downloadDocument(documentId) {
  if (!documentId) return;
  
  // Create a hidden link to download the file
  const downloadLink = document.createElement('a');
  downloadLink.href = `/api/documents/${documentId}/download`;
  downloadLink.target = '_blank';
  downloadLink.style.display = 'none';
  
  // Add to page and click
  document.body.appendChild(downloadLink);
  downloadLink.click();
  
  // Clean up
  document.body.removeChild(downloadLink);
}

/**
 * Use a document in RAG
 * @param {string} documentId - ID of the document to use in RAG
 */
function useDocumentInRag(documentId) {
  if (!documentId) return;
  
  // Get document from the list
  const document = documents.find(doc => doc.id === documentId);
  if (!document) {
    alert('Document not found');
    return;
  }
  
  // Send a message to the parent window if in an iframe
  if (window.parent && window.parent !== window) {
    window.parent.postMessage({
      type: 'use_document_in_rag',
      documentId: documentId,
      filename: document.filename
    }, '*');
  }
  
  // If not in an iframe, store in localStorage and redirect to chat
  localStorage.setItem('ragDocument', JSON.stringify({
    documentId: documentId,
    filename: document.filename
  }));
  
  // Close modal if open
  const modal = bootstrap.Modal.getInstance(document.getElementById('documentPreviewModal'));
  if (modal) {
    modal.hide();
  }
  
  // Redirect to chat page
  window.location.href = '/enhanced';
}

/**
 * Show the add tags modal
 * @param {string} documentId - ID of the document to add tags to
 */
function showAddTagsModal(documentId) {
  if (!documentId) return;
  
  // Get current tags for the document
  const document = documents.find(doc => doc.id === documentId);
  const tagsInput = document.getElementById('editDocumentTags');
  
  if (document && document.tags && tagsInput) {
    tagsInput.value = document.tags.join(', ');
  } else if (tagsInput) {
    tagsInput.value = '';
  }
  
  // Show the modal
  const modal = new bootstrap.Modal(document.getElementById('addTagsModal'));
  modal.show();
}

/**
 * Save tags for the current document
 */
function saveDocumentTags() {
  if (!currentDocumentId) return;
  
  const tagsInput = document.getElementById('editDocumentTags');
  if (!tagsInput) return;
  
  // Parse tags
  const tags = tagsInput.value.split(',')
    .map(tag => tag.trim())
    .filter(tag => tag.length > 0);
  
  // Make API request
  fetch(`/api/documents/${currentDocumentId}/tag`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ tags })
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Hide the modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addTagsModal'));
        if (modal) {
          modal.hide();
        }
        
        // Reload document preview and list
        previewDocument(currentDocumentId);
        loadDocuments();
      } else {
        alert(`Error saving tags: ${data.error || 'Unknown error'}`);
      }
    })
    .catch(error => {
      console.error('Error saving tags:', error);
      alert(`Error saving tags: ${error.message || 'Network error'}`);
    });
}

/**
 * Show delete confirmation modal
 * @param {string} documentId - ID of the document to delete
 */
function showDeleteConfirmation(documentId) {
  if (!documentId) return;
  
  // Get document info
  const document = documents.find(doc => doc.id === documentId);
  const deleteDocumentName = document.getElementById('deleteDocumentName');
  
  if (document && deleteDocumentName) {
    deleteDocumentName.textContent = document.filename;
  }
  
  // Show the modal
  const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
  modal.show();
}

/**
 * Delete the current document
 */
function deleteDocument() {
  if (!currentDocumentId) return;
  
  // Make API request
  fetch(`/api/documents/${currentDocumentId}/delete`, {
    method: 'POST'
  })
    .then(response => response.json())
    .then(data => {
      // Hide the modals
      const previewModal = bootstrap.Modal.getInstance(document.getElementById('documentPreviewModal'));
      const deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal'));
      
      if (previewModal) previewModal.hide();
      if (deleteModal) deleteModal.hide();
      
      if (data.success) {
        // Reload documents and stats
        loadDocuments();
        loadDocumentStats();
      } else {
        alert(`Error deleting document: ${data.error || 'Unknown error'}`);
      }
    })
    .catch(error => {
      console.error('Error deleting document:', error);
      alert(`Error deleting document: ${error.message || 'Network error'}`);
    });
}

/**
 * Format file size in human-readable form
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
