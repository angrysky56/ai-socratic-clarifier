#!/usr/bin/env python3
"""
Optimized start script for AI-Socratic-Clarifier
This script ensures proper initialization of all components
and uses optimized settings for Ollama.
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def set_ollama_env_vars():
    """Set Ollama optimization environment variables."""
    os.environ["OLLAMA_CONTEXT_LENGTH"] = "8192"
    os.environ["OLLAMA_FLASH_ATTENTION"] = "1"
    os.environ["OLLAMA_KV_CACHE_TYPE"] = "q8_0"
    logger.info("Set Ollama optimization environment variables")

def update_config():
    """Ensure config.json has correct settings."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Ensure Ollama settings are correct
            if "integrations" not in config:
                config["integrations"] = {}
            
            if "ollama" not in config["integrations"]:
                config["integrations"]["ollama"] = {}
            
            ollama_config = config["integrations"]["ollama"]
            
            # Set optimized settings
            ollama_config["context_length"] = 8192
            
            # Ensure multimodal settings
            if "multimodal_model" not in ollama_config:
                ollama_config["multimodal_model"] = "llava:latest"
            
            # Ensure settings are correct
            if "settings" not in config:
                config["settings"] = {}
            
            settings = config["settings"]
            settings["use_multimodal"] = True
            settings["use_sot"] = True
            settings["use_llm_reasoning"] = True
            
            # Write updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Updated config.json with optimized settings")
        else:
            logger.error(f"Configuration file not found at {config_path}")
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")

def ensure_document_storage():
    """Ensure document storage directory exists."""
    storage_dir = os.path.join(os.path.dirname(__file__), 'document_storage')
    os.makedirs(storage_dir, exist_ok=True)
    
    # Create necessary subdirectories
    subdirs = ['raw', 'processed', 'embeddings', 'temp']
    for subdir in subdirs:
        os.makedirs(os.path.join(storage_dir, subdir), exist_ok=True)
    
    logger.info(f"Ensured document storage directory at {storage_dir}")

def start_ui():
    """Start the UI with the standard script."""
    print("\nAccess the unified Socratic UI at: http://localhost:5000/socratic")
    
    try:
        import start_ui
        logger.info("Starting UI...")
        start_ui.main()
    except ImportError:
        try:
            # Fallback: Try running as script
            subprocess.run([sys.executable, "start_ui.py"])
        except Exception as e:
            logger.error(f"Error starting UI: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("=" * 70)
    print("   Optimized AI-Socratic-Clarifier Startup")
    print("   with Enhanced Multimodal and RAG Support")
    print("=" * 70)
    
    # Setup steps
    set_ollama_env_vars()
    update_config()
    ensure_document_storage()
    
    # Start UI
    start_ui()
