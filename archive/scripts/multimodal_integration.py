#!/usr/bin/env python3
"""
Multimodal Integration Module for AI-Socratic-Clarifier.
Adds support for OCR from images and PDF files, with multimodal model analysis.
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path
import tempfile
import traceback
from typing import Dict, List, Any, Optional, Union

# Define default globals
TESSERACT_AVAILABLE = False
PDF_SUPPORT = False
CV2_AVAILABLE = False

# Optional imports - will be checked and installed if needed
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    Image = None
    TESSERACT_AVAILABLE = False

try:
    import pdf2image
    PDF_SUPPORT = True
except ImportError:
    pdf2image = None
    PDF_SUPPORT = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False


def load_config():
    """Load configuration from config.json."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Configuration file not found at {config_path}")
            return {}
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {}


def check_dependencies():
    global TESSERACT_AVAILABLE, PDF_SUPPORT, CV2_AVAILABLE
    global pytesseract, Image, pdf2image, cv2
    """Check and install required dependencies."""
    missing_deps = []
    
    if not TESSERACT_AVAILABLE:
        missing_deps.append("pytesseract Pillow")
    
    if not PDF_SUPPORT:
        missing_deps.append("pdf2image")
    
    if not CV2_AVAILABLE:
        missing_deps.append("opencv-python")
    
    # Install missing dependencies
    if missing_deps:
        print("Installing missing dependencies...")
        for dep in missing_deps:
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"Installed {dep}")
            except Exception as e:
                print(f"Failed to install {dep}: {e}")
                return False
        
        # Reload modules
        if "pytesseract" in ' '.join(missing_deps):
            try:
                global pytesseract, Image
                import pytesseract
                from PIL import Image
                TESSERACT_AVAILABLE = True
            except ImportError:
                pass
        
        if "pdf2image" in ' '.join(missing_deps):
            try:
                global pdf2image
                import pdf2image
                PDF_SUPPORT = True
            except ImportError:
                pass
        
        if "opencv-python" in ' '.join(missing_deps):
            try:
                global cv2
                import cv2
                CV2_AVAILABLE = True
            except ImportError:
                pass
    
    # Check if tesseract is installed on the system
    if TESSERACT_AVAILABLE:
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            print("Tesseract OCR is not installed on your system.")
            print("Please install it from: https://github.com/tesseract-ocr/tesseract")
            print("On Ubuntu: sudo apt-get install tesseract-ocr")
            print("On macOS: brew install tesseract")
            print("On Windows: download installer from https://github.com/UB-Mannheim/tesseract/wiki")
            return False
    
    return True


def perform_ocr(image_path: str) -> str:
    """
    Perform OCR on an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text
    """
    if not TESSERACT_AVAILABLE:
        raise ImportError("Tesseract OCR is not available")
    
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Perform OCR
        text = pytesseract.image_to_string(img)
        
        return text
    except Exception as e:
        print(f"Error performing OCR: {e}")
        traceback.print_exc()
        return ""


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using OCR.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text
    """
    if not PDF_SUPPORT or not TESSERACT_AVAILABLE:
        raise ImportError("PDF support or Tesseract OCR is not available")
    
    try:
        # Convert PDF to images
        images = pdf2image.convert_from_path(pdf_path)
        
        # Perform OCR on each image and combine the results
        extracted_text = ""
        for i, img in enumerate(images):
            # Save the image to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
                img.save(temp.name)
                temp_path = temp.name
            
            # Perform OCR
            text = perform_ocr(temp_path)
            extracted_text += f"--- Page {i+1} ---\n{text}\n\n"
            
            # Remove temporary file
            os.unlink(temp_path)
        
        return extracted_text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        traceback.print_exc()
        return ""


def analyze_image_with_multimodal(image_path: str, prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze an image using a multimodal model through Ollama.
    
    Args:
        image_path: Path to the image file
        prompt: Optional prompt to guide the analysis
        
    Returns:
        Analysis result
    """
    # Get configuration
    config = load_config()
    
    # Check if multimodal models are defined
    multimodal_model = config.get("integrations", {}).get("ollama", {}).get("multimodal_model", "llava:latest")
    
    # Prepare the prompt
    if not prompt:
        prompt = "Please analyze this image and extract the text content. Then, provide any insights about the content and its context."
    
    try:
        # Read the image and encode as base64
        with open(image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode("utf-8")
        
        # Call Ollama API for multimodal analysis
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": multimodal_model,
                "messages": [
                    {"role": "user", "content": prompt, "images": [base64_image]}
                ]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "content": result.get("message", {}).get("content", ""),
                "model": multimodal_model
            }
        else:
            error_msg = f"Error calling multimodal model: {response.status_code} - {response.text}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    except Exception as e:
        error_msg = f"Error analyzing image with multimodal model: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return {
            "success": False,
            "error": error_msg
        }


def process_file(file_path: str, use_multimodal: bool = True) -> Dict[str, Any]:
    """
    Process a file (image or PDF) and extract text or analyze with multimodal model.
    
    Args:
        file_path: Path to the file
        use_multimodal: Whether to use multimodal analysis
        
    Returns:
        Processing result
    """
    # Ensure dependencies are installed
    if not check_dependencies():
        return {
            "success": False,
            "error": "Required dependencies are not available"
        }
    
    # Determine file type
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # For image files
    if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif']:
        if use_multimodal:
            # Use multimodal analysis
            return analyze_image_with_multimodal(file_path)
        else:
            # Use OCR
            try:
                text = perform_ocr(file_path)
                return {
                    "success": True,
                    "text": text,
                    "method": "ocr"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error performing OCR: {str(e)}"
                }
    
    # For PDF files
    elif file_ext == '.pdf':
        try:
            text = extract_text_from_pdf(file_path)
            
            # If multimodal is enabled and extracted text is short or empty, try multimodal
            if use_multimodal and (len(text.strip()) < 100 or "�" in text):
                # Convert first page to image and analyze with multimodal
                try:
                    # Convert first page to image
                    images = pdf2image.convert_from_path(file_path, first_page=1, last_page=1)
                    if images:
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
                            images[0].save(temp.name)
                            temp_path = temp.name
                        
                        # Analyze with multimodal
                        result = analyze_image_with_multimodal(temp_path)
                        
                        # Remove temporary file
                        os.unlink(temp_path)
                        
                        # If successful, return the result
                        if result.get("success", False):
                            result["method"] = "multimodal"
                            return result
                except Exception as e:
                    print(f"Error analyzing PDF with multimodal: {e}")
            
            # If multimodal failed or not enabled, return OCR result
            return {
                "success": True,
                "text": text,
                "method": "ocr"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing PDF: {str(e)}"
            }
    
    # Unsupported file type
    else:
        return {
            "success": False,
            "error": f"Unsupported file type: {file_ext}"
        }


def update_config_for_multimodal():
    """Update config.json to include multimodal settings."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    try:
        # Load existing config
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Add multimodal model if not present
        if "integrations" not in config:
            config["integrations"] = {}
        
        if "ollama" not in config["integrations"]:
            config["integrations"]["ollama"] = {}
        
        # Check if we need to add multimodal model
        if "multimodal_model" not in config["integrations"]["ollama"]:
            # Try to find available multimodal models
            try:
                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    multimodal_models = [
                        m.get("name") for m in models 
                        if any(mm in m.get("name", "") for mm in ["llava", "vision", "multi", "gemini", "bakllava"])
                    ]
                    
                    if multimodal_models:
                        config["integrations"]["ollama"]["multimodal_model"] = multimodal_models[0]
                    else:
                        config["integrations"]["ollama"]["multimodal_model"] = "llava:latest"
                else:
                    config["integrations"]["ollama"]["multimodal_model"] = "llava:latest"
            except:
                config["integrations"]["ollama"]["multimodal_model"] = "llava:latest"
        
        # Update settings
        if "settings" not in config:
            config["settings"] = {}
        
        config["settings"]["use_multimodal"] = True
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print("Config updated for multimodal support")
        return True
    except Exception as e:
        print(f"Error updating config: {e}")
        return False


if __name__ == "__main__":
    # Check dependencies and update config
    if check_dependencies():
        print("All dependencies are available.")
        
        if update_config_for_multimodal():
            print("Configuration updated for multimodal support.")
        
        # Test with an example file if provided
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.exists(file_path):
                print(f"Processing file: {file_path}")
                result = process_file(file_path)
                
                if result.get("success", False):
                    if "text" in result:
                        print("\nExtracted Text:")
                        print("-" * 40)
                        print(result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"])
                    elif "content" in result:
                        print("\nMultimodal Analysis:")
                        print("-" * 40)
                        print(result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"])
                else:
                    print(f"Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"File not found: {file_path}")
    else:
        print("Some dependencies are missing. Please install them to use multimodal features.")
