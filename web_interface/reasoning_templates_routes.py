"""
Routes for managing reasoning templates in the AI-Socratic-Clarifier.
"""

import os
import json
import sys
from flask import Blueprint, request, jsonify, render_template, current_app
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the reasoning template manager
from socratic_clarifier.reasoning_template_manager import get_reasoning_template_manager

# Create blueprint
reasoning_templates_bp = Blueprint('reasoning_templates', __name__)

@reasoning_templates_bp.route('/api/reasoning_templates', methods=['GET'])
def list_templates():
    """Get a list of all available reasoning templates."""
    try:
        # Get the template manager
        template_manager = get_reasoning_template_manager()
        
        # Get template names
        template_names = template_manager.get_template_names()
        
        # Get active template
        active_template_name = template_manager.active_template_name
        
        # Get additional information about each template
        templates = []
        for name in template_names:
            template = template_manager.get_template(name)
            if template:
                templates.append({
                    "name": name,
                    "description": template.get("description", ""),
                    "version": template.get("version", ""),
                    "author": template.get("author", ""),
                    "active": name == active_template_name
                })
        
        return jsonify({
            "success": True,
            "templates": templates,
            "active_template": active_template_name
        })
    except Exception as e:
        logger.error(f"Error listing reasoning templates: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@reasoning_templates_bp.route('/api/reasoning_templates/<template_name>', methods=['GET'])
def get_template(template_name):
    """Get a specific reasoning template."""
    try:
        # Get the template manager
        template_manager = get_reasoning_template_manager()
        
        # Get the template
        template = template_manager.get_template(template_name)
        
        if not template:
            return jsonify({
                "success": False,
                "error": f"Template '{template_name}' not found"
            }), 404
        
        return jsonify({
            "success": True,
            "template": template
        })
    except Exception as e:
        logger.error(f"Error getting reasoning template: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@reasoning_templates_bp.route('/api/reasoning_templates', methods=['POST'])
def create_template():
    """Create a new reasoning template."""
    try:
        # Get request data
        data = request.get_json()
        
        if not data or "template" not in data:
            return jsonify({
                "success": False,
                "error": "No template data provided"
            }), 400
        
        template_data = data["template"]
        file_name = data.get("file_name")
        
        # Get the template manager
        template_manager = get_reasoning_template_manager()
        
        # Create the template
        success = template_manager.create_template(template_data, file_name)
        
        if not success:
            return jsonify({
                "success": False,
                "error": "Failed to create template"
            }), 500
        
        return jsonify({
            "success": True,
            "message": f"Created template '{template_data.get('name', 'unnamed')}'"
        })
    except Exception as e:
        logger.error(f"Error creating reasoning template: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@reasoning_templates_bp.route('/api/reasoning_templates/<template_name>', methods=['PUT'])
def update_template(template_name):
    """Update an existing reasoning template."""
    try:
        # Get request data
        data = request.get_json()
        
        if not data or "template" not in data:
            return jsonify({
                "success": False,
                "error": "No template data provided"
            }), 400
        
        template_data = data["template"]
        
        # Get the template manager
        template_manager = get_reasoning_template_manager()
        
        # Update the template
        success = template_manager.update_template(template_name, template_data)
        
        if not success:
            return jsonify({
                "success": False,
                "error": f"Failed to update template '{template_name}'"
            }), 500
        
        return jsonify({
            "success": True,
            "message": f"Updated template '{template_name}'"
        })
    except Exception as e:
        logger.error(f"Error updating reasoning template: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@reasoning_templates_bp.route('/api/reasoning_templates/<template_name>', methods=['DELETE'])
def delete_template(template_name):
    """Delete a reasoning template."""
    try:
        # Get the template manager
        template_manager = get_reasoning_template_manager()
        
        # Delete the template
        success = template_manager.delete_template(template_name)
        
        if not success:
            return jsonify({
                "success": False,
                "error": f"Failed to delete template '{template_name}'"
            }), 500
        
        return jsonify({
            "success": True,
            "message": f"Deleted template '{template_name}'"
        })
    except Exception as e:
        logger.error(f"Error deleting reasoning template: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@reasoning_templates_bp.route('/api/reasoning_templates/active', methods=['POST'])
def set_active_template():
    """Set the active reasoning template."""
    try:
        # Get request data
        data = request.get_json()
        
        if not data or "template_name" not in data:
            return jsonify({
                "success": False,
                "error": "No template name provided"
            }), 400
        
        template_name = data["template_name"]
        
        # Get the template manager
        template_manager = get_reasoning_template_manager()
        
        # Set the active template
        success = template_manager.set_active_template(template_name)
        
        if not success:
            return jsonify({
                "success": False,
                "error": f"Failed to set active template to '{template_name}'"
            }), 500
        
        return jsonify({
            "success": True,
            "message": f"Set active template to '{template_name}'"
        })
    except Exception as e:
        logger.error(f"Error setting active reasoning template: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@reasoning_templates_bp.route('/reasoning_templates', methods=['GET'])
def reasoning_templates_page():
    """Render the reasoning templates management page."""
    return render_template('reasoning_templates.html')
