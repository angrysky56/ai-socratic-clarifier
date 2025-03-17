#!/usr/bin/env python3
"""
Installation script for the AI-Socratic-Clarifier.
This script automates the setup process for the enhanced version.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def create_venv():
    """Create a virtual environment if it doesn't exist."""
    print("Setting up virtual environment...")
    
    if os.path.exists("venv"):
        print("Virtual environment already exists.")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Virtual environment created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {e}")
        sys.exit(1)

def install_requirements():
    """Install the required packages."""
    print("Installing requirements...")
    
    # Determine the pip command based on the OS
    if sys.platform == "win32":
        pip_cmd = ["venv\\Scripts\\pip"]
    else:
        pip_cmd = ["./venv/bin/pip"]
    
    try:
        # Update pip first
        subprocess.run([*pip_cmd, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([*pip_cmd, "install", "-r", "requirements.txt"], check=True)
        
        # Install the package in development mode
        subprocess.run([*pip_cmd, "install", "-e", "."], check=True)
        
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def setup_config():
    """Set up the configuration file."""
    print("Setting up configuration...")
    
    config_path = Path("../../../../../../../../config.json")
    example_config_path = Path("config.example.json")
    
    # If ../../../../../../../../config.json already exists, ask if it should be replaced
    if config_path.exists():
        answer = input("Configuration file already exists. Replace it? (y/n): ")
        if answer.lower() != "y":
            print("Using existing configuration.")
            return
    
    # If example config doesn't exist, create a default one
    if not example_config_path.exists():
        default_config = {
            "integrations": {
                "lm_studio": {
                    "enabled": True,
                    "base_url": "http://localhost:1234/v1",
                    "api_key": None,
                    "default_model": "default",
                    "timeout": 60
                },
                "ollama": {
                    "enabled": True,
                    "base_url": "http://localhost:11434/api",
                    "api_key": None,
                    "default_model": "llama3",
                    "default_embedding_model": "nomic-embed-text",
                    "timeout": 60
                }
            },
            "settings": {
                "prefer_provider": "auto",
                "use_llm_questions": True,
                "use_llm_reasoning": True,
                "use_sot": True,
                "use_multimodal": True,
                "use_document_rag": True
            }
        }
        
        with open(example_config_path, "w") as f:
            json.dump(default_config, f, indent=4)
    
    # Copy example config to actual config
    shutil.copy2(example_config_path, config_path)
    print("Configuration set up successfully.")

def setup_directories():
    """Set up the necessary directories."""
    print("Setting up directories...")
    
    directories = [
        "document_storage",
        "web_interface/feedback",
        "web_interface/static/css",
        "web_interface/static/js",
        "web_interface/static/img",
        "custom_patterns"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {directory}")
    
    print("Directories set up successfully.")

def check_prerequisites():
    """Check if the prerequisites are installed."""
    print("Checking prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"Error: Python 3.8 or higher is required. Found: {sys.version}")
        sys.exit(1)
    
    # Check if pip is installed
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: pip is not installed or not in PATH. Please install pip first.")
        sys.exit(1)
    
    # Check if venv module is available
    try:
        import venv
    except ImportError:
        print("Error: venv module is not available. Please install it first.")
        sys.exit(1)
    
    print("Prerequisites check passed.")

def main():
    """Main installation function."""
    print("=" * 60)
    print("AI-Socratic-Clarifier Installation")
    print("=" * 60)
    
    # Check prerequisites
    check_prerequisites()
    
    # Setup directories
    setup_directories()
    
    # Create virtual environment
    create_venv()
    
    # Install requirements
    install_requirements()
    
    # Setup configuration
    setup_config()
    
    print("=" * 60)
    print("Installation completed successfully!")
    print("\nTo start the AI-Socratic-Clarifier, run:")
    if sys.platform == "win32":
        print("  venv\\Scripts\\python start_socratic.py")
    else:
        print("  ./venv/bin/python start_socratic.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
