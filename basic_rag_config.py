#!/usr/bin/env python3
"""
Basic Advanced RAG Configuration for AI-Socratic-Clarifier.

This script focuses only on configuration changes to enable advanced RAG features:
1. Updates the config.json with advanced RAG settings
2. Creates documentation without modifying code files
"""

import os
import json
import shutil

def backup_file(file_path):
    """Create a backup of a file."""
    backup_path = f"{file_path}.rag_config_bak"
    if os.path.exists(file_path):
        print(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
    return backup_path

def update_config_for_advanced_rag():
    """Update config.json with advanced RAG settings."""
    config_path = os.path.join('config.json')
    
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found")
        return False
    
    backup_file(config_path)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Ensure RAG settings are present and optimized
        if "settings" not in config:
            config["settings"] = {}
        
        config["settings"]["use_document_rag"] = True
        config["settings"]["advanced_rag"] = True  # New setting for advanced RAG
        config["settings"]["rag_context_limit"] = 50000  # Higher limit for large context models
        config["settings"]["use_model_for_rag"] = True  # Use the main model for RAG
        
        # Ensure Ollama settings include necessary models and context length
        if "integrations" not in config:
            config["integrations"] = {}
        
        if "ollama" not in config["integrations"]:
            config["integrations"]["ollama"] = {}
        
        # Update context length for Gemma 3
        if config["integrations"]["ollama"].get("default_model") == "gemma3:latest":
            config["integrations"]["ollama"]["context_length"] = 128000
        else:
            config["integrations"]["ollama"]["context_length"] = 8192
        
        # Ensure embedding model is set
        if "default_embedding_model" not in config["integrations"]["ollama"]:
            config["integrations"]["ollama"]["default_embedding_model"] = "nomic-embed-text"
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print("✅ Updated config.json with advanced RAG settings")
        return True
    except Exception as e:
        print(f"Error updating config with advanced RAG settings: {e}")
        return False

def create_advanced_rag_readme():
    """Create a README file explaining the advanced RAG integration."""
    readme_path = os.path.join('ADVANCED_RAG_README.md')
    
    readme_content = """# Advanced RAG Configuration for AI-Socratic-Clarifier

## Overview

This configuration enhances the Retrieval-Augmented Generation (RAG) capabilities of the AI-Socratic-Clarifier by:

1. **Leveraging Large Context Windows**: Configures the system to use the full context window of models like Gemma 3 (128k tokens)
2. **Enabling Multimodal Document Processing**: Configures settings to use the primary model for document processing
3. **Optimizing Document Retrieval**: Sets parameters for better document context integration

## Configuration Changes

Added settings in `config.json`:

- `advanced_rag`: Enable/disable advanced RAG features
- `rag_context_limit`: Control how much document content to include
- `use_model_for_rag`: Use the primary model for document processing when possible
- Increased context length for Gemma 3 to 128k tokens
- Configured default embedding model for document retrieval

## Usage

The advanced RAG capabilities are automatically enabled when documents are processed. Additional code improvements for better RAG functionality may be added in future updates.

## Requirements

- Ollama with models like Gemma 3, Llava, or other LLMs with large context windows
- Python dependencies for document processing (OCR, PDF handling, etc.)
- Sufficient system memory to handle large context windows
"""
    
    try:
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"✅ Created {readme_path}")
        return True
    except Exception as e:
        print(f"Error creating README: {e}")
        return False

def apply_config_changes():
    """Apply the configuration changes for advanced RAG."""
    print("\n===== APPLYING ADVANCED RAG CONFIGURATION =====\n")
    
    # Update configuration
    print("\nUpdating configuration...")
    config_updated = update_config_for_advanced_rag()
    
    # Create README
    print("\nCreating advanced RAG documentation...")
    readme_created = create_advanced_rag_readme()
    
    # Print summary
    print("\n===== ADVANCED RAG CONFIGURATION SUMMARY =====\n")
    print(f"✅ Configuration updated: {config_updated}")
    print(f"✅ Documentation created: {readme_created}")
    
    # Overall success
    all_succeeded = all([config_updated, readme_created])
    
    if all_succeeded:
        print("\n✅ All advanced RAG configuration applied successfully!")
    else:
        print("\n⚠️ Some configuration could not be applied. Check the logs above for details.")
    
    return all_succeeded

if __name__ == "__main__":
    # Apply all config changes when run directly
    apply_config_changes()
