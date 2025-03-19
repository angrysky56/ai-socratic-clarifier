#!/usr/bin/env python3
"""
Fix Project Script for AI-Socratic-Clarifier

This script fixes the AI-Socratic-Clarifier by:
1. Updating Multimodal integration
2. Enhancing Ollama support with optimized settings
3. Ensuring the RAG system is working correctly
4. Fixing any broken components in the UI
"""

import os
import sys
import shutil
import json
import logging
import tempfile
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUINED_REPO = "/home/ty/Repositories/ai_workspace/ai-socratic-clarifier-ruined"


def backup_file(file_path):
    """Create a backup of a file."""
    backup_path = f"{file_path}.fix_proj_bak"
    if os.path.exists(file_path):
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
    return backup_path


def copy_file_from_ruined(source_rel_path, target_rel_path=None):
    """
    Copy a file from the ruined repo to the current repo.
    
    Args:
        source_rel_path: Relative path in the ruined repo
        target_rel_path: Relative path in the current repo (defaults to source_rel_path)
    
    Returns:
        True if successful, False otherwise
    """
    if target_rel_path is None:
        target_rel_path = source_rel_path
    
    source_path = os.path.join(RUINED_REPO, source_rel_path)
    target_path = os.path.join(BASE_DIR, target_rel_path)
    
    if not os.path.exists(source_path):
        logger.error(f"Source file does not exist: {source_path}")
        return False
    
    # Create backup if target file exists
    if os.path.exists(target_path):
        backup_file(target_path)
    
    # Create target directory if it doesn't exist
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # Copy file
    try:
        shutil.copy2(source_path, target_path)
        logger.info(f"Copied {source_path} to {target_path}")
        return True
    except Exception as e:
        logger.error(f"Error copying file: {e}")
        return False


def fix_multimodal_integration():
    """Fix multimodal integration by copying improved version."""
    logger.info("Fixing multimodal integration...")
    
    # Copy improved multimodal integration files
    files_to_copy = [
        "fixed_multimodal_integration.py",
        "improved_multimodal.py",
        "improved_multimodal_ui.py"
    ]
    
    success = True
    for file in files_to_copy:
        if not copy_file_from_ruined(file):
            success = False
    
    # Update multimodal_integration.py with fixed version
    if os.path.exists(os.path.join(BASE_DIR, "fixed_multimodal_integration.py")):
        shutil.copy2(
            os.path.join(BASE_DIR, "fixed_multimodal_integration.py"),
            os.path.join(BASE_DIR, "multimodal_integration.py")
        )
        logger.info("Updated multimodal_integration.py with fixed version")
    
    # Apply improved multimodal UI changes
    try:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "improved_multimodal.py")], check=True)
        logger.info("Applied improved multimodal UI changes")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error applying improved multimodal UI changes: {e}")
        success = False
    
    return success


def fix_ollama_integration():
    """Fix Ollama integration with optimized settings."""
    logger.info("Fixing Ollama integration...")
    
    # Copy Ollama optimization files
    files_to_copy = [
        "OLLAMA_OPTIMIZATION.md",
        "start_with_optimized_ollama.sh"
    ]
    
    success = True
    for file in files_to_copy:
        if not copy_file_from_ruined(file):
            success = False
    
    # Make shell script executable
    script_path = os.path.join(BASE_DIR, "start_with_optimized_ollama.sh")
    if os.path.exists(script_path):
        os.chmod(script_path, 0o755)
        logger.info("Made start_with_optimized_ollama.sh executable")
    
    # Update config.json to include Ollama optimization settings
    config_path = os.path.join(BASE_DIR, "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Add context_length to Ollama settings
            if "integrations" in config and "ollama" in config["integrations"]:
                config["integrations"]["ollama"]["context_length"] = 8192
                logger.info("Added context_length: 8192 to Ollama settings in config.json")
            
            # Write updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Updated config.json with Ollama optimization settings")
        except Exception as e:
            logger.error(f"Error updating config.json: {e}")
            success = False
    
    return success


def fix_rag_integration():
    """Fix RAG integration to ensure it works correctly."""
    logger.info("Fixing RAG integration...")
    
    success = True
    
    # 1. First check document-rag-routes.py vs web_interface/document_rag_routes.py
    # and copy the more comprehensive version
    root_rag_path = os.path.join(BASE_DIR, "document-rag-routes.py")
    web_rag_path = os.path.join(BASE_DIR, "web_interface", "document_rag_routes.py")
    
    if os.path.exists(root_rag_path) and os.path.exists(web_rag_path):
        # Determine which file is more comprehensive (checking file size as a heuristic)
        root_size = os.path.getsize(root_rag_path)
        web_size = os.path.getsize(web_rag_path)
        
        if root_size > web_size:
            # Root version is more comprehensive, copy to web_interface
            backup_file(web_rag_path)
            shutil.copy2(root_rag_path, web_rag_path)
            logger.info("Copied document-rag-routes.py to web_interface/document_rag_routes.py")
        else:
            # Web version is more comprehensive, copy to root
            backup_file(root_rag_path)
            shutil.copy2(web_rag_path, root_rag_path)
            logger.info("Copied web_interface/document_rag_routes.py to document-rag-routes.py")
    elif os.path.exists(root_rag_path):
        # Only root version exists, copy to web_interface
        os.makedirs(os.path.dirname(web_rag_path), exist_ok=True)
        shutil.copy2(root_rag_path, web_rag_path)
        logger.info("Copied document-rag-routes.py to web_interface/document_rag_routes.py")
    elif os.path.exists(web_rag_path):
        # Only web version exists, copy to root
        shutil.copy2(web_rag_path, root_rag_path)
        logger.info("Copied web_interface/document_rag_routes.py to document-rag-routes.py")
    else:
        logger.error("Neither document-rag-routes.py nor web_interface/document_rag_routes.py exists!")
        success = False
    
    # 2. Make sure document_storage directory exists
    storage_dir = os.path.join(BASE_DIR, "document_storage")
    os.makedirs(storage_dir, exist_ok=True)
    logger.info(f"Ensured document_storage directory exists at {storage_dir}")
    
    # 3. Fix document deletion endpoint
    web_rag_path = os.path.join(BASE_DIR, "web_interface", "document_rag_routes.py")
    if os.path.exists(web_rag_path):
        try:
            with open(web_rag_path, 'r') as f:
                content = f.read()
            
            # Check if the file is using EnhancedDocumentManager and if it has a delete_document function
            if "from enhanced_integration.document_manager import get_document_manager" in content:
                # Using EnhancedDocumentManager, check for delete implementation
                if "# TODO: Add delete_document method" in content:
                    # Fix needed for delete_document method
                    
                    # Create a patched version with delete implementation
                    temp_path = os.path.join(tempfile.gettempdir(), "fixed_document_rag_routes.py")
                    with open(temp_path, 'w') as f:
                        # Replace the delete_document route
                        delete_route_start = content.find("@document_rag_bp.route('/api/documents/<document_id>/delete'")
                        delete_route_end = content.find("@document_rag_bp.route", delete_route_start + 1)
                        
                        if delete_route_start >= 0 and delete_route_end >= 0:
                            # Create new implementation
                            new_delete_route = """@document_rag_bp.route('/api/documents/<document_id>/delete', methods=['POST'])
def delete_document(document_id):
    \"\"\"
    Delete a document and its associated files.
    \"\"\"
    try:
        # Get document manager
        document_manager = get_document_manager()
        
        # Get document metadata
        doc_metadata = document_manager.get_document_by_id(document_id)
        
        if not doc_metadata:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        # Delete all document files
        raw_path = doc_metadata.get("raw_path")
        text_path = doc_metadata.get("text_path")
        embedding_path = doc_metadata.get("embedding_path")
        
        # Delete raw file and its directory
        if raw_path and os.path.exists(raw_path):
            doc_dir = os.path.dirname(raw_path)
            if os.path.exists(doc_dir):
                try:
                    shutil.rmtree(doc_dir)
                    logger.info(f"Deleted raw document directory: {doc_dir}")
                except Exception as e:
                    logger.error(f"Error deleting raw document directory: {e}")
        
        # Delete text file and its directory
        if text_path and os.path.exists(text_path):
            text_dir = os.path.dirname(text_path)
            if os.path.exists(text_dir):
                try:
                    shutil.rmtree(text_dir)
                    logger.info(f"Deleted text document directory: {text_dir}")
                except Exception as e:
                    logger.error(f"Error deleting text document directory: {e}")
        
        # Delete embedding file and its directory
        if embedding_path and os.path.exists(embedding_path):
            embedding_dir = os.path.dirname(embedding_path)
            if os.path.exists(embedding_dir):
                try:
                    shutil.rmtree(embedding_dir)
                    logger.info(f"Deleted embedding directory: {embedding_dir}")
                except Exception as e:
                    logger.error(f"Error deleting embedding directory: {e}")
        
        # Remove document from index
        documents = document_manager.index["documents"]
        document_manager.index["documents"] = [doc for doc in documents if doc.get("id") != document_id]
        document_manager._save_index()
        
        return jsonify({
            'success': True,
            'message': f"Document deleted successfully"
        })
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500"""
                            
                            # Replace the old implementation with the new one
                            new_content = content[:delete_route_start] + new_delete_route + content[delete_route_end:]
                            
                            # Write the patched file
                            backup_file(web_rag_path)
                            with open(web_rag_path, 'w') as f:
                                f.write(new_content)
                            
                            logger.info("Fixed delete_document implementation in document_rag_routes.py")
        except Exception as e:
            logger.error(f"Error patching document_rag_routes.py: {e}")
            success = False
    
    return success


def fix_ui_integration():
    """Fix UI integration to ensure all components work together."""
    logger.info("Fixing UI integration...")
    
    success = True
    
    # 1. Apply sre_sot fixes
    try:
        if os.path.exists(os.path.join(BASE_DIR, "fix_sre_sot_all.py")):
            subprocess.run([sys.executable, os.path.join(BASE_DIR, "fix_sre_sot_all.py")], check=True)
            logger.info("Applied SRE_SOT fixes")
        else:
            logger.warning("Could not find fix_sre_sot_all.py - skipping SRE_SOT fixes")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error applying SRE_SOT fixes: {e}")
        success = False
    
    # 2. Apply UI fixes
    try:
        if os.path.exists(os.path.join(BASE_DIR, "fix_ui_simplified.py")):
            subprocess.run([sys.executable, os.path.join(BASE_DIR, "fix_ui_simplified.py")], check=True)
            logger.info("Applied UI fixes")
        else:
            logger.warning("Could not find fix_ui_simplified.py - skipping UI fixes")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error applying UI fixes: {e}")
        success = False
    
    # 3. Copy START_GUIDE.md if it doesn't exist
    if not os.path.exists(os.path.join(BASE_DIR, "START_GUIDE.md")):
        if not copy_file_from_ruined("START_GUIDE.md"):
            logger.warning("Could not copy START_GUIDE.md")
    
    return success


def create_optimized_start_script():
    """Create an optimized start script that incorporates all fixes."""
    logger.info("Creating optimized start script...")
    
    script_path = os.path.join(BASE_DIR, "start_optimized.py")
    
    script_content = """#!/usr/bin/env python3
\"\"\"
Optimized start script for AI-Socratic-Clarifier
This script ensures proper initialization of all components
and uses optimized settings for Ollama.
\"\"\"

import os
import sys
import json
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def set_ollama_env_vars():
    \"\"\"Set Ollama optimization environment variables.\"\"\"
    os.environ["OLLAMA_CONTEXT_LENGTH"] = "8192"
    os.environ["OLLAMA_FLASH_ATTENTION"] = "1"
    os.environ["OLLAMA_KV_CACHE_TYPE"] = "q8_0"
    logger.info("Set Ollama optimization environment variables")

def update_config():
    \"\"\"Ensure config.json has correct settings.\"\"\"
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Ensure Ollama settings are correct
            if "integrations" not in config:
                config["integrations"] = {}
            
            if "ollama" not in config["integrations"]:
                config["integrations"]["ollama"] = {}
            
            ollama_config = config["integrations"]["ollama"]
            
            # Set optimized settings
            ollama_config["context_length"] = 8192
            
            # Ensure multimodal settings
            if "multimodal_model" not in ollama_config:
                ollama_config["multimodal_model"] = "llava:latest"
            
            # Ensure settings are correct
            if "settings" not in config:
                config["settings"] = {}
            
            settings = config["settings"]
            settings["use_multimodal"] = True
            settings["use_sot"] = True
            settings["use_llm_reasoning"] = True
            
            # Write updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Updated config.json with optimized settings")
        else:
            logger.error(f"Configuration file not found at {config_path}")
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")

def ensure_document_storage():
    \"\"\"Ensure document storage directory exists.\"\"\"
    storage_dir = os.path.join(os.path.dirname(__file__), 'document_storage')
    os.makedirs(storage_dir, exist_ok=True)
    
    # Create necessary subdirectories
    subdirs = ['raw', 'processed', 'embeddings', 'temp']
    for subdir in subdirs:
        os.makedirs(os.path.join(storage_dir, subdir), exist_ok=True)
    
    logger.info(f"Ensured document storage directory at {storage_dir}")

def start_ui():
    \"\"\"Start the UI with the standard script.\"\"\"
    try:
        import start_ui
        logger.info("Starting UI...")
        start_ui.main()
    except ImportError:
        try:
            # Fallback: Try running as script
            subprocess.run([sys.executable, "start_ui.py"])
        except Exception as e:
            logger.error(f"Error starting UI: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("=" * 70)
    print("   Optimized AI-Socratic-Clarifier Startup")
    print("   with Enhanced Multimodal and RAG Support")
    print("=" * 70)
    
    # Setup steps
    set_ollama_env_vars()
    update_config()
    ensure_document_storage()
    
    # Start UI
    start_ui()
"""
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    
    logger.info(f"Created optimized start script at {script_path}")
    return True


def main():
    """Main function to run all fixes."""
    print("\n" + "="*70)
    print("   AI-Socratic-Clarifier Fix Project Tool")
    print("="*70 + "\n")
    
    # Run all fixes
    multimodal_fixed = fix_multimodal_integration()
    ollama_fixed = fix_ollama_integration()
    rag_fixed = fix_rag_integration()
    ui_fixed = fix_ui_integration()
    start_script_created = create_optimized_start_script()
    
    # Print summary
    print("\n" + "="*70)
    print("   Fix Summary")
    print("="*70)
    print(f"✓ Multimodal Integration: {'Fixed' if multimodal_fixed else 'Some issues remain'}")
    print(f"✓ Ollama Optimization: {'Fixed' if ollama_fixed else 'Some issues remain'}")
    print(f"✓ RAG Integration: {'Fixed' if rag_fixed else 'Some issues remain'}")
    print(f"✓ UI Integration: {'Fixed' if ui_fixed else 'Some issues remain'}")
    print(f"✓ Optimized Start Script: {'Created' if start_script_created else 'Failed to create'}")
    
    # Print instructions
    print("\n" + "="*70)
    print("   Usage Instructions")
    print("="*70)
    print("1. Start the application with the optimized script:")
    print("   ./start_optimized.py")
    print("")
    print("2. Or use the Ollama optimized script:")
    print("   ./start_with_optimized_ollama.sh")
    print("")
    print("3. Access the web interface at:")
    print("   http://localhost:5000")
    print("")
    print("   - Enhanced UI: /enhanced")
    print("   - Reflective mode: /reflection")
    print("   - Document RAG: Available in all interfaces")
    print("")
    print("4. See OLLAMA_OPTIMIZATION.md for more details on performance optimization")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
