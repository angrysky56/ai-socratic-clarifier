#!/usr/bin/env python3
"""
Fix for model display and document download issues in AI-Socratic-Clarifier.
"""
import os
import json
from pathlib import Path

def fix_model_display():
    """Fix the model display to show the correct model from config."""
    # First, check the config file to confirm the model
    config_path = Path(__file__).parent / "../../../../../../../../config.json"
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}")
        return False
    
    # Read the config to get the actual model
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Get the model from config
    model_name = config.get("integrations", {}).get("ollama", {}).get("default_model", "gemma3")
    print(f"Config specifies model: {model_name}")
    
    # Fix the model in enhanced_chat.html
    html_path = Path(__file__).parent / "web_interface" / "templates" / "enhanced_chat.html"
    if not html_path.exists():
        print(f"Error: Enhanced chat HTML not found at {html_path}")
        return False
    
    # Read the file
    with open(html_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(html_path) + ".model_fix_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Update the model name in the HTML
    if '<span id="currentLLM">llama3</span>' in content:
        content = content.replace(
            '<span id="currentLLM">llama3</span>', 
            f'<span id="currentLLM">{model_name}</span>'
        )
        print(f"Updated model name in HTML to {model_name}")
    
    # Update the JavaScript to use the correct model
    model_update_js = f"""
                // Update model info from config
                document.getElementById('currentModel').textContent = 'Model: {model_name}';
                document.getElementById('currentLLM').textContent = '{model_name}';
    """
    
    # Add this to appropriate JavaScript sections
    if "function initialize() {" in content:
        content = content.replace(
            "function initialize() {",
            f"function initialize() {{{model_update_js}"
        )
        print("Added model update to initialization code")
    
    # Write the updated content
    with open(html_path, 'w') as f:
        f.write(content)
    
    # Now fix the model in direct_integration.py to ensure it uses the correct model
    integration_path = Path(__file__).parent / "web_interface" / "direct_integration.py"
    if not integration_path.exists():
        print(f"Error: Direct integration file not found at {integration_path}")
        return False
    
    # Read the file
    with open(integration_path, 'r') as f:
        integration_content = f.read()
    
    # Make a backup
    backup_path = str(integration_path) + ".model_fix_bak"
    with open(backup_path, 'w') as f:
        f.write(integration_content)
    print(f"Created backup at {backup_path}")
    
    # Update the default model in the code
    if 'model = "deepseek-r1:7b"  # Default' in integration_content:
        integration_content = integration_content.replace(
            'model = "deepseek-r1:7b"  # Default',
            f'model = "{model_name}"  # Default'
        )
        print(f"Updated default model in direct_integration.py to {model_name}")
    
    # Write the updated content
    with open(integration_path, 'w') as f:
        f.write(integration_content)
    
    return True

def fix_document_download():
    """Fix the document download functionality."""
    # Fix the enhanced_routes.py file send_file usage
    routes_path = Path(__file__).parent / "web_interface" / "enhanced_routes.py"
    if not routes_path.exists():
        print(f"Error: Enhanced routes file not found at {routes_path}")
        return False
    
    # Read the file
    with open(routes_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(routes_path) + ".download_fix2_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Replace the send_file usage with a more compatible version
    if "return send_file(" in content:
        # Find the download_document function
        download_func_start = content.find("def download_document(doc_id):")
        if download_func_start != -1:
            # Find the return send_file part
            send_file_start = content.find("return send_file(", download_func_start)
            if send_file_start != -1:
                # Find the end of the send_file statement
                send_file_end = content.find(")", send_file_start)
                if send_file_end != -1:
                    # Get the full send_file statement
                    send_file_statement = content[send_file_start:send_file_end+1]
                    
                    # Create a modified version with more basic parameters
                    new_send_file = """
        # Enhanced send_file with better compatibility
        try:
            # For newer Flask versions
            return send_file(
                raw_path,
                as_attachment=True,
                download_name=doc_metadata.get("name", "document")
            )
        except TypeError:
            # For older Flask versions
            return send_file(
                raw_path,
                as_attachment=True,
                attachment_filename=doc_metadata.get("name", "document")
            )
        except Exception as e:
            # Last resort fallback
            logger.error(f"Error using send_file: {e}")
            from flask import Response
            with open(raw_path, 'rb') as f:
                data = f.read()
            
            response = Response(data, mimetype='application/octet-stream')
            response.headers.set('Content-Disposition', f'attachment; filename={doc_metadata.get("name", "document")}')
            return response"""
                    
                    # Replace the send_file statement
                    content = content.replace(send_file_statement, new_send_file)
                    print("Updated send_file implementation with better compatibility")
        
        # Write the updated content
        with open(routes_path, 'w') as f:
            f.write(content)
    
    # Now fix the document_manager.py file
    manager_path = Path(__file__).parent / "enhanced_integration" / "document_manager.py"
    if not manager_path.exists():
        print(f"Error: Document manager file not found at {manager_path}")
        return False
    
    # Read the file
    with open(manager_path, 'r') as f:
        manager_content = f.read()
    
    # Make a backup
    backup_path = str(manager_path) + ".fix_bak"
    with open(backup_path, 'w') as f:
        f.write(manager_content)
    print(f"Created backup at {backup_path}")
    
    # Add debug logging for document retrieval
    if "def get_document_by_id(self, doc_id):" in manager_content:
        # Find the function
        func_start = manager_content.find("def get_document_by_id(self, doc_id):")
        if func_start != -1:
            # Insert logging after the function definition
            insert_point = manager_content.find("\n", func_start) + 1
            if insert_point > 0:
                log_line = '        logger.info(f"Retrieving document with ID: {doc_id}")\n'
                manager_content = manager_content[:insert_point] + log_line + manager_content[insert_point:]
                print("Added logging to document retrieval function")
            
            # Add logging before return statement
            if "return doc" in manager_content:
                return_point = manager_content.find("return doc", func_start)
                if return_point != -1:
                    log_line = '                logger.info(f"Found document: {doc.get(\'name\')}, raw_path exists: {os.path.exists(doc.get(\'raw_path\', \'\'))}")\n                '
                    manager_content = manager_content[:return_point] + log_line + manager_content[return_point:]
                    print("Added logging before return statement")
    
    # Write the updated content
    with open(manager_path, 'w') as f:
        f.write(manager_content)
    
    # Ensure document storage directories exist
    storage_dir = Path(__file__).parent / "document_storage"
    storage_dir.mkdir(exist_ok=True)
    
    for subdir in ["raw", "processed", "embeddings", "temp"]:
        (storage_dir / subdir).mkdir(exist_ok=True)
        print(f"Ensured {subdir} directory exists")
    
    # Ensure document index exists with proper structure
    index_path = storage_dir / "document_index.json"
    if not index_path.exists():
        with open(index_path, 'w') as f:
            json.dump({
                "documents": [],
                "last_updated": "",
                "version": "1.0"
            }, f, indent=2)
        print("Created document index file")
    
    return True

def main():
    """Main function."""
    print("Fixing model display and document download issues...")
    
    # Fix model display
    model_fixed = fix_model_display()
    if model_fixed:
        print("✅ Fixed model display")
    else:
        print("❌ Failed to fix model display")
    
    # Fix document download
    download_fixed = fix_document_download()
    if download_fixed:
        print("✅ Fixed document download")
    else:
        print("❌ Failed to fix document download")
    
    print("\nDone! Please restart the application with:")
    print("python start_enhanced_ui.py")

if __name__ == "__main__":
    main()
