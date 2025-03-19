/**
 * Socratic reasoning settings management for AI-Socratic-Clarifier
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize socratic reasoning settings from config
    initializeSocraticSettings();
    
    // Set up event listeners
    setupSocraticSettingsEvents();
});

/**
 * Initialize socratic reasoning settings from the server config
 */
function initializeSocraticSettings() {
    fetch('/api/settings')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.config && data.config.settings && data.config.settings.socratic_reasoning) {
                const socraticSettings = data.config.settings.socratic_reasoning;
                
                // Set switch state
                const socraticEnabledSwitch = document.getElementById('socraticReasoningSwitch');
                if (socraticEnabledSwitch) {
                    socraticEnabledSwitch.checked = socraticSettings.enabled !== false;
                }
                
                // Set reasoning depth
                const reasoningDepthSelect = document.getElementById('reasoningDepth');
                if (reasoningDepthSelect && socraticSettings.reasoning_depth) {
                    reasoningDepthSelect.value = socraticSettings.reasoning_depth;
                }
                
                // Set system prompt
                const systemPromptTextarea = document.getElementById('systemPrompt');
                if (systemPromptTextarea && socraticSettings.system_prompt) {
                    systemPromptTextarea.value = socraticSettings.system_prompt;
                }
            }
        })
        .catch(error => {
            console.error('Error fetching socratic settings:', error);
        });
}

/**
 * Set up event listeners for socratic settings controls
 */
function setupSocraticSettingsEvents() {
    // Save socratic settings button
    const saveButton = document.getElementById('saveSocraticSettings');
    if (saveButton) {
        saveButton.addEventListener('click', saveSocraticSettings);
    }
}

/**
 * Save socratic reasoning settings to the server
 */
function saveSocraticSettings() {
    // Get values from form
    const socraticEnabled = document.getElementById('socraticReasoningSwitch').checked;
    const reasoningDepth = document.getElementById('reasoningDepth').value;
    const systemPrompt = document.getElementById('systemPrompt').value;
    
    // Create settings object
    const settings = {
        socratic_reasoning: {
            enabled: socraticEnabled,
            reasoning_depth: reasoningDepth,
            system_prompt: systemPrompt
        }
    };
    
    // Send to server
    fetch('/api/settings/socratic', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            alert('Socratic reasoning settings saved successfully!');
        } else {
            // Show error message
            alert('Error saving settings: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error saving socratic settings:', error);
        alert('Error saving settings. See console for details.');
    });
}
