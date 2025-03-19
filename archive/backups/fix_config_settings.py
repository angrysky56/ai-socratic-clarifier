#!/usr/bin/env python3
"""
Fix configuration settings for SRE and SoT integration.

This script ensures that the config.json file contains all necessary settings
for the SRE and SoT components to work correctly.
"""

import os
import json
import logging
import shutil
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_config_settings():
    """Fix SRE and SoT configuration settings."""
    config_path = os.path.join("/home/ty/Repositories/ai_workspace/ai-socratic-clarifier", "config.json")
    
    if not os.path.exists(config_path):
        logger.error(f"Config file not found at: {config_path}")
        
        # Try to use the example config as a base
        example_path = os.path.join("/home/ty/Repositories/ai_workspace/ai-socratic-clarifier", "config.example.json")
        if os.path.exists(example_path):
            logger.info(f"Using example config from: {example_path}")
            shutil.copy2(example_path, config_path)
        else:
            logger.error("No example config found. Cannot continue.")
            return False
    
    # Backup the config file
    backup_path = f"{config_path}.settings_fix_bak"
    logger.info(f"Creating backup to {backup_path}")
    shutil.copy2(config_path, backup_path)
    
    try:
        # Load the current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Make sure 'settings' section exists
        if 'settings' not in config:
            config['settings'] = {}
        
        # Fix SRE settings
        logger.info("Applying SRE settings...")
        config['settings']['sre_global_resonance'] = config['settings'].get('sre_global_resonance', 0.8)
        config['settings']['sre_adaptive_flexibility'] = config['settings'].get('sre_adaptive_flexibility', 0.5)
        config['settings']['use_sre_visualization'] = config['settings'].get('use_sre_visualization', True)
        config['settings']['auto_expand_sre'] = config['settings'].get('auto_expand_sre', True)
        
        # Fix SoT settings
        logger.info("Applying SoT settings...")
        if 'sot' not in config['settings']:
            config['settings']['sot'] = {}
        
        config['settings']['sot']['default_paradigm'] = config['settings']['sot'].get('default_paradigm', 'auto')
        config['settings']['use_sot'] = config['settings'].get('use_sot', True)
        config['settings']['use_llm_questions'] = config['settings'].get('use_llm_questions', True)
        config['settings']['use_llm_reasoning'] = config['settings'].get('use_llm_reasoning', True)
        
        # Ensure both SRE and SoT ecosystem paths are correct
        if 'ecosystem_state_path' not in config['settings']:
            config['settings']['ecosystem_state_path'] = 'sequential_thinking/ecosystem_state.json'
        
        # Add ecosystem state path for both locations
        sequential_thinking_dir = os.path.join("/home/ty/Repositories/ai_workspace/ai-socratic-clarifier", "sequential_thinking")
        archive_dir = os.path.join("/home/ty/Repositories/ai_workspace/ai-socratic-clarifier", "archive", "fixes", "sequential_thinking")
        
        # Create directories if needed
        os.makedirs(sequential_thinking_dir, exist_ok=True)
        os.makedirs(archive_dir, exist_ok=True)
        
        # Copy ecosystem state to both locations if needed
        ecosystem_state = os.path.join(sequential_thinking_dir, "ecosystem_state.json")
        archive_ecosystem_state = os.path.join(archive_dir, "ecosystem_state.json")
        
        # If one location has the file but not the other, copy it
        if os.path.exists(ecosystem_state) and not os.path.exists(archive_ecosystem_state):
            logger.info(f"Copying ecosystem state to archive...")
            shutil.copy2(ecosystem_state, archive_ecosystem_state)
        elif os.path.exists(archive_ecosystem_state) and not os.path.exists(ecosystem_state):
            logger.info(f"Copying ecosystem state from archive...")
            shutil.copy2(archive_ecosystem_state, ecosystem_state)
        # If neither location has the file, create a default one
        elif not os.path.exists(ecosystem_state) and not os.path.exists(archive_ecosystem_state):
            logger.info("Creating default ecosystem state...")
            
            # Create a default ecosystem state
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
            
            # Write to both locations
            with open(ecosystem_state, 'w') as f:
                json.dump(default_state, f, indent=2)
            
            with open(archive_ecosystem_state, 'w') as f:
                json.dump(default_state, f, indent=2)
        
        # Save the updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info("Successfully updated config settings")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing config settings: {e}")
        return False

if __name__ == "__main__":
    try:
        if fix_config_settings():
            logger.info("✨ Successfully fixed config settings")
        else:
            logger.error("❌ Failed to fix config settings")
    except Exception as e:
        logger.error(f"Error: {e}")
