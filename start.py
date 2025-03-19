#!/usr/bin/env python3
"""
AI-Socratic-Clarifier Start Script

This is the single entry point to run the AI-Socratic-Clarifier with all optimizations.
Features:
- Ollama optimizations (context length, flash attention, etc.)
- Document management with RAG support
- Multimodal processing for images and PDFs
- Unified UI at /socratic
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def set_ollama_optimizations():
    """Set Ollama optimization environment variables."""
    os.environ["OLLAMA_CONTEXT_LENGTH"] = "8192"
    os.environ["OLLAMA_FLASH_ATTENTION"] = "1"
    os.environ["OLLAMA_KV_CACHE_TYPE"] = "q8_0"
    logger.info("Set Ollama optimization environment variables")

def ensure_config():
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
            settings["use_document_rag"] = True
            
            # Write updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Updated config.json with optimized settings")
        else:
            logger.error(f"Configuration file not found at {config_path}")
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")

def ensure_directories():
    """Ensure necessary directories exist."""
    # Create document storage directories
    storage_dir = os.path.join(os.path.dirname(__file__), 'document_storage')
    os.makedirs(storage_dir, exist_ok=True)
    
    # Create necessary subdirectories
    subdirs = ['raw', 'processed', 'embeddings', 'temp']
    for subdir in subdirs:
        os.makedirs(os.path.join(storage_dir, subdir), exist_ok=True)
    
    # Create web interface directories
    templates_dir = os.path.join(os.path.dirname(__file__), 'web_interface', 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    static_dir = os.path.join(os.path.dirname(__file__), 'web_interface', 'static')
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'img'), exist_ok=True)
    
    # Create feedback directory
    feedback_dir = os.path.join(os.path.dirname(__file__), 'web_interface', 'feedback')
    os.makedirs(feedback_dir, exist_ok=True)
    
    logger.info("Ensured all necessary directories exist")

def check_environment():
    """Check the environment for dependencies and models."""
    try:
        # Check for Ollama connection
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=1)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name') for m in models]
                
                # Load config
                config_path = os.path.join(os.path.dirname(__file__), 'config.json')
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    default_model = config.get('integrations', {}).get('ollama', {}).get('default_model', 'gemma3:latest')
                    multimodal_model = config.get('integrations', {}).get('ollama', {}).get('multimodal_model', 'llava:latest')
                    
                    if default_model in model_names:
                        logger.info(f"✅ Default model '{default_model}' is available")
                    else:
                        logger.warning(f"⚠️ Default model '{default_model}' not found in Ollama")
                        available_models = ", ".join(model_names[:5])
                        if len(model_names) > 5:
                            available_models += f" and {len(model_names)-5} more"
                        logger.warning(f"  Available models: {available_models}")
                    
                    if multimodal_model in model_names:
                        logger.info(f"✅ Multimodal model '{multimodal_model}' is available")
                    else:
                        logger.warning(f"⚠️ Multimodal model '{multimodal_model}' not found in Ollama")
                        logger.warning(f"  You can install it with: ollama pull {multimodal_model}")
            else:
                logger.warning("⚠️ Ollama is not responding - models may not be available")
        except Exception as e:
            logger.warning(f"⚠️ Ollama connection failed - ensure Ollama is running: {e}")
        
        # Check SRE and SoT integration
        try:
            from socratic_clarifier.integrations.sot_integration import SoTIntegration
            sot = SoTIntegration()
            logger.info(f"✅ SoT integration available: {sot.available}")
        except Exception as e:
            logger.warning(f"⚠️ SoT integration issue: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Error checking environment: {e}")
        return False

def main():
    """Run the AI-Socratic-Clarifier."""
    parser = argparse.ArgumentParser(description='Start the AI-Socratic-Clarifier')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--no-checks', action='store_true', help='Skip environment checks')
    parser.add_argument('--no-ollama-opt', action='store_true', help='Skip Ollama optimizations')
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("   AI-Socratic-Clarifier")
    print("   with Optimized Settings and Unified UI")
    print("="*70 + "\n")
    
    logger.info("Starting AI-Socratic-Clarifier...")
    
    # Apply Ollama optimizations
    if not args.no_ollama_opt:
        set_ollama_optimizations()
    
    # Ensure configuration and directories
    ensure_config()
    ensure_directories()
    
    # Check environment unless disabled
    if not args.no_checks:
        check_environment()
    
    try:
        # Import Flask app
        from web_interface.app import app as flask_app
        
        # Display startup information
        logger.info("\n" + "*"*60)
        logger.info("*  AI-Socratic-Clarifier Web Interface                   *")
        logger.info("*" + " "*58 + "*")
        logger.info(f"*  Web interface: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}  *")
        logger.info("*  Socratic UI: /socratic                                *")
        if args.debug:
            logger.info("*  RUNNING IN DEBUG MODE                                 *")
        logger.info("*"*60 + "\n")
        
        # Run the app
        logger.info(f"Starting web interface on {args.host}:{args.port}")
        flask_app.run(host=args.host, port=args.port, debug=args.debug)
        
    except Exception as e:
        logger.error(f"Error starting the web interface: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
