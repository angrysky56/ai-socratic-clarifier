#!/usr/bin/env python3
"""
Comprehensive fix for the AI-Socratic-Clarifier enhanced UI.

This script fixes various issues with the enhanced UI including:
1. Document loading and display
2. File download functionality
3. Multimodal integration
4. UI improvements
"""

import os
import sys
import subprocess
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_fix_script(script_path):
    """Run a fix script and return result."""
    try:
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def fix_all_ui():
    """Run all UI fixes."""
    logger.info("Starting comprehensive UI fixes...")
    
    # List of fix scripts to run
    fix_scripts = [
        ('Document Loading', '/home/ty/Repositories/ai_workspace/ai-socratic-clarifier/fix_document_loading_simple.py'),
        ('Multimodal Integration', '/home/ty/Repositories/ai_workspace/ai-socratic-clarifier/fix_multimodal_integration.py'),
        ('Document Download', '/home/ty/Repositories/ai_workspace/ai-socratic-clarifier/fix_document_download_fixed.py'),
        ('Document JS', '/home/ty/Repositories/ai_workspace/ai-socratic-clarifier/fix_document_js.py')
    ]
    
    results = {}
    all_success = True
    
    # Run each fix script
    for name, script_path in fix_scripts:
        logger.info(f"Running {name} fix...")
        success, output = run_fix_script(script_path)
        results[name] = success
        
        if success:
            logger.info(f"✅ {name} fix completed successfully")
        else:
            logger.error(f"❌ {name} fix failed: {output}")
            all_success = False
    
    # Print summary
    logger.info("\n===== Fix Summary =====")
    for name, success in results.items():
        logger.info(f"- {name}: {'✅ Success' if success else '❌ Failed'}")
    
    # Install dependencies if needed
    try:
        logger.info("\nChecking and installing dependencies...")
        dep_script = '/home/ty/Repositories/ai_workspace/ai-socratic-clarifier/install_dependencies.py'
        if os.path.exists(dep_script):
            success, output = run_fix_script(dep_script)
            if success:
                logger.info("✅ Dependencies check completed successfully")
            else:
                logger.warning(f"⚠️ Dependencies check had issues: {output}")
        else:
            logger.warning("⚠️ Dependencies script not found")
    except Exception as e:
        logger.error(f"❌ Error checking dependencies: {e}")
    
    return all_success

if __name__ == "__main__":
    try:
        if fix_all_ui():
            logger.info("\n✨ All UI fixes completed successfully! You can now restart the application.")
            sys.exit(0)
        else:
            logger.error("\n⚠️ Some UI fixes failed. Check the logs for details.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error during UI fixes: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
