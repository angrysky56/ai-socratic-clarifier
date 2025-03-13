"""
Integration manager for coordinating different LLM and embedding providers.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import os
import json
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
        # Load config if not provided
        if config is None:
            config = self._load_config()
        
        self.config = config
        self.llm_providers: Dict[str, LLMProvider] = {}
        self.embedding_providers: Dict[str, EmbeddingProvider] = {}
        
        # Discover available providers
        self._discover_providers()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json."""
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json'))
        default_config = {
            "integrations": {
                "lm_studio": {
                    "enabled": True,
                    "base_url": "http://localhost:1234/v1",
                    "api_key": None,
                    "default_model": "default",
                    "timeout": 60
                },
                "ollama": {
                    "enabled": True,
                    "base_url": "http://localhost:11434/api",
                    "api_key": None,
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
                "use_multimodal": True
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Configuration loaded from {config_path}")
                return config
            else:
                logger.warning(f"Configuration file not found at {config_path}. Using default configuration.")
                return default_config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}. Using default configuration.")
            return default_config
    
    def _discover_providers(self):
        """Discover and initialize available providers."""
        # Get configuration for providers
        lm_studio_config = self.config.get("integrations", {}).get("lm_studio", {})
        ollama_config = self.config.get("integrations", {}).get("ollama", {})
        
        # Only try to connect if enabled in config
        lm_studio_enabled = lm_studio_config.get("enabled", True)
        ollama_enabled = ollama_config.get("enabled", True)
        
        # Try to connect to LM Studio if enabled
        if lm_studio_enabled:
            try:
                lm_studio_url = lm_studio_config.get("base_url", "http://localhost:1234/v1")
                lm_studio_api_key = lm_studio_config.get("api_key")
                lm_studio_default_model = lm_studio_config.get("default_model", "default")
                
                lm_studio = LMStudioProvider(
                    base_url=lm_studio_url,
                    api_key=lm_studio_api_key,
                    default_model=lm_studio_default_model
                )
                
                models = lm_studio.get_available_models()
                if models:
                    logger.info(f"LM Studio detected with {len(models)} models available.")
                    self.llm_providers["lm_studio"] = lm_studio
            except Exception as e:
                logger.debug(f"LM Studio not available: {e}")
        
        # Try to connect to Ollama if enabled
        if ollama_enabled:
            try:
                ollama_url = ollama_config.get("base_url", "http://localhost:11434/api")
                ollama_api_key = ollama_config.get("api_key")
                ollama_default_model = ollama_config.get("default_model", "llama3")
                ollama_default_embedding_model = ollama_config.get("default_embedding_model", "nomic-embed-text")
                
                ollama = OllamaProvider(
                    base_url=ollama_url,
                    api_key=ollama_api_key,
                    default_model=ollama_default_model,
                    default_embedding_model=ollama_default_embedding_model
                )
                
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
        
        # Check for preferred provider in config
        preferred_provider = self.config.get("settings", {}).get("prefer_provider", "auto")
        
        if preferred_provider != "auto" and preferred_provider in self.llm_providers:
            return self.llm_providers[preferred_provider]
        
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
        # Check if multimodal is enabled in config
        multimodal_enabled = self.config.get("settings", {}).get("use_multimodal", True)
        if not multimodal_enabled:
            return False
            
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
        # Check if multimodal is enabled in config
        multimodal_enabled = self.config.get("settings", {}).get("use_multimodal", True)
        if not multimodal_enabled:
            return None
            
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
        # Check if LLM questions are enabled in config
        llm_questions_enabled = self.config.get("settings", {}).get("use_llm_questions", True)
        if not llm_questions_enabled:
            return []
            
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
        # Check if LLM reasoning is enabled in config
        llm_reasoning_enabled = self.config.get("settings", {}).get("use_llm_reasoning", True)
        if not llm_reasoning_enabled:
            return ""
            
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
