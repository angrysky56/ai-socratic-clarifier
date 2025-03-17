#!/usr/bin/env python3
"""
Start script for the enhanced AI-Socratic-Clarifier.
This script starts the web interface with all the enhancements.
"""

import os
import sys
import time
import json
import subprocess
import webbrowser
from pathlib import Path

def check_venv():
    """Check if running in a virtual environment."""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Not running in a virtual environment.")
        answer = input("Continue anyway? (y/n): ")
        if answer.lower() != "y":
            print("Exiting. Please run the script from the virtual environment.")
            sys.exit(1)

def check_configuration():
    """Check if the configuration file exists and is valid."""
    config_path = Path("config.json")
    
    if not config_path.exists():
        print("Error: Configuration file not found.")
        print("Please run the install.py script first or create a config.json file.")
        sys.exit(1)
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # Check for required configuration values
        if not config.get("integrations"):
            raise ValueError("Missing 'integrations' section in the configuration file.")
        
        # Check if at least one integration is enabled
        if not (config["integrations"].get("ollama", {}).get("enabled", False) or 
                config["integrations"].get("lm_studio", {}).get("enabled", False)):
            raise ValueError("No integrations enabled in the configuration file.")
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error in configuration file: {e}")
        print("Please fix the configuration file and try again.")
        sys.exit(1)
    
    return config

def check_ollama():
    """Check if Ollama is running."""
    if sys.platform == "win32":
        # On Windows, use tasklist to check if Ollama is running
        try:
            result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ollama.exe"], capture_output=True, text=True)
            if "ollama.exe" not in result.stdout:
                print("Warning: Ollama does not appear to be running.")
                return False
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Warning: Couldn't check if Ollama is running.")
            return False
    else:
        # On Unix-like systems, use ps to check if Ollama is running
        try:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            if "ollama serve" not in result.stdout:
                print("Warning: Ollama does not appear to be running.")
                return False
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Warning: Couldn't check if Ollama is running.")
            return False

def start_server():
    """Start the web server."""
    try:
        # Import the app module
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'web_interface')))
        
        # Check if we should use the enhanced app
        enhanced_app_path = os.path.join("web_interface", "enhanced_app.py")
        if os.path.exists(enhanced_app_path):
            print("Using enhanced app...")
            from web_interface.enhanced_app import app
        else:
            print("Using standard app...")
            from web_interface.app import app
        
        # Start the server
        print("Starting server...")
        app.run(debug=True, host="0.0.0.0", port=5000)
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure you have installed all the requirements.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

def open_browser():
    """Open the web browser after a short delay."""
    time.sleep(2)  # Give the server time to start
    webbrowser.open("http://localhost:5000")

def main():
    """Main function."""
    print("=" * 60)
    print("AI-Socratic-Clarifier Enhanced")
    print("=" * 60)
    
    # Check if running in a virtual environment
    check_venv()
    
    # Check configuration
    config = check_configuration()
    
    # If Ollama is enabled, check if it's running
    if config["integrations"].get("ollama", {}).get("enabled", False):
        if not check_ollama():
            print("Warning: Ollama is enabled but doesn't appear to be running.")
            print("Please start Ollama first with 'ollama serve' and try again,")
            print("or disable Ollama in the config.json file.")
            answer = input("Continue anyway? (y/n): ")
            if answer.lower() != "y":
                print("Exiting.")
                sys.exit(1)
    
    # Start web browser in a separate thread
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()
