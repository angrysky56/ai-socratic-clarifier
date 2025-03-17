/**
 * AI-Socratic-Clarifier Chat Interface
 * JavaScript for the enhanced chat interface with document RAG integration
 */

document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const chatMessages = document.getElementById('chatMessages');
    const typingIndicator = document.getElementById('typingIndicator');
    const modeSelect = document.getElementById('modeSelect');
    const showAnalysisSwitch = document.getElementById('showAnalysisSwitch');
    const useSoTSwitch = document.getElementById('useSoTSwitch');
    const useRAGSwitch = document.getElementById('useRAGSwitch');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const attachDocumentBtn = document.getElementById('attachDocumentBtn');
    const documentContext = document.getElementById('documentContext');
    const documentChips = document.getElementById('documentChips');
    const viewDocumentsBtn = document.getElementById('viewDocumentsBtn');
    
    // Context drawer elements
    const contextDrawer = document.getElementById('contextDrawer');
    const contextDrawerBackdrop = document.getElementById('contextDrawerBackdrop');
    const closeContextDrawer = document.getElementById('closeContextDrawer');
    const documentList = document.getElementById('documentList');
    const selectedDocuments = document.getElementById('selectedDocuments');
    const applyContextBtn = document.getElementById('applyContextBtn');
    const uploadDocumentBtn = document.getElementById('uploadDocumentBtn');
    
    // Upload modal elements
    const uploadDocumentModal = new bootstrap.Modal(document.getElementById('uploadDocumentModal'));
    const uploadDocumentForm = document.getElementById('uploadDocumentForm');
    const documentFile = document.getElementById('documentFile');
    const generateEmbeddingsCheck = document.getElementById('generateEmbeddingsCheck');
    const uploadDocumentSubmit = document.getElementById('uploadDocumentSubmit');
    const uploadProgress = document.querySelector('.upload-progress');
    const progressBar = document.querySelector('.progress-bar');
    const uploadStatus = document.getElementById('uploadStatus');
    
    // Store the active documents
    let activeDocuments = [];
    let allDocuments = [];

    // Check for redirected text from dashboard
    const chatRedirectText = sessionStorage.getItem('chatRedirectText');
    const chatRedirectQuestions = JSON.parse(sessionStorage.getItem('chatRedirectQuestions') || '[]');
    
    if (chatRedirectText) {
        // Add the text to the input
        messageInput.value = chatRedirectText;
        
        // Clear the session storage
        sessionStorage.removeItem('chatRedirectText');
        sessionStorage.removeItem('chatRedirectQuestions');
        
        // If there are questions, add a system message about them
        if (chatRedirectQuestions && chatRedirectQuestions.length > 0) {
            addSystemMessage(`Transferred from dashboard analysis with ${chatRedirectQuestions.length} related questions.`);
            
            // Add first question as assistant message
            addMessage(
                `I see you're exploring: "${chatRedirectText}". ${chatRedirectQuestions[0]}`, 
                'assistant', 
                { 
                    questions: chatRedirectQuestions,
                    redirected: true
                }
            );
        }
    }
    
    // Event listener for send button
    sendButton.addEventListener('click', sendMessage);
    
    // Event listener for enter key
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Clear chat button
    clearChatBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Keep only the first welcome message
            while (chatMessages.childNodes.length > 1) {
                chatMessages.removeChild(chatMessages.lastChild);
            }
            
            // Clear any active documents
            activeDocuments = [];
            documentContext.classList.add('d-none');
            documentChips.innerHTML = '';
        }
    });
    
    // Attach document button
    attachDocumentBtn.addEventListener('click', function() {
        // Open the context drawer
        openContextDrawer();
        
        // Load the document list
        loadDocuments();
    });
    
    // View documents button
    viewDocumentsBtn.addEventListener('click', function() {
        openContextDrawer();
        loadDocuments();
    });
    
    // Context drawer close button
    closeContextDrawer.addEventListener('click', closeContextDrawer);
    
    // Context drawer backdrop
    contextDrawerBackdrop.addEventListener('click', closeContextDrawer);
    
    // Apply context button
    applyContextBtn.addEventListener('click', function() {
        // Get selected documents
        const selectedDocs = [...document.querySelectorAll('.document-select:checked')].map(checkbox => {
            const docId = checkbox.value;
            const doc = allDocuments.find(d => d.id === docId);
            return doc;
        });
        
        // Update active documents
        activeDocuments = selectedDocs;
        
        // Update UI
        updateDocumentContext();
        
        // Close the drawer
        closeContextDrawer();
    });
    
    // Upload document button
    uploadDocumentBtn.addEventListener('click', function() {
        // Open the upload modal
        uploadDocumentModal.show();
        
        // Reset the form
        uploadDocumentForm.reset();
        uploadProgress.classList.add('d-none');
        progressBar.style.width = '0%';
    });
    
    // Upload document submit
    uploadDocumentSubmit.addEventListener('click', function() {
        const file = documentFile.files[0];
        if (!file) {
            alert('Please select a file to upload.');
            return;
        }
        
        // Show progress
        uploadProgress.classList.remove('d-none');
        uploadDocumentSubmit.disabled = true;
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('generate_embeddings', generateEmbeddingsCheck.checked ? '1' : '0');
        
        // Upload the file
        fetch('/api/documents/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                uploadStatus.textContent = 'Upload successful!';
                progressBar.style.width = '100%';
                
                // Wait a moment and close the modal
                setTimeout(() => {
                    uploadDocumentModal.hide();
                    uploadDocumentSubmit.disabled = false;
                    
                    // Reload the document list
                    loadDocuments();
                }, 1000);
            } else {
                uploadStatus.textContent = `Error: ${data.error}`;
                progressBar.style.width = '100%';
                progressBar.classList.remove('bg-primary');
                progressBar.classList.add('bg-danger');
                
                // Re-enable the submit button
                uploadDocumentSubmit.disabled = false;
            }
        })
        .catch(error => {
            uploadStatus.textContent = `Error: ${error.message}`;
            progressBar.style.width = '100%';
            progressBar.classList.remove('bg-primary');
            progressBar.classList.add('bg-danger');
            
            // Re-enable the submit button
            uploadDocumentSubmit.disabled = false;
        });
    });
    
    // Function to open context drawer
    function openContextDrawer() {
        contextDrawer.classList.add('open');
        contextDrawerBackdrop.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
    
    // Function to close context drawer
    function closeContextDrawer() {
        contextDrawer.classList.remove('open');
        contextDrawerBackdrop.classList.remove('open');
        document.body.style.overflow = '';
    }
    
    // Function to load documents
    function loadDocuments() {
        documentList.innerHTML = '<div class="placeholder-text text-muted">Loading documents...</div>';
        
        fetch('/api/documents')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    allDocuments = data.documents;
                    
                    if (data.documents.length === 0) {
                        documentList.innerHTML = '<div class="placeholder-text text-muted">No documents available</div>';
                    } else {
                        documentList.innerHTML = '';
                        
                        // Create document list items
                        data.documents.forEach(doc => {
                            const docItem = document.createElement('div');
                            docItem.className = 'document-preview';
                            
                            // Determine if this document is active
                            const isActive = activeDocuments.some(d => d.id === doc.id);
                            
                            // Create document HTML
                            docItem.innerHTML = `
                                <div class="document-preview-header">
                                    <div class="form-check">
                                        <input class="form-check-input document-select" type="checkbox" value="${doc.id}" id="doc-${doc.id}" ${isActive ? 'checked' : ''}>
                                        <label class="form-check-label" for="doc-${doc.id}">
                                            ${doc.filename}
                                        </label>
                                    </div>
                                    <span class="badge bg-secondary">${formatSize(doc.file_size)}</span>
                                </div>
                                <div class="text-muted small mb-2">
                                    Uploaded: ${formatDate(doc.upload_date)}
                                </div>
                            `;
                            
                            documentList.appendChild(docItem);
                            
                            // Add a preview button to fetch the document content
                            const previewBtn = document.createElement('button');
                            previewBtn.className = 'btn btn-sm btn-outline-secondary w-100';
                            previewBtn.innerHTML = '<i class="bi bi-eye"></i> Preview Document';
                            previewBtn.addEventListener('click', () => {
                                previewDocument(doc.id);
                            });
                            docItem.appendChild(previewBtn);
                        });
                        
                        // Update selected documents display
                        updateSelectedDocuments();
                    }
                } else {
                    documentList.innerHTML = `<div class="alert alert-danger">Error loading documents: ${data.error}</div>`;
                }
            })
            .catch(error => {
                documentList.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
            });
    }
    
    // Function to preview document
    function previewDocument(docId) {
        fetch(`/api/documents/${docId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const doc = data.document;
                    const docItem = document.getElementById(`doc-${docId}`).closest('.document-preview');
                    
                    // Check if preview already exists
                    const existingPreview = docItem.querySelector('.document-preview-content');
                    if (existingPreview) {
                        existingPreview.remove();
                        return;
                    }
                    
                    // Create preview content
                    const previewContent = document.createElement('div');
                    previewContent.className = 'document-preview-content mt-2';
                    previewContent.textContent = doc.text_content.substring(0, 500) + 
                        (doc.text_content.length > 500 ? '...' : '');
                    
                    docItem.appendChild(previewContent);
                } else {
                    alert(`Error loading document: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`Error: ${error.message}`);
            });
    }
    
    // Function to update selected documents display
    function updateSelectedDocuments() {
        const selectedDocs = [...document.querySelectorAll('.document-select:checked')].map(checkbox => {
            const docId = checkbox.value;
            const doc = allDocuments.find(d => d.id === docId);
            return doc;
        });
        
        if (selectedDocs.length === 0) {
            selectedDocuments.innerHTML = '<div class="placeholder-text text-muted">No documents selected</div>';
        } else {
            selectedDocuments.innerHTML = '';
            
            selectedDocs.forEach(doc => {
                const docItem = document.createElement('div');
                docItem.className = 'document-chip';
                docItem.innerHTML = `
                    <i class="bi bi-file-earmark-text"></i> ${doc.filename}
                `;
                selectedDocuments.appendChild(docItem);
            });
        }
    }
    
    // Listen for changes to document selection
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('document-select')) {
            updateSelectedDocuments();
        }
    });
    
    // Function to update document context display
    function updateDocumentContext() {
        if (activeDocuments.length === 0) {
            documentContext.classList.add('d-none');
            documentChips.innerHTML = '';
        } else {
            documentContext.classList.remove('d-none');
            documentChips.innerHTML = '';
            
            activeDocuments.forEach(doc => {
                const chip = document.createElement('div');
                chip.className = 'document-chip';
                chip.innerHTML = `
                    <i class="bi bi-file-earmark-text"></i> ${doc.filename}
                `;
                
                // Add remove button
                const removeBtn = document.createElement('i');
                removeBtn.className = 'bi bi-x ms-1';
                removeBtn.style.cursor = 'pointer';
                removeBtn.addEventListener('click', () => {
                    // Remove document from active list
                    activeDocuments = activeDocuments.filter(d => d.id !== doc.id);
                    updateDocumentContext();
                });
                chip.appendChild(removeBtn);
                
                documentChips.appendChild(chip);
            });
        }
    }
    
    function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        messageInput.value = '';
        
        // Show typing indicator
        typingIndicator.classList.remove('d-none');
        
        // Get current settings
        const mode = modeSelect.value;
        const showAnalysis = showAnalysisSwitch.checked;
        const useSoT = useSoTSwitch.checked;
        const useRAG = useRAGSwitch.checked;
        
        // Prepare document context if RAG is enabled
        let documentContext = [];
        if (useRAG && activeDocuments.length > 0) {
            documentContext = activeDocuments.map(doc => ({
                document_id: doc.id,
                filename: doc.filename
            }));
        }
        
        // Make API request to analyze
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                mode: mode,
                use_sot: useSoT,
                use_rag: useRAG,
                document_context: documentContext
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            typingIndicator.classList.add('d-none');
            
            if (data.error) {
                addErrorMessage(data.error);
                return;
            }
            
            // Add assistant's response
            addMessage(data.reply, 'assistant', showAnalysis ? data : null);
            
            // Update model info
            document.getElementById('currentLLM').textContent = data.model || 'Unknown';
            document.getElementById('sotEnabled').textContent = data.sot_enabled ? 'Yes' : 'No';
            document.getElementById('providerName').textContent = data.provider || 'None';
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        })
        .catch(error => {
            typingIndicator.classList.add('d-none');
            addErrorMessage('An error occurred while processing your message: ' + error.message);
        });
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function addMessage(text, sender, analysisData = null) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        // Main message text
        const textElement = document.createElement('div');
        textElement.textContent = text;
        messageElement.appendChild(textElement);
        
        // If it's an assistant message and we have analysis data, add it
        if (sender === 'assistant' && analysisData) {
            // Issues section
            if (analysisData.issues && analysisData.issues.length > 0) {
                const issuesElement = document.createElement('div');
                issuesElement.className = 'message-issues';
                
                const issuesTitle = document.createElement('strong');
                issuesTitle.textContent = 'Detected Issues:';
                issuesElement.appendChild(issuesTitle);
                
                const issuesList = document.createElement('ul');
                issuesList.className = 'mb-0 mt-1';
                
                analysisData.issues.forEach(issue => {
                    const issueItem = document.createElement('li');
                    issueItem.innerHTML = `<strong>${issue.issue}:</strong> "${issue.term}" - ${issue.description}`;
                    issuesList.appendChild(issueItem);
                });
                
                issuesElement.appendChild(issuesList);
                messageElement.appendChild(issuesElement);
            }
            
            // Questions section
            if (analysisData.questions && analysisData.questions.length > 0) {
                const questionsElement = document.createElement('div');
                questionsElement.className = 'message-questions';
                
                const questionsTitle = document.createElement('strong');
                questionsTitle.textContent = 'Socratic Questions:';
                questionsElement.appendChild(questionsTitle);
                
                const questionsList = document.createElement('ul');
                questionsList.className = 'mb-0 mt-1';
                
                analysisData.questions.forEach(question => {
                    const questionItem = document.createElement('li');
                    
                    // Create question text and "use this" button for follow-up
                    const questionText = document.createElement('span');
                    questionText.textContent = question;
                    questionItem.appendChild(questionText);
                    
                    // Add a "use this" button to use the question as a response
                    if (!analysisData.redirected) {
                        const useButton = document.createElement('button');
                        useButton.className = 'question-use-btn';
                        useButton.innerHTML = '<i class="bi bi-chat-left-text"></i> Use';
                        useButton.addEventListener('click', function() {
                            messageInput.value = question;
                            messageInput.focus();
                        });
                        questionItem.appendChild(useButton);
                    }
                    
                    questionsList.appendChild(questionItem);
                });
                
                questionsElement.appendChild(questionsList);
                messageElement.appendChild(questionsElement);
            }
            
            // Reasoning section
            if (analysisData.reasoning) {
                const reasoningElement = document.createElement('div');
                reasoningElement.className = 'message-reasoning';
                
                const reasoningTitle = document.createElement('strong');
                reasoningTitle.textContent = `SoT Reasoning (${analysisData.sot_paradigm || 'default'}):`;
                reasoningElement.appendChild(reasoningTitle);
                
                const reasoningText = document.createElement('pre');
                reasoningText.className = 'mb-0 mt-1';
                reasoningText.textContent = analysisData.reasoning;
                
                reasoningElement.appendChild(reasoningText);
                messageElement.appendChild(reasoningElement);
            }
            
            // Document context section
            if (analysisData.document_context && analysisData.document_context.length > 0) {
                const documentElement = document.createElement('div');
                documentElement.className = 'message-document';
                
                const documentTitle = document.createElement('strong');
                documentTitle.textContent = 'Document Context Used:';
                documentElement.appendChild(documentTitle);
                
                const documentList = document.createElement('ul');
                documentList.className = 'mb-0 mt-1';
                
                analysisData.document_context.forEach(doc => {
                    const documentItem = document.createElement('li');
                    documentItem.innerHTML = `<strong>${doc.filename}</strong> - Relevance: ${(doc.relevance * 100).toFixed(0)}%`;
                    documentList.appendChild(documentItem);
                });
                
                documentElement.appendChild(documentList);
                messageElement.appendChild(documentElement);
            }
        }
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function addSystemMessage(text) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message system-message';
        messageElement.textContent = text;
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function addErrorMessage(text) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message assistant-message';
        messageElement.style.backgroundColor = '#f8d7da';
        messageElement.textContent = 'Error: ' + text;
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Helper function to format file size
    function formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
    
    // Helper function to format date
    function formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
});
