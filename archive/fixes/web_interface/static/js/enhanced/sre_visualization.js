/**
 * SRE Visualization Script
 * 
 * This script visualizes the Symbiotic Reflective Ecosystem (SRE) in the UI.
 */

// Initialize visualization when document is ready
document.addEventListener('DOMContentLoaded', function() {
    initSREVisualization();
});

// Global visualization state
let sreState = {
    currentStage: 'stageWhy',
    reasoningPaths: [],
    advancement: 0,
    networkNodes: []
};

function initSREVisualization() {
    // Get visualization containers
    const metaMetaContainer = document.getElementById('meta-meta-visualization');
    const networkContainer = document.getElementById('network-visualization');
    
    if (!metaMetaContainer || !networkContainer) {
        console.warn('SRE visualization containers not found');
        return;
    }
    
    // Initialize visualization
    updateMetaMetaVisualization();
    initializeNetworkVisualization();
    
    // Listen for chat responses
    document.addEventListener('chatResponseReceived', function(e) {
        if (e.detail && e.detail.response) {
            updateSREState(e.detail.response);
        }
    });
}

function updateSREState(response) {
    // Update state from response
    if (response.reasoning_paths) {
        sreState.reasoningPaths = response.reasoning_paths;
    }
    
    if (response.meta_meta_stage) {
        sreState.currentStage = response.meta_meta_stage;
    }
    
    if (response.advancement) {
        sreState.advancement = response.advancement;
    }
    
    // Update visualizations
    updateMetaMetaVisualization();
    updateNetworkVisualization();
}

function updateMetaMetaVisualization() {
    const container = document.getElementById('meta-meta-visualization');
    if (!container) return;
    
    // Highlight current stage
    const stages = ['stageWhy', 'stageWhat', 'stageHow', 'stageWhatIf', 'stageHowElse', 'stageWhatNext', 'stageWhatNow'];
    
    stages.forEach(stage => {
        const el = document.getElementById(stage);
        if (el) {
            if (stage === sreState.currentStage) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        }
    });
    
    // Update advancement indicator if it exists
    const advancementEl = document.getElementById('advancement-indicator');
    if (advancementEl) {
        const advancementValue = sreState.advancement.advancement || 0;
        advancementEl.style.width = `${advancementValue * 100}%`;
    }
}

function initializeNetworkVisualization() {
    const container = document.getElementById('network-visualization');
    if (!container) return;
    
    // Create empty visualization
    container.innerHTML = '<div class="network-placeholder">Reflective network will appear here when analysis is performed</div>';
}

function updateNetworkVisualization() {
    const container = document.getElementById('network-visualization');
    if (!container) return;
    
    if (!sreState.reasoningPaths || sreState.reasoningPaths.length === 0) {
        container.innerHTML = '<div class="network-placeholder">No reasoning paths available yet</div>';
        return;
    }
    
    // Create a simple visualization of reasoning paths
    let html = '<div class="reasoning-paths">';
    
    sreState.reasoningPaths.forEach(path => {
        html += `<div class="reasoning-path">
            <div class="path-name">${path.name || 'Reasoning Path'}</div>
            <div class="path-steps">`;
        
        if (path.steps && path.steps.length > 0) {
            html += '<ol>';
            path.steps.forEach(step => {
                html += `<li>${step}</li>`;
            });
            html += '</ol>';
        }
        
        html += `</div></div>`;
    });
    
    html += '</div>';
    container.innerHTML = html;
    
    // Update the node count
    const nodeCountEl = document.getElementById('node-count');
    if (nodeCountEl) {
        const nodeCount = sreState.reasoningPaths.length;
        nodeCountEl.textContent = nodeCount;
    }
}

// Function to handle user feedback on questions
function processQuestionFeedback(questionId, helpful) {
    // Send feedback to the server
    fetch('/api/sre/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            question_id: questionId,
            helpful: helpful
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update visualization if feedback was processed
            updateSREState(data);
        }
    })
    .catch(error => {
        console.error('Error sending question feedback:', error);
    });
}
