"""
LM Studio integration for local LLM inference.

LM Studio provides an OpenAI-compatible API for local LLMs,
making it easy to run models like Llama 3, Mistral, and others locally.
"""

import requests
import json
import base64
from typing import List, Dict, Any, Optional, Union, Tuple
import os
from loguru import logger

from socratic_clarifier.integrations.llm_provider import LLMProvider


class LMStudioProvider(LLMProvider):
    """
    Provider integration for LM Studio's local inference server.
    
    LM Studio offers an OpenAI-compatible API for running models locally.
    """
    
    def __init__(self, 
                 base_url: str = "http://localhost:1234/v1", 
                 api_key: Optional[str] = None,
                 default_model: str = "default",
                 **kwargs):
        """
        Initialize the LM Studio provider.
        
        Args:
            base_url: Base URL for the LM Studio API (default: http://localhost:1234/v1)
            api_key: Optional API key (usually not needed for local LM Studio)
            default_model: Default model identifier to use
            **kwargs: Additional provider-specific parameters
        """
        self.base_url = base_url
        self.api_key = api_key
        self.default_model = default_model
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        
        # Check if LM Studio is available
        self._check_availability()
    
    def _check_availability(self):
        """Check if LM Studio server is running."""
        try:
            response = requests.get(f"{self.base_url}/models")
            if response.status_code == 200:
                logger.info("LM Studio server is available.")
                # Update the default model if not specified
                if self.default_model == "default":
                    models = response.json().get("data", [])
                    if models:
                        self.default_model = models[0].get("id", "default")
                        logger.info(f"Using default model: {self.default_model}")
            else:
                logger.warning(f"LM Studio server returned status code {response.status_code}")
        except requests.RequestException as e:
            logger.warning(f"LM Studio server not available: {e}")
    
    def generate_text(self, 
                      prompt: str, 
                      max_tokens: int = 256,
                      temperature: float = 0.7, 
                      model: Optional[str] = None,
                      **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate text using the LM Studio provider.
        
        Args:
            prompt: The input prompt to generate from
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (higher = more random)
            model: Model to use (defaults to self.default_model)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Tuple containing the generated text and metadata
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("choices", [{}])[0].get("text", "")
                return generated_text, result
            else:
                logger.error(f"Error from LM Studio API: {response.status_code} - {response.text}")
                return "", {"error": response.text}
        
        except Exception as e:
            logger.error(f"Error calling LM Studio API: {e}")
            return "", {"error": str(e)}
    
    def generate_chat(self, 
                      messages: List[Dict[str, str]], 
                      max_tokens: int = 256,
                      temperature: float = 0.7,
                      model: Optional[str] = None,
                      **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a chat response using the LM Studio provider.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (higher = more random)
            model: Model to use (defaults to self.default_model)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Tuple containing the generated response and metadata
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return generated_text, result
            else:
                logger.error(f"Error from LM Studio API: {response.status_code} - {response.text}")
                return "", {"error": response.text}
        
        except Exception as e:
            logger.error(f"Error calling LM Studio API: {e}")
            return "", {"error": str(e)}
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models from LM Studio.
        
        Returns:
            List of model information dictionaries
        """
        try:
            response = requests.get(f"{self.base_url}/models", headers=self.headers)
            
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                logger.error(f"Error getting models from LM Studio: {response.status_code} - {response.text}")
                return []
        
        except Exception as e:
            logger.error(f"Error getting models from LM Studio: {e}")
            return []
    
    def is_multimodal_supported(self) -> bool:
        """
        Check if the LM Studio server supports multimodal inputs.
        
        For LM Studio, this depends on the loaded model and version.
        Recent versions support multimodal models.
        
        Returns:
            True if multimodal is supported, False otherwise
        """
        # Try to detect if any available models support multimodal input
        models = self.get_available_models()
        
        # Check for models that might support vision based on naming
        multimodal_keywords = ["vision", "multimodal", "vqa", "llava", "clip", "mm"]
        for model in models:
            model_id = model.get("id", "").lower()
            if any(keyword in model_id for keyword in multimodal_keywords):
                return True
        
        return False
    
    def generate_multimodal(self, 
                         messages: List[Dict[str, Any]],
                         max_tokens: int = 256,
                         temperature: float = 0.7,
                         model: Optional[str] = None,
                         **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a response from multimodal input using the LM Studio provider.
        
        Args:
            messages: List of message dictionaries with 'role' and multimodal 'content'
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (higher = more random)
            model: Model to use (defaults to self.default_model)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Tuple containing the generated response and metadata
        """
        if not self.is_multimodal_supported():
            logger.warning("Multimodal input is not supported by the current LM Studio setup.")
            return "", {"error": "Multimodal input not supported"}
        
        model = model or self.default_model
        
        # Process messages to ensure they're in the right format for the API
        processed_messages = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            # Handle different content formats
            processed_content = content
            if isinstance(content, list):
                # Format for OpenAI-compatible multimodal API
                processed_content = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "image":
                        # Handle image data
                        image_data = item.get("image_url", {})
                        if isinstance(image_data, dict) and "url" in image_data:
                            if image_data["url"].startswith("data:image/"):
                                # It's a base64 image
                                processed_content.append({
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_data["url"]
                                    }
                                })
                            else:
                                # It's a file path
                                image_path = image_data["url"]
                                if os.path.exists(image_path):
                                    # Read the image and convert to base64
                                    with open(image_path, "rb") as img_file:
                                        img_data = img_file.read()
                                        b64_data = base64.b64encode(img_data).decode('utf-8')
                                        mime_type = self._guess_mime_type(image_path)
                                        data_url = f"data:{mime_type};base64,{b64_data}"
                                        processed_content.append({
                                            "type": "image_url",
                                            "image_url": {
                                                "url": data_url
                                            }
                                        })
                    elif isinstance(item, dict) and item.get("type") == "text":
                        processed_content.append({
                            "type": "text",
                            "text": item.get("text", "")
                        })
                    else:
                        # Default to text type
                        processed_content.append({
                            "type": "text",
                            "text": str(item)
                        })
            
            processed_messages.append({
                "role": role,
                "content": processed_content
            })
        
        payload = {
            "model": model,
            "messages": processed_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return generated_text, result
            else:
                logger.error(f"Error from LM Studio API: {response.status_code} - {response.text}")
                return "", {"error": response.text}
        
        except Exception as e:
            logger.error(f"Error calling LM Studio API: {e}")
            return "", {"error": str(e)}
    
    def _guess_mime_type(self, file_path: str) -> str:
        """Guess the MIME type based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.png':
            return 'image/png'
        elif ext in ['.jpg', '.jpeg']:
            return 'image/jpeg'
        elif ext == '.gif':
            return 'image/gif'
        elif ext == '.webp':
            return 'image/webp'
        else:
            return 'application/octet-stream'
