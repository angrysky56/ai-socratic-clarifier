#!/usr/bin/env python3
"""
AI-Socratic-Clarifier Web Interface

This script starts the integrated web interface with:
- Symbiotic Reflective Ecosystem (SRE) integration
- Sequential of Thought (SoT) integration 
- Unified document management
- Single-page UI with tabbed interface
- Multimodal support for images and documents
- Meta-Meta Framework for enhanced reasoning
"""

import os
import sys
import argparse
import traceback
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def check_environment():
    """Check and prepare the environment before starting."""
    try:
        # Check document storage
        from enhanced_integration.document_manager import get_document_manager
        document_manager = get_document_manager()
        
        # Ensure document directories exist
        storage_dir = document_manager.storage_dir
        if not os.path.exists(storage_dir):
            logger.warning(f"Document storage directory not found, creating: {storage_dir}")
            os.makedirs(storage_dir, exist_ok=True)
        
        # Check for document index
        index_file = os.path.join(storage_dir, 'document_index.json')
        if not os.path.exists(index_file):
            logger.warning("Document index not found, will be created on startup")
        
        # Check for multimodal support
        try:
            from socratic_clarifier.multimodal_integration import check_dependencies
            multimodal_status = check_dependencies()
            
            if all(multimodal_status.values()):
                logger.info("✅ Multimodal support is fully available")
            else:
                logger.warning("⚠️ Some multimodal dependencies are missing:")
                for dep, status in multimodal_status.items():
                    logger.warning(f"  - {dep}: {'✅' if status else '❌'}")
                logger.warning("Consider running `python install_dependencies.py` to fix")
        except ImportError:
            logger.warning("⚠️ Multimodal integration not available")
        
        # Check for Ollama connection
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=1)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name') for m in models]
                
                # Load config
                import json
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
                        logger.warning(f"  Available models: {', '.join(model_names[:5])}" + 
                                      (f" and {len(model_names)-5} more" if len(model_names) > 5 else ""))
                    
                    if multimodal_model in model_names:
                        logger.info(f"✅ Multimodal model '{multimodal_model}' is available")
                    else:
                        logger.warning(f"⚠️ Multimodal model '{multimodal_model}' not found in Ollama")
                        logger.warning(f"  You can install it with: ollama pull {multimodal_model}")
            else:
                logger.warning("⚠️ Ollama is not responding - models may not be available")
        except Exception:
            logger.warning("⚠️ Ollama connection failed - ensure Ollama is running")
        
        # Check SRE integration
        try:
            # First try enhanced version
            try:
                from enhanced_integration.enhanced_reflective_ecosystem import get_enhanced_ecosystem
                ecosystem = get_enhanced_ecosystem()
                logger.info("✅ Enhanced Reflective Ecosystem is available")
                
                # Check Meta-Meta Framework
                if hasattr(ecosystem, 'meta_meta_components'):
                    logger.info("✅ Meta-Meta Framework is available")
                else:
                    logger.warning("⚠️ Meta-Meta Framework is not fully integrated")
            except ImportError:
                # Fall back to basic version
                from sequential_thinking.reflective_ecosystem import ReflectiveEcosystem
                ecosystem = ReflectiveEcosystem()
                logger.info("✅ Basic Reflective Ecosystem is available")
                logger.warning("⚠️ Enhanced Reflective Ecosystem not available")
        except Exception as e:
            logger.warning(f"⚠️ Reflective Ecosystem issue: {e}")
        
        # Check SoT integration
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
    """Run the AI-Socratic-Clarifier integrated web interface."""
    parser = argparse.ArgumentParser(description='Start the AI-Socratic-Clarifier integrated web interface')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--no-checks', action='store_true', help='Skip environment checks')
    parser.add_argument('--lite', action='store_true', help='Use the lite UI version to avoid navbar duplication')
    args = parser.parse_args()
    
    logger.info("Starting AI-Socratic-Clarifier...")
    
    # Check environment unless disabled
    if not args.no_checks:
        logger.info("Checking environment...")
        check_environment()
    
    try:
        # Import Flask app
        from web_interface.app import app as flask_app
        
        # Initialize enhanced components
        from enhanced_integration.integration import get_enhanced_enhancer
        from enhanced_integration.document_manager import get_document_manager
        
        # Get enhancer and document manager to initialize them
        enhancer = get_enhanced_enhancer()
        document_manager = get_document_manager()
        
        logger.info(f"Enhanced Reflective Enhancer initialized: {enhancer.initialized}")
        logger.info(f"Document Manager initialized with storage at: {document_manager.storage_dir}")
        
        # Display startup information
        logger.info("\n" + "*" * 60)
        logger.info("*  AI-Socratic-Clarifier Web Interface                   *")
        logger.info("*  " + " " * 54 + " *")
        logger.info(f"*  Web interface: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}  *")
        logger.info("*  Socratic UI: /socratic                                *")
        if args.debug:
            logger.info("*  RUNNING IN DEBUG MODE                                 *")
        logger.info("*" * 60 + "\n")
        
        # Run the app
        logger.info(f"Starting web interface on {args.host}:{args.port}")
        flask_app.run(host=args.host, port=args.port, debug=args.debug)
        
    except Exception as e:
        logger.error(f"Error starting the web interface: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()
