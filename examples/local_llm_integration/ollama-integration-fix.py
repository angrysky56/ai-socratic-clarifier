# enhanced_clarifier.py
"""
Enhanced Socratic Clarifier with Ollama Integration

This module provides an improved version of the Socratic Clarifier
that uses Ollama for local LLM processing.
"""
import os
import sys
import json
import time
import logging
import requests
from typing import Dict, List, Optional, Tuple, Union
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import from the main package, assuming we're in examples/local_llm_integration/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from socratic_clarifier.clarifier import SocraticClarifier
from socratic_clarifier.question_analysis import analyze_question

# Import the SoT wrapper to ensure proper integration
from sot_integration import SoTWrapper

class EnhancedClarifier(SocraticClarifier):
    """
    Enhanced version of SocraticClarifier that uses Ollama for local processing
    
    This class extends the base SocraticClarifier by adding support for:
    1. Local LLM processing via Ollama
    2. Improved question analysis with SoT
    3. Better error handling and timeout management
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the enhanced clarifier with optional configuration"""
        super().__init__(config)
        
        # Default configuration
        self.default_config = {
            "ollama": {
                "base_url": "http://localhost:11434",
                "model": "llama3",  # Default model
                "timeout": 30,  # Seconds
                "temperature": 0.7,
                "top_p": 0.9,
                "retries": 3
            },
            "use_ollama": True,
            "use_sot": True,
            "fallback_to_base": True
        }
        
        # Merge provided config with defaults
        self.config = {**self.default_config, **(config or {})}
        
        # Initialize SoT wrapper if enabled
        if self.config["use_sot"]:
            self.sot = SoTWrapper()
        else:
            self.sot = None
        
        # Check if Ollama is available
        if self.config["use_ollama"]:
            self.ollama_available = self._check_ollama()
        else:
            self.ollama_available = False
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available and running"""
        try:
            response = requests.get(
                f"{self.config['ollama']['base_url']}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except (requests.RequestException, ConnectionError) as e:
            logger.warning(f"Ollama check failed: {e}")
            return False
    
    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call Ollama API with the given prompt
        
        Args:
            prompt: The user prompt to send
            system_prompt: Optional system prompt
            
        Returns:
            The model's response text
        
        Raises:
            Exception: If the API call fails after retries
        """
        url = f"{self.config['ollama']['base_url']}/api/generate"
        
        # Prepare the payload
        payload = {
            "model": self.config['ollama']['model'],
            "prompt": prompt,
            "temperature": self.config['ollama']['temperature'],
            "top_p": self.config['ollama']['top_p'],
            "stream": False,
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt
        
        # Implement retry logic
        retries = self.config['ollama']['retries']
        timeout = self.config['ollama']['timeout']
        
        for attempt in range(retries):
            try:
                logger.info(f"Calling Ollama API (attempt {attempt+1}/{retries})")
                response = requests.post(
                    url, 
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', '')
                else:
                    logger.warning(f"Ollama API returned status code {response.status_code}: {response.text}")
            except (requests.RequestException, ConnectionError) as e:
                logger.warning(f"Ollama API call failed: {e}")
            
            # Wait before retrying (exponential backoff)
            if attempt < retries - 1:
                backoff_time = 2 ** attempt
                logger.info(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
        
        # All retries failed
        raise Exception(f"Failed to get response from Ollama after {retries} attempts")
    
    def process_with_ollama(self, question: str) -> Dict:
        """
        Process a question using Ollama
        
        Args:
            question: The question to process
            
        Returns:
            Dict containing the processed results
        """
        if not self.ollama_available:
            if self.config["fallback_to_base"]:
                logger.warning("Ollama not available, falling back to base processing")
                return super().process(question)
            else:
                raise Exception("Ollama is not available and fallback is disabled")
        
        try:
            # Analyze the question
            analysis = analyze_question(question)
            
            # Get appropriate SoT paradigm if enabled
            if self.sot:
                paradigm = self.sot.classify_question(question)
                system_prompt = self.sot.get_system_prompt(paradigm)
                logger.info(f"Using SoT paradigm: {paradigm}")
            else:
                system_prompt = "You are a helpful AI assistant that helps clarify questions by breaking them down into clear, logical components."
            
            # Create prompts for clarification
            clarification_prompt = self._generate_clarification_prompt(question, analysis)
            
            # Process with Ollama
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Set a timeout to prevent hanging
                future = executor.submit(self._call_ollama, clarification_prompt, system_prompt)
                try:
                    clarification_response = future.result(timeout=self.config['ollama']['timeout'])
                except concurrent.futures.TimeoutError:
                    logger.error(f"Ollama processing timed out after {self.config['ollama']['timeout']} seconds")
                    if self.config["fallback_to_base"]:
                        logger.warning("Falling back to base processing")
                        return super().process(question)
                    else:
                        raise Exception("Ollama processing timed out")
            
            # Parse and process the response
            socratic_questions = self._extract_socratic_questions(clarification_response)
            
            return {
                "original_question": question,
                "analysis": analysis,
                "clarification": clarification_response,
                "socratic_questions": socratic_questions,
                "processed_with": "ollama"
            }
        except Exception as e:
            logger.error(f"Error in enhanced processing: {e}")
            if self.config["fallback_to_base"]:
                logger.warning("Falling back to base processing due to error")
                return super().process(question)
            else:
                raise
    
    def process(self, question: str) -> Dict:
        """
        Process a question using enhanced methods if available, fallback to base otherwise
        
        Args:
            question: The question to process
            
        Returns:
            Dict containing the processed results
        """
        if self.config["use_ollama"] and self.ollama_available:
            return self.process_with_ollama(question)
        else:
            return super().process(question)
        