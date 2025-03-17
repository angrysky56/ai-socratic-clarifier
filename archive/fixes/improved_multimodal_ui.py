#!/usr/bin/env python3
"""
Improves the multimodal UI with better controls and fixed reflective analysis integration.

This script:
1. Creates the improved templates directory if it doesn't exist
2. Copies the improved UI template to the templates directory
3. Creates route files for the improved UI
4. Ensures all required files for the improved UI are in place
"""

import os
import sys
import shutil

def create_improved_template():
    """Create the improved multimodal template with numeric input instead of slider."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_interface_dir = os.path.join(base_dir, "web_interface")
    templates_dir = os.path.join(web_interface_dir, "templates")
    
    # Create the templates directory if it doesn't exist
    os.makedirs(templates_dir, exist_ok=True)
    
    improved_template_path = os.path.join(templates_dir, "multimodal_improved.html")
    
    # Create a simplified version of the improved template
    with open(improved_template_path, "w") as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Socratic-Clarifier - Improved Multimodal Analysis</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background-color: #1e1e1e;
            color: #e0e0e0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }
        .navbar, .sidebar {
            background-color: #252525;
            border-bottom: 1px solid #3d3d3d;
        }
        .sidebar {
            border-right: 1px solid #3d3d3d;
            height: calc(100vh - 56px);
            width: 250px;
            position: fixed;
            top: 56px;
            left: 0;
            overflow-y: auto;
        }
        .content {
            margin-left: 250px;
            padding: 20px;
        }
        .card {
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
            margin-bottom: 20px;
        }
        .card-header {
            background-color: #363636;
            border-bottom: 1px solid #3d3d3d;
            color: #ffffff;
        }
        .max-questions-control {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        .max-questions-control input[type="number"] {
            width: 60px;
            text-align: center;
            margin: 0 10px;
            padding: 6px;
            background-color: #333;
            color: #e0e0e0;
            border: 1px solid #444;
            border-radius: 4px;
        }
        .max-questions-control button {
            height: 32px;
            width: 32px;
            padding: 0;
            line-height: 1;
            background-color: #444;
            color: #e0e0e0;
            border: none;
            border-radius: 4px;
        }
        .upload-area {
            border: 2px dashed #444;
            border-radius: 5px;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            background-color: #2a2a2a;
            transition: all 0.3s;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">AI-Socratic-Clarifier</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/chat">Chat</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/reflection">Reflection</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/multimodal">Original Multimodal</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/improved_multimodal">Improved Multimodal</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/settings">Settings</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="content">
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <h3>Improved Multimodal Analysis</h3>
                    <p>This version includes improved controls and functionality.</p>
                </div>
            </div>

            <div class="row">
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Upload Document</h5>
                        </div>
                        <div class="card-body">
                            <label for="fileInput" class="upload-area" id="uploadArea">
                                <i class="fas fa-cloud-upload-alt fa-3x mb-3"></i>
                                <h5>Drag & Drop Files Here</h5>
                                <p>Or click to browse files</p>
                                <small class="text-muted">Supported formats: JPG, PNG, PDF, BMP, TIFF</small>
                            </label>
                            <input type="file" id="fileInput" accept=".jpg,.jpeg,.png,.pdf,.bmp,.tiff,.tif" style="display: none;">

                            <div class="mt-3">
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="analysisMode" id="ocrMode" value="ocr" checked>
                                    <label class="form-check-label" for="ocrMode">OCR Only</label>
                                </div>
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="analysisMode" id="multimodalMode" value="multimodal">
                                    <label class="form-check-label" for="multimodalMode">Multimodal Analysis</label>
                                </div>
                                <div class="form-check form-check-inline">
                                    <input class="form-check-input" type="radio" name="analysisMode" id="socraticMode" value="socratic">
                                    <label class="form-check-label" for="socraticMode">Socratic Analysis</label>
                                </div>
                            </div>
                            
                            <!-- Improved Socratic Options -->
                            <div class="mt-3 p-3 bg-dark border border-secondary rounded" id="socraticOptions" style="display:none;">
                                <h6 class="mb-3">Socratic Analysis Options</h6>
                                
                                <div class="mb-3">
                                    <label for="maxQuestionsInput" class="form-label">Maximum Questions:</label>
                                    <div class="max-questions-control">
                                        <button type="button" id="decreaseQuestions" class="btn">
                                            <i class="fas fa-minus"></i>
                                        </button>
                                        <input type="number" id="maxQuestionsInput" min="1" max="10" value="5" class="form-control">
                                        <button type="button" id="increaseQuestions" class="btn">
                                            <i class="fas fa-plus"></i>
                                        </button>
                                    </div>
                                </div>
                                
                                <div class="form-check mt-2">
                                    <input class="form-check-input" type="checkbox" id="useSreCheckbox" checked>
                                    <label class="form-check-label" for="useSreCheckbox">
                                        Use Socratic Reasoning Engine for improved questions
                                    </label>
                                </div>
                            </div>

                            <div class="mt-3">
                                <button class="btn btn-primary w-100" id="processButton" disabled>
                                    <i class="fas fa-cogs me-2"></i>Process Document
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Results</h5>
                        </div>
                        <div class="card-body">
                            <p>Select a file and processing mode to get started.</p>
                            <div class="d-flex justify-content-end mt-3">
                                <button class="btn btn-info" id="analyzeTextButton" disabled>
                                    <i class="fas fa-brain me-1"></i>Analyze in Reflective Ecosystem
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Setup for max questions input with +/- buttons
            const maxQuestionsInput = document.getElementById('maxQuestionsInput');
            const decreaseQuestions = document.getElementById('decreaseQuestions');
            const increaseQuestions = document.getElementById('increaseQuestions');
            
            if (decreaseQuestions && maxQuestionsInput && increaseQuestions) {
                decreaseQuestions.addEventListener('click', function() {
                    const currentValue = parseInt(maxQuestionsInput.value) || 5;
                    if (currentValue > 1) {
                        maxQuestionsInput.value = currentValue - 1;
                    }
                });
                
                increaseQuestions.addEventListener('click', function() {
                    const currentValue = parseInt(maxQuestionsInput.value) || 5;
                    if (currentValue < 10) {
                        maxQuestionsInput.value = currentValue + 1;
                    }
                });
                
                maxQuestionsInput.addEventListener('change', function() {
                    let value = parseInt(this.value) || 5;
                    if (value < 1) value = 1;
                    if (value > 10) value = 10;
                    this.value = value;
                });
            }
            
            // Toggle socratic options based on selected mode
            document.querySelectorAll('input[name="analysisMode"]').forEach(radio => {
                radio.addEventListener('change', function() {
                    const socraticOptions = document.getElementById('socraticOptions');
                    if (this.value === 'socratic') {
                        socraticOptions.style.display = 'block';
                    } else {
                        socraticOptions.style.display = 'none';
                    }
                });
            });
            
            // Handle file upload
            const fileInput = document.getElementById('fileInput');
            const uploadArea = document.getElementById('uploadArea');
            const processButton = document.getElementById('processButton');
            
            uploadArea.addEventListener('click', function() {
                fileInput.click();
            });
            
            fileInput.addEventListener('change', function() {
                if (fileInput.files.length > 0) {
                    processButton.disabled = false;
                    uploadArea.innerHTML = `<i class="fas fa-file fa-3x mb-3"></i><h5>${fileInput.files[0].name}</h5>`;
                }
            });
            
            // Reflective analysis button - opens in new tab
            document.getElementById('analyzeTextButton')?.addEventListener('click', function() {
                window.open('/reflection_improved', '_blank');
            });
        });
    </script>
</body>
</html>''')
    
    print(f"Created simplified improved template: {improved_template_path}")
    
    # Create a route file to use the improved template
    routes_path = os.path.join(web_interface_dir, "fixed_routes_multimodal.py")
    with open(routes_path, "w") as f:
        f.write('''"""
Fixed routes for multimodal analysis with improved UI.
"""

import os
import sys
from flask import Blueprint, render_template

# Create a blueprint
improved_multimodal_bp = Blueprint('improved_multimodal', __name__)

@improved_multimodal_bp.route('/improved_multimodal', methods=['GET'])
def improved_multimodal_page():
    """Render the improved multimodal analysis page."""
    return render_template('multimodal_improved.html')
''')
    
    print(f"Created fixed routes file: {routes_path}")

def main():
    """Main function to improve the multimodal UI."""
    try:
        create_improved_template()
        print("\nImproved multimodal UI setup successfully!")
        print("\nTo access the improved UI, go to: /improved_multimodal")
        return 0
    except Exception as e:
        print(f"Error setting up improved UI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
