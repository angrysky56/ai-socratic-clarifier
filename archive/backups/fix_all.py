#!/usr/bin/env python3
"""
Comprehensive fix for SRE and SoT integration in the AI-Socratic-Clarifier.

This script runs all the necessary fixes to ensure proper integration of the
Sequential of Thought (SoT) and Symbiotic Reflective Ecosystem (SRE) components.
"""

import os
import sys
import logging
import importlib.util
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def import_script(script_path):
    """Import a Python script as a module."""
    if not os.path.exists(script_path):
        logger.error(f"Script not found: {script_path}")
        return None
    
    module_name = os.path.basename(script_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_fix_script(script_path, function_name):
    """Run a fix script by importing it and calling the main function."""
    try:
        module = import_script(script_path)
        if module and hasattr(module, function_name):
            logger.info(f"Running {os.path.basename(script_path)}...")
            result = getattr(module, function_name)()
            
            if result:
                logger.info(f"✅ {os.path.basename(script_path)} completed successfully")
            else:
                logger.warning(f"⚠️ {os.path.basename(script_path)} reported issues")
            
            return result
        else:
            logger.error(f"Could not find function {function_name} in {script_path}")
            return False
    except Exception as e:
        logger.error(f"Error running {script_path}: {e}")
        return False

def fix_everything():
    """Run all fix scripts in the correct order."""
    project_root = "/home/ty/Repositories/ai_workspace/ai-socratic-clarifier"
    
    # List of scripts and their main functions to run
    scripts = [
        (os.path.join(project_root, "fix_ui_simplified.py"), "fix_ui_issues"),
        (os.path.join(project_root, "fix_config_settings.py"), "fix_config_settings"),
        (os.path.join(project_root, "fix_config_paths.py"), "fix_all_config_paths")
    ]
    
    success = True
    for script_path, function_name in scripts:
        if os.path.exists(script_path):
            success &= run_fix_script(script_path, function_name)
        else:
            logger.warning(f"⚠️ Script not found: {script_path}")
    
    # Try to run the original fix_sre_sot_settings.py script
    original_fix_script = os.path.join(project_root, "fix_sre_sot_settings.py")
    if os.path.exists(original_fix_script):
        logger.info("Running original fix_sre_sot_settings.py script...")
        
        try:
            result = subprocess.run([
                os.path.join(project_root, "venv", "bin", "python"),
                original_fix_script
            ], check=True)
            
            if result.returncode == 0:
                logger.info("✅ Original fix script completed successfully")
            else:
                logger.warning(f"⚠️ Original fix script exited with code {result.returncode}")
                success = False
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running original fix script: {e}")
            success = False
    
    return success

if __name__ == "__main__":
    try:
        print("\n" + "="*80)
        print(" 🔧 AI-Socratic-Clarifier SRE and SoT Integration Fix Tool 🔧 ")
        print("="*80 + "\n")
        
        if fix_everything():
            logger.info("✨ All fixes applied successfully")
            print("\n" + "="*80)
            print(" ✅ SRE and SoT integration successfully fixed! ")
            print("="*80 + "\n")
            print("You can now start the UI with:")
            print("/home/ty/Repositories/ai_workspace/ai-socratic-clarifier/venv/bin/python /home/ty/Repositories/ai_workspace/ai-socratic-clarifier/start_ui.py")
            sys.exit(0)
        else:
            logger.warning("⚠️ Some fixes could not be applied")
            print("\n" + "="*80)
            print(" ⚠️ Some issues could not be fixed automatically ")
            print("="*80 + "\n")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error applying fixes: {e}")
        print("\n" + "="*80)
        print(" ❌ Error occurred during fix process ")
        print("="*80 + "\n")
        sys.exit(1)
