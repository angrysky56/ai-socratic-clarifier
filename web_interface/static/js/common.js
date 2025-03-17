/**
 * AI-Socratic-Clarifier Common JavaScript Functions
 * Contains shared functionality for the enhanced UI
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mode selection
    initModeSelection();
    
    // Initialize debug mode toggle
    initDebugMode();
    
    // Check model status periodically
    checkModelStatus();
    setInterval(checkModelStatus, 30000);
});

/**
 * Initialize mode selection functionality
 */
function initModeSelection() {
    const modeButtons = document.querySelectorAll('.mode-select');
    modeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const mode = this.dataset.mode;
            document.getElementById('currentMode').textContent = `Mode: ${mode}`;
            localStorage.setItem('preferredMode', mode);
            
            // Update any active mode-dependent components on the page
            if (typeof updateMode === 'function') {
                updateMode(mode);
            }
        });
    });
    
    // Set initial mode from localStorage or default to 'standard'
    const savedMode = localStorage.getItem('preferredMode') || 'standard';
    document.getElementById('currentMode').textContent = `Mode: ${savedMode}`;
}

/**
 * Initialize debug mode toggle
 */
function initDebugMode() {
    const debugModeToggle = document.getElementById('debugModeToggle');
    if (debugModeToggle) {
        debugModeToggle.addEventListener('click', function() {
            const debugMode = localStorage.getItem('debugMode') === 'true';
            localStorage.setItem('debugMode', (!debugMode).toString());
            this.innerHTML = !debugMode ? 
                '<i class="bi bi-bug"></i> Debug Mode: ON' : 
                '<i class="bi bi-bug"></i> Debug Mode: OFF';
                
            // Update UI based on debug mode
            document.body.classList.toggle('debug-mode', !debugMode);
        });
        
        // Initialize debug mode
        const initialDebugMode = localStorage.getItem('debugMode') === 'true';
        debugModeToggle.innerHTML = initialDebugMode ? 
            '<i class="bi bi-bug"></i> Debug Mode: ON' : 
            '<i class="bi bi-bug"></i> Debug Mode: OFF';
        document.body.classList.toggle('debug-mode', initialDebugMode);
    }
}

/**
 * Check the status of the model/API
 */
function checkModelStatus() {
    fetch('/api/test')
        .then(response => response.json())
        .then(data => {
            const modelStatus = document.getElementById('modelStatus');
            const systemStatus = document.getElementById('systemStatus');
            const currentModel = document.getElementById('currentModel');
            
            if (data.status === 'ok') {
                modelStatus.className = 'badge bg-success me-2';
                modelStatus.innerHTML = '<i class="bi bi-cpu"></i> Model Ready';
                systemStatus.textContent = 'Ready';
                
                if (currentModel) {
                    currentModel.textContent = `Model: ${data.model || 'llama3'}`;
                }
            } else {
                modelStatus.className = 'badge bg-danger me-2';
                modelStatus.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Model Error';
                systemStatus.textContent = 'Error';
            }
        })
        .catch(error => {
            const modelStatus = document.getElementById('modelStatus');
            const systemStatus = document.getElementById('systemStatus');
            
            modelStatus.className = 'badge bg-warning me-2';
            modelStatus.innerHTML = '<i class="bi bi-question-circle"></i> Status Unknown';
            systemStatus.textContent = 'Unknown';
            
            console.error('Error checking model status:', error);
        });
}

/**
 * Helper function to format file size
 */
function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * Helper function to format date
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}
