#!/usr/bin/env python3
"""
Comprehensive fix script for the enhanced UI issues.

This script fixes:
1. The document_context parameter issue in direct_integration.py
2. Updates the base.html to handle the enhanced UI tab
3. Ensures PDFs are properly saved and analyzed
4. Fixes any issues with the LLM integration
"""

import os
import sys
import re
from pathlib import Path
import shutil
from loguru import logger

def fix_direct_integration():
    """Fix the direct_integration.py file to add document_context support."""
    integration_path = Path(__file__).parent / "web_interface" / "direct_integration.py"
    
    if not integration_path.exists():
        print(f"Error: Cannot find direct_integration.py at {integration_path}")
        return False
    
    # Read the current content
    with open(integration_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = integration_path.with_suffix('.py.doc_context_bak')
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup of direct_integration.py at {backup_path}")
    
    # Find the direct_analyze_text function signature
    function_pattern = r'def direct_analyze_text\(text, mode="standard", use_sot=True, max_questions=5\):'
    
    # Check if the function exists and update it
    if re.search(function_pattern, content):
        # Update the function signature to include document_context
        updated_signature = 'def direct_analyze_text(text, mode="standard", use_sot=True, max_questions=5, document_context=None):'
        content = re.sub(function_pattern, updated_signature, content)
        
        print("Updated direct_analyze_text function signature to include document_context parameter")
        
        # Find where we process the text content and add document context handling
        # Look for "# Use Ollama to detect issues" which is right before the prompt construction
        prompt_section = r'# Use Ollama to detect issues\s+prompt = f"""'
        
        if re.search(prompt_section, content):
            # Add document context handling before the prompt is constructed
            context_handling = '''    # Initialize document_context if not provided
    if document_context is None:
        document_context = []
        
    # If we have document context, enrich the prompt
    document_text = ""
    if document_context:
        document_text = "\\n\\nRelevant context from documents:\\n"
        for i, doc in enumerate(document_context):
            if "content" in doc:
                # Truncate content if too long
                content = doc["content"]
                if len(content) > 1000:
                    content = content[:1000] + "... [truncated]"
                document_text += f"Document {i+1}: {content}\\n\\n"
    
'''
            # Insert before the prompt construction
            content = re.sub(prompt_section, context_handling + prompt_section, content)
            print("Added document context handling code")
        
        # Update the prompt to include document context if available
        prompt_construction = r'(prompt = f""".*?INSTRUCTIONS:)'
        if re.search(prompt_construction, content, re.DOTALL):
            updated_prompt = r'\1\n    - Consider any provided document context when analyzing the text\n'
            content = re.sub(prompt_construction, updated_prompt, content, flags=re.DOTALL)
            print("Updated prompt to consider document context")
            
            # Add document context to the prompt if available
            prompt_after_text = r'(Please analyze this text: "{text}")'
            updated_text_part = r'\1{document_text}'
            content = re.sub(prompt_after_text, updated_text_part, content)
            print("Added document context to prompt text")
        
        # Write the modified content
        with open(integration_path, 'w') as f:
            f.write(content)
        
        print(f"Successfully updated {integration_path} to handle document_context")
        return True
    else:
        print("Error: Could not find the direct_analyze_text function")
        return False

def fix_base_html():
    """Update the base.html template to include enhanced UI tab."""
    base_path = Path(__file__).parent / "web_interface" / "templates" / "base.html"
    
    if not base_path.exists():
        print(f"Error: Cannot find base.html at {base_path}")
        return False
    
    # Read the current content
    with open(base_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = base_path.with_suffix('.html.navbar_bak')
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup of base.html at {backup_path}")
    
    # Check if the enhanced UI link already exists
    if '<a class="nav-link {% if request.path == \'/enhanced\' %}active{% endif %}" href="/enhanced">' in content:
        print("Enhanced UI tab already exists in base.html")
        return True
    
    # Find the navigation menu items section
    nav_items_pattern = r'<ul class="navbar-nav me-auto">(.*?)</ul>'
    nav_items_match = re.search(nav_items_pattern, content, re.DOTALL)
    
    if nav_items_match:
        # Add enhanced UI tab after the chat tab
        chat_item_pattern = r'<li class="nav-item">\s*<a class="nav-link.*?href="/chat".*?>.*?Chat.*?</a>\s*</li>'
        chat_item_match = re.search(chat_item_pattern, content, re.DOTALL)
        
        if chat_item_match:
            enhanced_tab = '''
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/enhanced' %}active{% endif %}" href="/enhanced">
                            <i class="bi bi-stars"></i> Enhanced
                        </a>
                    </li>'''
            
            modified_nav = content.replace(
                chat_item_match.group(0),
                chat_item_match.group(0) + enhanced_tab
            )
            
            # Write the modified content
            with open(base_path, 'w') as f:
                f.write(modified_nav)
            
            print("Added Enhanced UI tab to navigation menu")
            return True
        else:
            print("Error: Could not find the chat tab in the navigation menu")
            return False
    else:
        print("Error: Could not find the navigation menu in base.html")
        return False

def fix_pdf_storage():
    """Ensure the document storage directories exist and have proper permissions."""
    document_storage_path = Path(__file__).parent / "document_storage"
    
    # Create main document storage directory
    if not document_storage_path.exists():
        document_storage_path.mkdir(parents=True, exist_ok=True)
        print(f"Created main document storage directory at {document_storage_path}")
    
    # Create subdirectories
    for subdir in ["raw", "processed", "embeddings", "temp"]:
        subdir_path = document_storage_path / subdir
        if not subdir_path.exists():
            subdir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created {subdir} directory at {subdir_path}")
    
    # Set proper permissions (for Linux/Mac)
    if sys.platform != "win32":
        try:
            # Make directories writable
            for root, dirs, files in os.walk(document_storage_path):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o644)
                    
            print("Set proper permissions for document storage directories")
        except Exception as e:
            print(f"Warning: Could not set permissions on document storage: {e}")
    
    return True

def fix_enhanced_routes():
    """Fix the enhanced_routes.py file to properly work with the document manager."""
    routes_path = Path(__file__).parent / "web_interface" / "enhanced_routes.py"
    
    if not routes_path.exists():
        print(f"Error: Cannot find enhanced_routes.py at {routes_path}")
        return False
    
    # Read the current content
    with open(routes_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = routes_path.with_suffix('.py.fix_bak')
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup of enhanced_routes.py at {backup_path}")
    
    # Fix import for document_context parameter error
    direct_analyze_import = 'from web_interface.direct_integration import direct_analyze_text'
    
    # Check if there's a direct_analyze_text import issue
    try_except_block = '''
            # Use direct integration to analyze the text
            try:
                # Use the enhancer for question generation
                from web_interface.direct_integration import direct_analyze_text
                result = direct_analyze_text(message, mode, use_sot, document_context=document_context)
            except TypeError as e:
                # Fall back to version without document_context
                if "document_context" in str(e):
                    from web_interface.direct_integration import direct_analyze_text
                    result = direct_analyze_text(message, mode, use_sot)
                    result["document_context"] = document_context
                else:
                    raise'''
    
    # Fix any document_context parameter related errors in the chat_message function
    chat_message_pattern = r'@enhanced_bp\.route\(\'/api/chat\', methods=\[\'POST\'\]\)\ndef chat_message\(\):(.*?)return jsonify\(response\)'
    chat_message_match = re.search(chat_message_pattern, content, re.DOTALL)
    
    if chat_message_match:
        # Replace any direct calls to direct_analyze_text with the try-except block
        chat_content = chat_message_match.group(1)
        if 'result = direct_analyze_text(message, mode, use_sot, document_context=document_context)' in chat_content:
            modified_chat_content = chat_content.replace(
                'result = direct_analyze_text(message, mode, use_sot, document_context=document_context)',
                try_except_block
            )
            
            content = content.replace(chat_content, modified_chat_content)
            print("Added error handling for document_context parameter in chat_message function")
        
        # Write the modified content
        with open(routes_path, 'w') as f:
            f.write(content)
        
        print(f"Successfully updated {routes_path} to handle document_context errors")
        return True
    else:
        print("Error: Could not find the chat_message function in enhanced_routes.py")
        return False

def ensure_temp_directory():
    """Ensure the temp directory exists for document uploads."""
    web_interface_path = Path(__file__).parent / "web_interface"
    temp_path = web_interface_path / "temp"
    
    if not temp_path.exists():
        temp_path.mkdir(parents=True, exist_ok=True)
        print(f"Created temp directory at {temp_path}")
    
    # Set proper permissions (for Linux/Mac)
    if sys.platform != "win32":
        try:
            os.chmod(temp_path, 0o755)
            print("Set proper permissions for temp directory")
        except Exception as e:
            print(f"Warning: Could not set permissions on temp directory: {e}")
    
    return True

def fix_enhanced_ui_redirect():
    """Fix the root route in app.py to properly redirect to enhanced UI."""
    app_path = Path(__file__).parent / "web_interface" / "app.py"
    
    if not app_path.exists():
        print(f"Error: Cannot find app.py at {app_path}")
        return False
    
    # Read the current content
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = app_path.with_suffix('.py.redirect_bak')
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup of app.py at {backup_path}")
    
    # Fix the root route to properly redirect to enhanced UI
    root_route_pattern = r'@app\.route\(\'/\', methods=\[\'GET\'\]\)\s*def index\(\):'
    
    if re.search(root_route_pattern, content):
        # Find the whole function
        index_function_match = re.search(
            r'(@app\.route\(\'/\', methods=\[\'GET\'\]\)\s*def index\(\):.*?)(?=@app\.route|$)', 
            content, 
            re.DOTALL
        )
        
        if index_function_match:
            new_root_route = '''@app.route('/', methods=['GET'])
def index():
    """Redirect to enhanced UI if available, otherwise render the main page."""
    if 'enhanced' in app.blueprints:
        return redirect('/enhanced')
    return render_template('index.html', modes=clarifier.available_modes())
'''
            # Replace the whole function
            content = content.replace(index_function_match.group(1), new_root_route)
            print("Modified root route to redirect to enhanced UI")
            
            # Make sure redirect is imported
            if 'from flask import redirect' not in content:
                # Replace the flask import line
                flask_import_pattern = r'from flask import (.*)'
                if re.search(flask_import_pattern, content):
                    content = re.sub(
                        flask_import_pattern,
                        r'from flask import \1, redirect',
                        content
                    )
                    print("Added redirect import to Flask imports")
            
            # Write the modified content
            with open(app_path, 'w') as f:
                f.write(content)
            
            print(f"Successfully updated {app_path} to redirect root to enhanced UI")
            return True
        else:
            print("Error: Could not find the index function")
            return False
    else:
        print("Error: Could not find the root route in app.py")
        return False

def main():
    """Main function to fix all enhanced UI issues."""
    print("Starting comprehensive enhanced UI fix...")
    
    # Fix document_context parameter issue in direct_integration.py
    if fix_direct_integration():
        print("✅ Fixed document_context parameter issue")
    else:
        print("❌ Failed to fix document_context parameter issue")
    
    # Fix base.html to include enhanced UI tab
    if fix_base_html():
        print("✅ Added enhanced UI tab to navigation")
    else:
        print("❌ Failed to add enhanced UI tab")
    
    # Ensure PDF storage works properly
    if fix_pdf_storage():
        print("✅ Set up document storage directories")
    else:
        print("❌ Failed to set up document storage")
    
    # Ensure temp directory exists
    if ensure_temp_directory():
        print("✅ Set up temp directory for uploads")
    else:
        print("❌ Failed to set up temp directory")
    
    # Fix enhanced routes
    if fix_enhanced_routes():
        print("✅ Fixed enhanced routes for document handling")
    else:
        print("❌ Failed to fix enhanced routes")
    
    # Fix root redirect
    if fix_enhanced_ui_redirect():
        print("✅ Fixed root redirect to enhanced UI")
    else:
        print("❌ Failed to fix root redirect")
    
    print("\nFix complete! Restart the application with 'python start_enhanced_ui.py' to apply changes.")

if __name__ == "__main__":
    main()
