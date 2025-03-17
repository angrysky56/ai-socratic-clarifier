/**
 * Integrated UI JavaScript
 * 
 * This file handles all the JavaScript functionality for the integrated UI
 * combining chat, analysis, reflection, multimodal, and settings features.
 */

// API endpoint mapping
const API_ENDPOINTS = {
    chat: '/api/chat',
    analyze: '/analyze',
    reflection: '/api/reflective/analyze',
    feedback: '/api/reflective/feedback',
    status: '/api/reflective/status',
    multimodal: '/api/multimodal/process',
};

// Handles integrating all UI components
class IntegratedUI {
    constructor() {
        this.initializeEventListeners();
        this.loadSettings();
        this.initializeResonanceVisualizer();
        
        // Initialize document RAG context indicator
        this.updateDocumentContextIndicator();
        
        // Check reflective ecosystem status
        this.getReflectiveStatus();
        
        // Initialize visualizers if available
        if (window.sreVisualizer) {
            window.sreVisualizer.initialize();
        }
        
        if (window.documentManager) {
            window.documentManager.initialize();
        }
    }
    
    // Set up all event listeners
    initializeEventListeners() {
        // Navigation tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.getAttribute('data-tab');
                this.setActiveTab(tabId);
            });
        });
        
        // Sidebar tabs
        document.querySelectorAll('.sidebar-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.getAttribute('data-sidebar-tab');
                this.setActiveSidebarTab(tabId);
            });
        });
        
        // Chat functionality
        const sendButton = document.getElementById('sendButton');
        const messageInput = document.getElementById('messageInput');
        
        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        if (messageInput) {
            messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        // View context button
        const viewContextBtn = document.getElementById('viewContextBtn');
        if (viewContextBtn) {
            viewContextBtn.addEventListener('click', () => {
                this.setActiveSidebarTab('documents');
            });
        }
        
        // Clear chat button
        const clearChatBtn = document.getElementById('clearChatBtn');
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => this.clearChat());
        }
        
        // Analysis functionality
        const analyzeButton = document.getElementById('analyzeButton');
        if (analyzeButton) {
            analyzeButton.addEventListener('click', () => this.analyzeText());
        }
        
        // Reflection functionality
        const reflectButton = document.getElementById('reflectButton');
        const resonanceLevel = document.getElementById('resonanceLevel');
        
        if (reflectButton) {
            reflectButton.addEventListener('click', () => {
                const text = document.getElementById('reflectionInput')?.value.trim();
                if (!text) {
                    alert('Please enter some text to analyze with resonance-based reflection.');
                    return;
                }
                
                const mode = document.getElementById('reflectionMode')?.value;
                const resonance = parseFloat(document.getElementById('resonanceLevel')?.value || '1.0');
                this.analyzeWithReflection(text, mode, resonance);
            });
        }
        
        if (resonanceLevel) {
            resonanceLevel.addEventListener('input', () => {
                const value = parseFloat(resonanceLevel.value);
                document.getElementById('resonanceValue').textContent = value.toFixed(1);
                document.querySelector('.resonance-info').textContent = `Global Resonance: ${value.toFixed(1)}`;
                this.updateResonanceVisualizer(value);
            });
        }
        
        // Multimodal functionality
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const processButton = document.getElementById('processButton');
        const copyButton = document.getElementById('copyButton');
        const sendToChatButton = document.getElementById('sendToChatButton');
        
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });
            
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('border-primary');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('border-primary');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('border-primary');
                
                if (e.dataTransfer.files.length > 0) {
                    fileInput.files = e.dataTransfer.files;
                    this.handleFileSelect();
                }
            });
            
            fileInput.addEventListener('change', () => this.handleFileSelect());
        }
        
        if (processButton) {
            processButton.addEventListener('click', () => this.processDocument());
        }
        
        if (copyButton) {
            copyButton.addEventListener('click', () => {
                const extractedText = document.getElementById('textOutput')?.textContent;
                if (extractedText) {
                    navigator.clipboard.writeText(extractedText).then(() => {
                        const originalText = copyButton.innerHTML;
                        copyButton.innerHTML = '<i class="bi bi-check"></i> Copied!';
                        setTimeout(() => {
                            copyButton.innerHTML = originalText;
                        }, 2000);
                    });
                }
            });
        }
        
        if (sendToChatButton) {
            sendToChatButton.addEventListener('click', () => {
                const extractedText = document.getElementById('textOutput')?.textContent;
                if (extractedText) {
                    this.setActiveTab('chat-tab');
                    document.getElementById('messageInput').value = extractedText;
                    document.getElementById('messageInput').focus();
                }
            });
        }
        
        // Settings changes
        const settingsElements = [
            'modeSelect', 'showAnalysisSwitch', 'useSoTSwitch', 
            'useRAGSwitch', 'useSRESwitch'
        ];
        
        settingsElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', () => {
                    if (id === 'useRAGSwitch') {
                        this.updateDocumentContextIndicator();
                    }
                    if (id === 'useSRESwitch') {
                        this.updateSREVisibility();
                    }
                    this.saveSettings();
                });
            }
        });
        
        // Save detector settings
        const saveDetectorBtn = document.getElementById('saveDetectorSettings');
        if (saveDetectorBtn) {
            saveDetectorBtn.addEventListener('click', () => this.saveDetectorSettings());
        }
    }
    
    // Tab navigation
    setActiveTab(tabId) {
        // Update tab buttons
        document.querySelectorAll('.nav-tab').forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
        
        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            if (panel.id === tabId) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });
    }
    
    setActiveSidebarTab(tabId) {
        // Update sidebar tab buttons
        document.querySelectorAll('.sidebar-tab').forEach(tab => {
            if (tab.getAttribute('data-sidebar-tab') === tabId) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
        
        // Update sidebar panes
        document.querySelectorAll('.sidebar-pane').forEach(pane => {
            if (pane.id === `${tabId}-pane`) {
                pane.classList.add('active');
            } else {
                pane.classList.remove('active');
            }
        });
    }
    
    // Chat functionality
    sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        const chatMessages = document.getElementById('chatMessages');
        const typingIndicator = document.getElementById('typingIndicator');
        const sendButton = document.getElementById('sendButton');
        
        if (!message || this.isWaitingForResponse) return;
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Clear input
        messageInput.value = '';
        
        // Show typing indicator
        typingIndicator.classList.remove('d-none');
        
        // Set waiting state
        this.isWaitingForResponse = true;
        sendButton.disabled = true;
        
        // Get settings
        const modeSelect = document.getElementById('modeSelect');
        const useSoTSwitch = document.getElementById('useSoTSwitch');
        const useRAGSwitch = document.getElementById('useRAGSwitch');
        const useSRESwitch = document.getElementById('useSRESwitch');
        
        const mode = modeSelect.value;
        const useSoT = useSoTSwitch.checked;
        const useRAG = useRAGSwitch.checked;
        const useSRE = useSRESwitch.checked;
        
        // Get document context if RAG is enabled
        let documentContext = [];
        if (useRAG && window.documentManager) {
            documentContext = window.documentManager.getSelectedDocumentsForRag();
        }
        
        // Send to backend
        fetch(API_ENDPOINTS.chat, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                mode: mode,
                use_sot: useSoT,
                use_sre: useSRE,
                use_rag: useRAG,
                document_context: documentContext
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            typingIndicator.classList.add('d-none');
            
            // Reset waiting state
            this.isWaitingForResponse = false;
            sendButton.disabled = false;
            
            // Add response to chat
            this.addMessage('assistant', data.reply, data);
            
            // Update the analysis and questions sidebars
            this.updateAnalysisSidebar(data);
            this.updateQuestionsSidebar(data);
            
            // Update SRE visualization if available
            if (useSRE && window.sreVisualizer) {
                const sreData = {
                    metrics: {
                        truth_value: data.advancement?.truth_value || 0.7,
                        scrutiny_value: data.advancement?.scrutiny_value || 0.4,
                        improvement_value: data.advancement?.improvement_value || 0.6,
                        advancement: data.advancement?.advancement || 0.68,
                        global_coherence: data.global_coherence || 0.82
                    },
                    paradigm: data.sot_paradigm || mode,
                    reasoning_paths: data.reasoning_paths || [],
                    meta_meta_stage: data.meta_meta_stage || 'stageWhy'
                };
                
                window.sreVisualizer.updateVisualization(sreData);
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            
            // Hide typing indicator
            typingIndicator.classList.add('d-none');
            
            // Reset waiting state
            this.isWaitingForResponse = false;
            sendButton.disabled = false;
            
            // Add error message
            this.addMessage('system', `Error: ${error.message}`);
        });
    }
    
    addMessage(role, content, data = null) {
        const showAnalysisSwitch = document.getElementById('showAnalysisSwitch');
        const chatMessages = document.getElementById('chatMessages');
        
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = `message ${role}-message`;
        
        // Add content
        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        contentEl.textContent = content;
        messageEl.appendChild(contentEl);
        
        // Add metadata if available
        if (role === 'assistant' && data) {
            const metadataEl = document.createElement('div');
            metadataEl.className = 'message-metadata';
            metadataEl.textContent = `Model: ${data.model || 'Unknown'} | Mode: ${data.sot_paradigm || 'standard'}`;
            messageEl.appendChild(metadataEl);
        }
        
        // If assistant message and we have analysis data and showing analysis
        if (role === 'assistant' && data && showAnalysisSwitch.checked) {
            // If we have issues
            if (data.issues && data.issues.length > 0) {
                const issuesEl = document.createElement('div');
                issuesEl.className = 'message-issues';
                
                const issuesTitle = document.createElement('h6');
                issuesTitle.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Detected Issues:';
                issuesEl.appendChild(issuesTitle);
                
                const issuesList = document.createElement('ul');
                issuesList.className = 'mb-0';
                
                data.issues.forEach(issue => {
                    const issueItem = document.createElement('li');
                    issueItem.innerHTML = `<strong>${issue.issue}:</strong> "${issue.term}" - ${issue.description}`;
                    issuesList.appendChild(issueItem);
                });
                
                issuesEl.appendChild(issuesList);
                messageEl.appendChild(issuesEl);
            }
            
            // If we have questions
            if (data.questions && data.questions.length > 0) {
                const questionsEl = document.createElement('div');
                questionsEl.className = 'message-questions';
                
                const questionsTitle = document.createElement('h6');
                questionsTitle.innerHTML = '<i class="bi bi-question-circle"></i> Socratic Questions:';
                questionsEl.appendChild(questionsTitle);
                
                const questionsList = document.createElement('ul');
                questionsList.className = 'mb-0';
                
                data.questions.forEach(question => {
                    const questionItem = document.createElement('li');
                    questionItem.textContent = question;
                    questionsList.appendChild(questionItem);
                });
                
                questionsEl.appendChild(questionsList);
                messageEl.appendChild(questionsEl);
            }
            
            // If we have reasoning
            if (data.reasoning) {
                const reasoningEl = document.createElement('div');
                reasoningEl.className = 'message-reasoning';
                
                const reasoningTitle = document.createElement('h6');
                reasoningTitle.innerHTML = `<i class="bi bi-diagram-3"></i> Reasoning (${data.sot_paradigm || 'standard'}):`;
                reasoningEl.appendChild(reasoningTitle);
                
                const reasoningContent = document.createElement('pre');
                reasoningContent.textContent = data.reasoning;
                reasoningEl.appendChild(reasoningContent);
                
                messageEl.appendChild(reasoningEl);
            }
            
            // If we have document context
            if (data.document_context && data.document_context.length > 0) {
                const documentEl = document.createElement('div');
                documentEl.className = 'message-document';
                
                const documentTitle = document.createElement('h6');
                documentTitle.innerHTML = '<i class="bi bi-files"></i> Document Context:';
                documentEl.appendChild(documentTitle);
                
                data.document_context.forEach(doc => {
                    const docEl = document.createElement('div');
                    docEl.className = 'mb-2';
                    
                    const docHeader = document.createElement('div');
                    docHeader.className = 'document-header';
                    docHeader.innerHTML = `<strong>${doc.filename}</strong> <span class="text-muted">(relevance: ${(doc.relevance * 100).toFixed(0)}%)</span>`;
                    docEl.appendChild(docHeader);
                    
                    if (doc.content) {
                        const docContent = document.createElement('div');
                        docContent.className = 'document-content small';
                        docContent.textContent = doc.content.substring(0, 200) + (doc.content.length > 200 ? '...' : '');
                        docEl.appendChild(docContent);
                    }
                    
                    documentEl.appendChild(docEl);
                });
                
                messageEl.appendChild(documentEl);
            }
        }
        
        // Add to chat
        chatMessages.appendChild(messageEl);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Save to history
        this.chatHistory = this.chatHistory || [];
        this.chatHistory.push({
            role: role,
            content: content,
            data: data
        });
    }
    
    clearChat() {
        // Confirm
        if (!confirm('Are you sure you want to clear the chat history?')) {
            return;
        }
        
        const chatMessages = document.getElementById('chatMessages');
        
        // Clear chat messages
        chatMessages.innerHTML = '';
        
        // Add welcome message
        this.addMessage('assistant', 'Hello! I\'m the Socratic Clarifier with integrated capabilities including document context, reflection, and multimodal analysis. How can I assist you today?');
        
        // Clear history
        this.chatHistory = [];
    }
    
    // Analysis functionality
    analyzeText() {
        const analysisInput = document.getElementById('analysisInput');
        const text = analysisInput.value.trim();
        const analyzeButton = document.getElementById('analyzeButton');
        const analysisResults = document.getElementById('analysisResults');
        const analysisIssues = document.getElementById('analysisIssues');
        const analysisQuestions = document.getElementById('analysisQuestions');
        const analysisReasoning = document.getElementById('analysisReasoning');
        
        if (!text) {
            alert('Please enter some text to analyze.');
            return;
        }
        
        // Show loading state
        analyzeButton.disabled = true;
        analyzeButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
        
        // Get settings
        const analysisMode = document.getElementById('analysisMode');
        const mode = analysisMode.value;
        const useSoT = true; // Always use SoT for analysis
        const useRAG = window.documentManager && window.documentManager.getSelectedDocumentsForRag().length > 0;
        
        // Get document context if RAG is enabled
        let documentContext = [];
        if (useRAG && window.documentManager) {
            documentContext = window.documentManager.getSelectedDocumentsForRag();
        }
        
        // Call API
        fetch(API_ENDPOINTS.analyze, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                mode: mode,
                use_sot: useSoT,
                use_rag: useRAG,
                document_context: documentContext
            })
        })
        .then(response => response.json())
        .then(data => {
            // Reset button
            analyzeButton.disabled = false;
            analyzeButton.innerHTML = '<i class="bi bi-search"></i> Analyze';
            
            // Store the results
            this.lastAnalysisResults = data;
            
            // Display the results
            this.displayAnalysisResults(data);
            
            // Update the analysis and questions sidebars
            this.updateAnalysisSidebar(data);
            this.updateQuestionsSidebar(data);
        })
        .catch(error => {
            console.error('Error analyzing text:', error);
            
            // Reset button
            analyzeButton.disabled = false;
            analyzeButton.innerHTML = '<i class="bi bi-search"></i> Analyze';
            
            // Show error
            alert(`Error analyzing text: ${error.message}`);
        });
    }
    
    displayAnalysisResults(data) {
        const analysisResults = document.getElementById('analysisResults');
        const analysisIssues = document.getElementById('analysisIssues');
        const analysisQuestions = document.getElementById('analysisQuestions');
        const analysisReasoning = document.getElementById('analysisReasoning');
        
        // Show results container
        analysisResults.classList.remove('d-none');
        
        // Display issues
        analysisIssues.innerHTML = '';
        if (data.issues && data.issues.length > 0) {
            const issuesHtml = data.issues.map(issue => `
                <div class="card mb-3">
                    <div class="card-body">
                        <h6 class="card-title">${issue.issue}: "${issue.term}"</h6>
                        <p class="card-text">${issue.description}</p>
                        <div class="text-end">
                            <span class="badge bg-info text-dark">${Math.round(issue.confidence * 100)}% confidence</span>
                        </div>
                    </div>
                </div>
            `).join('');
            
            analysisIssues.innerHTML = issuesHtml;
        } else {
            analysisIssues.innerHTML = '<div class="alert alert-success">No issues detected in the text.</div>';
        }
        
        // Display questions
        analysisQuestions.innerHTML = '';
        if (data.questions && data.questions.length > 0) {
            const questionsHtml = data.questions.map(question => `
                <div class="alert alert-info">
                    <i class="bi bi-question-circle me-2"></i> ${question}
                </div>
            `).join('');
            
            analysisQuestions.innerHTML = questionsHtml;
        } else {
            analysisQuestions.innerHTML = '<div class="alert alert-warning">No questions generated for this text.</div>';
        }
        
        // Display reasoning
        if (data.reasoning && data.reasoning.trim()) {
            analysisReasoning.textContent = data.reasoning;
        } else {
            analysisReasoning.textContent = 'No detailed reasoning available for this analysis.';
        }
    }
    
    updateAnalysisSidebar(data) {
        const analysisList = document.getElementById('analysisList');
        
        // Skip if there is no data
        if (!data || !data.issues || data.issues.length === 0) return;
        
        // Get the text snippet to display
        const textSnippet = data.text ? 
            (data.text.length > 50 ? data.text.substring(0, 50) + '...' : data.text) : 
            'Analysis';
        
        // Create analysis item
        const analysisItem = document.createElement('div');
        analysisItem.className = 'analysis-item';
        analysisItem.innerHTML = `
            <div class="analysis-item-title">${textSnippet}</div>
            <div class="analysis-item-subtitle">${data.issues.length} issue(s) detected • ${data.sot_paradigm || 'standard'} mode</div>
        `;
        
        // Add click handler to show analysis tab with this data
        analysisItem.addEventListener('click', () => {
            this.setActiveTab('analysis-tab');
            document.getElementById('analysisInput').value = data.text || '';
            this.lastAnalysisResults = data;
            this.displayAnalysisResults(data);
        });
        
        // Add to the list (at the beginning)
        if (analysisList.querySelector('.alert')) {
            analysisList.innerHTML = '';
        }
        
        analysisList.insertBefore(analysisItem, analysisList.firstChild);
        
        // Limit the number of items (keep last 5)
        const items = analysisList.querySelectorAll('.analysis-item');
        if (items.length > 5) {
            analysisList.removeChild(items[items.length - 1]);
        }
    }
    
    updateQuestionsSidebar(data) {
        const questionsList = document.getElementById('questionsList');
        
        // Skip if there are no questions
        if (!data || !data.questions || data.questions.length === 0) return;
        
        // Create question items
        data.questions.forEach(question => {
            const questionItem = document.createElement('div');
            questionItem.className = 'question-item';
            questionItem.textContent = question;
            
            // Add click handler to insert this question into the chat input
            questionItem.addEventListener('click', () => {
                this.setActiveTab('chat-tab');
                document.getElementById('messageInput').value = question;
                document.getElementById('messageInput').focus();
            });
            
            // Add to the list (at the beginning)
            if (questionsList.querySelector('.alert')) {
                questionsList.innerHTML = '';
            }
            
            questionsList.insertBefore(questionItem, questionsList.firstChild);
        });
        
        // Limit the number of items (keep last 10)
        const items = questionsList.querySelectorAll('.question-item');
        if (items.length > 10) {
            for (let i = 10; i < items.length; i++) {
                questionsList.removeChild(items[i]);
            }
        }
    }
    
    // Reflection functionality
    analyzeWithReflection(text, mode, resonance) {
        const reflectButton = document.getElementById('reflectButton');
        const reflectionResults = document.getElementById('reflectionResults');
        
        // Show loading
        reflectButton.disabled = true;
        reflectButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Analyzing...';
        reflectionResults.classList.add('d-none');
        
        // Call API
        fetch(API_ENDPOINTS.reflection, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                mode: mode,
                use_sot: true,
                resonance: resonance
            })
        })
        .then(response => response.json())
        .then(data => {
            // Reset button
            reflectButton.disabled = false;
            reflectButton.innerHTML = '<i class="bi bi-diagram-3"></i> Analyze with Reflective Ecosystem';
            
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            // Display reflection results
            this.displayReflectionResults(data, text, resonance);
            
            // Update the analysis and questions sidebars
            this.updateAnalysisSidebar(data);
            this.updateQuestionsSidebar(data);
        })
        .catch(error => {
            console.error('Error analyzing with reflection:', error);
            
            // Reset button
            reflectButton.disabled = false;
            reflectButton.innerHTML = '<i class="bi bi-diagram-3"></i> Analyze with Reflective Ecosystem';
            
            // Show error
            alert(`Error analyzing with reflection: ${error.message}`);
        });
    }
    
    displayReflectionResults(data, text, globalResonance) {
        const reflectionResults = document.getElementById('reflectionResults');
        
        // Prepare the HTML
        let html = `
            <div class="card mb-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Resonance-Enhanced Analysis</h5>
                    <span class="badge bg-primary">Resonance: ${globalResonance.toFixed(1)}</span>
                </div>
                <div class="card-body">
                    <p>Original text: <strong>${text}</strong></p>
                    <div class="row">
        `;
        
        // Issues section
        html += `
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Detected Issues</h5>
                        <span class="badge bg-primary">Resonance: ${globalResonance.toFixed(1)}</span>
                    </div>
                    <div class="card-body">
        `;
        
        if (data.issues && data.issues.length > 0) {
            data.issues.forEach(issue => {
                let badgeClass = 'bg-secondary';
                if (issue.issue && issue.issue.includes('bias')) badgeClass = 'bg-danger';
                if (issue.issue && issue.issue.includes('vague')) badgeClass = 'bg-warning text-dark';
                if (issue.issue && issue.issue.includes('absolute')) badgeClass = 'bg-info text-dark';
                
                html += `
                    <div class="mb-3">
                        <span class="badge ${badgeClass}">${issue.issue || 'unknown'}</span>
                        <strong>"${issue.term}"</strong> - 
                        <span class="text-muted small">(${Math.round((issue.confidence || 0) * 100)}% resonance)</span>
                        <div>${issue.description || ''}</div>
                    </div>
                `;
            });
        } else {
            html += '<div class="alert alert-success">No issues detected in resonance field.</div>';
        }
        
        html += `
                    </div>
                </div>
            </div>
        `;
        
        // Reasoning section
        html += `
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Reflective Reasoning</h5>
                        <span class="badge bg-info text-dark">Resonance: ${globalResonance.toFixed(1)}</span>
                    </div>
                    <div class="card-body">
                        <div class="reasoning-box">${data.reasoning || 'Insufficient resonance for reasoning generation.'}</div>
                        <div class="text-muted small mt-2">Paradigm: ${data.sot_paradigm || ''}</div>
                    </div>
                </div>
            </div>
        `;
        
        html += `
                    </div>
                </div>
            </div>
        `;
        
        // Questions section
        html += `
            <div class="card mb-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Resonance-Modulated Questions</h5>
                    <span class="badge bg-success">Resonance: ${globalResonance.toFixed(1)}</span>
                </div>
                <div class="card-body">
        `;
        
        if (data.questions && data.questions.length > 0) {
            const resonancePrefix = globalResonance > 0.7 ? '(Deep Inquiry) ' : 
                                    globalResonance > 0.4 ? '' : '(Surface Inquiry) ';
            
            data.questions.forEach(question => {
                const escapedQuestion = question.replace(/'/g, "\\'");
                html += `
                    <div class="question-item mb-3">
                        <div>${resonancePrefix}${question}</div>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-success feedback-btn" onclick="window.sendFeedback('${escapedQuestion}', true)">
                                <i class="bi bi-hand-thumbs-up"></i> Helpful
                            </button>
                            <button class="btn btn-sm btn-outline-danger feedback-btn" onclick="window.sendFeedback('${escapedQuestion}', false)">
                                <i class="bi bi-hand-thumbs-down"></i> Not Helpful
                            </button>
                        </div>
                    </div>
                `;
            });
        } else {
            html += '<div class="alert alert-info">No questions generated in resonance field.</div>';
        }
        
        html += `
                </div>
            </div>
        `;
        
        // Set the HTML and show the results
        reflectionResults.innerHTML = html;
        reflectionResults.classList.remove('d-none');
    }
    
    // Feedback function for reflection
    sendFeedback(question, helpful) {
        const reflectionMode = document.getElementById('reflectionMode');
        
        fetch(API_ENDPOINTS.feedback, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                helpful: helpful,
                paradigm: reflectionMode.value
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Feedback sent:', data);
        })
        .catch(error => {
            console.error('Error sending feedback:', error);
        });
    }
    
    // Function for getting status from the reflective ecosystem
    getReflectiveStatus() {
        fetch(API_ENDPOINTS.status)
            .then(response => response.json())
            .then(data => {
                if (data.available) {
                    // Update the interface with real stats
                    const resonanceLevel = document.getElementById('resonanceLevel');
                    const resonanceValue = document.getElementById('resonanceValue');
                    const resonanceInfo = document.querySelector('.resonance-info');
                    
                    if (resonanceLevel) resonanceLevel.value = data.global_coherence;
                    if (resonanceValue) resonanceValue.textContent = data.global_coherence.toFixed(1);
                    if (resonanceInfo) resonanceInfo.textContent = `Global Resonance: ${data.global_coherence.toFixed(1)}`;
                    
                    this.updateResonanceVisualizer(data.global_coherence);
                    
                    // Show a message about the real ecosystem
                    console.log('Reflective ecosystem available:', data);
                } else {
                    console.log('Reflective ecosystem not available:', data.reason);
                }
            })
            .catch(error => {
                console.error('Error getting reflective status:', error);
            });
    }
    
    // Multimodal functionality
    handleFileSelect() {
        const fileInput = document.getElementById('fileInput');
        const previewContainer = document.getElementById('previewContainer');
        const preview = document.getElementById('preview');
        const processButton = document.getElementById('processButton');
        
        if (fileInput.files.length > 0) {
            this.selectedFile = fileInput.files[0];
            
            // Check if file type is supported
            const validTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'application/pdf'];
            if (!validTypes.includes(this.selectedFile.type) && !this.selectedFile.name.endsWith('.pdf')) {
                this.resetMultimodalUI();
                alert('Please select a supported file type (JPG, PNG, PDF, BMP, TIFF)');
                return;
            }
            
            // Show preview
            previewContainer.classList.remove('d-none');
            preview.innerHTML = '';
            
            if (this.selectedFile.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(this.selectedFile);
                img.className = 'img-fluid';
                img.style.maxHeight = '200px';
                preview.appendChild(img);
            } else {
                // PDF preview
                const pdfInfo = document.createElement('div');
                pdfInfo.className = 'alert alert-info';
                pdfInfo.innerHTML = `<i class="bi bi-file-pdf me-2"></i> <strong>${this.selectedFile.name}</strong> (${this.formatFileSize(this.selectedFile.size)})`;
                preview.appendChild(pdfInfo);
            }
            
            // Enable the process button
            processButton.disabled = false;
        } else {
            this.resetMultimodalUI();
        }
    }
    
    processDocument() {
        if (!this.selectedFile) return;
        
        const processButton = document.getElementById('processButton');
        const textStatus = document.getElementById('textStatus');
        const textOutput = document.getElementById('textOutput');
        
        // Set processing state
        processButton.disabled = true;
        processButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';
        
        // Update status indicators
        textStatus.innerHTML = '<span class="badge bg-info">Processing...</span>';
        textOutput.textContent = 'Extracting text...';
        
        // Get selected mode
        const analysisMode = document.querySelector('input[name="analysisMode"]:checked');
        const mode = analysisMode ? analysisMode.value : 'ocr';
        
        // Create FormData
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        formData.append('mode', mode);
        
        // Add socratic options if applicable
        if (mode === 'socratic') {
            formData.append('max_questions', '5');
            formData.append('use_sre', '1');
        }
        
        // Send to server
        fetch(API_ENDPOINTS.multimodal, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Reset button
            processButton.disabled = false;
            processButton.innerHTML = '<i class="bi bi-gear"></i> Process Document';
            
            if (data.success) {
                // Update UI with results
                this.updateMultimodalResults(data, mode);
            } else {
                // Show error
                textStatus.innerHTML = '<span class="badge bg-danger">Error</span>';
                textOutput.textContent = `Error: ${data.error}`;
                
                document.getElementById('analysisStatus').innerHTML = '<span class="badge bg-danger">Error</span>';
                document.getElementById('analysisOutput').textContent = 'Analysis failed';
            }
        })
        .catch(error => {
            console.error('Error processing document:', error);
            
            // Reset button
            processButton.disabled = false;
            processButton.innerHTML = '<i class="bi bi-gear"></i> Process Document';
            
            // Show error
            textStatus.innerHTML = '<span class="badge bg-danger">Error</span>';
            textOutput.textContent = `Error: ${error.message}`;
        });
    }
    
    updateMultimodalResults(data, mode) {
        const textStatus = document.getElementById('textStatus');
        const textOutput = document.getElementById('textOutput');
        const analysisStatus = document.getElementById('analysisStatus');
        const analysisOutput = document.getElementById('analysisOutput');
        const issuesStatus = document.getElementById('issuesStatus');
        const issuesOutput = document.getElementById('issuesOutput');
        const questionsStatus = document.getElementById('questionsStatus');
        const questionsOutput = document.getElementById('questionsOutput');
        const copyButton = document.getElementById('copyButton');
        const sendToChatButton = document.getElementById('sendToChatButton');
        
        // Update extracted text
        if (data.text) {
            this.extractedText = data.text;
            textStatus.innerHTML = '<span class="badge bg-success">Text Extracted</span>';
            textOutput.textContent = data.text;
            copyButton.disabled = false;
            sendToChatButton.disabled = false;
        } else {
            textStatus.innerHTML = '<span class="badge bg-warning">No Text Found</span>';
            textOutput.textContent = 'No text could be extracted from this document.';
        }
        
        // Update analysis if available
        if (data.analysis) {
            analysisStatus.innerHTML = '<span class="badge bg-success">Analysis Complete</span>';
            analysisOutput.textContent = data.analysis;
        } else {
            analysisStatus.innerHTML = '<span class="badge bg-secondary">No Analysis</span>';
            analysisOutput.textContent = 'No analysis was performed.';
        }
        
        // Update issues if available
        if (data.issues && data.issues.length > 0) {
            issuesStatus.innerHTML = `<span class="badge bg-warning">${data.issues.length} Issues Found</span>`;
            issuesOutput.innerHTML = '';
            
            data.issues.forEach(issue => {
                const issueCard = document.createElement('div');
                issueCard.className = 'card mb-2';
                issueCard.style.borderLeft = '4px solid #007bff';
                
                issueCard.innerHTML = `
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <strong>${issue.term}</strong>
                                <span class="badge bg-secondary ms-2">${issue.issue}</span>
                            </div>
                            <div>
                                <span class="badge bg-info">${(issue.confidence * 100).toFixed(0)}% confidence</span>
                            </div>
                        </div>
                        <p class="mt-2 mb-0">${issue.description}</p>
                    </div>
                `;
                
                issuesOutput.appendChild(issueCard);
            });
            
            // Update the analysis sidebar
            this.updateAnalysisSidebar(data);
        } else {
            issuesStatus.innerHTML = '<span class="badge bg-success">No Issues</span>';
            issuesOutput.innerHTML = '<p>No issues were detected in the text.</p>';
        }
        
        // Update questions if available
        if (data.questions && data.questions.length > 0) {
            questionsStatus.innerHTML = `<span class="badge bg-success">${data.questions.length} Questions</span>`;
            questionsOutput.innerHTML = '';
            
            const ul = document.createElement('ul');
            ul.className = 'list-group';
            
            data.questions.forEach(question => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.innerHTML = `<i class="bi bi-question-circle me-2 text-info"></i>${question}`;
                ul.appendChild(li);
            });
            
            questionsOutput.appendChild(ul);
            
            // Update the questions sidebar
            this.updateQuestionsSidebar(data);
        } else {
            questionsStatus.innerHTML = '<span class="badge bg-secondary">No Questions</span>';
            questionsOutput.innerHTML = '<p>No questions were generated.</p>';
        }
        
        // Show appropriate tab based on mode
        if (mode === 'multimodal') {
            document.getElementById('analysis-result-tab').click();
        } else if (mode === 'socratic') {
            document.getElementById('questions-tab').click();
        }
    }
    
    resetMultimodalUI() {
        const previewContainer = document.getElementById('previewContainer');
        const preview = document.getElementById('preview');
        const processButton = document.getElementById('processButton');
        const copyButton = document.getElementById('copyButton');
        const sendToChatButton = document.getElementById('sendToChatButton');
        const textStatus = document.getElementById('textStatus');
        const textOutput = document.getElementById('textOutput');
        const analysisStatus = document.getElementById('analysisStatus');
        const analysisOutput = document.getElementById('analysisOutput');
        const issuesStatus = document.getElementById('issuesStatus');
        const issuesOutput = document.getElementById('issuesOutput');
        const questionsStatus = document.getElementById('questionsStatus');
        const questionsOutput = document.getElementById('questionsOutput');
        
        this.selectedFile = null;
        this.extractedText = '';
        previewContainer.classList.add('d-none');
        preview.innerHTML = '';
        processButton.disabled = true;
        copyButton.disabled = true;
        sendToChatButton.disabled = true;
        
        textStatus.innerHTML = '<span class="badge bg-secondary">No file processed</span>';
        textOutput.textContent = 'Select a file to process';
        
        analysisStatus.innerHTML = '<span class="badge bg-secondary">No analysis available</span>';
        analysisOutput.textContent = 'Select multimodal or socratic analysis mode';
        
        issuesStatus.innerHTML = '<span class="badge bg-secondary">No issues detected</span>';
        issuesOutput.innerHTML = '<p>Socratic analysis will detect potential issues in the text</p>';
        
        questionsStatus.innerHTML = '<span class="badge bg-secondary">No questions generated</span>';
        questionsOutput.innerHTML = '<p>Socratic analysis will generate questions based on detected issues</p>';
    }
    
    // Save detector settings
    saveDetectorSettings() {
        const vagueTerms = document.getElementById('vagueTerms').value.split('\n').filter(term => term.trim());
        const genderBias = document.getElementById('genderBias').value.split('\n').filter(term => term.trim());
        const stereotypes = document.getElementById('stereotypes').value.split('\n').filter(term => term.trim());
        const nonInclusive = document.getElementById('nonInclusive').value.split('\n').filter(term => term.trim());
        
        fetch('/api/settings/detectors', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                vague: vagueTerms,
                gender_bias: genderBias,
                stereotype: stereotypes,
                non_inclusive: nonInclusive
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Detector settings saved successfully.');
            } else {
                alert('Error saving detector settings: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error saving detector settings:', error);
            alert('Error saving detector settings: ' + error.message);
        });
    }
    
    // ----- UTILITIES -----
    updateDocumentContextIndicator() {
        const useRAGSwitch = document.getElementById('useRAGSwitch');
        const documentContextIndicator = document.getElementById('documentContextIndicator');
        const contextDocCount = document.getElementById('contextDocCount');
        
        const useRAG = useRAGSwitch?.checked;
        
        if (useRAG && window.documentManager && window.documentManager.selectedDocuments.length > 0) {
            documentContextIndicator.classList.remove('d-none');
            contextDocCount.textContent = window.documentManager.selectedDocuments.length;
        } else {
            documentContextIndicator.classList.add('d-none');
        }
    }
    
    updateSREVisibility() {
        const useSRESwitch = document.getElementById('useSRESwitch');
        const sreVisualizationContainer = document.getElementById('sreVisualizationContainer');
        
        const useSRE = useSRESwitch?.checked;
        
        if (useSRE && this.sreVisible) {
            sreVisualizationContainer.classList.remove('d-none');
        } else {
            sreVisualizationContainer.classList.add('d-none');
        }
    }
    
    toggleSRE() {
        this.sreVisible = !this.sreVisible;
        this.updateSREVisibility();
    }
    
    loadSettings() {
        try {
            const settings = JSON.parse(localStorage.getItem('integratedUISettings'));
            if (settings) {
                const modeSelect = document.getElementById('modeSelect');
                const showAnalysisSwitch = document.getElementById('showAnalysisSwitch');
                const useSoTSwitch = document.getElementById('useSoTSwitch');
                const useRAGSwitch = document.getElementById('useRAGSwitch');
                const useSRESwitch = document.getElementById('useSRESwitch');
                
                if (settings.mode && modeSelect) modeSelect.value = settings.mode;
                if (settings.showAnalysis !== undefined && showAnalysisSwitch) showAnalysisSwitch.checked = settings.showAnalysis;
                if (settings.useSoT !== undefined && useSoTSwitch) useSoTSwitch.checked = settings.useSoT;
                if (settings.useRAG !== undefined && useRAGSwitch) useRAGSwitch.checked = settings.useRAG;
                if (settings.useSRE !== undefined && useSRESwitch) useSRESwitch.checked = settings.useSRE;
                if (settings.sreVisible !== undefined) this.sreVisible = settings.sreVisible;
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }
    
    saveSettings() {
        try {
            const modeSelect = document.getElementById('modeSelect');
            const showAnalysisSwitch = document.getElementById('showAnalysisSwitch');
            const useSoTSwitch = document.getElementById('useSoTSwitch');
            const useRAGSwitch = document.getElementById('useRAGSwitch');
            const useSRESwitch = document.getElementById('useSRESwitch');
            
            const settings = {
                mode: modeSelect?.value,
                showAnalysis: showAnalysisSwitch?.checked,
                useSoT: useSoTSwitch?.checked,
                useRAG: useRAGSwitch?.checked,
                useSRE: useSRESwitch?.checked,
                sreVisible: this.sreVisible
            };
            
            localStorage.setItem('integratedUISettings', JSON.stringify(settings));
            
            // Update model info
            this.updateModelInfo();
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }
    
    updateModelInfo() {
        const currentLLM = document.getElementById('currentLLM');
        const sotEnabled = document.getElementById('sotEnabled');
        const sreEnabled = document.getElementById('sreEnabled');
        const providerName = document.getElementById('providerName');
        const useSoTSwitch = document.getElementById('useSoTSwitch');
        const useSRESwitch = document.getElementById('useSRESwitch');
        
        if (currentLLM) currentLLM.textContent = 'gemma3:latest';
        if (sotEnabled) sotEnabled.textContent = useSoTSwitch?.checked ? 'Yes' : 'No';
        if (sreEnabled) sreEnabled.textContent = useSRESwitch?.checked ? 'Yes' : 'No';
        if (providerName) providerName.textContent = 'ollama';
    }
    
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }
    
    // ----- RESONANCE VISUALIZER -----
    initializeResonanceVisualizer() {
        const visualizer = document.getElementById('resonanceVisualizer');
        if (!visualizer) return;
        
        // Create nodes
        for (let i = 0; i < 5; i++) {
            const node = document.createElement('div');
            node.className = 'resonance-node';
            node.style.width = `${8 + Math.random() * 10}px`;
            node.style.height = node.style.width;
            node.style.left = `${10 + Math.random() * 80}%`;
            node.style.top = `${10 + Math.random() * 70}%`;
            visualizer.appendChild(node);
        }
        
        // Create connections between nodes
        const nodes = visualizer.querySelectorAll('.resonance-node');
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                if (Math.random() > 0.3) {
                    this.createConnection(nodes[i], nodes[j], visualizer);
                }
            }
        }
        
        // Initial update
        this.updateResonanceVisualizer(1.0);
    }
    
    createConnection(node1, node2, container) {
        const connection = document.createElement('div');
        connection.className = 'resonance-connection';
        
        const rect1 = node1.getBoundingClientRect();
        const rect2 = node2.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        
        const x1 = rect1.left + rect1.width / 2 - containerRect.left;
        const y1 = rect1.top + rect1.height / 2 - containerRect.top;
        const x2 = rect2.left + rect2.width / 2 - containerRect.left;
        const y2 = rect2.top + rect2.height / 2 - containerRect.top;
        
        const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
        const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
        
        connection.style.width = `${length}px`;
        connection.style.height = '1px';
        connection.style.left = `${x1}px`;
        connection.style.top = `${y1}px`;
        connection.style.transform = `rotate(${angle}deg)`;
        
        container.appendChild(connection);
    }
    
    updateResonanceVisualizer(value) {
        const visualizer = document.getElementById('resonanceVisualizer');
        if (!visualizer) return;
        
        const nodes = visualizer.querySelectorAll('.resonance-node');
        const connections = visualizer.querySelectorAll('.resonance-connection');
        
        // Update nodes
        nodes.forEach(node => {
            const size = 8 + Math.random() * 10 * value;
            node.style.width = `${size}px`;
            node.style.height = `${size}px`;
            node.style.boxShadow = `0 0 ${10 * value}px ${5 * value}px rgba(255, 255, 255, ${0.4 * value})`;
        });
        
        // Update connections
        connections.forEach(connection => {
            connection.style.height = `${1 * value}px`;
            connection.style.opacity = 0.4 * value;
        });
        
        // Update wave
        const wave = visualizer.querySelector('.resonance-wave');
        if (wave) {
            wave.style.background = `radial-gradient(circle, rgba(0,123,255,${0.5 * value}) 0%, rgba(0,0,0,0) 70%)`;
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    window.integratedUI = new IntegratedUI();
    
    // Expose feedback function to global scope (for the reflection tab)
    window.sendFeedback = function(question, helpful) {
        window.integratedUI.sendFeedback(question, helpful);
    };
});
