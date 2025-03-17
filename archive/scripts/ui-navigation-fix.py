#!/usr/bin/env python3
"""
Fix for the index redirection and navigation tab issues.
"""

import os
from pathlib import Path

def fix_app_redirect():
    """Fix app.py to properly redirect to enhanced UI."""
    file_path = Path(__file__).parent / "web_interface" / "app.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Make a backup
    backup_path = str(file_path) + ".redirect_bak"
    with open(backup_path, 'w') as f:
        f.writelines(lines)
    print(f"Created backup at {backup_path}")
    
    # Check for Flask import
    has_redirect_import = False
    for line in lines:
        if "from flask import" in line and "redirect" in line:
            has_redirect_import = True
            break
    
    if not has_redirect_import:
        # Update Flask import to include redirect
        for i, line in enumerate(lines):
            if "from flask import" in line and "redirect" not in line:
                if line.strip().endswith(")"):
                    # Import line already has a closing parenthesis
                    new_line = line.replace(")", ", redirect)")
                else:
                    # Add redirect to the import list
                    new_line = line.rstrip() + ", redirect\n"
                lines[i] = new_line
                print("Added redirect to Flask imports")
                break
    
    # Find the index route
    index_start = None
    index_end = None
    
    for i, line in enumerate(lines):
        if "@app.route('/', methods=['GET'])" in line:
            index_start = i
            # Find the end of the function (next route or end of file)
            for j in range(i + 1, len(lines)):
                if "@app.route" in lines[j] or j == len(lines) - 1:
                    index_end = j
                    break
    
    if index_start is not None and index_end is not None:
        # Create a new index route that redirects to enhanced UI
        new_index = [
            "@app.route('/', methods=['GET'])\n",
            "def index():\n",
            "    \"\"\"Redirect to enhanced UI if available, otherwise render the main page.\"\"\"\n",
            "    if 'enhanced' in app.blueprints:\n",
            "        return redirect('/enhanced')\n",
            "    return render_template('index.html', modes=clarifier.available_modes())\n",
            "\n"
        ]
        
        # Replace the old index route with the new one
        lines[index_start:index_end] = new_index
        print("Updated index route to redirect to enhanced UI")
        
        # Write the modified file
        with open(file_path, 'w') as f:
            f.writelines(lines)
        
        print(f"Successfully updated {file_path}")
        return True
    else:
        print("Could not find the index route")
        return False

def fix_base_html():
    """Fix base.html to add enhanced UI tab."""
    file_path = Path(__file__).parent / "web_interface" / "templates" / "base.html"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(file_path) + ".navbar_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Check if enhanced tab already exists
    if '<a class="nav-link {% if request.path == \'/enhanced\' %}active{% endif %}" href="/enhanced">' in content:
        print("Enhanced tab already exists in the navigation")
        return True
    
    # Find the chat tab and add enhanced tab after it
    chat_tab = '<a class="nav-link {% if request.path == \'/chat\' %}active{% endif %}" href="/chat">'
    if chat_tab in content:
        enhanced_tab = '''                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/enhanced' %}active{% endif %}" href="/enhanced">
                            <i class="bi bi-stars"></i> Enhanced
                        </a>
                    </li>'''
        
        # Insert after the chat nav-item closing tag
        parts = content.split('</a>\n                    </li>')
        if len(parts) >= 2:
            updated_content = parts[0] + '</a>\n                    </li>' + enhanced_tab + ''.join(parts[1:])
            
            # Write the modified content
            with open(file_path, 'w') as f:
                f.write(updated_content)
            
            print("Added Enhanced UI tab to navigation")
            return True
        else:
            print("Could not properly split the content to insert the Enhanced tab")
            return False
    else:
        print("Could not find the chat tab in the navigation")
        return False

def main():
    """Main entry point."""
    print("Running UI navigation fix...")
    
    app_fixed = fix_app_redirect()
    nav_fixed = fix_base_html()
    
    if app_fixed and nav_fixed:
        print("All fixes completed successfully!")
    elif app_fixed:
        print("App redirect fixed, but navigation tab fix failed.")
    elif nav_fixed:
        print("Navigation tab fixed, but app redirect fix failed.")
    else:
        print("Both fixes failed.")

if __name__ == "__main__":
    main()
