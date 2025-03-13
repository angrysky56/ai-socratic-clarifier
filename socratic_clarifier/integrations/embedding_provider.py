"""
Base class for embedding provider integrations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding provider integrations.
    
    This defines the interface that all embedding provider implementations must follow.
    """
    
    @abstractmethod
    def __init__(self, base_url: str, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the embedding provider.
        
        Args:
            base_url: Base URL for the API endpoint
            api_key: Optional API key for authentication
            **kwargs: Additional provider-specific parameters
        """
        pass
    
    @abstractmethod
    def get_text_embedding(self, text: str, **kwargs) -> Tuple[List[float], Dict[str, Any]]:
        """
        Generate an embedding vector for text.
        
        Args:
            text: The input text to embed
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Tuple containing the embedding vector and metadata
        """
        pass
    
    @abstractmethod
    def get_batch_embeddings(self, texts: List[str], **kwargs) -> Tuple[List[List[float]], Dict[str, Any]]:
        """
        Generate embedding vectors for multiple texts.
        
        Args:
            texts: List of input texts to embed
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Tuple containing a list of embedding vectors and metadata
        """
        pass
    
    @abstractmethod
    def is_multimodal_supported(self) -> bool:
        """
        Check if the provider supports multimodal inputs.
        
        Returns:
            True if multimodal embeddings are supported, False otherwise
        """
        pass
    
    @abstractmethod
    def get_multimodal_embedding(self, 
                              image_path: Optional[str] = None,
                              image_bytes: Optional[bytes] = None,
                              text: Optional[str] = None,
                              **kwargs) -> Tuple[List[float], Dict[str, Any]]:
        """
        Generate an embedding vector for multimodal input.
        
        Args:
            image_path: Path to an image file
            image_bytes: Raw image bytes
            text: Optional text to accompany the image
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Tuple containing the embedding vector and metadata
        """
        pass
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (between -1 and 1)
        """
        embedding1_np = np.array(embedding1)
        embedding2_np = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(embedding1_np, embedding2_np)
        norm1 = np.linalg.norm(embedding1_np)
        norm2 = np.linalg.norm(embedding2_np)
        
        return dot_product / (norm1 * norm2)
