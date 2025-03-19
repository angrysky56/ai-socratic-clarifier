#!/usr/bin/env python3
"""
Unify UI Script for AI-Socratic-Clarifier

This script consolidates all separate UIs into a single, unified UI at /socratic
with tabs for different functionality:
- Chat & Reasoning
- Document RAG
- Reflection Visualization
- Multimodal Analysis
- Settings

It also updates all routes to redirect to the new unified UI.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_INTERFACE_DIR = os.path.join(BASE_DIR, "web_interface")
TEMPLATES_DIR = os.path.join(WEB_INTERFACE_DIR, "templates")
STATIC_DIR = os.path.join(WEB_INTERFACE_DIR, "static")


def backup_file(file_path):
    """Create a backup of a file."""
    backup_path = f"{file_path}.unify_ui_bak"
    if os.path.exists(file_path):
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
    return backup_path


def create_unified_template():
    """Create a unified UI template."""
    logger.info("Creating unified UI template...")
    
    # Create template path
    unified_template_path = os.path.join(TEMPLATES_DIR, "socratic_ui.html")
    
    # First, check if we have an integrated_ui.html to use as a base
    integrated_ui_path = os.path.join(TEMPLATES_DIR, "integrated_ui.html")
    if os.path.exists(integrated_ui_path):
        # Start with the integrated UI as a base
        with open(integrated_ui_path, 'r') as f:
            content = f.read()
        
        # Update title and add tabs
        content = content.replace("<title>AI-Socratic-Clarifier</title>", 
                                 "<title>AI-Socratic-Clarifier - Unified UI</title>")
        
        # Find where to insert tabs (after the sidebar)
        sidebar_end = content.find("</div>", content.find("sidebar-content"))
        if sidebar_end > 0:
            # Add tabs
            tabs_html = """
            <!-- Tab navigation -->
            <ul class="nav nav-tabs mb-3" id="mainTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="chat-tab" data-bs-toggle="tab" data-bs-target="#chat-content" 
                        type="button" role="tab" aria-controls="chat-content" aria-selected="true">
                        <i class="bi bi-chat-dots"></i> Chat & Reasoning
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="documents-tab" data-bs-toggle="tab" data-bs-target="#documents-content" 
                        type="button" role="tab" aria-controls="documents-content" aria-selected="false">
                        <i class="bi bi-file-text"></i> Documents
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="reflection-tab" data-bs-toggle="tab" data-bs-target="#reflection-content" 
                        type="button" role="tab" aria-controls="reflection-content" aria-selected="false">
                        <i class="bi bi-diagram-3"></i> Reflection
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="multimodal-tab" data-bs-toggle="tab" data-bs-target="#multimodal-content" 
                        type="button" role="tab" aria-controls="multimodal-content" aria-selected="false">
                        <i class="bi bi-image"></i> Multimodal
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="settings-tab" data-bs-toggle="tab" data-bs-target="#settings-content" 
                        type="button" role="tab" aria-controls="settings-content" aria-selected="false">
                        <i class="bi bi-gear"></i> Settings
                    </button>
                </li>
            </ul>
            
            <!-- Tab content -->
            <div class="tab-content" id="mainTabsContent">
                <!-- Chat & Reasoning Tab -->
                <div class="tab-pane fade show active" id="chat-content" role="tabpanel" aria-labelledby="chat-tab">
                    <!-- Existing chat UI will go here -->
                    <div id="integrated-chat-container">
                        <div id="message-container" class="mb-3"></div>
                        <div id="input-container" class="d-flex">
                            <textarea id="user-input" class="form-control me-2" placeholder="Enter your message..." rows="2"></textarea>
                            <button id="send-button" class="btn btn-primary">Send</button>
                        </div>
                    </div>
                </div>
                
                <!-- Documents Tab -->
                <div class="tab-pane fade" id="documents-content" role="tabpanel" aria-labelledby="documents-tab">
                    <div id="document-management">
                        <h3>Document Library</h3>
                        <div class="mb-3">
                            <button id="upload-document-btn" class="btn btn-primary">
                                <i class="bi bi-upload"></i> Upload Document
                            </button>
                            <input type="file" id="document-file-input" style="display: none;">
                        </div>
                        <div id="document-list" class="list-group mb-3">
                            <!-- Documents will be loaded here -->
                            <div class="text-center py-3" id="document-list-loading">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <p>Loading documents...</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Reflection Tab -->
                <div class="tab-pane fade" id="reflection-content" role="tabpanel" aria-labelledby="reflection-tab">
                    <div id="reflection-visualization">
                        <h3>Reflection Visualization</h3>
                        <div id="ecosystem-graph" style="height: 500px; border: 1px solid #ddd;"></div>
                        <div id="reflection-controls" class="mt-3 d-flex justify-content-between">
                            <button id="reset-ecosystem" class="btn btn-outline-secondary">Reset</button>
                            <button id="refresh-ecosystem" class="btn btn-outline-primary">Refresh</button>
                        </div>
                    </div>
                </div>
                
                <!-- Multimodal Tab -->
                <div class="tab-pane fade" id="multimodal-content" role="tabpanel" aria-labelledby="multimodal-tab">
                    <div id="multimodal-analysis">
                        <h3>Multimodal Analysis</h3>
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title">Upload an Image or PDF</h5>
                                <div class="mb-3">
                                    <input class="form-control" type="file" id="multimodal-file-input" accept=".jpg,.jpeg,.png,.gif,.pdf">
                                </div>
                                
                                <div class="mode-toggle mb-3">
                                    <div class="form-check form-check-inline">
                                        <input class="form-check-input" type="radio" name="analysisMode" id="multimodalMode" value="multimodal" checked>
                                        <label class="form-check-label" for="multimodalMode">Multimodal Analysis</label>
                                    </div>
                                    <div class="form-check form-check-inline">
                                        <input class="form-check-input" type="radio" name="analysisMode" id="socraticMode" value="socratic">
                                        <label class="form-check-label" for="socraticMode">Socratic Analysis</label>
                                    </div>
                                </div>
                                
                                <div class="mt-3" id="socraticOptions" style="display:none;">
                                    <label for="maxQuestionsSlider" class="form-label">Maximum Questions: <span id="maxQuestionsValue">5</span></label>
                                    <input type="range" class="form-range" min="1" max="10" step="1" value="5" id="maxQuestionsSlider">
                                    
                                    <div class="form-check mt-2">
                                        <input class="form-check-input" type="checkbox" id="useSreCheckbox" checked>
                                        <label class="form-check-label" for="useSreCheckbox">
                                            Use Socratic Reasoning Engine for improved questions
                                        </label>
                                    </div>
                                </div>
                                
                                <button id="process-multimodal-button" class="btn btn-primary mt-3">Process</button>
                            </div>
                        </div>
                        
                        <div id="multimodal-result" style="display: none;">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Analysis Results</h5>
                                    <div id="multimodal-content-display"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Settings Tab -->
                <div class="tab-pane fade" id="settings-content" role="tabpanel" aria-labelledby="settings-tab">
                    <div id="settings-panel">
                        <h3>Settings</h3>
                        <form id="settings-form" class="mb-3">
                            <div class="mb-3">
                                <label for="provider-select" class="form-label">AI Provider</label>
                                <select id="provider-select" class="form-select">
                                    <option value="auto">Auto-Select</option>
                                    <option value="ollama">Ollama (Local)</option>
                                    <option value="external">External API</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label for="model-select" class="form-label">Default Model</label>
                                <select id="model-select" class="form-select">
                                    <!-- Will be populated dynamically -->
                                </select>
                            </div>
                            
                            <div class="mb-3 form-check">
                                <input type="checkbox" class="form-check-input" id="use-sot-checkbox" checked>
                                <label class="form-check-label" for="use-sot-checkbox">Use Sequential of Thought</label>
                            </div>
                            
                            <div class="mb-3 form-check">
                                <input type="checkbox" class="form-check-input" id="use-multimodal-checkbox" checked>
                                <label class="form-check-label" for="use-multimodal-checkbox">Enable Multimodal Support</label>
                            </div>
                            
                            <button type="submit" class="btn btn-primary">Save Settings</button>
                        </form>
                    </div>
                </div>
            </div>"""
            
            # Insert tabs after sidebar
            content = content[:sidebar_end + 6] + tabs_html + content[sidebar_end + 6:]
        
        # Add additional scripts for tab handling
        script_section = """
        <script>
            // Tab navigation and content loading
            document.addEventListener('DOMContentLoaded', function() {
                // Handle tab switching
                const tabs = document.querySelectorAll('#mainTabs button');
                tabs.forEach(tab => {
                    tab.addEventListener('click', function(e) {
                        e.preventDefault();
                        // Show the selected tab
                        const tabId = this.getAttribute('data-bs-target');
                        
                        // Load content based on tab
                        switch(this.id) {
                            case 'documents-tab':
                                loadDocuments();
                                break;
                            case 'reflection-tab':
                                loadReflectionVisualization();
                                break;
                            case 'multimodal-tab':
                                setupMultimodalTab();
                                break;
                            case 'settings-tab':
                                loadSettings();
                                break;
                        }
                    });
                });
                
                // Document tab functions
                function loadDocuments() {
                    if (!window.documentsLoaded) {
                        fetch('/api/documents')
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    displayDocuments(data.documents);
                                } else {
                                    showError('Failed to load documents: ' + data.error);
                                }
                                document.getElementById('document-list-loading').style.display = 'none';
                            })
                            .catch(error => {
                                console.error('Error loading documents:', error);
                                document.getElementById('document-list-loading').style.display = 'none';
                                showError('Error loading documents');
                            });
                            
                        window.documentsLoaded = true;
                    }
                }
                
                function displayDocuments(documents) {
                    const documentList = document.getElementById('document-list');
                    documentList.innerHTML = '';
                    
                    if (documents.length === 0) {
                        documentList.innerHTML = '<div class="text-center py-3">No documents yet. Upload one to get started.</div>';
                        return;
                    }
                    
                    documents.forEach(doc => {
                        const docElement = document.createElement('div');
                        docElement.className = 'list-group-item';
                        docElement.innerHTML = `
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h5 class="mb-1">${doc.filename}</h5>
                                    <small>${formatFileSize(doc.file_size)} | ${doc.file_type} | ${formatDate(doc.upload_date)}</small>
                                </div>
                                <div>
                                    <button class="btn btn-sm btn-outline-primary view-document" data-id="${doc.id}">
                                        <i class="bi bi-eye"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger delete-document" data-id="${doc.id}">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </div>
                            </div>
                        `;
                        documentList.appendChild(docElement);
                    });
                    
                    // Add event listeners
                    document.querySelectorAll('.view-document').forEach(btn => {
                        btn.addEventListener('click', function() {
                            viewDocument(this.getAttribute('data-id'));
                        });
                    });
                    
                    document.querySelectorAll('.delete-document').forEach(btn => {
                        btn.addEventListener('click', function() {
                            deleteDocument(this.getAttribute('data-id'));
                        });
                    });
                }
                
                // Reflection tab functions
                function loadReflectionVisualization() {
                    if (!window.reflectionLoaded) {
                        // Load reflection visualization
                        fetch('/api/reflection/ecosystem')
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    drawEcosystemGraph(data.ecosystem);
                                } else {
                                    showError('Failed to load reflection data: ' + data.error);
                                }
                            })
                            .catch(error => {
                                console.error('Error loading reflection:', error);
                                showError('Error loading reflection visualization');
                            });
                            
                        window.reflectionLoaded = true;
                    }
                }
                
                // Multimodal tab functions
                function setupMultimodalTab() {
                    if (!window.multimodalSetup) {
                        // Toggle socratic options based on selected mode
                        document.querySelectorAll('input[name="analysisMode"]').forEach(radio => {
                            radio.addEventListener('change', function() {
                                const socraticOptions = document.getElementById('socraticOptions');
                                if (this.value === 'socratic') {
                                    socraticOptions.style.display = 'block';
                                } else {
                                    socraticOptions.style.display = 'none';
                                }
                            });
                        });
                        
                        // Max questions slider
                        const maxQuestionsSlider = document.getElementById('maxQuestionsSlider');
                        const maxQuestionsValue = document.getElementById('maxQuestionsValue');
                        
                        if (maxQuestionsSlider && maxQuestionsValue) {
                            maxQuestionsSlider.addEventListener('input', function() {
                                maxQuestionsValue.textContent = this.value;
                            });
                        }
                        
                        // Process button
                        document.getElementById('process-multimodal-button').addEventListener('click', function() {
                            processMultimodalFile();
                        });
                        
                        window.multimodalSetup = true;
                    }
                }
                
                // Settings tab functions
                function loadSettings() {
                    if (!window.settingsLoaded) {
                        // Load settings
                        fetch('/api/settings')
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    populateSettingsForm(data.settings);
                                } else {
                                    showError('Failed to load settings: ' + data.error);
                                }
                            })
                            .catch(error => {
                                console.error('Error loading settings:', error);
                                showError('Error loading settings');
                            });
                            
                        window.settingsLoaded = true;
                    }
                }
                
                // Utilities
                function formatFileSize(bytes) {
                    if (bytes < 1024) return bytes + ' B';
                    if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB';
                    return (bytes / 1048576).toFixed(2) + ' MB';
                }
                
                function formatDate(dateStr) {
                    try {
                        const date = new Date(dateStr);
                        return date.toLocaleDateString();
                    } catch (e) {
                        return dateStr;
                    }
                }
                
                function showError(message) {
                    // Create toast or notification
                    console.error(message);
                    alert(message);
                }
                
                // Initialize upload button
                document.getElementById('upload-document-btn').addEventListener('click', function() {
                    document.getElementById('document-file-input').click();
                });
                
                document.getElementById('document-file-input').addEventListener('change', function() {
                    if (this.files.length > 0) {
                        uploadDocument(this.files[0]);
                    }
                });
                
                // Init
                setupInitialUI();
            });
            
            function setupInitialUI() {
                // Set up chat UI
                setupChatInterface();
            }
            
            function setupChatInterface() {
                const sendButton = document.getElementById('send-button');
                const userInput = document.getElementById('user-input');
                const messageContainer = document.getElementById('message-container');
                
                sendButton.addEventListener('click', function() {
                    sendMessage();
                });
                
                userInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                    }
                });
                
                function sendMessage() {
                    const message = userInput.value.trim();
                    if (message) {
                        // Add user message to UI
                        addMessageToUI('user', message);
                        
                        // Clear input
                        userInput.value = '';
                        
                        // Send to backend
                        fetch('/api/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                message: message,
                                use_sot: true,
                                use_documents: true
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                addMessageToUI('assistant', data.response);
                                
                                // If there's reasoning data, update the reflection tab
                                if (data.reasoning) {
                                    updateReflectionData(data.reasoning);
                                }
                            } else {
                                addMessageToUI('system', 'Error: ' + data.error);
                            }
                        })
                        .catch(error => {
                            console.error('Error sending message:', error);
                            addMessageToUI('system', 'Error sending message. Please try again.');
                        });
                    }
                }
                
                function addMessageToUI(sender, content) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${sender}-message mb-2 p-2 ${sender === 'user' ? 'ms-auto' : ''}`;
                    
                    // Create message content with markdown rendering if needed
                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'message-content';
                    
                    if (sender === 'assistant') {
                        // Render markdown for assistant messages
                        try {
                            // If you have a markdown library
                            contentDiv.innerHTML = window.markdownit ? window.markdownit().render(content) : content;
                        } catch (e) {
                            contentDiv.textContent = content;
                        }
                    } else {
                        contentDiv.textContent = content;
                    }
                    
                    messageDiv.appendChild(contentDiv);
                    messageContainer.appendChild(messageDiv);
                    
                    // Scroll to bottom
                    messageContainer.scrollTop = messageContainer.scrollHeight;
                }
            }
        </script>
        """
        
        # Add script before end of body
        body_end = content.find("</body>")
        if body_end > 0:
            content = content[:body_end] + script_section + content[body_end:]
        
        # Write to the new template file
        with open(unified_template_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Created unified UI template at {unified_template_path}")
        return True
    else:
        logger.error("Could not find integrated_ui.html template to use as base")
        return False


def update_app_routes():
    """Update app.py to include the new unified UI route."""
    logger.info("Updating app routes...")
    
    app_path = os.path.join(WEB_INTERFACE_DIR, "app.py")
    if not os.path.exists(app_path):
        logger.error(f"Could not find app.py at {app_path}")
        return False
    
    # Create backup
    backup_file(app_path)
    
    try:
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Check if we already have the socratic route
        if "def socratic_ui" in content:
            logger.info("Socratic UI route already exists in app.py")
        else:
            # Add the new route
            routes_section = content.find("# Routes")
            if routes_section > 0:
                # Find a good insertion point after other routes
                next_section = content.find("# API endpoints", routes_section)
                if next_section < 0:
                    next_section = content.find("# Setup error handlers", routes_section)
                
                if next_section > 0:
                    # Create the new route
                    socratic_route = """
@app.route('/socratic')
def socratic_ui():
    \"\"\"
    Unified Socratic UI with tabs for all functionality.
    \"\"\"
    return render_template('socratic_ui.html')
                    
# Redirect old routes to the unified UI
@app.route('/integrated')
@app.route('/integrated_lite')
@app.route('/enhanced')
@app.route('/reflection')
def redirect_to_socratic():
    \"\"\"
    Redirect old UI routes to the unified Socratic UI.
    \"\"\"
    return redirect('/socratic')

"""
                    # Insert the new route
                    content = content[:next_section] + socratic_route + content[next_section:]
                    
                    # Update the app.py file
                    with open(app_path, 'w') as f:
                        f.write(content)
                    
                    logger.info("Added Socratic UI route to app.py")
                    return True
                else:
                    logger.error("Could not find appropriate section to add route in app.py")
                    return False
            else:
                logger.error("Could not find routes section in app.py")
                return False
    except Exception as e:
        logger.error(f"Error updating app.py: {e}")
        return False


def update_start_script():
    """Update start_ui.py to show the new unified UI path."""
    logger.info("Updating start_ui.py...")
    
    start_ui_path = os.path.join(BASE_DIR, "start_ui.py")
    if not os.path.exists(start_ui_path):
        logger.error(f"Could not find start_ui.py at {start_ui_path}")
        return False
    
    # Create backup
    backup_file(start_ui_path)
    
    try:
        with open(start_ui_path, 'r') as f:
            content = f.read()
        
        # Update the UI paths in the startup message
        if "print(\"*  Socratic UI: /socratic" not in content:
            # Find the startup message section
            start_section = content.find("print(\"***")
            if start_section > 0:
                # Find the end of the message section
                end_section = content.find("print(\"***", start_section + 10)
                if end_section > 0:
                    # Get all lines
                    lines = content[start_section:end_section].split("\n")
                    
                    # Create new lines
                    new_lines = []
                    added_socratic = False
                    
                    for line in lines:
                        if "print(\"*  Integrated UI: /integrated" in line:
                            # Replace with Socratic UI
                            new_lines.append("    print(\"*  Socratic UI: /socratic" + " " * 30 + "*\")")
                            added_socratic = True
                        elif "print(\"*  Integrated UI (Lite): /integrated_lite" in line or \
                             "print(\"*  Enhanced UI: /enhanced" in line or \
                             "print(\"*  Reflective mode: /reflection" in line:
                            # Skip these lines
                            pass
                        else:
                            new_lines.append(line)
                    
                    # If we didn't add the socratic line, add it now
                    if not added_socratic:
                        # Find where to insert (before the closing stars)
                        for i, line in enumerate(new_lines):
                            if "print(\"****" in line and i > 0:
                                new_lines.insert(i, "    print(\"*  Socratic UI: /socratic" + " " * 30 + "*\")")
                                break
                    
                    # Replace the section
                    new_section = "\n".join(new_lines)
                    content = content[:start_section] + new_section + content[end_section:]
                    
                    # Update the start_ui.py file
                    with open(start_ui_path, 'w') as f:
                        f.write(content)
                    
                    logger.info("Updated start_ui.py with Socratic UI path")
                    return True
                else:
                    logger.error("Could not find end of startup message section in start_ui.py")
                    return False
            else:
                logger.error("Could not find startup message section in start_ui.py")
                return False
        else:
            logger.info("start_ui.py already shows the Socratic UI path")
            return True
    except Exception as e:
        logger.error(f"Error updating start_ui.py: {e}")
        return False


def update_optimized_script():
    """Update start_optimized.py to prefer the unified UI."""
    logger.info("Updating start_optimized.py...")
    
    optimized_path = os.path.join(BASE_DIR, "start_optimized.py")
    if not os.path.exists(optimized_path):
        logger.error(f"Could not find start_optimized.py at {optimized_path}")
        return False
    
    # Create backup
    backup_file(optimized_path)
    
    try:
        with open(optimized_path, 'r') as f:
            content = f.read()
        
        # Add a print statement to show the unified UI path
        if "Optimized AI-Socratic-Clarifier Startup" in content and "with Enhanced Multimodal and RAG Support" in content:
            # Find where to add the print
            start_ui_section = content.find("def start_ui()")
            if start_ui_section > 0:
                # Find the function body
                start_ui_body = content.find("\"\"\"", start_ui_section) + 3
                start_ui_body = content.find("\n", start_ui_body) + 1
                
                # Add print statement
                print_statement = """    print("\\nAccess the unified Socratic UI at: http://localhost:5000/socratic")
    """
                
                # Insert the print statement
                content = content[:start_ui_body] + print_statement + content[start_ui_body:]
                
                # Update the optimized script
                with open(optimized_path, 'w') as f:
                    f.write(content)
                
                logger.info("Updated start_optimized.py to show unified UI path")
                return True
            else:
                logger.error("Could not find start_ui function in start_optimized.py")
                return False
        else:
            logger.error("Could not find appropriate section in start_optimized.py")
            return False
    except Exception as e:
        logger.error(f"Error updating start_optimized.py: {e}")
        return False


def main():
    """Main function to unify all UIs."""
    print("\n" + "="*70)
    print("   AI-Socratic-Clarifier UI Unification Tool")
    print("="*70 + "\n")
    
    # Run all fixes
    template_created = create_unified_template()
    routes_updated = update_app_routes()
    start_script_updated = update_start_script()
    optimized_script_updated = update_optimized_script()
    
    # Print summary
    print("\n" + "="*70)
    print("   Unification Summary")
    print("="*70)
    print(f"✓ Unified UI Template: {'Created' if template_created else 'Failed'}")
    print(f"✓ App Routes: {'Updated' if routes_updated else 'Failed'}")
    print(f"✓ Start Script: {'Updated' if start_script_updated else 'Failed'}")
    print(f"✓ Optimized Script: {'Updated' if optimized_script_updated else 'Failed'}")
    
    # Print instructions
    print("\n" + "="*70)
    print("   Usage Instructions")
    print("="*70)
    print("1. Start the application:")
    print("   ./start_optimized.py")
    print("")
    print("2. Access the unified UI at:")
    print("   http://localhost:5000/socratic")
    print("")
    print("3. The unified UI has tabs for:")
    print("   - Chat & Reasoning")
    print("   - Document RAG")
    print("   - Reflection Visualization")
    print("   - Multimodal Analysis")
    print("   - Settings")
    print("")
    print("4. Old UI paths will automatically redirect to the unified UI")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
