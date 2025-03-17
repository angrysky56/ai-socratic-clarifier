#!/usr/bin/env python3
"""
Script to apply fixes to the AI-Socratic-Clarifier:
1. Fixes the duplicate navbar issue
2. Adds document deletion functionality
3. Ensures vector database is properly set up
"""

import os
import sys
import shutil
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

def backup_file(file_path):
    """Create a backup of a file with .bak extension."""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak"
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    return False

def apply_ui_fixes():
    """Apply UI fixes for the duplicate navbar and document management."""
    logger.info("Applying UI fixes...")
    
    # Copy the fixed app.py
    src_file = os.path.join(script_dir, "web_interface", "fixed_app.py")
    dst_file = os.path.join(script_dir, "web_interface", "app.py")
    if os.path.exists(src_file):
        backup_file(dst_file)
        shutil.copy2(src_file, dst_file)
        logger.info(f"Applied app.py fixes (replaced with fixed_app.py)")
    else:
        logger.error(f"Fixed app file not found: {src_file}")

    # Copy the fixed integrated UI template
    src_file = os.path.join(script_dir, "web_interface", "templates", "fixed_integrated_ui.html")
    os.makedirs(os.path.join(script_dir, "web_interface", "templates"), exist_ok=True)
    dst_file = os.path.join(script_dir, "web_interface", "templates", "integrated_ui.html")
    if os.path.exists(src_file):
        backup_file(dst_file)
        shutil.copy2(src_file, dst_file)
        logger.info(f"Applied integrated UI template fixes")
    else:
        logger.error(f"Fixed integrated UI template not found: {src_file}")

    # Copy the document preview modal
    os.makedirs(os.path.join(script_dir, "web_interface", "templates", "components"), exist_ok=True)
    src_file = os.path.join(script_dir, "web_interface", "templates", "components", "document_preview_modal.html")
    dst_file = os.path.join(script_dir, "web_interface", "templates", "components", "document_preview_modal.html")
    if os.path.exists(src_file):
        logger.info(f"Document preview modal template already exists")
    else:
        logger.error(f"Document preview modal template not found: {src_file}")

    # Copy the document manager with delete functionality
    src_file = os.path.join(script_dir, "web_interface", "static", "js", "enhanced", "document_manager_delete.js")
    dst_file = os.path.join(script_dir, "web_interface", "static", "js", "enhanced", "document_manager.js")
    if os.path.exists(src_file):
        backup_file(dst_file)
        shutil.copy2(src_file, dst_file)
        logger.info(f"Applied document manager fixes for delete functionality")
    else:
        logger.error(f"Fixed document manager file not found: {src_file}")
    
    # Copy the fixed document_rag_routes.py
    src_file = os.path.join(script_dir, "web_interface", "fixed_document_rag_routes.py")
    dst_file = os.path.join(script_dir, "web_interface", "document_rag_routes.py")
    if os.path.exists(src_file):
        backup_file(dst_file)
        shutil.copy2(src_file, dst_file)
        logger.info(f"Applied document_rag_routes.py fixes for document deletion")
    else:
        logger.error(f"Fixed document routes file not found: {src_file}")
        
    # Copy the fixed settings routes
    src_file = os.path.join(script_dir, "web_interface", "fixed_settings_routes.py")
    dst_file = os.path.join(script_dir, "web_interface", "fixed_settings_routes.py")
    if not os.path.exists(dst_file) and os.path.exists(src_file):
        shutil.copy2(src_file, dst_file)
        logger.info(f"Applied settings routes fixes")
    else:
        logger.info(f"Settings routes already exist")
    
    # Copy the fixed settings page template
    src_file = os.path.join(script_dir, "web_interface", "templates", "fixed_settings_page.html")
    dst_file = os.path.join(script_dir, "web_interface", "templates", "fixed_settings_page.html")
    if not os.path.exists(dst_file) and os.path.exists(src_file):
        shutil.copy2(src_file, dst_file)
        logger.info(f"Applied settings page template fixes")
    else:
        logger.info(f"Settings page template already exists")

def check_vector_db_setup():
    """Check if the vector database is properly set up."""
    logger.info("Checking vector database setup...")
    
    # Check if the configuration has embedding model set
    config_path = os.path.join(script_dir, "config.json")
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        config_updated = False
        
        # Check if the embedding model is configured
        if 'integrations' in config and 'ollama' in config['integrations']:
            # Check for embedding model
            if 'default_embedding_model' not in config['integrations']['ollama']:
                config['integrations']['ollama']['default_embedding_model'] = 'nomic-embed-text:latest'
                logger.info("Added default embedding model 'nomic-embed-text:latest' to config.json")
                config_updated = True
            else:
                logger.info(f"Found embedding model in config: {config['integrations']['ollama']['default_embedding_model']}")
            
            # Check for multimodal model
            if 'multimodal_model' not in config['integrations']['ollama']:
                config['integrations']['ollama']['multimodal_model'] = 'llava:latest'
                logger.info("Added default multimodal model 'llava:latest' to config.json")
                config_updated = True
            else:
                logger.info(f"Found multimodal model in config: {config['integrations']['ollama']['multimodal_model']}")
                
            # Save config if updated
            if config_updated:
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=4)
                
                # Check if Ollama is available and try to pull the models
                try:
                    import requests
                    
                    # Check for embedding model
                    embedding_model = config['integrations']['ollama']['default_embedding_model']
                    try:
                        logger.info(f"Checking if embedding model {embedding_model} exists...")
                        response = requests.get("http://localhost:11434/api/tags")
                        if response.status_code == 200:
                            # Check if the embedding model exists
                            models = response.json().get("models", [])
                            model_names = [model.get("name") for model in models]
                            
                            if embedding_model not in model_names:
                                logger.info(f"Embedding model not found in Ollama. Pulling {embedding_model}...")
                                # Try to pull the model
                                pull_response = requests.post(
                                    "http://localhost:11434/api/pull",
                                    json={"name": embedding_model}
                                )
                                
                                if pull_response.status_code == 200:
                                    logger.info("Successfully pulled embedding model")
                                else:
                                    logger.warning(f"Failed to pull embedding model: {pull_response.text}")
                                    logger.warning(f"You may need to manually run: ollama pull {embedding_model}")
                            else:
                                logger.info("Embedding model already exists in Ollama")
                    except Exception as e:
                        logger.warning(f"Error checking embedding model: {e}")
                    
                    # Check for multimodal model
                    multimodal_model = config['integrations']['ollama']['multimodal_model']
                    try:
                        logger.info(f"Checking if multimodal model {multimodal_model} exists...")
                        response = requests.get("http://localhost:11434/api/tags")
                        if response.status_code == 200:
                            # Check if the multimodal model exists
                            models = response.json().get("models", [])
                            model_names = [model.get("name") for model in models]
                            
                            if multimodal_model not in model_names:
                                logger.info(f"Multimodal model not found in Ollama. Pulling {multimodal_model}...")
                                # Try to pull the model
                                pull_response = requests.post(
                                    "http://localhost:11434/api/pull",
                                    json={"name": multimodal_model}
                                )
                                
                                if pull_response.status_code == 200:
                                    logger.info("Successfully pulled multimodal model")
                                else:
                                    logger.warning(f"Failed to pull multimodal model: {pull_response.text}")
                                    logger.warning(f"You may need to manually run: ollama pull {multimodal_model}")
                            else:
                                logger.info("Multimodal model already exists in Ollama")
                    except Exception as e:
                        logger.warning(f"Error checking multimodal model: {e}")
                        
                except Exception as e:
                    logger.warning(f"Error checking Ollama: {e}")
            
            return True
        else:
            logger.error("Could not find integrations.ollama section in config.json")
            return False
    
    except Exception as e:
        logger.error(f"Error checking vector database setup: {e}")
        return False

def ensure_document_storage():
    """Ensure document storage directories exist."""
    logger.info("Setting up document storage directories...")
    
    storage_base = os.path.join(script_dir, "document_storage")
    
    # Create main storage directory
    os.makedirs(storage_base, exist_ok=True)
    
    # Create subdirectories
    subdirs = ["raw", "processed", "embeddings", "temp"]
    for subdir in subdirs:
        os.makedirs(os.path.join(storage_base, subdir), exist_ok=True)
    
    # Create index file if it doesn't exist
    index_file = os.path.join(storage_base, "document_index.json")
    if not os.path.exists(index_file):
        with open(index_file, 'w') as f:
            json.dump({
                "documents": [],
                "last_updated": "",
                "version": "1.0"
            }, f, indent=2)
        logger.info("Created document index file")
    
    logger.info("Document storage directories set up")
    return True

def cleanup_document_index():
    """Clean up the document index by removing entries with invalid file paths."""
    logger.info("Cleaning up document index...")
    
    # Get document index file path
    index_file = os.path.join(script_dir, "document_storage", "document_index.json")
    if not os.path.exists(index_file):
        logger.error(f"Document index file not found: {index_file}")
        return False
    
    # Create backup of index file
    backup_file(index_file)
    
    # Load document index
    try:
        with open(index_file, 'r') as f:
            index_data = json.load(f)
        
        documents = index_data.get("documents", [])
        original_count = len(documents)
        valid_documents = []
        
        # Check each document
        for doc in documents:
            file_path = doc.get("file_path")
            # Skip documents with None or invalid file paths
            if file_path and os.path.exists(file_path):
                valid_documents.append(doc)
            else:
                logger.info(f"Removing invalid document entry: {doc.get('id')} - {doc.get('filename', 'unknown')}")
        
        # Update index with valid documents only
        index_data["documents"] = valid_documents
        
        # Save updated index
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        logger.info(f"Cleaned up document index - removed {original_count - len(valid_documents)} invalid entries")
        return True
    
    except Exception as e:
        logger.error(f"Error cleaning up document index: {e}")
        return False

def main():
    """Apply all fixes and check configurations."""
    logger.info("Starting to apply fixes to AI-Socratic-Clarifier...")
    
    # Apply UI fixes
    apply_ui_fixes()
    
    # Check vector database setup
    check_vector_db_setup()
    
    # Ensure document storage exists
    ensure_document_storage()
    
    # Clean up document index
    cleanup_document_index()
    
    logger.info("Fixes applied successfully. Restart the application to see the changes.")

if __name__ == "__main__":
    main()
