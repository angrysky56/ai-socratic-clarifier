#!/usr/bin/env python3
"""
Fix for duplicate UI tabs and navigation issues.
"""
import os
from pathlib import Path

def fix_base_html():
    """Fix the base.html template to properly close tags and structure navigation."""
    file_path = Path(__file__).parent / "web_interface" / "templates" / "base.html"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Create a fresh version of the HTML
    new_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AI-Socratic-Clarifier{% endblock %}</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    
    <!-- Page-specific CSS -->
    {% block additional_css %}{% endblock %}
</head>
<body>
    <!-- Main Navigation -->
    <nav class="navbar navbar-expand-lg navbar-custom navbar-light sticky-top">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="bi bi-lightbulb-fill text-warning"></i>
                AI-Socratic-Clarifier
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
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
                </ul>
                <!-- Status Indicators -->
                <div class="d-flex align-items-center">
                    <span class="badge bg-success me-2" id="modelStatus">
                        <i class="bi bi-cpu"></i> Model Ready
                    </span>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" id="modeDropdown" data-bs-toggle="dropdown">
                            <i class="bi bi-sliders"></i> Mode
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="modeDropdown">
                            <li><button class="dropdown-item mode-select" data-mode="standard">Standard</button></li>
                            <li><button class="dropdown-item mode-select" data-mode="deep">Deep Inquiry</button></li>
                            <li><button class="dropdown-item mode-select" data-mode="reflective">Reflective Ecosystem</button></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><button class="dropdown-item" id="debugModeToggle">Debug Mode</button></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="main-content">
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p class="mb-0">&copy; 2025 AI-Socratic-Clarifier | <a href="https://github.com/angrysky56/ai-socratic-clarifier" target="_blank">GitHub</a></p>
                </div>
                <div class="col-md-6 text-md-end">
                    <div class="small text-muted">
                        <span id="currentModel">Model: llama3</span> | 
                        <span id="currentMode">Mode: standard</span> |
                        <span id="systemStatus">Ready</span>
                    </div>
                </div>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Common JavaScript -->
    <script src="{{ url_for('static', filename='js/common.js') }}"></script>
    
    <!-- Page-specific JavaScript -->
    {% block additional_js %}{% endblock %}
</body>
</html>
"""
    
    # Make a backup
    backup_path = str(file_path) + ".dupe_fix_bak"
    with open(backup_path, 'w') as f:
        with open(file_path, 'r') as src:
            f.write(src.read())
    print(f"Created backup at {backup_path}")
    
    # Write the new HTML
    with open(file_path, 'w') as f:
        f.write(new_html)
    
    print("Replaced base.html with clean version")
    return True

def update_app_route_priorities():
    """Update app.py to ensure proper route priorities."""
    file_path = Path(__file__).parent / "web_interface" / "app.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(file_path) + ".route_fix_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Remove the chat route to avoid duplicates with enhanced
    chat_route_start = content.find("@app.route('/chat', methods=['GET'])")
    
    if chat_route_start != -1:
        # Find the end of the function
        next_route = content.find("@app.route", chat_route_start + 1)
        
        if next_route != -1:
            # Remove the chat route
            content = content[:chat_route_start] + content[next_route:]
            print("Removed duplicate chat route from app.py")
        else:
            print("Could not find end of chat route function")
    else:
        print("Chat route not found in app.py")
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Updated app.py route priorities")
    return True

def main():
    """Main function."""
    print("Fixing duplicate UI issues...")
    
    # Fix base.html
    fix_base_html()
    
    # Update app.py route priorities
    update_app_route_priorities()
    
    print("Done!")

if __name__ == "__main__":
    main()
