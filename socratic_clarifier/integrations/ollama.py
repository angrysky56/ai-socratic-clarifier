"""
Ollama integration for local LLM inference and embeddings.

Ollama provides a simple API for running open source
language models locally, including models like Llama, Mistral, and more.
"""

import requests
import json
import base64
from typing import List, Dict, Any, Optional, Union, Tuple
import os
from loguru import logger

from socratic_clarifier.integrations.llm_provider import LLMProvider
from socratic_clarifier.integrations.embedding_provider import EmbeddingProvider


class OllamaProvider(LLMProvider, EmbeddingProvider):
    """
    Provider integration for Ollama's local inference server.
    
    Ollama offers an API for running models locally and generating embeddings.
    """
    
    def __init__(self, 
                 base_url: str = "http://localhost:11434/api", 
                 api_key: Optional[str] = None,
                 default_model: str = "llama3",
                 default_embedding_model: str = "nomic-embed-text",
                 **kwargs):
        """
        Initialize the Ollama provider.
        
        Args:
            base_url: Base URL for the Ollama API (default: http://localhost:11434/api)
            api_key: Optional API key (usually not needed for local Ollama)
            default_model: Default model identifier to use for generation
            default_embedding_model: Default model to use for embeddings
            **kwargs: Additional provider-specific parameters
        """
        self.base_url = base_url
        self.api_key = api_key
        self.default_model = default_model
        self.default_embedding_model = default_embedding_model
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        
        # Check if Ollama is available
        self._check_availability()
    
    def _check_availability(self):
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self.base_url}/tags")
            if response.status_code == 200:
                logger.info("Ollama server is available.")
                # Update the default model if not specified
                if response.json().get("models"):
                    available_models = [m.get("name") for m in response.json().get("models", [])]
                    if available_models and self.default_model not in available_models:
                        self.default_model = available_models[0]
                        logger.info(f"Using default model: {self.default_model}")
            else:
                logger.warning(f"Ollama server returned status code {response.status_code}")
        except requests.RequestException as e:
            logger.warning(f"Ollama server not available: {e}")
    
    def generate_text(self, 
                      prompt: str, 
                      max_tokens: int = 256,
                      temperature: float = 0.7, 
                      model: Optional[str] = None,
                      **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate text using the Ollama provider.
        
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
        
        # Add parameters to payload
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,  # Disable streaming by default to avoid JSON parsing issues
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                headers=self.headers,
                json=payload,
                timeout=kwargs.get("timeout", 60)
            )
            
            # For streaming responses, Ollama might return multiple JSON objects
            # We need to handle this case
            try:
                if response.status_code == 200:
                    try:
                        result = response.json()
                        return result.get("response", ""), result
                    except json.JSONDecodeError:
                        # Handle streaming response or multiple JSON objects
                        text_content = response.text
                        if text_content.strip():
                            # Try to parse as multiple JSON objects
                            lines = text_content.strip().split("\n")
                            if lines:
                                try:
                                    # Parse the last complete JSON object
                                    last_json = json.loads(lines[-1])
                                    return last_json.get("response", ""), last_json
                                except json.JSONDecodeError:
                                    # If that fails, extract content another way
                                    contents = []
                                    for line in lines:
                                        try:
                                            obj = json.loads(line)
                                            if "response" in obj:
                                                contents.append(obj["response"])
                                        except json.JSONDecodeError:
                                            pass
                                    
                                    if contents:
                                        return " ".join(contents), {"response": " ".join(contents)}
                        
                        logger.error(f"Error parsing Ollama API response: {response.text[:100]}...")
                        return "", {"error": "Failed to parse response"}
                else:
                    logger.error(f"Error from Ollama API: {response.status_code} - {response.text}")
                    return "", {"error": response.text}
            
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                return "", {"error": f"Error processing response: {e}"}
        
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return "", {"error": str(e)}
    
    def generate_chat(self, 
                      messages: List[Dict[str, str]], 
                      max_tokens: int = 256,
                      temperature: float = 0.7,
                      model: Optional[str] = None,
                      **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a chat response using the Ollama provider.
        
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
        
        # Add parameters to payload
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,  # Disable streaming by default to avoid JSON parsing issues
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                headers=self.headers,
                json=payload,
                timeout=kwargs.get("timeout", 60)
            )
            
            # For streaming responses, Ollama might return multiple JSON objects
            # We need to handle this case
            try:
                if response.status_code == 200:
                    try:
                        result = response.json()
                        return result.get("message", {}).get("content", ""), result
                    except json.JSONDecodeError:
                        # Handle streaming response or multiple JSON objects
                        text_content = response.text
                        if text_content.strip():
                            # Try to parse as multiple JSON objects
                            lines = text_content.strip().split("\n")
                            if lines:
                                try:
                                    # Parse the last complete JSON object
                                    last_json = json.loads(lines[-1])
                                    return last_json.get("message", {}).get("content", ""), last_json
                                except json.JSONDecodeError:
                                    # If that fails, extract content another way
                                    contents = []
                                    for line in lines:
                                        try:
                                            obj = json.loads(line)
                                            if "message" in obj and "content" in obj["message"]:
                                                contents.append(obj["message"]["content"])
                                        except json.JSONDecodeError:
                                            pass
                                    
                                    if contents:
                                        return " ".join(contents), {"message": {"content": " ".join(contents)}}
                        
                        logger.error(f"Error parsing Ollama API response: {response.text[:100]}...")
                        return "", {"error": "Failed to parse response"}
                else:
                    logger.error(f"Error from Ollama API: {response.status_code} - {response.text}")
                    return "", {"error": response.text}
            
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                return "", {"error": f"Error processing response: {e}"}
        
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return "", {"error": str(e)}
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models from Ollama.
        
        Returns:
            List of model information dictionaries
        """
        try:
            response = requests.get(f"{self.base_url}/tags", headers=self.headers)
            
            if response.status_code == 200:
                return response.json().get("models", [])
            else:
                logger.error(f"Error getting models from Ollama: {response.status_code} - {response.text}")
                return []
        
        except Exception as e:
            logger.error(f"Error getting models from Ollama: {e}")
            return []
    
    def is_multimodal_supported(self) -> bool:
        """
        Check if the Ollama server supports multimodal inputs.
        
        For Ollama, this depends on the loaded models.
        Recent versions support multimodal models like llava.
        
        Returns:
            True if multimodal is supported, False otherwise
        """
        # Try to detect if any available models support multimodal input
        models = self.get_available_models()
        
        # Check for models that might support vision based on naming
        multimodal_keywords = ["vision", "llava", "clip", "bakllava", "vqa", "visual"]
        for model in models:
            model_name = model.get("name", "").lower()
            if any(keyword in model_name for keyword in multimodal_keywords):
                return True
        
        return False
    
    def generate_multimodal(self, 
                         messages: List[Dict[str, Any]],
                         max_tokens: int = 256,
                         temperature: float = 0.7,
                         model: Optional[str] = None,
                         **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a response from multimodal input using the Ollama provider.
        
        Args:
            messages: List of message dictionaries with 'role' and multimodal 'content'
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (higher = more random)
            model: Model to use (defaults to a vision model if available)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Tuple containing the generated response and metadata
        """
        if not self.is_multimodal_supported():
            logger.warning("Multimodal input is not supported by the current Ollama setup.")
            return "", {"error": "Multimodal input not supported"}
        
        # If no model specified, find a vision model
        if model is None:
            models = self.get_available_models()
            for m in models:
                model_name = m.get("name", "").lower()
                if any(keyword in model_name for keyword in ["llava", "vision", "bakllava"]):
                    model = m.get("name")
                    break
            
            if model is None:
                logger.error("No vision model found in Ollama.")
                return "", {"error": "No vision model available"}
        
        # Process messages to Ollama's format
        processed_messages = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            # Handle different content formats
            if isinstance(content, list):
                # Format for Ollama multimodal API
                text_parts = []
                images = []
                
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "image":
                            # Handle image data
                            image_data = item.get("image_url", {})
                            if isinstance(image_data, dict) and "url" in image_data:
                                image_url = image_data["url"]
                                if image_url.startswith("data:image/"):
                                    # It's base64 image data
                                    # Extract the base64 part
                                    base64_data = image_url.split(",")[1]
                                    images.append(base64_data)
                                else:
                                    # It's a file path
                                    if os.path.exists(image_url):
                                        with open(image_url, "rb") as img_file:
                                            img_data = img_file.read()
                                            b64_data = base64.b64encode(img_data).decode('utf-8')
                                            images.append(b64_data)
                        elif item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                    else:
                        # Default to text
                        text_parts.append(str(item))
                
                # Combine text parts
                text_content = " ".join(text_parts)
                
                # Create an Ollama compatible message
                if images:
                    processed_message = {
                        "role": role,
                        "content": text_content,
                        "images": images
                    }
                else:
                    processed_message = {
                        "role": role,
                        "content": text_content
                    }
            else:
                # Simple text message
                processed_message = {
                    "role": role,
                    "content": content
                }
            
            processed_messages.append(processed_message)
        
        # Add parameters to payload
        payload = {
            "model": model,
            "messages": processed_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,  # Disable streaming by default to avoid JSON parsing issues
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                headers=self.headers,
                json=payload,
                timeout=kwargs.get("timeout", 60)
            )
            
            # For streaming responses, Ollama might return multiple JSON objects
            # We need to handle this case
            try:
                if response.status_code == 200:
                    try:
                        result = response.json()
                        return result.get("message", {}).get("content", ""), result
                    except json.JSONDecodeError:
                        # Handle streaming response or multiple JSON objects
                        text_content = response.text
                        if text_content.strip():
                            # Try to parse as multiple JSON objects
                            lines = text_content.strip().split("\n")
                            if lines:
                                try:
                                    # Parse the last complete JSON object
                                    last_json = json.loads(lines[-1])
                                    return last_json.get("message", {}).get("content", ""), last_json
                                except json.JSONDecodeError:
                                    # If that fails, extract content another way
                                    contents = []
                                    for line in lines:
                                        try:
                                            obj = json.loads(line)
                                            if "message" in obj and "content" in obj["message"]:
                                                contents.append(obj["message"]["content"])
                                        except json.JSONDecodeError:
                                            pass
                                    
                                    if contents:
                                        return " ".join(contents), {"message": {"content": " ".join(contents)}}
                        
                        logger.error(f"Error parsing Ollama API response: {response.text[:100]}...")
                        return "", {"error": "Failed to parse response"}
                else:
                    logger.error(f"Error from Ollama API: {response.status_code} - {response.text}")
                    return "", {"error": response.text}
            
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                return "", {"error": f"Error processing response: {e}"}
        
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return "", {"error": str(e)}

    # Embedding methods
    
    def get_text_embedding(self, 
                           text: str, 
                           model: Optional[str] = None, 
                           **kwargs) -> Tuple[List[float], Dict[str, Any]]:
        """
        Generate an embedding vector for text using Ollama.
        
        Args:
            text: The input text to embed
            model: Model to use (defaults to self.default_embedding_model)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Tuple containing the embedding vector and metadata
        """
        model = model or self.default_embedding_model
        
        # Add parameters to payload
        payload = {
            "model": model,
            "prompt": text,
            "stream": False,  # Disable streaming by default to avoid JSON parsing issues
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json=payload,
                timeout=kwargs.get("timeout", 60)
            )
            
            # For streaming responses, Ollama might return multiple JSON objects
            try:
                if response.status_code == 200:
                    try:
                        result = response.json()
                        embedding = result.get("embedding", [])
                        return embedding, result
                    except json.JSONDecodeError:
                        # Handle streaming response or multiple JSON objects
                        text_content = response.text
                        if text_content.strip():
                            # Try to parse as multiple JSON objects
                            lines = text_content.strip().split("\n")
                            if lines:
                                try:
                                    # Parse the last complete JSON object
                                    last_json = json.loads(lines[-1])
                                    embedding = last_json.get("embedding", [])
                                    return embedding, last_json
                                except json.JSONDecodeError:
                                    pass
                        
                        logger.error(f"Error parsing Ollama API response: {response.text[:100]}...")
                        return [], {"error": "Failed to parse response"}
                else:
                    logger.error(f"Error from Ollama API: {response.status_code} - {response.text}")
                    return [], {"error": response.text}
            
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                return [], {"error": f"Error processing response: {e}"}
        
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return [], {"error": str(e)}
    
    def get_batch_embeddings(self, 
                             texts: List[str], 
                             model: Optional[str] = None, 
                             **kwargs) -> Tuple[List[List[float]], Dict[str, Any]]:
        """
        Generate embedding vectors for multiple texts using Ollama.
        
        Args:
            texts: List of input texts to embed
            model: Model to use (defaults to self.default_embedding_model)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Tuple containing a list of embedding vectors and metadata
        """
        model = model or self.default_embedding_model
        
        embeddings = []
        metadata = {"model": model, "batch_size": len(texts)}
        
        for text in texts:
            embedding, meta = self.get_text_embedding(text, model, **kwargs)
            if embedding:
                embeddings.append(embedding)
            else:
                logger.warning(f"Failed to get embedding for text: {text[:50]}...")
        
        return embeddings, metadata
    
    def get_multimodal_embedding(self, 
                              image_path: Optional[str] = None,
                              image_bytes: Optional[bytes] = None,
                              text: Optional[str] = None,
                              model: Optional[str] = None,
                              **kwargs) -> Tuple[List[float], Dict[str, Any]]:
        """
        Generate an embedding vector for multimodal input using Ollama.
        
        Note: Ollama has limited support for multimodal embeddings.
        This tries to use a vision model if available.
        
        Args:
            image_path: Path to an image file
            image_bytes: Raw image bytes
            text: Optional text to accompany the image
            model: Model to use (defaults to a vision model if available)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Tuple containing the embedding vector and metadata
        """
        if not self.is_multimodal_supported():
            logger.warning("Multimodal embeddings are not officially supported by Ollama.")
            return [], {"error": "Multimodal embeddings not supported"}
        
        # Find a multimodal model if not specified
        if model is None:
            models = self.get_available_models()
            for m in models:
                model_name = m.get("name", "").lower()
                if any(keyword in model_name for keyword in ["clip", "llava", "vision"]):
                    model = m.get("name")
                    break
            
            if model is None:
                logger.error("No vision model found for multimodal embeddings.")
                return [], {"error": "No multimodal embedding model available"}
        
        # Prepare the image data
        image_b64 = None
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, "rb") as img_file:
                    image_bytes = img_file.read()
            except Exception as e:
                logger.error(f"Error reading image file: {e}")
                return [], {"error": f"Error reading image file: {e}"}
        
        if image_bytes:
            try:
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            except Exception as e:
                logger.error(f"Error encoding image: {e}")
                return [], {"error": f"Error encoding image: {e}"}
        
        # Combine text and image for the prompt
        prompt = text or ""
        
        # Create payload for the API
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,  # Disable streaming by default
            **kwargs
        }
        
        if image_b64:
            payload["images"] = [image_b64]
        
        try:
            # Attempt to use the embeddings endpoint
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json=payload,
                timeout=kwargs.get("timeout", 60)  # Add a timeout
            )
            
            try:
                if response.status_code == 200:
                    try:
                        result = response.json()
                        embedding = result.get("embedding", [])
                        return embedding, result
                    except json.JSONDecodeError:
                        # Handle streaming response or multiple JSON objects
                        text_content = response.text
                        if text_content.strip():
                            # Try to parse as multiple JSON objects
                            lines = text_content.strip().split("\n")
                            if lines:
                                try:
                                    # Parse the last complete JSON object
                                    last_json = json.loads(lines[-1])
                                    embedding = last_json.get("embedding", [])
                                    return embedding, last_json
                                except json.JSONDecodeError:
                                    pass
                        
                        logger.warning("Direct multimodal embeddings failed, using alternative approach.")
                else:
                    logger.warning(f"Embeddings endpoint failed with status {response.status_code}, trying alternative approach.")
                
                # Fallback to using generate with special embedding extraction
                special_prompt = f"EMBEDDING_ONLY: {prompt}"
                payload["prompt"] = special_prompt
                
                response = requests.post(
                    f"{self.base_url}/generate",
                    headers=self.headers,
                    json=payload,
                    timeout=kwargs.get("timeout", 60)  # Add a timeout
                )
                
                if response.status_code == 200:
                    # Attempt to extract embedding data from the response
                    # This is a fallback and not guaranteed to work with all models
                    logger.warning("Multimodal embedding extraction may not be accurate.")
                    return [], {"warning": "Multimodal embeddings not directly supported"}
                else:
                    logger.error(f"Error from Ollama API: {response.status_code} - {response.text}")
                    return [], {"error": response.text}
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                return [], {"error": f"Error processing response: {e}"}
        
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return [], {"error": str(e)}
