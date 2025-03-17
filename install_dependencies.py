#!/usr/bin/env python3
"""
Dependency installer for AI-Socratic-Clarifier.

This script checks for and installs missing dependencies for:
- Document processing
- Multimodal integration
- Web interface
"""

import os
import sys
import subprocess
import importlib.util
from loguru import logger

# Required dependencies
REQUIRED_PACKAGES = {
    "Flask": "flask",
    "Loguru": "loguru",
    "Werkzeug": "werkzeug",
    "Requests": "requests",
    "Pillow": "pillow",
    "PyTesseract": "pytesseract",
    "PDF2Image": "pdf2image",
    "NumPy": "numpy"
}

# Optional but recommended
OPTIONAL_PACKAGES = {
    "Flask-CORS": "flask-cors",
    "Markdown": "markdown",
    "PyPDF2": "pypdf2"
}

def check_installed(package_name):
    """Check if a package is installed."""
    try:
        importlib.util.find_spec(package_name.lower())
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing {package_name}: {e}")
        return False

def check_tesseract():
    """Check if tesseract is installed."""
    try:
        result = subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_dependencies():
    """Install missing dependencies."""
    
    # Check for Python package dependencies
    missing_required = {}
    missing_optional = {}
    
    for name, package in REQUIRED_PACKAGES.items():
        if not check_installed(package):
            missing_required[name] = package
    
    for name, package in OPTIONAL_PACKAGES.items():
        if not check_installed(package):
            missing_optional[name] = package
    
    # Check for system dependencies
    tesseract_installed = check_tesseract()
    
    # Report status
    logger.info("Dependency check complete:")
    logger.info(f"- Required packages: {len(REQUIRED_PACKAGES) - len(missing_required)}/{len(REQUIRED_PACKAGES)} installed")
    logger.info(f"- Optional packages: {len(OPTIONAL_PACKAGES) - len(missing_optional)}/{len(OPTIONAL_PACKAGES)} installed")
    logger.info(f"- Tesseract OCR: {'Installed' if tesseract_installed else 'Not installed'}")
    
    if not missing_required and not missing_optional and tesseract_installed:
        logger.info("✅ All dependencies installed!")
        return True
    
    # Install missing required packages
    if missing_required:
        logger.info("Installing missing required packages...")
        for name, package in missing_required.items():
            logger.info(f"Installing {name} ({package})...")
            if install_package(package):
                logger.info(f"✅ Installed {name}")
            else:
                logger.error(f"❌ Failed to install {name}")
                return False
    
    # Install missing optional packages
    if missing_optional:
        logger.info("Installing missing optional packages...")
        for name, package in missing_optional.items():
            logger.info(f"Installing {name} ({package})...")
            if install_package(package):
                logger.info(f"✅ Installed {name}")
            else:
                logger.warning(f"⚠️ Failed to install optional package {name}")
    
    # Check for tesseract again (if it was missing)
    if not tesseract_installed:
        logger.warning("\n⚠️ Tesseract OCR is not installed.")
        logger.warning("Multimodal document processing will not work properly without it.")
        logger.warning("Please install Tesseract OCR manually:")
        logger.warning("- Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        logger.warning("- macOS: brew install tesseract")
        logger.warning("- Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    
    return True

if __name__ == "__main__":
    try:
        if install_dependencies():
            logger.info("✨ Dependencies installation complete")
            sys.exit(0)
        else:
            logger.error("⚠️ Some dependencies could not be installed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error installing dependencies: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
