"""
Integration manager for coordinating different LLM and embedding providers.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import os
from loguru import logger

from socratic_clarifier.integrations.llm_provider import LLMProvider
from socratic_clarifier.integrations.embedding_provider import EmbeddingProvider
from socratic_clarifier.integrations.lm_studio import LMStudioProvider
from socratic_clarifier.integrations.ollama import OllamaProvider


class IntegrationManager:
    """
    Manager for coordinating different LLM and embedding providers.
    
    This class handles the discovery and management of available providers,
    fallback strategies, and selecting the best provider for a given task.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the integration manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.llm_providers: Dict[str, LLMProvider] = {}
        self.embedding_providers: Dict[str, EmbeddingProvider] = {}
        
        # Discover available providers
        self._discover_providers()
    
    def _discover_providers(self):
        """Discover and initialize available providers."""
        # Try to connect to LM Studio
        try:
            lm_studio_url = self.config.get("lm_studio_url", "http://localhost:1234/v1")
            lm_studio = LMStudioProvider(base_url=lm_studio_url)
            models = lm_studio.get_available_models()
            if models:
                logger.info(f"LM Studio detected with {len(models)} models available.")
                self.llm_providers["lm_studio"] = lm_studio
        except Exception as e:
            logger.debug(f"LM Studio not available: {e}")
        
        # Try to connect to Ollama
        try:
            ollama_url = self.config.get("ollama_url", "http://localhost:11434/api")
            ollama = OllamaProvider(base_url=ollama_url)
            models = ollama.get_available_models()
            if models:
                logger.info(f"Ollama detected with {len(models)} models available.")
                self.llm_providers["ollama"] = ollama
                self.embedding_providers["ollama"] = ollama
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
        
        # Log provider status
        if not self.llm_providers:
            logger.warning("No local LLM providers detected. Running without LLM integration.")
        if not self.embedding_providers:
            logger.warning("No embedding providers detected. Running without embedding integration.")
    
    def get_llm_provider(self, provider_name: Optional[str] = None) -> Optional[LLMProvider]:
        """
        Get an LLM provider by name or the best available provider.
        
        Args:
            provider_name: Optional name of the provider to get
            
        Returns:
            LLMProvider instance or None if not available
        """
        if provider_name:
            return self.llm_providers.get(provider_name)
        
        # If no specific provider requested, return the best available
        # Preference order: LM Studio, Ollama
        if "lm_studio" in self.llm_providers:
            return self.llm_providers["lm_studio"]
        elif "ollama" in self.llm_providers:
            return self.llm_providers["ollama"]
        
        return None
    
    def get_embedding_provider(self, provider_name: Optional[str] = None) -> Optional[EmbeddingProvider]:
        """
        Get an embedding provider by name or the best available provider.
        
        Args:
            provider_name: Optional name of the provider to get
            
        Returns:
            EmbeddingProvider instance or None if not available
        """
        if provider_name:
            return self.embedding_providers.get(provider_name)
        
        # If no specific provider requested, return the best available
        # Currently only Ollama supports embeddings in our implementation
        if "ollama" in self.embedding_providers:
            return self.embedding_providers["ollama"]
        
        return None
    
    def get_available_llm_providers(self) -> List[str]:
        """
        Get a list of available LLM provider names.
        
        Returns:
            List of provider names
        """
        return list(self.llm_providers.keys())
    
    def get_available_embedding_providers(self) -> List[str]:
        """
        Get a list of available embedding provider names.
        
        Returns:
            List of provider names
        """
        return list(self.embedding_providers.keys())
    
    def is_multimodal_available(self) -> bool:
        """
        Check if any provider supports multimodal inputs.
        
        Returns:
            True if multimodal is supported, False otherwise
        """
        for provider in self.llm_providers.values():
            if provider.is_multimodal_supported():
                return True
        
        return False
    
    def get_multimodal_provider(self) -> Optional[LLMProvider]:
        """
        Get a provider that supports multimodal inputs.
        
        Returns:
            LLMProvider instance or None if none support multimodal
        """
        for name, provider in self.llm_providers.items():
            if provider.is_multimodal_supported():
                return provider
        
        return None
    
    def generate_socratic_questions(self, text: str, issues: List[Dict[str, Any]], 
                                   provider_name: Optional[str] = None,
                                   use_sot: bool = True) -> List[str]:
        """
        Generate Socratic questions using a local LLM.
        
        This method combines the detected issues with SoT reasoning
        to enhance the quality of generated questions.
        
        Args:
            text: The original text being analyzed
            issues: List of detected issues
            provider_name: Optional name of provider to use
            use_sot: Whether to use SoT reasoning format
            
        Returns:
            List of generated questions
        """
        provider = self.get_llm_provider(provider_name)
        if not provider:
            logger.warning("No LLM provider available for question generation.")
            return []
        
        # Create a system prompt for the LLM
        system_prompt = """
        You are an expert at creating Socratic questions to help improve communication clarity and reduce bias.
        Based on the text and detected issues, generate thought-provoking questions that will help the author clarify their meaning, 
        consider potential biases, and strengthen their reasoning.
        
        Focus on questions that:
        - Ask for clarification of ambiguous terms
        - Challenge biased assumptions
        - Request evidence for unsupported claims
        - Identify logical inconsistencies
        - Encourage deeper reflection
        
        Your questions should be specific to the issues detected and should help improve the text.
        """
        
        # Create context from the text and issues
        context = f"Text: \"{text}\"\n\nDetected issues:\n"
        for i, issue in enumerate(issues):
            context += f"{i+1}. {issue.get('issue', 'Unknown issue')} - '{issue.get('term', '')}'\n"
            context += f"   {issue.get('description', '')}\n"
        
        # Add SoT format instructions if enabled
        if use_sot:
            context += "\nGenerate questions using Sketch-of-Thought format. Begin with analyzing the issues, then present 3-5 questions.\n"
        
        # Create messages for the chat API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ]
        
        # Generate questions using the provider
        generated_text, _ = provider.generate_chat(
            messages=messages,
            max_tokens=512,
            temperature=0.7
        )
        
        # Parse the response to extract questions
        questions = []
        for line in generated_text.strip().split("\n"):
            line = line.strip()
            if line and ("?" in line) and not line.startswith("#") and not line.startswith("<"):
                # Clean up numbering or bullet points
                clean_line = line
                if line[0].isdigit() and line[1:3] in ['. ', ') ']:
                    clean_line = line[3:].strip()
                elif line.startswith('- '):
                    clean_line = line[2:].strip()
                
                questions.append(clean_line)
        
        return questions
    
    def enhance_reasoning(self, text: str, issues: List[Dict[str, Any]], sot_paradigm: str,
                         provider_name: Optional[str] = None) -> str:
        """
        Enhance SoT reasoning using a local LLM.
        
        This method combines the base SoT reasoning with LLM-generated insights.
        
        Args:
            text: The original text being analyzed
            issues: List of detected issues
            sot_paradigm: The SoT paradigm being used
            provider_name: Optional name of provider to use
            
        Returns:
            Enhanced reasoning string
        """
        provider = self.get_llm_provider(provider_name)
        if not provider:
            logger.warning("No LLM provider available for reasoning enhancement.")
            return ""
        
        # Create a system prompt for the LLM
        system_prompt = f"""
        You are an expert at creating structured reasoning in the {sot_paradigm} format.
        Analyze the text and issues to create a concise reasoning diagram.
        
        Use the following format for your response:
        
        <think>
        # Your structured reasoning here
        </think>
        """
        
        # Create context from the text and issues
        context = f"Text: \"{text}\"\n\nDetected issues:\n"
        for i, issue in enumerate(issues):
            context += f"{i+1}. {issue.get('issue', 'Unknown issue')} - '{issue.get('term', '')}'\n"
            context += f"   {issue.get('description', '')}\n"
        
        # Add paradigm-specific instructions
        if sot_paradigm == "conceptual_chaining":
            context += "\nCreate conceptual chains showing how the issues connect to clarity problems.\n"
            context += "Example: #ambiguous_term → #multiple_interpretations → #needs_clarification\n"
        elif sot_paradigm == "chunked_symbolism":
            context += "\nUse symbolic notation to represent the issues and their implications.\n"
            context += "Example: clarity_score = 0.4\nissue_count = 3\nclarification_needed = True\n"
        elif sot_paradigm == "expert_lexicons":
            context += "\nUse domain-specific notation to analyze the issues.\n"
            context += "Example: ambiguity(term) → ¬clarity\n∴ requires_revision\n"
        
        # Create messages for the chat API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ]
        
        # Generate reasoning using the provider
        generated_text, _ = provider.generate_chat(
            messages=messages,
            max_tokens=512,
            temperature=0.5  # Lower temperature for more consistent reasoning
        )
        
        # Extract the reasoning
        reasoning = generated_text
        
        # Ensure the reasoning has the proper format
        if "<think>" not in reasoning:
            reasoning = f"<think>\n{reasoning}\n</think>"
        
        return reasoning
