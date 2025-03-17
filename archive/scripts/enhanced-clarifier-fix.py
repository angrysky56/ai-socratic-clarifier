#!/usr/bin/env python
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

# Fix the import path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Check if the socratic_clarifier module exists in the correct location
expected_module_path = os.path.join(project_root, 'socratic_clarifier')
if not os.path.exists(expected_module_path):
    logger.error(f"socratic_clarifier module not found at: {expected_module_path}")
    logger.error("Please make sure the project structure is correct")
    sys.exit(1)

# Now try to import
try:
    # First, try to import from the module structure
    from socratic_clarifier.core import SocraticClarifier
    from socratic_clarifier.analysis import analyze_question
    logger.info("Successfully imported from socratic_clarifier module")
except ImportError:
    try:
        # If that fails, try alternative import paths based on typical project structures
        if os.path.exists(os.path.join(project_root, 'socratic_clarifier', 'clarifier.py')):
            from socratic_clarifier.clarifier import SocraticClarifier
            from socratic_clarifier.question_analysis import analyze_question
            logger.info("Successfully imported from alternative module path")
        else:
            logger.error("Could not find the SocraticClarifier class")
            logger.error("Please check the project structure and import paths")
            sys.exit(1)
    except ImportError as e:
        logger.error(f"Could not import SocraticClarifier: {e}")
        logger.error("Please check the project structure and import paths")
        sys.exit(1)

# Import the SoT wrapper if it exists, otherwise create a minimal version
sot_integration_path = os.path.join(project_root, 'sot_integration.py')
if os.path.exists(sot_integration_path):
    # If sot_integration.py exists, import from it
    sys.path.insert(0, project_root)
    try:
        from sot_integration import SoTWrapper
        logger.info("Successfully imported SoTWrapper from sot_integration.py")
    except ImportError as e:
        logger.error(f"Could not import SoTWrapper: {e}")
        SoTWrapper = None
else:
    # If it doesn't exist, define a minimal SoTWrapper class
    logger.warning("sot_integration.py not found, using minimal SoTWrapper")
    class SoTWrapper:
        """Minimal SoT wrapper for when the integration file isn't available"""
        def __init__(self):
            self.available_paradigms = ['conceptual_chaining']
        
        def classify_question(self, question: str) -> str:
            return "conceptual_chaining"
        
        def get_system_prompt(self, paradigm: str) -> str:
            return "You are a helpful AI assistant that helps clarify questions."
        
        def get_initialized_context(self, paradigm: str, question: Optional[str] = None, 
                                  format: str = "llm", include_system_prompt: bool = True):
            return []


class EnhancedClarifier:
    """
    Enhanced version of SocraticClarifier that uses Ollama for local processing
    
    This class extends the base SocraticClarifier by adding support for:
    1. Local LLM processing via Ollama
    2. Improved question analysis with SoT
    3. Better error handling and timeout management
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the enhanced clarifier with optional configuration"""
        self.base_clarifier = SocraticClarifier()
        
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
        
        # Initialize SoT wrapper if enabled and available
        if self.config["use_sot"] and SoTWrapper is not None:
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
    
    def _generate_clarification_prompt(self, question: str, analysis: Dict) -> str:
        """Generate a prompt for the clarification step"""
        # Delegate to the base clarifier for prompt generation
        # This assumes the base clarifier has a method for this
        # If not, you'll need to implement it here
        return self.base_clarifier._generate_clarification_prompt(question, analysis)
    
    def _extract_socratic_questions(self, clarification_text: str) -> List[str]:
        """Extract Socratic questions from the clarification text"""
        # Delegate to the base clarifier for extraction
        # This assumes the base clarifier has a method for this
        # If not, you'll need to implement it here
        return self.base_clarifier._extract_socratic_questions(clarification_text)
    
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
                return self.base_clarifier.process(question)
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
                        return self.base_clarifier.process(question)
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
                return self.base_clarifier.process(question)
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
            return self.base_clarifier.process(question)

# Example usage when run directly
if __name__ == "__main__":
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running")
        else:
            print("✗ Ollama is not running correctly")
    except Exception:
        print("✗ Ollama is not running")
        
    # Create an instance of the enhanced clarifier
    clarifier = EnhancedClarifier()
    
    # Example question
    question = "What causes the seasons to change on Earth?"
    
    # Process the question
    result = clarifier.process(question)
    
    # Display the results
    print(f"\nQuestion: {result['original_question']}\n")
    print(f"Clarification:\n{result['clarification']}\n")
    print("Socratic Questions:")
    for i, q in enumerate(result['socratic_questions'], 1):
        print(f"{i}. {q}")
