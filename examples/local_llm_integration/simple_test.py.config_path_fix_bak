"""
Simplified test for the local LLM integration.
This only checks if Ollama is available and can be configured correctly.
"""

import sys
import os
import json
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from socratic_clarifier.integrations.integration_manager import IntegrationManager
from loguru import logger


def load_config():
    """Load configuration from config.json."""
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json'))
    default_config = {
        "integrations": {
            "ollama": {
                "enabled": True,
                "base_url": "http://localhost:11434/api",
                "api_key": None,
                "default_model": "llama3",
                "default_embedding_model": "nomic-embed-text",
                "timeout": 10  # Use a shorter timeout
            }
        },
        "settings": {
            "prefer_provider": "auto",
            "use_llm_questions": True,
            "use_llm_reasoning": True,
            "use_sot": True,
            "use_multimodal": True
        }
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            
            # Ensure timeout is set to a reasonable value
            if "integrations" in config and "ollama" in config["integrations"]:
                if "timeout" not in config["integrations"]["ollama"]:
                    config["integrations"]["ollama"]["timeout"] = 10
                else:
                    # Make sure it's not too long
                    config["integrations"]["ollama"]["timeout"] = min(
                        config["integrations"]["ollama"]["timeout"], 10
                    )
            
            return config
        else:
            logger.warning(f"Configuration file not found at {config_path}. Using default configuration.")
            return default_config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}. Using default configuration.")
        return default_config


def main():
    """Test Ollama integration."""
    # Load configuration
    config = load_config()
    
    print(f"Using Ollama configuration with models:")
    if "integrations" in config and "ollama" in config["integrations"]:
        ollama_config = config["integrations"]["ollama"]
        print(f"  - Default model: {ollama_config.get('default_model', 'llama3')}")
        print(f"  - Default embedding model: {ollama_config.get('default_embedding_model', 'nomic-embed-text')}")
        print(f"  - Timeout: {ollama_config.get('timeout', 60)}")
    else:
        print("  No Ollama configuration found!")
    
    # Initialize the integration manager
    print("\nInitializing IntegrationManager...")
    integration_manager = IntegrationManager(config=config)
    
    # Check if Ollama is available
    print("\nChecking available providers:")
    llm_providers = integration_manager.get_available_llm_providers()
    
    if "ollama" in llm_providers:
        print("✓ Ollama is available")
        
        # Get the Ollama provider
        ollama_provider = integration_manager.get_llm_provider("ollama")
        
        # Check what models are available
        print("\nAvailable Ollama models:")
        try:
            models = ollama_provider.get_available_models()
            if models:
                for model in models:
                    print(f"  - {model.get('name', 'Unknown')}")
            else:
                print("  No models available")
        except Exception as e:
            print(f"  Error getting models: {e}")
        
        # Check if multimodal is supported
        print("\nMultimodal support:")
        if ollama_provider.is_multimodal_supported():
            print("✓ Multimodal support available")
        else:
            print("✗ Multimodal support not available")
    else:
        print("✗ Ollama is not available")
    
    print("\nTest completed.")


if __name__ == "__main__":
    main()
