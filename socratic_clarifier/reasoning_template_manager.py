"""
Reasoning Template Manager for AI-Socratic-Clarifier

This module manages the loading, selection, and application of reasoning templates
that define how Socratic questioning and analysis is performed.
"""

import os
import json
import glob
from typing import Dict, List, Any, Optional
from loguru import logger

class ReasoningTemplateManager:
    """
    Manages the loading and application of reasoning templates for Socratic questioning.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the reasoning template manager.
        
        Args:
            templates_dir: Directory containing reasoning template JSON files.
                          If None, defaults to 'reasoning_templates' in the project root.
        """
        if templates_dir is None:
            # Default to reasoning_templates in the project root
            self.templates_dir = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'reasoning_templates'))
        else:
            self.templates_dir = os.path.abspath(templates_dir)
        
        # Ensure the templates directory exists
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Track currently loaded templates
        self.templates = {}
        
        # Track currently active template
        self.active_template_name = None
        
        # Load available templates
        self.load_templates()
        
        logger.info(f"Reasoning Template Manager initialized with {len(self.templates)} templates")
    
    def load_templates(self) -> bool:
        """
        Load all template files from the templates directory.
        
        Returns:
            bool: True if templates were loaded successfully, False otherwise
        """
        try:
            # Find all JSON files in the templates directory
            template_files = glob.glob(os.path.join(self.templates_dir, "*.json"))
            
            if not template_files:
                logger.warning(f"No template files found in {self.templates_dir}")
                return False
            
            # Clear existing templates
            self.templates = {}
            
            # Load each template
            for template_file in template_files:
                try:
                    with open(template_file, 'r') as f:
                        template_data = json.load(f)
                    
                    # Check if template has required fields
                    if 'name' not in template_data or 'system_prompt' not in template_data:
                        logger.warning(f"Template file {template_file} missing required fields")
                        continue
                    
                    # Add to templates dict, keyed by name
                    self.templates[template_data['name']] = {
                        'data': template_data,
                        'file_path': template_file,
                        'file_name': os.path.basename(template_file)
                    }
                    
                    logger.info(f"Loaded template: {template_data['name']}")
                except Exception as e:
                    logger.error(f"Error loading template {template_file}: {e}")
            
            # Set default active template if none is set
            if not self.active_template_name and self.templates:
                self.active_template_name = next(iter(self.templates.keys()))
                logger.info(f"Set default active template: {self.active_template_name}")
            
            return True
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            return False
    
    def get_template_names(self) -> List[str]:
        """
        Get a list of available template names.
        
        Returns:
            List of template names
        """
        return list(self.templates.keys())
    
    def get_template(self, template_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a template by name.
        
        Args:
            template_name: Name of the template to get.
                          If None, returns the active template.
        
        Returns:
            Template data or None if not found
        """
        if template_name is None:
            template_name = self.active_template_name
        
        if template_name in self.templates:
            return self.templates[template_name]['data']
        
        return None
    
    def set_active_template(self, template_name: str) -> bool:
        """
        Set the active template.
        
        Args:
            template_name: Name of the template to set as active
        
        Returns:
            True if successful, False otherwise
        """
        if template_name in self.templates:
            self.active_template_name = template_name
            logger.info(f"Set active template to: {template_name}")
            return True
        
        logger.warning(f"Template '{template_name}' not found")
        return False
    
    def create_template(self, template_data: Dict[str, Any], file_name: Optional[str] = None) -> bool:
        """
        Create a new template.
        
        Args:
            template_data: Template data to save
            file_name: Optional file name. If None, uses sanitized template name.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check required fields
            if 'name' not in template_data or 'system_prompt' not in template_data:
                logger.error("Template data missing required fields 'name' and/or 'system_prompt'")
                return False
            
            # Create file name if not provided
            if file_name is None:
                # Sanitize template name for file name
                file_name = template_data['name'].lower().replace(' ', '_') + '.json'
            elif not file_name.endswith('.json'):
                file_name += '.json'
            
            # Check if template with this name already exists
            if template_data['name'] in self.templates:
                logger.warning(f"Template with name '{template_data['name']}' already exists")
                return False
            
            # Save template to file
            file_path = os.path.join(self.templates_dir, file_name)
            with open(file_path, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            # Add to templates dict
            self.templates[template_data['name']] = {
                'data': template_data,
                'file_path': file_path,
                'file_name': file_name
            }
            
            logger.info(f"Created new template: {template_data['name']}")
            return True
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return False
    
    def update_template(self, template_name: str, template_data: Dict[str, Any]) -> bool:
        """
        Update an existing template.
        
        Args:
            template_name: Name of the template to update
            template_data: New template data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if template_name not in self.templates:
                logger.warning(f"Template '{template_name}' not found")
                return False
            
            # Get existing file path
            file_path = self.templates[template_name]['file_path']
            
            # Save updated template to file
            with open(file_path, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            # Update templates dict
            self.templates[template_name]['data'] = template_data
            
            # If template name changed, update the dict key
            if template_data['name'] != template_name:
                self.templates[template_data['name']] = self.templates.pop(template_name)
                
                # Update active template if needed
                if self.active_template_name == template_name:
                    self.active_template_name = template_data['name']
            
            logger.info(f"Updated template: {template_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            return False
    
    def delete_template(self, template_name: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_name: Name of the template to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if template_name not in self.templates:
                logger.warning(f"Template '{template_name}' not found")
                return False
            
            # Get file path
            file_path = self.templates[template_name]['file_path']
            
            # Delete file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Remove from templates dict
            del self.templates[template_name]
            
            # Reset active template if needed
            if self.active_template_name == template_name:
                if self.templates:
                    self.active_template_name = next(iter(self.templates.keys()))
                else:
                    self.active_template_name = None
            
            logger.info(f"Deleted template: {template_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            return False
    
    def get_system_prompt(self, template_name: Optional[str] = None) -> str:
        """
        Get the system prompt from a template.
        
        Args:
            template_name: Name of the template to get the prompt from.
                         If None, uses the active template.
        
        Returns:
            System prompt string, or empty string if not found
        """
        template = self.get_template(template_name)
        if template and 'system_prompt' in template:
            return template['system_prompt']
        
        return ""
    
    def get_prompt_template(self, template_name: Optional[str] = None, 
                           prompt_key: str = "document_analysis") -> Optional[str]:
        """
        Get a specific prompt template from a template.
        
        Args:
            template_name: Name of the template to get the prompt from.
                         If None, uses the active template.
            prompt_key: Key of the specific prompt template to get
        
        Returns:
            Prompt template string, or None if not found
        """
        template = self.get_template(template_name)
        if not template:
            return None
        
        # Look for prompt in prompt_templates dict
        if 'prompt_templates' in template and prompt_key in template['prompt_templates']:
            return template['prompt_templates'][prompt_key]
        
        return None
    
    def fill_prompt_template(self, template_string: str, variables: Dict[str, str]) -> str:
        """
        Fill in a prompt template with variables.
        
        Args:
            template_string: Prompt template string with placeholders like {{VARIABLE}}
            variables: Dictionary of variable names and values
        
        Returns:
            Filled prompt template
        """
        result = template_string
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            result = result.replace(placeholder, var_value)
        
        return result

# Create a singleton instance
_template_manager = None

def get_reasoning_template_manager() -> ReasoningTemplateManager:
    """
    Get or create the singleton ReasoningTemplateManager instance.
    
    Returns:
        ReasoningTemplateManager instance
    """
    global _template_manager
    if _template_manager is None:
        _template_manager = ReasoningTemplateManager()
    return _template_manager
