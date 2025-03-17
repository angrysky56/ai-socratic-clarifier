#!/usr/bin/env python3
"""
Updated fix for SRE and SoT integration issues in the AI-Socratic-Clarifier.

This script ensures that both the Sequential of Thought (SoT) and Symbiotic Reflective
Ecosystem (SRE) are properly integrated and working correctly in the UI.
"""

import os
import sys
import json
import shutil
from loguru import logger

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../..'))
sys.path.insert(0, project_root)

def check_sot_integration():
    """Check and fix SoT integration."""
    try:
        # Import SoT integration
        from socratic_clarifier.core import import_sot
        has_sot = import_sot()
        
        logger.info(f"SoT integration available: {has_sot}")
        
        # Check if we have the model directory
        sot_dir = os.path.join(project_root, 'sot_2e9hb5_3')
        if os.path.exists(sot_dir):
            logger.info(f"Found SoT directory: {sot_dir}")
        else:
            logger.warning(f"SoT directory not found at: {sot_dir}")
            logger.warning("Run install_sot.py to install SoT.")
        
        return has_sot
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
        if isinstance(test_result, dict) and ("reasoning_paths" in test_result or "meta_meta_stage" in test_result):
            logger.info("SRE integration is working correctly")
            return True
        else:
            logger.warning("SRE integration is not returning the expected structure")
            logger.debug(f"SRE test result: {test_result}")
            return False
            
    except Exception as e:
        logger.error(f"Error checking SRE integration: {e}")
        return False

def check_ecosystem_state():
    """Check and fix the ecosystem state file."""
    try:
        # Look for existing ecosystem state
        state_path = os.path.join(project_root, 'sequential_thinking', 'ecosystem_state.json')
        
        if not os.path.exists(state_path):
            logger.info("Ecosystem state file doesn't exist, creating default state")
            
            # Make sure the directory exists
            os.makedirs(os.path.dirname(state_path), exist_ok=True)
            
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
            # Validate the file is a valid JSON
            try:
                with open(state_path, 'r') as f:
                    ecosystem_state = json.load(f)
                logger.info("Ecosystem state is valid JSON")
                return True
            except json.JSONDecodeError:
                logger.error("Ecosystem state file is invalid JSON")
                backup_path = f"{state_path}.invalid_backup"
                logger.info(f"Backing up invalid state to {backup_path}")
                shutil.copy2(state_path, backup_path)
                logger.info("Creating a new default state")
                # Call this function again to create default state
                os.remove(state_path)
                return check_ecosystem_state()
            
    except Exception as e:
        logger.error(f"Error checking ecosystem state: {e}")
        return False

def check_frontend_scripts():
    """Check SRE visualization and CSS files in the UI."""
    try:
        # Check for visualization JS file
        js_path = os.path.join(project_root, 'web_interface', 'static', 'js', 'enhanced', 'sre_visualization.js')
        
        if not os.path.exists(js_path):
            logger.warning(f"SRE visualization JS file not found at: {js_path}")
            return False
        
        # Check for CSS file
        css_path = os.path.join(project_root, 'web_interface', 'static', 'css', 'enhanced', 'sre_visualization.css')
        
        if not os.path.exists(css_path):
            logger.warning(f"SRE visualization CSS file not found at: {css_path}")
            return False
        
        logger.info("All SRE frontend files are present")
        return True
        
    except Exception as e:
        logger.error(f"Error checking SRE frontend scripts: {e}")
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
    
    # Check frontend scripts
    logger.info("Checking SRE frontend files...")
    scripts_ok = check_frontend_scripts()
    if not scripts_ok:
        logger.warning("SRE frontend files have issues")
        success = False
    else:
        logger.info("✅ SRE frontend files look good")
    
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
