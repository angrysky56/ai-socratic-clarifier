"""
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
