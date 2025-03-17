
"""
Multimodal Integration for AI-Socratic-Clarifier.

This module provides functionality for processing images, PDFs, and other files
with OCR and multimodal AI models.
"""

import os
import sys
import tempfile
import json
import base64
from typing import Dict, Any, Optional, List, Union, Tuple
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global state
MULTIMODAL_AVAILABLE = True
dependencies_checked = False
dependencies_installed = False

def check_dependencies() -> Dict[str, bool]:
    """
    Check if required dependencies are installed.
    
    Returns:
        Dict with status of each dependency
    """
    global dependencies_checked, dependencies_installed
    
    # Don't check multiple times
    if dependencies_checked:
        return {
            "tesseract": dependencies_installed,
            "pytesseract": dependencies_installed,
            "pillow": dependencies_installed,
            "pdf2image": dependencies_installed,
            "numpy": dependencies_installed
        }
    
    dependencies_checked = True
    status = {}
    
    # Check for Tesseract binary
    try:
        import subprocess
        result = subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status["tesseract"] = result.returncode == 0
    except:
        status["tesseract"] = False
    
    # Check for Python packages
    for package in ["pytesseract", "PIL", "pdf2image", "numpy"]:
        try:
            if package == "PIL":
                import PIL
                status["pillow"] = True
            else:
                exec(f"import {package}")
                status[package] = True
        except:
            status[package] = False
    
    # All dependencies need to be available
    dependencies_installed = all(status.values())
    
    return status

def process_image(image_path: str) -> Dict[str, Any]:
    """
    Process an image with OCR or multimodal LLM.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dict with processing results
    """
    # Check if dependencies are installed
    deps_status = check_dependencies()
    if not deps_status.get("tesseract", False) or not deps_status.get("pytesseract", False):
        return {
            "success": False,
            "error": "Required dependencies (tesseract, pytesseract) not available"
        }
    
    try:
        # Import required packages
        import pytesseract
        from PIL import Image
        
        # Open the image
        image = Image.open(image_path)
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        return {
            "success": True,
            "text": text,
            "method": "tesseract-ocr"
        }
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def process_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Process a PDF document with OCR.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dict with processing results
    """
    # Check if dependencies are installed
    deps_status = check_dependencies()
    if not deps_status.get("tesseract", False) or not deps_status.get("pdf2image", False):
        return {
            "success": False,
            "error": "Required dependencies (tesseract, pdf2image) not available"
        }
    
    try:
        # Import required packages
        import pytesseract
        from PIL import Image
        from pdf2image import convert_from_path
        
        # Create temp directory for images
        temp_dir = tempfile.mkdtemp()
        
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        # Extract text from each page
        text = ""
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            text += f"--- Page {i+1} ---\n{page_text}\n\n"
        
        return {
            "success": True,
            "text": text,
            "page_count": len(images),
            "method": "pdf2image+tesseract"
        }
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def process_with_multimodal_llm(file_path: str) -> Dict[str, Any]:
    """
    Process a file with a multimodal LLM (e.g., LLaVA).
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dict with processing results
    """
    try:
        # Import required packages
        from PIL import Image
        import base64
        import io
        import requests
        import json
        
        # Load config
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.json'))
        
        if not os.path.exists(config_path):
            return {
                "success": False,
                "error": f"Config file not found at {config_path}"
            }
            
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Get multimodal model from config
        multimodal_model = config.get('integrations', {}).get('ollama', {}).get('multimodal_model', 'llava:latest')
        
        # Prepare the image
        try:
            # Open the image
            image = Image.open(file_path)
            
            # Convert to RGB if necessary (for PNG transparency)
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            
            # Resize if too large
            max_size = 1024
            if image.width > max_size or image.height > max_size:
                ratio = min(max_size / image.width, max_size / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error preparing image: {e}")
            return {
                "success": False,
                "error": f"Error preparing image: {str(e)}"
            }
        
        # Use Ollama API for multimodal processing
        try:
            # Prepare prompt
            prompt = "Analyze this image in detail. Describe what you see, including any text content, visuals, and key elements."
            
            # Make request to Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": multimodal_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3
                    },
                    "images": [img_str]
                }
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Ollama API error: {response.status_code} - {response.text}"
                }
            
            # Parse response
            result = response.json()
            
            return {
                "success": True,
                "content": result.get("response", ""),
                "model": multimodal_model,
                "method": "multimodal-llm"
            }
            
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return {
                "success": False,
                "error": f"Error calling Ollama API: {str(e)}"
            }
            
    except Exception as e:
        logger.error(f"Error processing with multimodal LLM: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def process_file(file_path: str, use_multimodal: bool = False) -> Dict[str, Any]:
    """
    Process a file with OCR or multimodal LLM.
    
    Args:
        file_path: Path to the file
        use_multimodal: Whether to use multimodal LLM if available
        
    Returns:
        Dict with processing results
    """
    # Get file type from extension
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # If using multimodal and the model is available, try that first
    if use_multimodal:
        try:
            # Check if Ollama is available and a multimodal model is configured
            import requests
            response = requests.get("http://localhost:11434/api/tags")
            
            if response.status_code == 200:
                # Load config
                config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.json'))
                
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Get multimodal model from config
                    multimodal_model = config.get('integrations', {}).get('ollama', {}).get('multimodal_model', 'llava:latest')
                    
                    # Check if the model is available
                    models = response.json().get('models', [])
                    model_names = [m.get('name') for m in models]
                    
                    if multimodal_model in model_names:
                        # Process with multimodal LLM
                        result = process_with_multimodal_llm(file_path)
                        if result.get('success', False):
                            return result
        except Exception as e:
            logger.warning(f"Error checking multimodal availability: {e}")
    
    # If not using multimodal or it failed, fall back to OCR
    if file_ext in ['.pdf']:
        return process_pdf(file_path)
    elif file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif']:
        return process_image(file_path)
    else:
        return {
            "success": False,
            "error": f"Unsupported file type: {file_ext}"
        }

# Check dependencies on import
check_dependencies()
