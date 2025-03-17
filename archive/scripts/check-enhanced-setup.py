#!/usr/bin/env python3
"""
Setup verification script for the enhanced UI.

This script checks and creates all necessary directories and files
for the enhanced UI to work properly.
"""

import os
import sys
import shutil
from pathlib import Path

def check_directory(dir_path, create=True):
    """Check if directory exists and create it if needed."""
    if not os.path.exists(dir_path):
        if create:
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory: {dir_path}")
            return True
        else:
            print(f"Directory does not exist: {dir_path}")
            return False
    return True

def check_file(file_path, template_path=None):
    """Check if file exists and copy template if needed."""
    if not os.path.exists(file_path):
        if template_path and os.path.exists(template_path):
            shutil.copy2(template_path, file_path)
            print(f"Created file from template: {file_path}")
            return True
        else:
            print(f"File does not exist: {file_path}")
            return False
    return True

def setup_enhanced_ui():
    """Set up all required components for the enhanced UI."""
    # Set up base paths
    base_dir = Path(__file__).parent
    web_interface_dir = base_dir / "web_interface"
    enhanced_integration_dir = base_dir / "enhanced_integration"
    
    # Check enhanced_integration directory
    if check_directory(enhanced_integration_dir):
        # Check required integration files
        integration_py = enhanced_integration_dir / "integration.py"
        document_manager_py = enhanced_integration_dir / "document_manager.py"
        enhanced_ecosystem_py = enhanced_integration_dir / "enhanced_reflective_ecosystem.py"
        
        if not check_file(integration_py):
            print("Missing integration.py in enhanced_integration directory")
        
        if not check_file(document_manager_py):
            print("Missing document_manager.py in enhanced_integration directory")
        
        if not check_file(enhanced_ecosystem_py):
            print("Missing enhanced_reflective_ecosystem.py in enhanced_integration directory")
    
    # Check web_interface directory
    if check_directory(web_interface_dir):
        # Check required web interface files
        enhanced_routes_py = web_interface_dir / "enhanced_routes.py"
        if not check_file(enhanced_routes_py):
            print("Missing enhanced_routes.py in web_interface directory")
        
        # Check templates directory
        templates_dir = web_interface_dir / "templates"
        if check_directory(templates_dir):
            enhanced_chat_html = templates_dir / "enhanced_chat.html"
            if not check_file(enhanced_chat_html):
                print("Missing enhanced_chat.html in templates directory")
            
            # Check components directory
            components_dir = templates_dir / "components"
            if check_directory(components_dir):
                document_panel_html = components_dir / "document_panel.html"
                sre_visualization_html = components_dir / "sre_visualization.html"
                
                if not check_file(document_panel_html):
                    print("Missing document_panel.html in components directory")
                
                if not check_file(sre_visualization_html):
                    print("Missing sre_visualization.html in components directory")
        
        # Check static directory
        static_dir = web_interface_dir / "static"
        if check_directory(static_dir):
            # Check CSS directory
            css_dir = static_dir / "css"
            if check_directory(css_dir):
                enhanced_css_dir = css_dir / "enhanced"
                if check_directory(enhanced_css_dir):
                    document_panel_css = enhanced_css_dir / "document_panel.css"
                    sre_visualization_css = enhanced_css_dir / "sre_visualization.css"
                    
                    if not check_file(document_panel_css):
                        print("Missing document_panel.css in enhanced CSS directory")
                    
                    if not check_file(sre_visualization_css):
                        print("Missing sre_visualization.css in enhanced CSS directory")
            
            # Check JS directory
            js_dir = static_dir / "js"
            if check_directory(js_dir):
                enhanced_js_dir = js_dir / "enhanced"
                if check_directory(enhanced_js_dir):
                    document_manager_js = enhanced_js_dir / "document_manager.js"
                    sre_visualization_js = enhanced_js_dir / "sre_visualization.js"
                    
                    if not check_file(document_manager_js):
                        print("Missing document_manager.js in enhanced JS directory")
                    
                    if not check_file(sre_visualization_js):
                        print("Missing sre_visualization.js in enhanced JS directory")
    
    # Check document_storage directory
    document_storage_dir = base_dir / "document_storage"
    if check_directory(document_storage_dir):
        # Create subdirectories
        check_directory(document_storage_dir / "raw")
        check_directory(document_storage_dir / "processed")
        check_directory(document_storage_dir / "embeddings")
        check_directory(document_storage_dir / "temp")
    
    # Check start_enhanced_ui.py
    start_enhanced_ui_py = base_dir / "start_enhanced_ui.py"
    if not check_file(start_enhanced_ui_py):
        print("Missing start_enhanced_ui.py in root directory")

def main():
    """Main entry point for setup verification."""
    print("Checking enhanced UI setup...")
    
    # Add the parent directory to the Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Set up enhanced UI
    setup_enhanced_ui()
    
    print("\nSetup verification complete. If any issues were reported above, please fix them.")
    print("To fix the root route redirect issue, run: python fix_enhanced_ui_redirect.py")
    print("Then start the enhanced UI with: python start_enhanced_ui.py")

if __name__ == "__main__":
    main()
