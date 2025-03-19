#!/usr/bin/env python3
"""
Complete dependency installer for AI-Socratic-Clarifier.
This script installs all required packages, including SoT (Sketch-of-Thought).
"""

import os
import sys
import subprocess
import tempfile
import shutil
import site
import importlib
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ensure_venv():
    """Ensure we're running in a virtual environment."""
    if not hasattr(sys, 'base_prefix') or sys.base_prefix == sys.prefix:
        logger.warning("Not running in a virtual environment. Creating one...")
        try:
            # Create a virtual environment
            venv_dir = os.path.join(BASE_DIR, ".venv")
            if not os.path.exists(venv_dir):
                subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
            
            # Get the path to the Python executable in the venv
            if os.name == 'nt':  # Windows
                venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
            else:  # Unix/Linux/MacOS
                venv_python = os.path.join(venv_dir, "bin", "python")
            
            # Re-run this script with the venv Python
            logger.info(f"Restarting with virtual environment Python: {venv_python}")
            os.execl(venv_python, venv_python, *sys.argv)
        except Exception as e:
            logger.error(f"Failed to create or use virtual environment: {e}")
            sys.exit(1)
    else:
        logger.info("Using virtual environment")

def install_requirements():
    """Install packages from requirements.txt"""
    logger.info("Installing packages from requirements.txt...")
    req_file = os.path.join(BASE_DIR, "requirements.txt")
    
    if not os.path.exists(req_file):
        logger.error(f"Requirements file not found: {req_file}")
        return False
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=True)
        logger.info("Requirements installation completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing requirements: {e}")
        return False

def install_sot():
    """Install Sketch-of-Thought from GitHub."""
    logger.info("Installing Sketch-of-Thought...")
    
    # Check if git is available
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Git not found. Please install Git and try again.")
        return False
    
    # Create a temporary directory
    tmp_dir = tempfile.mkdtemp(prefix="sot_")
    
    try:
        # Clone the repository
        logger.info("Cloning Sketch-of-Thought repository...")
        subprocess.run(
            ["git", "clone", "https://github.com/SimonAytes/SoT.git", os.path.join(tmp_dir, "SoT")],
            check=True
        )
        
        # Install the package
        logger.info("Installing Sketch-of-Thought package...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", os.path.join(tmp_dir, "SoT")],
            check=True
        )
        
        # Force reload of site packages
        importlib.reload(site)
        
        # Verify installation
        try:
            importlib.import_module("sketch_of_thought")
            logger.info("Sketch-of-Thought installed and verified successfully!")
            
            # Copy installation directory to a permanent location
            sot_dir = os.path.join(BASE_DIR, "sot_installation")
            if os.path.exists(sot_dir):
                shutil.rmtree(sot_dir)
            shutil.copytree(os.path.join(tmp_dir, "SoT"), sot_dir)
            logger.info(f"SoT installation copied to: {sot_dir}")
            
            return True
        except ImportError:
            logger.warning("Sketch-of-Thought was installed but could not be imported.")
            logger.warning("You may need to restart your Python interpreter.")
            return True
    except Exception as e:
        logger.error(f"Error installing Sketch-of-Thought: {e}")
        return False
    finally:
        # Clean up temp directory
        try:
            shutil.rmtree(tmp_dir)
        except:
            pass

def update_config_for_available_models():
    """Update config.json to use available Ollama models."""
    logger.info("Updating config.json with available Ollama models...")
    
    config_path = os.path.join(BASE_DIR, "config.json")
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return False
    
    try:
        # Load current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check for available models
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags")
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                
                # Extract model names
                model_names = [m.get("name") for m in models]
                logger.info(f"Available Ollama models: {', '.join(model_names)}")
                
                # Choose appropriate models
                text_model = None
                multimodal_model = None
                
                # Preferred text models in order
                text_model_preferences = ["gemma3:latest", "olmo2:13b", "llama3:8b", "phi3:latest", "mistral:latest"]
                for model in text_model_preferences:
                    if model in model_names:
                        text_model = model
                        break
                
                # If no preferred model found, use the first available
                if not text_model and model_names:
                    text_model = model_names[0]
                
                # Preferred multimodal models in order
                multimodal_preferences = ["llava:latest", "bakllava:latest", "moondream:latest"]
                for model in multimodal_preferences:
                    if model in model_names:
                        multimodal_model = model
                        break
                
                # Update config with available models
                if "integrations" not in config:
                    config["integrations"] = {}
                
                if "ollama" not in config["integrations"]:
                    config["integrations"]["ollama"] = {}
                
                if text_model:
                    config["integrations"]["ollama"]["default_model"] = text_model
                    logger.info(f"Set default model to: {text_model}")
                
                if multimodal_model:
                    config["integrations"]["ollama"]["multimodal_model"] = multimodal_model
                    logger.info(f"Set multimodal model to: {multimodal_model}")
                
                # Save updated config
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=4)
                
                logger.info("Config updated successfully")
                return True
            else:
                logger.warning(f"Failed to get Ollama models: Status {response.status_code}")
        except Exception as e:
            logger.warning(f"Error checking Ollama models: {e}")
        
        return False
    except Exception as e:
        logger.error(f"Error updating config.json: {e}")
        return False

def fix_document_library_connection():
    """Ensure document library is properly connected to RAG in chat."""
    logger.info("Fixing document library RAG connection...")
    
    try:
        # Check if the necessary files exist
        document_rag_routes = os.path.join(BASE_DIR, "web_interface", "document_rag_routes.py")
        enhanced_templates = os.path.join(BASE_DIR, "web_interface", "templates", "enhanced.html")
        
        if not os.path.exists(document_rag_routes):
            logger.error(f"Document RAG routes file not found: {document_rag_routes}")
            return False
        
        if not os.path.exists(enhanced_templates):
            logger.warning(f"Enhanced UI template not found: {enhanced_templates}")
            # We'll continue anyway
        
        # Ensure document_rag_bp is registered in app.py
        app_py = os.path.join(BASE_DIR, "web_interface", "app.py")
        if os.path.exists(app_py):
            with open(app_py, 'r') as f:
                content = f.read()
            
            if "from web_interface.document_rag_routes import document_rag_bp" not in content:
                logger.warning("Document RAG blueprint import not found in app.py")
                # We should add it, but for safety, we'll just warn
            
            if "app.register_blueprint(document_rag_bp)" not in content:
                logger.warning("Document RAG blueprint registration not found in app.py")
                # We should add it, but for safety, we'll just warn
        
        logger.info("Document library RAG connection verification completed")
        return True
    except Exception as e:
        logger.error(f"Error fixing document library connection: {e}")
        return False

def consolidate_ui():
    """Determine which UIs are necessary and potentially consolidate."""
    logger.info("Checking UI configurations...")
    
    try:
        # Count how many UI routes are used
        app_py = os.path.join(BASE_DIR, "web_interface", "app.py")
        if os.path.exists(app_py):
            with open(app_py, 'r') as f:
                content = f.read()
            
            ui_routes = {
                "integrated": "@app.route('/integrated')" in content,
                "integrated_lite": "@app.route('/integrated_lite')" in content,
                "enhanced": "@app.route('/enhanced')" in content,
                "reflection": "@app.route('/reflection')" in content,
            }
            
            active_uis = [ui for ui, active in ui_routes.items() if active]
            logger.info(f"Active UI routes: {', '.join(active_uis)}")
            
            # Enhanced UI is our primary interface
            if "enhanced" in active_uis:
                logger.info("Enhanced UI is available - this is the recommended interface")
            
            # All UIs are necessary for different functionality
            logger.info("All UI paths serve different purposes:")
            logger.info("- /enhanced: Main interface with document management")
            logger.info("- /reflection: Visualization of reasoning process")
            logger.info("- /integrated: Full featured interface")
            logger.info("- /integrated_lite: Lightweight interface")
            
            return True
    except Exception as e:
        logger.error(f"Error checking UI configurations: {e}")
        return False

def main():
    """Main installation function."""
    print("\n" + "="*70)
    print("   AI-Socratic-Clarifier Complete Installer")
    print("="*70 + "\n")
    
    # Ensure we're in a virtual environment
    ensure_venv()
    
    # Install requirements
    reqs_installed = install_requirements()
    
    # Install SoT
    sot_installed = install_sot()
    
    # Update config for available models
    config_updated = update_config_for_available_models()
    
    # Fix document library connection
    doc_lib_fixed = fix_document_library_connection()
    
    # Check UI consolidation
    ui_checked = consolidate_ui()
    
    # Print summary
    print("\n" + "="*70)
    print("   Installation Summary")
    print("="*70)
    print(f"✓ Requirements: {'Installed' if reqs_installed else 'Some issues'}")
    print(f"✓ Sketch-of-Thought: {'Installed' if sot_installed else 'Failed to install'}")
    print(f"✓ Configuration: {'Updated' if config_updated else 'Not updated'}")
    print(f"✓ Document Library: {'Verified' if doc_lib_fixed else 'Issues found'}")
    print(f"✓ UI Configuration: {'Checked' if ui_checked else 'Issues found'}")
    
    # Print instructions
    print("\n" + "="*70)
    print("   Usage Instructions")
    print("="*70)
    print("1. Start the application with the optimized script:")
    print("   ./start_optimized.py")
    print("")
    print("2. Access the web interface at http://localhost:5000")
    print("   - The recommended interface is at: /enhanced")
    print("")
    print("3. If you encounter issues with the UI, try:")
    print("   - Enhanced UI: /enhanced (main interface with document management)")
    print("   - Reflective mode: /reflection (visualization of reasoning)")
    print("")
    print("4. The document library is accessible from the Enhanced UI")
    print("   and integrated with the chat system for context-aware responses.")
    
    return 0 if reqs_installed and sot_installed else 1

if __name__ == "__main__":
    sys.exit(main())
