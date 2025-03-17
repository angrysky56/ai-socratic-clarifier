#!/usr/bin/env python3
"""
Comprehensive fix for the enhanced UI of AI-Socratic-Clarifier.

This script fixes various issues with the enhanced UI including:
1. Document loading and display
2. File download functionality
3. Multimodal integration
4. Reflective ecosystem network display
"""

import os
import sys
import importlib
import subprocess
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_fix_script(script_name):
    """Run a fix script and return result."""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        logger.error(f"Fix script not found: {script_path}")
        return False
    
    try:
        # Try to import and run function
        module_name = os.path.splitext(script_name)[0]
        if module_name in sys.modules:
            # Remove from sys.modules to reload
            del sys.modules[module_name]
            
        module = importlib.import_module(module_name)
        
        # Get the main function (assume it's the module name without .py)
        function_name = module_name.replace('-', '_')
        if hasattr(module, function_name):
            function = getattr(module, function_name)
            result = function()
            return result
        else:
            # If function not found, run as subprocess
            logger.warning(f"Function {function_name} not found in {module_name}, running as subprocess")
            result = subprocess.run([sys.executable, script_path], capture_output=True)
            return result.returncode == 0
    except Exception as e:
        logger.error(f"Error running fix script {script_name}: {e}")
        # Try running as subprocess
        try:
            result = subprocess.run([sys.executable, script_path], capture_output=True)
            return result.returncode == 0
        except Exception as e2:
            logger.error(f"Error running subprocess for {script_name}: {e2}")
            return False

def fix_enhanced_ui():
    """Fix issues with the enhanced UI."""
    
    # Dictionary of fixes to run
    fixes = {
        "Document Loading": "fix_document_loading.py",
        "Multimodal Integration": "fix_multimodal_integration.py",
        "Document Download": "fix_document_download.py"
    }
    
    results = {}
    all_success = True
    
    # Run each fix
    for name, script in fixes.items():
        logger.info(f"Running fix for {name}...")
        success = run_fix_script(script)
        results[name] = success
        
        if success:
            logger.info(f"✅ Successfully fixed {name}")
        else:
            logger.error(f"❌ Failed to fix {name}")
            all_success = False
    
    logger.info("Fix summary:")
    for name, success in results.items():
        logger.info(f"- {name}: {'✅ Success' if success else '❌ Failed'}")
    
    return all_success

if __name__ == "__main__":
    try:
        if fix_enhanced_ui():
            logger.info("✨ Successfully fixed the enhanced UI")
            sys.exit(0)
        else:
            logger.error("⚠️ Some fixes failed, check the logs for details")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error fixing enhanced UI: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
