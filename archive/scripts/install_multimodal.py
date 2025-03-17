#!/usr/bin/env python3
"""
Setup script for multimodal functionality in AI-Socratic-Clarifier.
This script installs all necessary dependencies for OCR and multimodal analysis.
"""

import os
import sys
import subprocess
import platform
import traceback

def print_banner():
    """Display a nice banner at startup."""
    banner = """
    ╔═════════════════════════════════════════════════════════╗
    ║         Multimodal Integration for Socratic Clarifier   ║
    ╚═════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_pip():
    """Check if pip is available and install packages."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available.")
        return False

def install_python_dependencies():
    """Install required Python packages."""
    dependencies = [
        "pytesseract",
        "Pillow",
        "pdf2image",
        "opencv-python",
        "numpy",
        "requests"
    ]
    
    print("\nInstalling Python dependencies...")
    
    try:
        for package in dependencies:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ])
            print(f"✅ {package} installed successfully")
    except Exception as e:
        print(f"❌ Error installing Python packages: {e}")
        return False
    
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed on the system."""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR is installed (version {version})")
        return True
    except:
        print("❌ Tesseract OCR is not installed or not found")
        return False

def install_tesseract():
    """Provide instructions for installing Tesseract OCR."""
    system = platform.system()
    
    print("\nTesseract OCR installation instructions:")
    
    if system == "Linux":
        print("For Ubuntu/Debian:")
        print("    sudo apt-get update")
        print("    sudo apt-get install -y tesseract-ocr")
        print("\nFor Fedora:")
        print("    sudo dnf install tesseract")
        print("\nFor Arch Linux:")
        print("    sudo pacman -S tesseract")
    
    elif system == "Darwin":  # macOS
        print("Using Homebrew:")
        print("    brew install tesseract")
    
    elif system == "Windows":
        print("1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Run the installer and follow the instructions")
        print("3. Add the Tesseract installation directory to your PATH")
    
    else:
        print("Please refer to the Tesseract documentation for your system:")
        print("    https://github.com/tesseract-ocr/tesseract")
    
    return False

def check_poppler():
    """Check if Poppler is installed (required for pdf2image)."""
    try:
        from pdf2image import convert_from_path
        # Create a simple test
        test_successful = False
        
        try:
            # Check if we can import without error
            import pdf2image
            test_successful = True
        except:
            pass
        
        if test_successful:
            print("✅ Poppler is installed (pdf2image works)")
            return True
        else:
            print("❌ Poppler is not properly installed")
            return False
    except:
        print("❌ Cannot check Poppler (pdf2image not installed)")
        return False

def install_poppler():
    """Provide instructions for installing Poppler."""
    system = platform.system()
    
    print("\nPoppler installation instructions:")
    
    if system == "Linux":
        print("For Ubuntu/Debian:")
        print("    sudo apt-get update")
        print("    sudo apt-get install -y poppler-utils")
        print("\nFor Fedora:")
        print("    sudo dnf install poppler-utils")
        print("\nFor Arch Linux:")
        print("    sudo pacman -S poppler")
    
    elif system == "Darwin":  # macOS
        print("Using Homebrew:")
        print("    brew install poppler")
    
    elif system == "Windows":
        print("1. Download the latest binary from: https://github.com/oschwartz10612/poppler-windows/releases")
        print("2. Extract the files and add the bin directory to your PATH")
    
    else:
        print("Please refer to the Poppler documentation for your system.")
    
    return False

def update_config_for_multimodal():
    """Update config.json to include multimodal settings."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    try:
        # Load existing config
        import json
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Add multimodal model if not present
        if "integrations" not in config:
            config["integrations"] = {}
        
        if "ollama" not in config["integrations"]:
            config["integrations"]["ollama"] = {}
        
        # Add multimodal model configuration
        if "multimodal_model" not in config["integrations"]["ollama"]:
            config["integrations"]["ollama"]["multimodal_model"] = "llava:latest"
        
        # Enable multimodal setting
        if "settings" not in config:
            config["settings"] = {}
        
        config["settings"]["use_multimodal"] = True
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print("✅ Configuration updated for multimodal support")
        return True
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False

def check_ollama_multimodal():
    """Check if Ollama is available and has multimodal models."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            multimodal_models = [
                m.get("name") for m in models 
                if any(mm in m.get("name", "").lower() for mm in ["llava", "vision", "multi", "gemini", "bakllava"])
            ]
            
            if multimodal_models:
                print(f"✅ Ollama has multimodal models: {', '.join(multimodal_models)}")
                return True, multimodal_models[0]
            else:
                print("❌ No multimodal models found in Ollama")
                return False, None
        else:
            print(f"❌ Error checking Ollama: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False, None

def install_multimodal_models():
    """Provide instructions for installing multimodal models in Ollama."""
    print("\nTo use multimodal features, you need to install at least one multimodal model in Ollama.")
    print("\nRecommended models:")
    print("    llava:latest - General purpose vision-language model")
    print("    bakllava:latest - Vision model based on Llama 2")
    print("    llava-phi3:latest - Microsoft's Phi-3 vision model")
    
    print("\nInstall with:")
    print("    ollama pull llava")
    print("    ollama pull bakllava")
    print("    ollama pull llava-phi3")
    
    choice = input("\nWould you like to automatically run 'ollama pull llava'? (y/n): ")
    if choice.lower() == 'y':
        try:
            print("Running 'ollama pull llava'...")
            subprocess.call(["ollama", "pull", "llava"])
            return True
        except Exception as e:
            print(f"❌ Error pulling model: {e}")
            return False
    return False

def main():
    """Main installation function."""
    print_banner()
    
    print("This script will set up multimodal integration for AI-Socratic-Clarifier.")
    print("This includes OCR capabilities for images and PDFs, and multimodal analysis.")
    
    # Check pip
    if not check_pip():
        print("❌ pip is required for installation.")
        return False
    
    # Install Python packages
    if not install_python_dependencies():
        print("❌ Failed to install required Python packages.")
        return False
    
    # Check and install Tesseract
    if not check_tesseract():
        install_tesseract()
        print("\n⚠️ Please install Tesseract OCR and run this script again.")
    
    # Check and install Poppler
    if not check_poppler():
        install_poppler()
        print("\n⚠️ Please install Poppler and run this script again.")
    
    # Check Ollama multimodal models
    has_models, recommended_model = check_ollama_multimodal()
    if not has_models:
        install_multimodal_models()
    
    # Update configuration
    update_config_for_multimodal()
    
    # Final status
    print("\n" + "=" * 50)
    if check_tesseract() and check_poppler() and has_models:
        print("✅ All dependencies are installed!")
        print("✅ Multimodal integration is ready to use.")
    else:
        print("⚠️ Some dependencies are missing:")
        if not check_tesseract():
            print("  - Tesseract OCR")
        if not check_poppler():
            print("  - Poppler")
        if not has_models:
            print("  - Multimodal models in Ollama")
        print("\nPlease install the missing dependencies and run this script again.")
    
    print("\nYou can now start the application with:")
    print("    python start_socratic.py")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        traceback.print_exc()
