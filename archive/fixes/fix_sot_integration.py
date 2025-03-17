#!/usr/bin/env python3
"""
Fix for SoT (Sketch of Thought) integration in the AI-Socratic-Clarifier.

This script ensures that Sketch of Thought is properly integrated and working
correctly with the Socratic Clarifier.
"""

import os
import sys
import json
from loguru import logger
import importlib.util
import shutil

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def check_sot_directory():
    """Check if SoT directory structure is correct."""
    sot_dir = os.path.join(os.path.dirname(__file__), 'sot_2e9hb5_3')
    
    if not os.path.exists(sot_dir):
        logger.error(f"SoT directory not found at: {sot_dir}")
        return False
    
    # Check if SoT directory contains the correct structure
    sot_subdir = os.path.join(sot_dir, 'SoT')
    if not os.path.exists(sot_subdir):
        logger.error(f"SoT subdirectory not found at: {sot_subdir}")
        return False
    
    # Check if sketch_of_thought directory exists
    sketch_dir = os.path.join(sot_subdir, 'sketch_of_thought')
    if not os.path.exists(sketch_dir):
        logger.error(f"sketch_of_thought directory not found at: {sketch_dir}")
        return False
    
    logger.info(f"SoT directory structure looks correct: {sot_dir}")
    return True

def check_sot_importability():
    """Check if SoT is importable."""
    try:
        # Try importing the SoT integration
        from socratic_clarifier.integrations.sot_integration import SoTIntegration
        sot = SoTIntegration()
        
        logger.info(f"SoT integration importable: {sot.available}")
        return sot.available
    except ImportError as e:
        logger.error(f"Error importing SoT integration: {e}")
        return False
    except Exception as e:
        logger.error(f"Error initializing SoT integration: {e}")
        return False

def fix_sot_path():
    """Fix SoT path in Python path."""
    sot_dir = os.path.join(os.path.dirname(__file__), 'sot_2e9hb5_3', 'SoT')
    
    # Check if sot_dir exists and contains sketch_of_thought
    sketch_dir = os.path.join(sot_dir, 'sketch_of_thought')
    if not os.path.exists(sketch_dir):
        logger.error(f"sketch_of_thought directory not found at: {sketch_dir}")
        return False
    
    # Create a .pth file in site-packages to add SoT to Python path
    try:
        site_packages = None
        for path in sys.path:
            if path.endswith('site-packages'):
                site_packages = path
                break
        
        if site_packages:
            pth_file = os.path.join(site_packages, 'sot.pth')
            with open(pth_file, 'w') as f:
                f.write(sot_dir)
            
            logger.info(f"Created .pth file at {pth_file} pointing to {sot_dir}")
            return True
        else:
            logger.warning("Could not find site-packages directory")
            
            # Alternative: create a symlink in the socratic_clarifier directory
            socratic_dir = os.path.join(os.path.dirname(__file__), 'socratic_clarifier')
            if os.path.exists(socratic_dir):
                symlink_path = os.path.join(socratic_dir, 'sketch_of_thought')
                
                # Remove existing symlink if it exists
                if os.path.exists(symlink_path):
                    if os.path.islink(symlink_path):
                        os.unlink(symlink_path)
                    else:
                        logger.warning(f"{symlink_path} exists but is not a symlink")
                        return False
                
                # Create symlink
                try:
                    os.symlink(sketch_dir, symlink_path)
                    logger.info(f"Created symlink at {symlink_path} pointing to {sketch_dir}")
                    return True
                except Exception as e:
                    logger.error(f"Error creating symlink: {e}")
                    
                    # If symlink fails, copy the directory
                    try:
                        shutil.copytree(sketch_dir, symlink_path)
                        logger.info(f"Copied sketch_of_thought directory to {symlink_path}")
                        return True
                    except Exception as e:
                        logger.error(f"Error copying directory: {e}")
                        return False
            else:
                logger.warning(f"socratic_clarifier directory not found at: {socratic_dir}")
                return False
    except Exception as e:
        logger.error(f"Error fixing SoT path: {e}")
        return False

def fix_sot_integration_file():
    """Fix SoT integration file."""
    # Path to the SoT integration file
    integration_file = os.path.join(os.path.dirname(__file__), 'socratic_clarifier', 'integrations', 'sot_integration.py')
    
    if not os.path.exists(integration_file):
        logger.error(f"SoT integration file not found at: {integration_file}")
        return False
    
    try:
        # Read the current file
        with open(integration_file, 'r') as f:
            content = f.read()
        
        # Correct the model path
        if 'self._find_sot_directory()' in content:
            logger.info("Integration file has _find_sot_directory method, updating model loading")
            
            # Fix the model path
            updated_content = content.replace(
                "model_path = \"saytes/SoT_DistilBERT\"  # Default HF path",
                """# Try to find the SoT model directory
sot_dir = self._find_sot_directory()
model_path = os.path.join(sot_dir, "sketch_of_thought", "model") if sot_dir else "saytes/SoT_DistilBERT"

# If local model doesn't exist, fall back to HF path
if not os.path.exists(model_path):
    model_path = "saytes/SoT_DistilBERT"  # Default HF path"""
            )
            
            # Fix the model loading code - add device mapping
            updated_content = updated_content.replace(
                "self.model = DistilBertForSequenceClassification.from_pretrained(model_path)",
                "self.model = DistilBertForSequenceClassification.from_pretrained(model_path, device_map='auto')"
            )
            
            # Write the updated content back to the file
            with open(integration_file, 'w') as f:
                f.write(updated_content)
            
            logger.info(f"Updated SoT integration file: {integration_file}")
            return True
        else:
            logger.warning("Integration file doesn't have expected structure")
            return False
    except Exception as e:
        logger.error(f"Error fixing SoT integration file: {e}")
        return False

def install_sot_manually():
    """Install SoT manually if needed."""
    # Check if SoT is already installed
    if check_sot_importability():
        logger.info("SoT is already importable, no need for manual installation")
        return True
    
    # Check if we have the SoT directory
    if not check_sot_directory():
        logger.error("SoT directory structure is incorrect, manual installation not possible")
        return False
    
    # Fix SoT path
    if not fix_sot_path():
        logger.warning("Failed to fix SoT path")
    
    # Fix integration file
    if not fix_sot_integration_file():
        logger.warning("Failed to fix SoT integration file")
    
    # Create a Python package installer file
    setup_py = os.path.join(os.path.dirname(__file__), 'sot_2e9hb5_3', 'SoT', 'setup.py')
    
    if not os.path.exists(setup_py):
        try:
            with open(setup_py, 'w') as f:
                f.write("""from setuptools import setup, find_packages

setup(
    name="sketch_of_thought",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "numpy>=1.20.0"
    ],
    package_data={
        "sketch_of_thought": [
            "config/**/*.md",
            "config/**/*.json",
            "model/**/*"
        ]
    },
    include_package_data=True,
)
""")
            
            logger.info(f"Created setup.py at {setup_py}")
        except Exception as e:
            logger.error(f"Error creating setup.py: {e}")
            return False
    
    # Install the package
    try:
        # Use pip to install the package
        sot_dir = os.path.join(os.path.dirname(__file__), 'sot_2e9hb5_3', 'SoT')
        result = os.system(f"{sys.executable} -m pip install -e {sot_dir}")
        
        if result == 0:
            logger.info(f"Successfully installed SoT from {sot_dir}")
            return True
        else:
            logger.error(f"Error installing SoT, pip returned: {result}")
            return False
    except Exception as e:
        logger.error(f"Error installing SoT: {e}")
        return False

def enable_sot_in_config():
    """Enable SoT in the config file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    if not os.path.exists(config_path):
        logger.error(f"Config file not found at: {config_path}")
        return False
    
    try:
        # Read the current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Make sure SoT is enabled
        if "settings" in config and "use_sot" in config["settings"]:
            if not config["settings"]["use_sot"]:
                config["settings"]["use_sot"] = True
                
                # Write the updated config
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=4)
                
                logger.info("Enabled SoT in config.json")
            else:
                logger.info("SoT is already enabled in config.json")
            
            return True
        else:
            logger.warning("Config file doesn't have expected structure")
            return False
    except Exception as e:
        logger.error(f"Error enabling SoT in config: {e}")
        return False

def fix_sot_integration():
    """Fix SoT integration issues."""
    success = True
    
    # Check SoT directory structure
    logger.info("Checking SoT directory structure...")
    directory_ok = check_sot_directory()
    if not directory_ok:
        logger.warning("SoT directory structure has issues")
        success = False
    else:
        logger.info("✅ SoT directory structure looks good")
    
    # Check SoT importability
    logger.info("Checking SoT importability...")
    import_ok = check_sot_importability()
    if not import_ok:
        logger.warning("SoT is not importable, attempting manual installation")
        install_ok = install_sot_manually()
        if not install_ok:
            logger.warning("Failed to install SoT manually")
            success = False
        else:
            logger.info("✅ Successfully installed SoT manually")
    else:
        logger.info("✅ SoT is importable")
    
    # Enable SoT in config
    logger.info("Ensuring SoT is enabled in config...")
    config_ok = enable_sot_in_config()
    if not config_ok:
        logger.warning("Failed to enable SoT in config")
        success = False
    else:
        logger.info("✅ SoT is enabled in config")
    
    return success

if __name__ == "__main__":
    try:
        if fix_sot_integration():
            logger.info("✨ Successfully fixed SoT integration issues")
            sys.exit(0)
        else:
            logger.error("⚠️ Some SoT integration issues could not be fixed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error fixing SoT integration: {e}")
        sys.exit(1)
