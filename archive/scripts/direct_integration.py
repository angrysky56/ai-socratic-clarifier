"""
Direct integration module for the enhanced AI-Socratic-Clarifier.
This module provides direct access to the core functionality without the web interface.
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from socratic_clarifier import SocraticClarifier
from loguru import logger

# Initialize the clarifier
def initialize_clarifier():
    """Initialize the clarifier with the configuration."""
    config_path = os.path.join(os.path.dirname(__file__), '../../../../../../../../config.json')
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
        else:
            logger.warning(f"Configuration file not found at {config_path}. Using default configuration.")
            config = {
                "integrations": {
                    "ollama": {
                        "enabled": True,
                        "base_url": "http://localhost:11434/api",
                        "default_model": "llama3",
                        "default_embedding_model": "nomic-embed-text",
                        "timeout": 60
                    }
                },
                "settings": {
                    "prefer_provider": "auto",
                    "use_llm_questions": True,
                    "use_llm_reasoning": True,
                    "use_sot": True,
                    "use_multimodal": True,
                    "use_document_rag": True
                }
            }
        
        return SocraticClarifier(config=config)
    except Exception as e:
        logger.error(f"Error initializing clarifier: {e}")
        # Use default configuration
        return SocraticClarifier()

# Global clarifier instance
_clarifier = None

def get_clarifier():
    """Get the clarifier instance, initializing it if necessary."""
    global _clarifier
    if _clarifier is None:
        _clarifier = initialize_clarifier()
    return _clarifier

def direct_analyze_text(
    text: str, 
    mode: str = 'standard', 
    use_sot: bool = True, 
    max_questions: int = 5,
    document_context: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Analyze text directly using the clarifier.
    
    Args:
        text: The text to analyze
        mode: The analysis mode to use ('standard', 'deep', 'reflective')
        use_sot: Whether to use sequential thinking
        max_questions: Maximum number of questions to generate
        document_context: Optional list of document contexts for RAG
    
    Returns:
        A dictionary with the analysis results
    """
    clarifier = get_clarifier()
    
    try:
        # Check if the mode is available
        available_modes = clarifier.available_modes()
        if mode not in available_modes:
            logger.warning(f"Mode '{mode}' not available. Using 'standard' mode.")
            mode = 'standard'
        
        # Prepare document context for analysis
        rag_context = ""
        if document_context:
            # Extract text from document contexts
            context_parts = []
            for doc in document_context:
                if doc.get('content'):
                    context_parts.append(f"Document: {doc.get('filename', 'Unnamed')}\n{doc.get('content')}")
            
            if context_parts:
                rag_context = "\n\n".join(context_parts)
        
        # Use the specified mode
        if mode == 'standard':
            issues, questions, reasoning = clarifier.analyze_text(
                text, 
                use_sot=use_sot, 
                max_questions=max_questions,
                document_context=rag_context
            )
        elif mode == 'deep':
            issues, questions, reasoning = clarifier.analyze_text_deep(
                text, 
                use_sot=use_sot, 
                max_questions=max_questions,
                document_context=rag_context
            )
        elif mode == 'reflective':
            issues, questions, reasoning = clarifier.analyze_text_reflective(
                text, 
                use_sot=use_sot, 
                max_questions=max_questions,
                document_context=rag_context
            )
        else:
            # Fallback to standard mode
            issues, questions, reasoning = clarifier.analyze_text(
                text, 
                use_sot=use_sot, 
                max_questions=max_questions,
                document_context=rag_context
            )
        
        # Prepare the result
        result = {
            'text': text,
            'issues': issues,
            'questions': questions,
            'reasoning': reasoning,
            'sot_paradigm': clarifier.sot_paradigm if hasattr(clarifier, 'sot_paradigm') else None,
            'confidence': 0.85,  # Default confidence
            'sot_enabled': use_sot,
            'model': clarifier.model if hasattr(clarifier, 'model') else 'llama3',
            'provider': clarifier.provider if hasattr(clarifier, 'provider') else 'ollama'
        }
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        return {
            'text': text,
            'issues': [],
            'questions': [],
            'reasoning': None,
            'sot_paradigm': None,
            'confidence': 0.0,
            'sot_enabled': use_sot,
            'model': 'unknown',
            'provider': 'unknown',
            'error': str(e)
        }

def get_reflective_ecosystem_status() -> Dict[str, Any]:
    """
    Get the status of the reflective ecosystem.
    
    Returns:
        A dictionary with the status information
    """
    clarifier = get_clarifier()
    
    try:
        # Check if the reflective ecosystem is available
        if hasattr(clarifier, 'reflective_ecosystem') and clarifier.reflective_ecosystem:
            return {
                'available': True,
                'global_coherence': 0.85,
                'paradigm': clarifier.sot_paradigm if hasattr(clarifier, 'sot_paradigm') else 'default',
                'model': clarifier.model if hasattr(clarifier, 'model') else 'llama3',
                'provider': clarifier.provider if hasattr(clarifier, 'provider') else 'ollama'
            }
        else:
            return {
                'available': False,
                'reason': 'Reflective ecosystem not initialized'
            }
    except Exception as e:
        logger.error(f"Error getting reflective ecosystem status: {e}")
        return {
            'available': False,
            'reason': str(e)
        }

def process_feedback(question: str, helpful: bool, paradigm: Optional[str] = None) -> bool:
    """
    Process feedback through the reflective ecosystem.
    
    Args:
        question: The question to provide feedback for
        helpful: Whether the question was helpful
        paradigm: The paradigm used for the question
    
    Returns:
        Whether the feedback was processed successfully
    """
    clarifier = get_clarifier()
    
    try:
        # Check if the reflective ecosystem is available
        if hasattr(clarifier, 'reflective_ecosystem') and clarifier.reflective_ecosystem:
            # Process the feedback
            # This is a stub - in a real implementation, the feedback would be
            # processed through the reflective ecosystem
            logger.info(f"Processing feedback: {question}, helpful: {helpful}, paradigm: {paradigm}")
            return True
        else:
            logger.warning("Reflective ecosystem not available. Feedback not processed.")
            return False
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        return False
