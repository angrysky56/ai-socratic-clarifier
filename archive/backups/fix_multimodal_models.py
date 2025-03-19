#!/usr/bin/env python3
"""
Fix Multimodal Models Support for AI-Socratic-Clarifier

This script adds support for multiple multimodal models including:
- Gemma3 models with multimodal capabilities 
- Better model selection in the UI
- Fallback options if a specific model isn't available
"""

import os
import sys
import json
import shutil
import requests
from pathlib import Path

def backup_file(file_path):
    """Create a backup of a file."""
    backup_path = f"{file_path}.mm_models_bak"
    if os.path.exists(file_path):
        print(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
    return backup_path

def update_config_multimodal_models():
    """Update config.json to include all multimodal models."""
    config_path = os.path.join('config.json')
    
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found")
        return False
    
    backup_file(config_path)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Add multimodal models section to config
        if "integrations" not in config:
            config["integrations"] = {}
        
        if "ollama" not in config["integrations"]:
            config["integrations"]["ollama"] = {}
        
        # Try to detect available multimodal models from Ollama
        multimodal_models = []
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                
                # Look for models with multimodal capabilities
                for model in models:
                    name = model.get("name", "")
                    if any(mm in name.lower() for mm in ["llava", "vision", "multi", "bakllava", "gemma3", "phi4"]):
                        multimodal_models.append(name)
                
                if not multimodal_models:
                    multimodal_models = ["llava:latest", "gemma3:latest"]
            else:
                multimodal_models = ["llava:latest", "gemma3:latest"]
        except:
            # Fallback options
            multimodal_models = ["llava:latest", "gemma3:latest"]
        
        # Add all available multimodal models to config
        config["integrations"]["ollama"]["multimodal_models"] = multimodal_models
        
        # Set default model (prefer Gemma3 if available)
        default_mm_model = "llava:latest"
        for model in multimodal_models:
            if "gemma3" in model.lower():
                default_mm_model = model
                break
            
        config["integrations"]["ollama"]["multimodal_model"] = default_mm_model
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"✅ Updated config.json with multimodal models: {', '.join(multimodal_models)}")
        print(f"   Default multimodal model set to: {default_mm_model}")
        return True
    except Exception as e:
        print(f"Error updating config: {e}")
        return False

def update_multimodal_template():
    """Update multimodal.html template to add model selection."""
    template_path = os.path.join('web_interface', 'templates', 'multimodal.html')
    
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found")
        return False
    
    backup_file(template_path)
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check if model selection already exists
        if 'id="multimodal-model-select"' in content:
            print("Model selection already exists in template")
            return True
        
        # Add model selection dropdown
        if 'class="mode-toggle"' in content:
            # Find the analysis mode toggle section
            mode_toggle = content.find('class="mode-toggle"')
            end_of_section = content.find("</div>", mode_toggle)
            end_of_section = content.find("</div>", end_of_section + 1)
            
            if mode_toggle > 0 and end_of_section > 0:
                # Add model selection dropdown
                model_selection = """
                <div class="mb-3 mt-3">
                    <label for="multimodal-model-select" class="form-label">Multimodal Model:</label>
                    <select id="multimodal-model-select" class="form-select">
                        <!-- Options will be populated by JavaScript -->
                    </select>
                </div>
"""
                # Insert after mode toggle
                new_content = content[:end_of_section + 6] + model_selection + content[end_of_section + 6:]
                
                # Add JavaScript to populate model selection
                script_section = """
<script>
    // Populate multimodal model selection dropdown
    function populateMultimodalModels() {
        fetch('/api/settings')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const modelSelect = document.getElementById('multimodal-model-select');
                    if (modelSelect) {
                        // Clear existing options
                        modelSelect.innerHTML = '';
                        
                        // Get multimodal models
                        const multimodalModels = data.settings?.integrations?.ollama?.multimodal_models || [];
                        const defaultModel = data.settings?.integrations?.ollama?.multimodal_model || 'llava:latest';
                        
                        // Add options
                        multimodalModels.forEach(model => {
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            option.selected = (model === defaultModel);
                            modelSelect.appendChild(option);
                        });
                        
                        // Add llava:latest as fallback if not in the list
                        if (multimodalModels.length === 0) {
                            const option = document.createElement('option');
                            option.value = 'llava:latest';
                            option.text = 'llava:latest';
                            option.selected = true;
                            modelSelect.appendChild(option);
                            
                            // Also add gemma3:latest
                            const gemmaOption = document.createElement('option');
                            gemmaOption.value = 'gemma3:latest';
                            gemmaOption.text = 'gemma3:latest';
                            modelSelect.appendChild(gemmaOption);
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error loading multimodal models:', error);
                // Add fallback option
                const modelSelect = document.getElementById('multimodal-model-select');
                if (modelSelect) {
                    modelSelect.innerHTML = '';
                    
                    const defaultOption = document.createElement('option');
                    defaultOption.value = 'llava:latest';
                    defaultOption.text = 'llava:latest';
                    defaultOption.selected = true;
                    modelSelect.appendChild(defaultOption);
                    
                    const gemmaOption = document.createElement('option');
                    gemmaOption.value = 'gemma3:latest';
                    gemmaOption.text = 'gemma3:latest';
                    modelSelect.appendChild(gemmaOption);
                }
            });
    }
    
    // Call on page load
    document.addEventListener('DOMContentLoaded', function() {
        populateMultimodalModels();
    });
</script>
"""
                
                # Add script to the end of the file (before closing body tag)
                body_end = new_content.rfind("</body>")
                if body_end > 0:
                    new_content = new_content[:body_end] + script_section + new_content[body_end:]
                
                # Modify the FormData in the processFile function to include the selected model
                process_function = new_content.find("function processFile")
                if process_function > 0:
                    form_data_section = new_content.find("const formData = new FormData()", process_function)
                    form_data_end = new_content.find("// Send to server", form_data_section)
                    
                    if form_data_section > 0 and form_data_end > 0:
                        # Get the current formData section
                        current_form_data = new_content[form_data_section:form_data_end]
                        
                        # Add model selection to formData
                        updated_form_data = current_form_data
                        if "formData.append('model'" not in updated_form_data:
                            # Add after mode
                            mode_append = updated_form_data.find("formData.append('mode'")
                            if mode_append > 0:
                                end_of_line = updated_form_data.find("\n", mode_append)
                                if end_of_line > 0:
                                    updated_form_data = (
                                        updated_form_data[:end_of_line + 1] + 
                                        "                const selectedModel = document.getElementById('multimodal-model-select').value;\n" +
                                        "                formData.append('model', selectedModel);\n" + 
                                        updated_form_data[end_of_line + 1:]
                                    )
                        
                        # Replace the form data section
                        new_content = new_content[:form_data_section] + updated_form_data + new_content[form_data_end:]
                
                # Write updated template
                with open(template_path, 'w') as f:
                    f.write(new_content)
                
                print("✅ Added multimodal model selection to template")
                return True
            else:
                print("Could not find mode toggle section in template")
                return False
        else:
            print("Could not find mode toggle section in template")
            return False
            
    except Exception as e:
        print(f"Error updating multimodal template: {e}")
        return False

def update_routes_multimodal():
    """Update routes_multimodal.py to support model selection."""
    routes_path = os.path.join('web_interface', 'routes_multimodal.py')
    
    if not os.path.exists(routes_path):
        print(f"Error: {routes_path} not found")
        return False
    
    backup_file(routes_path)
    
    try:
        with open(routes_path, 'r') as f:
            content = f.read()
        
        # Check if model selection already supported
        if "model = request.form.get('model'" in content:
            print("Model selection already supported in routes")
            return True
        
        # Update the process_document function
        process_function = content.find("def process_document()")
        if process_function > 0:
            # Find where to add the model parameter
            file_path_line = content.find("file_path = os.path.join", process_function)
            
            if file_path_line > 0:
                # Add before this line
                model_code = "    # Get multimodal model if specified\n    model = request.form.get('model')\n\n"
                new_content = content[:file_path_line] + model_code + content[file_path_line:]
                
                # Find multimodal analysis section
                multimodal_section = new_content.find("if mode == 'multimodal':", process_function)
                if multimodal_section > 0:
                    # Find the process_file call
                    process_call = new_content.find("result = process_file", multimodal_section)
                    
                    if process_call > 0:
                        # Find the end of the line
                        end_of_line = new_content.find(")", process_call)
                        
                        if end_of_line > 0:
                            # Add model parameter to process_file call
                            current_call = new_content[process_call:end_of_line + 1]
                            
                            # Check if it already includes model
                            if "model" not in current_call:
                                # Add model parameter
                                updated_call = current_call.replace(")", ", model=model)")
                                
                                # Replace the call
                                new_content = new_content[:process_call] + updated_call + new_content[end_of_line + 1:]
                                
                                # Write updated content
                                with open(routes_path, 'w') as f:
                                    f.write(new_content)
                                
                                print("✅ Updated routes_multimodal.py to support model selection")
                                return True
                            else:
                                print("Model parameter already included in process_file call")
                                return True
                        else:
                            print("Could not find end of process_file call")
                            return False
                    else:
                        print("Could not find process_file call in multimodal section")
                        return False
                else:
                    print("Could not find multimodal section")
                    return False
            else:
                print("Could not find file_path line in process_document function")
                return False
        else:
            print("Could not find process_document function")
            return False
            
    except Exception as e:
        print(f"Error updating routes_multimodal.py: {e}")
        return False

def update_multimodal_integration():
    """Update multimodal_integration.py to support model selection."""
    integration_path = os.path.join('socratic_clarifier', 'multimodal_integration.py')
    
    if not os.path.exists(integration_path):
        print(f"Error: {integration_path} not found")
        return False
    
    backup_file(integration_path)
    
    try:
        with open(integration_path, 'r') as f:
            content = f.read()
        
        # Check if model parameter already supported
        if "def process_file(file_path: str, use_multimodal: bool = True, model: str = None)" in content:
            print("Model parameter already supported in process_file function")
            return True
        
        # Update the process_file function
        process_function = content.find("def process_file(file_path: str, use_multimodal: bool = True)")
        if process_function > 0:
            # Update the function signature
            updated_signature = "def process_file(file_path: str, use_multimodal: bool = True, model: str = None)"
            new_content = content[:process_function] + updated_signature + content[process_function + len("def process_file(file_path: str, use_multimodal: bool = True)"):]
            
            # Find analyze_image_with_multimodal call
            analyze_call = new_content.find("return analyze_image_with_multimodal(file_path)")
            if analyze_call > 0:
                # Update to pass model parameter
                updated_call = "return analyze_image_with_multimodal(file_path, model=model)"
                
                # Get the line end
                line_end = new_content.find("\n", analyze_call)
                
                if line_end > 0:
                    # Replace the call
                    new_content = new_content[:analyze_call] + updated_call + new_content[line_end:]
                    
                    # Now find second call to analyze_image_with_multimodal in the PDF section
                    second_call = new_content.find("result = analyze_image_with_multimodal(temp_path)")
                    
                    if second_call > 0:
                        # Update second call
                        updated_second_call = "result = analyze_image_with_multimodal(temp_path, model=model)"
                        
                        # Get the line end
                        second_line_end = new_content.find("\n", second_call)
                        
                        if second_line_end > 0:
                            # Replace the call
                            new_content = new_content[:second_call] + updated_second_call + new_content[second_line_end:]
                        
                    # Now update analyze_image_with_multimodal function
                    analyze_function = new_content.find("def analyze_image_with_multimodal(image_path: str, prompt: Optional[str] = None)")
                    
                    if analyze_function > 0:
                        # Update function signature
                        updated_analyze_sig = "def analyze_image_with_multimodal(image_path: str, prompt: Optional[str] = None, model: Optional[str] = None)"
                        new_content = new_content[:analyze_function] + updated_analyze_sig + new_content[analyze_function + len("def analyze_image_with_multimodal(image_path: str, prompt: Optional[str] = None)"):]
                        
                        # Find multimodal_model assignment
                        model_assignment = new_content.find("multimodal_model = config.get", analyze_function)
                        
                        if model_assignment > 0:
                            # Find the end of line
                            assignment_end = new_content.find("\n", model_assignment)
                            
                            if assignment_end > 0:
                                # Update to use passed model if provided
                                updated_assignment = """    # Use provided model if specified, otherwise get from config
    if model:
        multimodal_model = model
    else:
        multimodal_model = config.get("integrations", {}).get("ollama", {}).get("multimodal_model", "llava:latest")"""
                                
                                # Replace assignment
                                new_content = new_content[:model_assignment] + updated_assignment + new_content[assignment_end + 1:]
                                
                                # Write updated content
                                with open(integration_path, 'w') as f:
                                    f.write(new_content)
                                
                                print("✅ Updated multimodal_integration.py to support model selection")
                                return True
                            else:
                                print("Could not find end of model assignment")
                                return False
                        else:
                            print("Could not find multimodal_model assignment")
                            return False
                    else:
                        print("Could not find analyze_image_with_multimodal function")
                        return False
                else:
                    print("Could not find end of analyze_image_with_multimodal call")
                    return False
            else:
                print("Could not find analyze_image_with_multimodal call")
                return False
        else:
            print("Could not find process_file function")
            return False
            
    except Exception as e:
        print(f"Error updating multimodal_integration.py: {e}")
        return False

def update_api_settings():
    """Update api_settings.py to include multimodal models in settings response."""
    settings_path = os.path.join('web_interface', 'api_settings.py')
    
    if not os.path.exists(settings_path):
        print(f"Error: {settings_path} not found")
        return False
    
    backup_file(settings_path)
    
    try:
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Check if multimodal_models already included
        if "'multimodal_models': ollama_config.get('multimodal_models'," in content:
            print("Multimodal models already included in settings response")
            return True
        
        # Find where to add multimodal_models in API response
        settings_route = content.find("@settings_bp.route('/api/settings'")
        
        if settings_route > 0:
            # Find the settings response construction
            multimodal_model_line = content.find("'multimodal_model': ollama_config.get('multimodal_model'", settings_route)
            
            if multimodal_model_line > 0:
                # Find the end of line
                line_end = content.find(",", multimodal_model_line)
                
                if line_end > 0:
                    # Add multimodal_models after multimodal_model
                    updated_line = content[multimodal_model_line:line_end + 1] + "\n                'multimodal_models': ollama_config.get('multimodal_models', []),"
                    
                    # Replace the line
                    new_content = content[:multimodal_model_line] + updated_line + content[line_end + 1:]
                    
                    # Write updated content
                    with open(settings_path, 'w') as f:
                        f.write(new_content)
                    
                    print("✅ Updated api_settings.py to include multimodal models in settings response")
                    return True
                else:
                    print("Could not find end of multimodal_model line")
                    return False
            else:
                print("Could not find multimodal_model in settings response")
                return False
        else:
            print("Could not find settings route")
            return False
            
    except Exception as e:
        print(f"Error updating api_settings.py: {e}")
        return False

def update_socratic_ui_template():
    """Update socratic_ui.html to include multimodal model selection."""
    template_path = os.path.join('web_interface', 'templates', 'socratic_ui.html')
    
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found")
        return False
    
    backup_file(template_path)
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check if multimodal model selection already exists
        if 'id="multimodal-model-select"' in content:
            print("Multimodal model selection already exists in socratic_ui.html")
            return True
        
        # Find multimodal panel
        multimodal_panel = content.find('<div class="panel" id="multimodal-panel">')
        
        if multimodal_panel > 0:
            # Find the analysis mode section
            mode_toggle = content.find('class="mode-toggle', multimodal_panel)
            
            if mode_toggle > 0:
                # Find the end of the section
                section_end = content.find("</div>", mode_toggle)
                section_end = content.find("</div>", section_end + 1)
                
                if section_end > 0:
                    # Add model selection dropdown
                    model_selection = """
                                <div class="mb-3 mt-3">
                                    <label for="multimodal-model-select" class="form-label">Multimodal Model:</label>
                                    <select id="multimodal-model-select" class="form-select">
                                        <!-- Options will be populated by JavaScript -->
                                    </select>
                                </div>
"""
                    # Insert after mode toggle
                    new_content = content[:section_end + 6] + model_selection + content[section_end + 6:]
                    
                    # Add JavaScript to populate the dropdown
                    # First check if we already have a function for this
                    if "function populateMultimodalModels" not in new_content:
                        # Find a good place to add the function
                        script_section = new_content.find("<script>", 0)
                        
                        if script_section > 0:
                            # Find window.onload or DOMContentLoaded
                            dom_ready = new_content.find("document.addEventListener('DOMContentLoaded'", script_section)
                            
                            if dom_ready > 0:
                                # Find the function for setup
                                setup_function = new_content.find("setupMultimodal();", dom_ready)
                                
                                if setup_function > 0:
                                    # Add our function call
                                    updated_init = "            populateMultimodalModels();\n            setupMultimodal();"
                                    
                                    # Replace the call
                                    new_content = new_content[:setup_function] + updated_init + new_content[setup_function + len("setupMultimodal();"):]
                                    
                                    # Add our function
                                    multimodal_function = """
        // Populate multimodal model selection dropdown
        function populateMultimodalModels() {
            fetch('/api/settings')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const modelSelect = document.getElementById('multimodal-model-select');
                        if (modelSelect) {
                            // Clear existing options
                            modelSelect.innerHTML = '';
                            
                            // Get multimodal models
                            const multimodalModels = data.settings?.integrations?.ollama?.multimodal_models || [];
                            const defaultModel = data.settings?.integrations?.ollama?.multimodal_model || 'llava:latest';
                            
                            // Add options
                            multimodalModels.forEach(model => {
                                const option = document.createElement('option');
                                option.value = model;
                                option.text = model;
                                option.selected = (model === defaultModel);
                                modelSelect.appendChild(option);
                            });
                            
                            // Add llava:latest as fallback if not in the list
                            if (multimodalModels.length === 0) {
                                const option = document.createElement('option');
                                option.value = 'llava:latest';
                                option.text = 'llava:latest';
                                option.selected = true;
                                modelSelect.appendChild(option);
                                
                                // Also add gemma3:latest
                                const gemmaOption = document.createElement('option');
                                gemmaOption.value = 'gemma3:latest';
                                gemmaOption.text = 'gemma3:latest';
                                modelSelect.appendChild(gemmaOption);
                            }
                        }
                    }
                })
                .catch(error => {
                    console.error('Error loading multimodal models:', error);
                    // Add fallback option
                    const modelSelect = document.getElementById('multimodal-model-select');
                    if (modelSelect) {
                        modelSelect.innerHTML = '';
                        
                        const defaultOption = document.createElement('option');
                        defaultOption.value = 'llava:latest';
                        defaultOption.text = 'llava:latest';
                        defaultOption.selected = true;
                        modelSelect.appendChild(defaultOption);
                        
                        const gemmaOption = document.createElement('option');
                        gemmaOption.value = 'gemma3:latest';
                        gemmaOption.text = 'gemma3:latest';
                        modelSelect.appendChild(gemmaOption);
                    }
                });
        }
"""
                                    
                                    # Find a good place to add it - before setupMultimodal function
                                    setup_multimodal_func = new_content.find("function setupMultimodal()", dom_ready)
                                    
                                    if setup_multimodal_func > 0:
                                        # Add our function
                                        new_content = new_content[:setup_multimodal_func] + multimodal_function + new_content[setup_multimodal_func:]
                                        
                                        # Now update the processMultimodalFile function to include the selected model
                                        process_func = new_content.find("function processMultimodalFile()")
                                        
                                        if process_func > 0:
                                            # Find form data creation
                                            form_data = new_content.find("const formData = new FormData();", process_func)
                                            
                                            if form_data > 0:
                                                # Find where to add model selection
                                                end_of_form_data = new_content.find("fetch(", form_data)
                                                
                                                if end_of_form_data > 0:
                                                    # Add model selection
                                                    model_selection_code = """                // Get selected model
                const selectedModel = document.getElementById('multimodal-model-select').value;
                formData.append('model', selectedModel);
                
"""
                                                    # Insert before fetch
                                                    new_content = new_content[:end_of_form_data] + model_selection_code + new_content[end_of_form_data:]
                                                    
                                                    # Write updated content
                                                    with open(template_path, 'w') as f:
                                                        f.write(new_content)
                                                    
                                                    print("✅ Updated socratic_ui.html to include multimodal model selection")
                                                    return True
                                                else:
                                                    print("Could not find end of form data section")
                                                    return False
                                            else:
                                                print("Could not find form data creation")
                                                return False
                                        else:
                                            print("Could not find processMultimodalFile function")
                                            return False
                                    else:
                                        print("Could not find setupMultimodal function")
                                        return False
                                else:
                                    print("Could not find setupMultimodal call")
                                    return False
                            else:
                                print("Could not find document.addEventListener('DOMContentLoaded'")
                                return False
                        else:
                            print("Could not find script section")
                            return False
                    else:
                        print("populateMultimodalModels function already exists")
                else:
                    print("Could not find end of mode toggle section")
                    return False
            else:
                print("Could not find mode toggle in multimodal panel")
                return False
        else:
            print("Could not find multimodal panel")
            return False
            
    except Exception as e:
        print(f"Error updating socratic_ui.html: {e}")
        return False

def main():
    """Main function to fix multimodal models support."""
    print("\n=== Adding Support for Multiple Multimodal Models ===\n")
    
    # Update config with multimodal models
    config_updated = update_config_multimodal_models()
    
    # Update multimodal integration to support model selection
    integration_updated = update_multimodal_integration()
    
    # Update routes to support model selection
    routes_updated = update_routes_multimodal()
    
    # Update API settings
    api_updated = update_api_settings()
    
    # Update templates
    template_updated = update_multimodal_template()
    socratic_updated = update_socratic_ui_template()
    
    # Print summary
    print("\n=== Fix Summary ===")
    print(f"✓ Config updated with multimodal models: {'Yes' if config_updated else 'No'}")
    print(f"✓ Multimodal integration updated: {'Yes' if integration_updated else 'No'}")
    print(f"✓ Routes updated: {'Yes' if routes_updated else 'No'}")
    print(f"✓ API settings updated: {'Yes' if api_updated else 'No'}")
    print(f"✓ Multimodal template updated: {'Yes' if template_updated else 'No'}")
    print(f"✓ Socratic UI template updated: {'Yes' if socratic_updated else 'No'}")
    
    print("\n=== Instructions ===")
    print("1. Restart the server with: ./start.py")
    print("2. Access the unified UI at: http://localhost:5000/socratic")
    print("3. Go to the Multimodal Analysis tab and select a different model from the dropdown")
    print("4. Available models should include Gemma3 and/or other multimodal models")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
