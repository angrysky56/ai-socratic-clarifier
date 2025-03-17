#!/usr/bin/env python3
"""
Comprehensive fix for the enhanced UI issues in AI-Socratic-Clarifier.

This script:
1. Fixes the HTML structure in base.html
2. Ensures the document storage directories are properly set up
3. Fixes the navigation structure to avoid duplicate tabs
4. Ensures LLM integration works properly
"""

import os
import sys
import json
from pathlib import Path
import shutil

def fix_base_html():
    """Fix the HTML structure in base.html."""
    file_path = Path(__file__).parent / "web_interface" / "templates" / "base.html"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(file_path) + ".fix_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Fix the navigation HTML structure (properly close tags)
    fixed_nav = """                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/' %}active{% endif %}" href="/">
                            <i class="bi bi-house-door"></i> Home
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/enhanced' %}active{% endif %}" href="/enhanced">
                            <i class="bi bi-stars"></i> Enhanced
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/chat' %}active{% endif %}" href="/chat">
                            <i class="bi bi-chat-dots"></i> Chat
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/reflection' %}active{% endif %}" href="/reflection">
                            <i class="bi bi-diagram-3"></i> Reflection
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/multimodal' %}active{% endif %}" href="/multimodal">
                            <i class="bi bi-file-earmark-image"></i> Documents
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/settings' %}active{% endif %}" href="/settings">
                            <i class="bi bi-gear"></i> Settings
                        </a>
                    </li>
                </ul>"""
    
    # Find the navigation section and replace it
    nav_start = content.find('<ul class="navbar-nav me-auto">')
    nav_end = content.find('</ul>', nav_start) + 5
    
    if nav_start != -1 and nav_end != -1:
        updated_content = content[:nav_start] + fixed_nav + content[nav_end:]
        
        # Write the updated content
        with open(file_path, 'w') as f:
            f.write(updated_content)
        
        print("Fixed HTML structure in base.html")
        return True
    else:
        print("Error: Could not find navigation section in base.html")
        return False

def ensure_document_storage():
    """Ensure document storage directories exist and have proper permissions."""
    # Create main directory if it doesn't exist
    storage_dir = Path(__file__).parent / "document_storage"
    storage_dir.mkdir(exist_ok=True)
    print(f"Ensured document storage directory exists at {storage_dir}")
    
    # Create subdirectories
    for subdir in ["raw", "processed", "embeddings", "temp"]:
        (storage_dir / subdir).mkdir(exist_ok=True)
    
    # Create an empty document index if it doesn't exist
    index_file = storage_dir / "document_index.json"
    if not index_file.exists():
        with open(index_file, 'w') as f:
            json.dump({
                "documents": [],
                "last_updated": "",
                "version": "1.0"
            }, f, indent=2)
        print("Created empty document index")
    
    # Create temp directory for uploads
    temp_dir = Path(__file__).parent / "web_interface" / "temp"
    temp_dir.mkdir(exist_ok=True)
    print(f"Created temp directory at {temp_dir}")
    
    # Ensure proper permissions
    if sys.platform != "win32":
        try:
            import stat
            os.chmod(storage_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
            for subdir in storage_dir.iterdir():
                if subdir.is_dir():
                    os.chmod(subdir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
            os.chmod(temp_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
            print("Set proper directory permissions")
        except Exception as e:
            print(f"Warning: Could not set permissions: {e}")
    
    return True

def fix_direct_integration():
    """Fix the direct_integration.py to properly handle document_context."""
    file_path = Path(__file__).parent / "web_interface" / "direct_integration.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(file_path) + ".fix_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Check if the function signature already includes document_context
    if "def direct_analyze_text(text, mode=\"standard\", use_sot=True, max_questions=5, document_context=None):" in content:
        print("direct_analyze_text already has document_context parameter")
    else:
        # Replace the function signature
        old_signature = "def direct_analyze_text(text, mode=\"standard\", use_sot=True, max_questions=5):"
        new_signature = "def direct_analyze_text(text, mode=\"standard\", use_sot=True, max_questions=5, document_context=None):"
        content = content.replace(old_signature, new_signature)
        print("Updated direct_analyze_text function signature")
    
    # Fix the document_context handling code - move it to the right position
    doccontext_code = """    # Initialize document_context if not provided
    if document_context is None:
        document_context = []
    
    # Process any document context if provided
    document_text = ""
    if document_context:
        logger.info(f"Processing document context with {len(document_context)} documents")
        for doc in document_context:
            if isinstance(doc, dict) and "content" in doc:
                # Add document content to analysis context
                content = doc.get("content", "")
                if content:
                    document_text += f"\\n\\nDocument content: {content[:500]}..."
"""
    
    # Check if document_context handling code is in the wrong place (before docstring)
    if "# Initialize document_context if not provided" in content and 'document_text = ""' in content:
        # Remove the misplaced code
        start_idx = content.find("# Initialize document_context if not provided")
        end_idx = content.find('"""', start_idx)
        if start_idx != -1 and end_idx != -1:
            content = content[:start_idx] + content[end_idx:]
            print("Removed misplaced document_context code")
    
    # Add the document_context handling code at the correct position (after docstring)
    function_start = content.find("def direct_analyze_text")
    docstring_end = content.find('"""', function_start)
    docstring_end = content.find('"""', docstring_end + 3) + 3
    
    if docstring_end != 2:  # -1 + 3 = 2, meaning docstring not found
        # Insert at the right position (after docstring)
        content = content[:docstring_end] + "\n" + doccontext_code + content[docstring_end:]
        print("Added document_context handling code at correct position")
    
    # Update the document_text variable in the prompt
    if 'Please analyze this text: "{text}"' in content:
        content = content.replace(
            'Please analyze this text: "{text}"',
            'Please analyze this text: "{text}"{document_text}'
        )
        print("Added document_text to prompt")
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed direct_integration.py")
    return True

def fix_enhanced_routes():
    """Fix the enhanced_routes.py to better handle the document_context parameter errors."""
    file_path = Path(__file__).parent / "web_interface" / "enhanced_routes.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(file_path) + ".fix_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Check if error handling is already added
    if "try:" in content and "document_context" in str(content) and "TypeError as e" in content:
        print("Enhanced routes already has error handling for document_context")
    else:
        # Find the call to direct_analyze_text with document_context and add error handling
        old_call = "result = direct_analyze_text(message, mode, use_sot, document_context=document_context)"
        new_call = """try:
                # Try with document_context parameter
                result = direct_analyze_text(message, mode, use_sot, document_context=document_context)
            except TypeError as e:
                if "document_context" in str(e):
                    # Fallback to call without document_context
                    logger.warning("direct_analyze_text() doesn't support document_context, falling back")
                    result = direct_analyze_text(message, mode, use_sot)
                    
                    # Add document context to the result manually
                    if document_context:
                        result["document_context"] = document_context
                else:
                    # Re-raise any other errors
                    raise"""
        
        content = content.replace(old_call, new_call)
        print("Added error handling for document_context parameter in enhanced_routes.py")
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed enhanced_routes.py")
    return True

def fix_root_redirect():
    """Ensure the root route properly redirects to the enhanced UI."""
    file_path = Path(__file__).parent / "web_interface" / "app.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(file_path) + ".redirect_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Check for duplicate redirect imports
    if content.count('redirect') > 10:  # Arbitrary threshold to detect duplicates
        # Fix duplicate imports
        from_flask_line = "from flask import Flask, render_template, request, jsonify, session, redirect, url_for"
        if from_flask_line not in content:
            # Find the Flask import line
            flask_import_line = content.find("from flask import")
            flask_import_end = content.find("\n", flask_import_line)
            
            if flask_import_line != -1 and flask_import_end != -1:
                # Replace with a clean import line
                content = content[:flask_import_line] + from_flask_line + content[flask_import_end:]
                print("Fixed duplicate Flask imports")
    
    # Check if root redirect is correct
    if "def index():" in content and "return redirect('/enhanced')" in content:
        print("Root redirect to enhanced UI already exists")
    else:
        # Find the index route
        index_start = content.find("@app.route('/', methods=['GET'])")
        index_end = content.find("@app.route", index_start + 1)
        
        if index_start != -1 and index_end != -1:
            # Create new index route
            new_index = """@app.route('/', methods=['GET'])
def index():
    \"\"\"Redirect to enhanced UI if available, otherwise render the main page.\"\"\"
    if 'enhanced' in app.blueprints:
        return redirect('/enhanced')
    return render_template('index.html', modes=clarifier.available_modes())

"""
            # Replace the old index route
            content = content[:index_start] + new_index + content[index_end:]
            print("Updated root redirect to enhanced UI")
        else:
            print("Could not find index route")
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed root redirect in app.py")
    return True
def ensure_temp_directory():
    """Ensure the temp directory exists for file uploads."""
    temp_dir = Path(__file__).parent / "web_interface" / "temp"
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Created temp directory at {temp_dir}")
    return True

def fix_start_enhanced_ui():
    """Fix the start_enhanced_ui.py script to avoid blueprint registration issues."""
    file_path = Path(__file__).parent / "start_enhanced_ui.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(file_path) + ".fix_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Check if the script already has the blueprint check
    if "is_enhanced_registered" in content and "app.blueprints" in content:
        print("start_enhanced_ui.py already has blueprint registration check")
    else:
        # Find the blueprint registration section
        reg_line = content.find("flask_app.register_blueprint(enhanced_bp)")
        
        if reg_line != -1:
            # Replace with conditional registration
            old_reg = "flask_app.register_blueprint(enhanced_bp)"
            new_reg = """# Check if enhanced_bp is already registered to avoid duplicate registration
        is_enhanced_registered = False
        if hasattr(flask_app, 'blueprints'):
            is_enhanced_registered = 'enhanced' in flask_app.blueprints
        
        # Register enhanced routes only if not already registered
        if not is_enhanced_registered:
            flask_app.register_blueprint(enhanced_bp)
            logger.info("Enhanced routes registered")
        else:
            logger.info("Enhanced routes already registered, skipping registration")"""
            
            content = content.replace(old_reg, new_reg)
            print("Added blueprint registration check to start_enhanced_ui.py")
        else:
            print("Could not find blueprint registration in start_enhanced_ui.py")
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed start_enhanced_ui.py")
    return True

def main():
    """Run all fixes."""
    print("Starting comprehensive fix for enhanced UI issues...")
    
    # Fix HTML structure
    if fix_base_html():
        print("✅ Fixed HTML structure in base.html")
    else:
        print("❌ Failed to fix HTML structure")
    
    # Ensure document storage
    if ensure_document_storage():
        print("✅ Ensured document storage directories exist")
    else:
        print("❌ Failed to ensure document storage")
    
    # Fix direct_integration.py
    if fix_direct_integration():
        print("✅ Fixed direct_integration.py")
    else:
        print("❌ Failed to fix direct_integration.py")
    
    # Fix enhanced_routes.py
    if fix_enhanced_routes():
        print("✅ Fixed enhanced_routes.py")
    else:
        print("❌ Failed to fix enhanced_routes.py")
    
    # Fix root redirect
    if fix_root_redirect():
        print("✅ Fixed root redirect in app.py")
    else:
        print("❌ Failed to fix root redirect")
    
    # Ensure temp directory
    if ensure_temp_directory():
        print("✅ Ensured temp directory exists")
    else:
        print("❌ Failed to ensure temp directory")
    
    # Fix start_enhanced_ui.py
    if fix_start_enhanced_ui():
        print("✅ Fixed start_enhanced_ui.py")
    else:
        print("❌ Failed to fix start_enhanced_ui.py")
    
    print("\nAll fixes applied! Please restart the application with:")
    print("python start_enhanced_ui.py")

if __name__ == "__main__":
    main()
