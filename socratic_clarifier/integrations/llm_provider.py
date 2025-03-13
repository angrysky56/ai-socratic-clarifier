"""
Base class for LLM provider integrations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple


class LLMProvider(ABC):
    """
    Abstract base class for LLM provider integrations.
    
    This defines the interface that all provider implementations must follow.
    """
    
    @abstractmethod
    def __init__(self, base_url: str, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the LLM provider.
        
        Args:
            base_url: Base URL for the API endpoint
            api_key: Optional API key for authentication
            **kwargs: Additional provider-specific parameters
        """
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, 
                      max_tokens: int = 256,
                      temperature: float = 0.7, 
                      **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate text using the LLM provider.
        
        Args:
            prompt: The input prompt to generate from
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (higher = more random)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Tuple containing the generated text and metadata
        """
        pass
    
    @abstractmethod
    def generate_chat(self, messages: List[Dict[str, str]], 
                      max_tokens: int = 256,
                      temperature: float = 0.7,
                      **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a chat response using the LLM provider.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (higher = more random)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Tuple containing the generated response and metadata
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models from the provider.
        
        Returns:
            List of model information dictionaries
        """
        pass
    
    @abstractmethod
    def is_multimodal_supported(self) -> bool:
        """
        Check if the provider supports multimodal inputs.
        
        Returns:
            True if multimodal is supported, False otherwise
        """
        pass
    
    @abstractmethod
    def generate_multimodal(self, 
                         messages: List[Dict[str, Any]],
                         max_tokens: int = 256,
                         temperature: float = 0.7,
                         **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a response from multimodal input using the LLM provider.
        
        Args:
            messages: List of message dictionaries with 'role' and multimodal 'content'
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (higher = more random)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Tuple containing the generated response and metadata
        """
        pass
