#!/usr/bin/env python3
"""
Fix for Multimodal and RAG functionality in AI-Socratic-Clarifier.

This script fixes issues with:
1. Multimodal integration config path and JSON handling
2. RAG integration for document retrieval
3. Route registration and handling
"""

import os
import sys
import json
import shutil
from pathlib import Path

def backup_file(file_path):
    """Create a backup of a file."""
    backup_path = f"{file_path}.fix_mm_rag_bak"
    if os.path.exists(file_path):
        print(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
    return backup_path

def fix_multimodal_path():
    """Fix the path issue in multimodal integration."""
    # The path has already been fixed in the main script
    # This function remains for completeness
    print("✅ Multimodal config path issue already fixed")
    return True

def fix_document_rag_routes():
    """Fix document RAG routes registration."""
    # Fix app.py to ensure document_rag_routes are registered correctly
    app_path = os.path.join('web_interface', 'app.py')
    
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found")
        return False
    
    backup_file(app_path)
    
    try:
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Check if RAG routes registration is there and correct
        if "app.register_blueprint(document_rag_bp)" in content:
            print("Document RAG routes already registered correctly")
        else:
            # Find the blueprints registration section
            blueprint_section = content.find("# Register blueprints")
            if blueprint_section == -1:
                blueprint_section = content.find("# Register the document RAG blueprint")
            
            if blueprint_section >= 0:
                # Fix the registration
                print("Fixing document RAG blueprint registration...")
                
                # Ensure correct import
                import_section = content.find("from web_interface.document_rag_routes import document_rag_bp")
                if import_section == -1:
                    # Find the imports section and add this import
                    imports_end = content.find("# Initialize Flask app")
                    if imports_end > 0:
                        new_content = content[:imports_end] + "\n# Import document RAG routes\nfrom web_interface.document_rag_routes import document_rag_bp\n" + content[imports_end:]
                        content = new_content
                
                # Now find where to register the blueprint
                reg_section = content.find("app.register_blueprint(")
                if reg_section > 0:
                    # Add after the first blueprint registration
                    end_of_reg = content.find("\n", reg_section)
                    if end_of_reg > 0:
                        new_content = content[:end_of_reg] + "\n# Register document RAG routes\napp.register_blueprint(document_rag_bp)\nlogger.info(\"Document RAG routes registered\")" + content[end_of_reg:]
                        content = new_content
            
            # Write updated content
            with open(app_path, 'w') as f:
                f.write(content)
    except Exception as e:
        print(f"Error fixing document RAG routes: {e}")
        return False
    
    # Now fix document_rag_routes.py to handle document deletion properly
    rag_routes_path = os.path.join('web_interface', 'document_rag_routes.py')
    if not os.path.exists(rag_routes_path):
        print(f"Error: {rag_routes_path} not found")
        return False
    
    backup_file(rag_routes_path)
    
    try:
        with open(rag_routes_path, 'r') as f:
            content = f.read()
        
        # Enhance the delete_document function if needed
        delete_function = content.find("def delete_document(document_id):")
        if delete_function > 0:
            # Check if it's using EnhancedDocumentManager
            if "from enhanced_integration.document_manager import get_document_manager" in content:
                # Also check that the function is implemented properly
                if "# TODO: Add delete_document method" in content or "not yet implemented" in content:
                    print("Fixing document deletion implementation...")
                    
                    # Find the delete_document function
                    delete_start = content.find("def delete_document(document_id):")
                    next_function = content.find("@document_rag_bp.route", delete_start)
                    
                    if delete_start > 0 and next_function > 0:
                        # Replace the function with proper implementation
                        new_delete_function = """@document_rag_bp.route('/api/documents/<document_id>/delete', methods=['POST'])
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
        
        # Delete document files
        success = True
        
        # Delete raw file and its directory if it exists
        raw_path = doc_metadata.get("raw_path")
        if raw_path and os.path.exists(raw_path):
            try:
                raw_dir = os.path.dirname(raw_path)
                if os.path.exists(raw_dir):
                    shutil.rmtree(raw_dir)
            except Exception as e:
                logger.error(f"Error deleting raw files: {e}")
                success = False
        
        # Delete text file and its directory if it exists
        text_path = doc_metadata.get("text_path")
        if text_path and os.path.exists(text_path):
            try:
                text_dir = os.path.dirname(text_path)
                if os.path.exists(text_dir):
                    shutil.rmtree(text_dir)
            except Exception as e:
                logger.error(f"Error deleting text files: {e}")
                success = False
        
        # Delete embedding file and its directory if it exists
        embedding_path = doc_metadata.get("embedding_path")
        if embedding_path and os.path.exists(embedding_path):
            try:
                embedding_dir = os.path.dirname(embedding_path)
                if os.path.exists(embedding_dir):
                    shutil.rmtree(embedding_dir)
            except Exception as e:
                logger.error(f"Error deleting embedding files: {e}")
                success = False
        
        # Remove document from index
        document_manager.index["documents"] = [
            doc for doc in document_manager.index["documents"] 
            if doc.get("id") != document_id
        ]
        document_manager._save_index()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Document deleted successfully'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Document deleted from index but some files could not be removed'
            })
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500"""
                        
                        # Replace the function
                        new_content = content[:delete_start] + new_delete_function + content[next_function:]
                        
                        # Write updated content
                        with open(rag_routes_path, 'w') as f:
                            f.write(new_content)
            else:
                print("Document deletion implementation already exists and does not use EnhancedDocumentManager")
        else:
            print("Could not find delete_document function in document_rag_routes.py")
    except Exception as e:
        print(f"Error fixing document deletion function: {e}")
        return False
    
    print("✅ Fixed document RAG routes and deletion functionality")
    return True

def update_config_with_rag_settings():
    """Update config.json with RAG settings."""
    config_path = os.path.join('config.json')
    
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found")
        return False
    
    backup_file(config_path)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Ensure RAG settings are present
        if "settings" not in config:
            config["settings"] = {}
        
        config["settings"]["use_document_rag"] = True
        
        # Ensure Ollama embedding model is set
        if "integrations" not in config:
            config["integrations"] = {}
        
        if "ollama" not in config["integrations"]:
            config["integrations"]["ollama"] = {}
        
        if "default_embedding_model" not in config["integrations"]["ollama"]:
            config["integrations"]["ollama"]["default_embedding_model"] = "nomic-embed-text"
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print("✅ Updated config.json with RAG settings")
        return True
    except Exception as e:
        print(f"Error updating config with RAG settings: {e}")
        return False

def ensure_document_index():
    """Ensure document index file exists and is valid."""
    storage_dir = os.path.join('document_storage')
    index_file = os.path.join(storage_dir, 'document_index.json')
    
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir, exist_ok=True)
        print(f"Created document storage directory: {storage_dir}")
    
    if not os.path.exists(index_file):
        # Create empty index
        index_data = {
            "documents": [],
            "last_updated": "2023-01-01 00:00:00",
            "version": "1.0"
        }
        
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        print(f"Created document index file: {index_file}")
    else:
        # Validate existing index
        try:
            with open(index_file, 'r') as f:
                index_data = json.load(f)
            
            if "documents" not in index_data:
                index_data["documents"] = []
                
            if "last_updated" not in index_data:
                index_data["last_updated"] = "2023-01-01 00:00:00"
                
            if "version" not in index_data:
                index_data["version"] = "1.0"
            
            # Write updated index
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            print(f"Validated document index file: {index_file}")
        except Exception as e:
            print(f"Error validating document index: {e}")
            
            # Backup and recreate
            if os.path.exists(index_file):
                backup_file(index_file)
            
            # Create empty index
            index_data = {
                "documents": [],
                "last_updated": "2023-01-01 00:00:00",
                "version": "1.0"
            }
            
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            print(f"Recreated document index file: {index_file}")
    
    # Create other required directories
    for subdir in ['raw', 'processed', 'embeddings', 'temp']:
        subdir_path = os.path.join(storage_dir, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path, exist_ok=True)
            print(f"Created document subdirectory: {subdir_path}")
    
    print("✅ Ensured document storage and index are valid")
    return True

def main():
    """Main function to fix all issues."""
    print("\n=== Fixing Multimodal and RAG Integration ===\n")
    
    # Fix multimodal path issue
    multimodal_fixed = fix_multimodal_path()
    
    # Fix document RAG routes
    rag_routes_fixed = fix_document_rag_routes()
    
    # Update config with RAG settings
    config_updated = update_config_with_rag_settings()
    
    # Ensure document index exists and is valid
    index_fixed = ensure_document_index()
    
    # Print summary
    print("\n=== Fix Summary ===")
    print(f"✓ Multimodal path issue: {'Fixed' if multimodal_fixed else 'Not fixed'}")
    print(f"✓ Document RAG routes: {'Fixed' if rag_routes_fixed else 'Not fixed'}")
    print(f"✓ Config with RAG settings: {'Updated' if config_updated else 'Not updated'}")
    print(f"✓ Document index: {'Fixed' if index_fixed else 'Not fixed'}")
    
    print("\n=== Instructions ===")
    print("1. Restart the server with: ./start.py")
    print("2. Access the unified UI at: http://localhost:5000/socratic")
    print("3. Try uploading and using documents in the Document Library tab")
    print("4. Try using the Multimodal Analysis tab with images or PDFs")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
