#!/usr/bin/env python3
"""
Install requirements for AI-Socratic-Clarifier.

This script installs the required dependencies for the AI-Socratic-Clarifier.
"""

import os
import sys
import subprocess
from loguru import logger

def install_requirements():
    """Install required dependencies from requirements.txt."""
    requirements_path = os.path.join(
        os.path.dirname(__file__), 
        'requirements.txt'
    )
    
    if not os.path.exists(requirements_path):
        logger.error(f"Requirements file not found at: {requirements_path}")
        return False
    
    logger.info(f"Installing requirements from: {requirements_path}")
    
    try:
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "-r", 
            requirements_path
        ])
        
        logger.info("Successfully installed all requirements")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing requirements: {e}")
        return False

if __name__ == "__main__":
    try:
        if install_requirements():
            logger.info("✅ Requirements installation completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Failed to install requirements")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)
