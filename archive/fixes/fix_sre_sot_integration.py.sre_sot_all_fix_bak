#!/usr/bin/env python3
"""
Fix for SRE and SoT integration issues in the AI-Socratic-Clarifier.

This script ensures that both the Sequential of Thought (SoT) and Symbiotic Reflective
Ecosystem (SRE) are properly integrated and working correctly in the UI.
"""

import os
import sys
import json
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def check_sot_integration():
    """Check and fix SoT integration."""
    try:
        # Import SoT integration
        from socratic_clarifier.integrations.sot_integration import SoTIntegration
        
        # Create a test instance
        sot = SoTIntegration()
        
        logger.info(f"SoT integration available: {sot.available}")
        
        # Check if initialization was successful
        if not sot.available:
            logger.warning("SoT integration is not fully available, trying to fix...")
            
            # Check if we have the model directory
            sot_dir = os.path.join(os.path.dirname(__file__), 'sot_2e9hb5_3')
            if os.path.exists(sot_dir):
                logger.info(f"Found SoT directory: {sot_dir}")
            else:
                logger.warning(f"SoT directory not found at: {sot_dir}")
                logger.warning("Run install_sot.py to install SoT.")
        
        return sot.available
    except Exception as e:
        logger.error(f"Error checking SoT integration: {e}")
        return False

def check_sre_integration():
    """Check and fix SRE integration."""
    try:
        # Import enhanced reflective ecosystem
        from enhanced_integration.enhanced_reflective_ecosystem import EnhancedReflectiveEcosystem, get_enhanced_ecosystem
        
        # Create a test instance
        ecosystem = get_enhanced_ecosystem()
        
        # Test if reasoning context generation works
        test_result = ecosystem.apply_enhancement(
            text="This is a test",
            issues=[{"issue": "vagueness", "term": "test", "confidence": 0.8}],
            paradigm="conceptual_chaining"
        )
        
        # Check if it's returning the expected structure
        if "reasoning_paths" in test_result:
            logger.info("SRE integration is working correctly")
            return True
        else:
            logger.warning("SRE integration is not returning reasoning paths")
            return False
            
    except Exception as e:
        logger.error(f"Error checking SRE integration: {e}")
        return False

def check_ecosystem_state():
    """Check and fix the ecosystem state file."""
    try:
        # Look for existing ecosystem state
        state_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')), 'sequential_thinking', 'ecosystem_state.json')
        
        if not os.path.exists(state_path):
            logger.info("Ecosystem state file doesn't exist, creating default state")
            
            # Create a minimal state file
            default_state = {
                "nodes": {
                    "conceptual_chaining": {
                        "id": "conceptual_chaining",
                        "name": "Conceptual Chaining",
                        "count": 0,
                        "success_count": 0
                    },
                    "chunked_symbolism": {
                        "id": "chunked_symbolism",
                        "name": "Chunked Symbolism",
                        "count": 0,
                        "success_count": 0
                    },
                    "expert_lexicons": {
                        "id": "expert_lexicons",
                        "name": "Expert Lexicons",
                        "count": 0,
                        "success_count": 0
                    }
                },
                "global_coherence": 0.8,
                "question_history": [],
                "meta_meta_framework": {
                    "principle_of_inquiry": "Improve critical thinking through effective Socratic questioning",
                    "dimensional_axes": {
                        "reasoning_approach": {
                            "description": "Reasoning approach to use",
                            "values": ["conceptual_chaining", "chunked_symbolism", "expert_lexicons", "socratic_questioning"]
                        },
                        "question_focus": {
                            "description": "Focus area for generated questions",
                            "values": ["definitions", "evidence", "assumptions", "implications", "alternatives"]
                        },
                        "complexity_level": {
                            "description": "Complexity level of exploration",
                            "values": ["simple", "moderate", "complex"]
                        }
                    },
                    "constraints": [
                        {"constraint": "Questions must be genuinely helpful", "purpose": "Ensure practical value"},
                        {"constraint": "Questions must address specific issues", "purpose": "Maintain relevance"},
                        {"constraint": "Questions should be open-ended", "purpose": "Encourage deeper thinking"}
                    ],
                    "controlled_emergence": 0.3,
                    "feedback_loops": [
                        {
                            "name": "Question effectiveness",
                            "metric": "user_feedback",
                            "current_value": 0.5,
                            "target_value": 0.8
                        },
                        {
                            "name": "Reasoning coherence",
                            "metric": "global_coherence",
                            "current_value": 0.8,
                            "target_value": 0.9
                        },
                        {
                            "name": "Paradigm selection accuracy",
                            "metric": "paradigm_accuracy",
                            "current_value": 0.5,
                            "target_value": 0.85
                        }
                    ],
                    "adaptive_flexibility": 0.5
                },
                "intellisynth": {
                    "truth_value": 0.7,
                    "scrutiny_value": 0.0,
                    "improvement_value": 0.0,
                    "advancement": 0.0,
                    "alpha": 0.5,
                    "beta": 0.5
                }
            }
            
            # Save the default state
            with open(state_path, 'w') as f:
                json.dump(default_state, f, indent=2)
            
            logger.info(f"Created default ecosystem state at: {state_path}")
            return True
        else:
            logger.info(f"Ecosystem state file exists at: {state_path}")
            return True
            
    except Exception as e:
        logger.error(f"Error checking ecosystem state: {e}")
        return False

def fix_sre_frontend_scripts():
    """Fix SRE visualization in the frontend."""
    try:
        # Check if the visualization JS file exists
        js_path = os.path.join(os.path.dirname(__file__), 'web_interface', 'static', 'js', 'enhanced', 'sre_visualization.js')
        
        if not os.path.exists(js_path):
            logger.warning(f"SRE visualization JS file not found at: {js_path}")
            
            # Create directory if needed
            os.makedirs(os.path.dirname(js_path), exist_ok=True)
            
            # Create a basic visualization script
            with open(js_path, 'w') as f:
                f.write("""/**
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
""")
            
            logger.info(f"Created basic SRE visualization script at: {js_path}")
        
        # Check if the CSS file exists
        css_path = os.path.join(os.path.dirname(__file__), 'web_interface', 'static', 'css', 'enhanced', 'sre_visualization.css')
        
        if not os.path.exists(css_path):
            logger.warning(f"SRE visualization CSS file not found at: {css_path}")
            
            # Create directory if needed
            os.makedirs(os.path.dirname(css_path), exist_ok=True)
            
            # Create a basic CSS file
            with open(css_path, 'w') as f:
                f.write("""/* SRE Visualization Styles */

/* Meta-Meta Framework Visualization */
.meta-meta-visualization {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background-color: var(--card-bg, #f8f9fa);
    border-radius: 8px;
    margin-bottom: 15px;
}

.meta-meta-stage {
    text-align: center;
    padding: 5px;
    width: 70px;
    border-radius: 5px;
    position: relative;
    font-size: 0.7rem;
    cursor: help;
}

.meta-meta-stage:not(:last-child)::after {
    content: "→";
    position: absolute;
    right: -15px;
    top: 50%;
    transform: translateY(-50%);
}

.meta-meta-stage.active {
    background-color: var(--primary, #0d6efd);
    color: white;
    font-weight: bold;
}

/* Network Visualization */
.network-visualization {
    min-height: 200px;
    background-color: var(--card-bg, #f8f9fa);
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
}

.network-placeholder {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    color: var(--text-muted, #6c757d);
    font-style: italic;
}

/* Reasoning Paths */
.reasoning-paths {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.reasoning-path {
    border: 1px solid var(--border-color, #dee2e6);
    border-radius: 6px;
    overflow: hidden;
}

.path-name {
    background-color: var(--secondary-bg, #e9ecef);
    padding: 8px 12px;
    font-weight: bold;
    border-bottom: 1px solid var(--border-color, #dee2e6);
}

.path-steps {
    padding: 8px 12px;
}

.path-steps ol {
    margin: 0;
    padding-left: 20px;
}

.path-steps li {
    margin-bottom: 5px;
}

/* Global stats */
.sre-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background-color: var(--card-bg, #f8f9fa);
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 0.8rem;
}

.advancement-container {
    width: 150px;
    height: 8px;
    background-color: var(--border-color, #dee2e6);
    border-radius: 4px;
    overflow: hidden;
}

.advancement-indicator {
    height: 100%;
    background-color: var(--success, #198754);
    width: 0%;
    transition: width 0.5s ease;
}
""")
            
            logger.info(f"Created basic SRE visualization CSS at: {css_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error fixing SRE frontend scripts: {e}")
        return False

def fix_sre_sot_integration():
    """Fix SRE and SoT integration issues."""
    success = True
    
    # Check SoT integration
    logger.info("Checking SoT integration...")
    sot_ok = check_sot_integration()
    if not sot_ok:
        logger.warning("SoT integration has issues")
        success = False
    else:
        logger.info("✅ SoT integration looks good")
    
    # Check SRE integration
    logger.info("Checking SRE integration...")
    sre_ok = check_sre_integration()
    if not sre_ok:
        logger.warning("SRE integration has issues")
        success = False
    else:
        logger.info("✅ SRE integration looks good")
    
    # Fix ecosystem state
    logger.info("Checking ecosystem state...")
    state_ok = check_ecosystem_state()
    if not state_ok:
        logger.warning("Ecosystem state has issues")
        success = False
    else:
        logger.info("✅ Ecosystem state looks good")
    
    # Fix SRE frontend scripts
    logger.info("Checking SRE frontend scripts...")
    scripts_ok = fix_sre_frontend_scripts()
    if not scripts_ok:
        logger.warning("SRE frontend scripts have issues")
        success = False
    else:
        logger.info("✅ SRE frontend scripts look good")
    
    return success

if __name__ == "__main__":
    try:
        if fix_sre_sot_integration():
            logger.info("✨ Successfully fixed SRE and SoT integration issues")
            sys.exit(0)
        else:
            logger.error("⚠️ Some SRE and SoT integration issues could not be fixed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error fixing SRE and SoT integration: {e}")
        sys.exit(1)
