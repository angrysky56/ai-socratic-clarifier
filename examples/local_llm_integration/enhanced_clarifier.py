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

# Now try to import - using the correct module structure
try:
    from socratic_clarifier.core import SocraticClarifier, load_config
    # Use the correct class name from the sot_integration module
    from socratic_clarifier.integrations.sot_integration import SoTIntegration
    logger.info("Successfully imported from socratic_clarifier module")
except ImportError as e:
    logger.error(f"Could not import SocraticClarifier: {e}")
    logger.error("Please check the project structure and import paths")
    sys.exit(1)

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
        
        # Load config from the project's config.json
        self.project_config = load_config()
        
        # Default configuration - use project config values where available
        self.default_config = {
            "ollama": self.project_config.get("integrations", {}).get("ollama", {}).copy()
        }
        
        # Ensure basic defaults if not in project config
        if "base_url" not in self.default_config["ollama"]:
            self.default_config["ollama"]["base_url"] = "http://localhost:11434"
        
        # Add defaults for other settings
        self.default_config.update({
            "use_ollama": True,
            "use_sot": True,
            "fallback_to_base": True
        })
        
        # Merge provided config with defaults
        if config is None:
            self.config = self.default_config
        else:
            self.config = self.default_config.copy()
            # Merge only the ollama section if it exists
            if "ollama" in config:
                self.config["ollama"].update(config["ollama"])
            # Merge top-level configuration
            for key, value in config.items():
                if key != "ollama":
                    self.config[key] = value
        
        logger.info(f"Using Ollama model: {self.config['ollama'].get('default_model', 'not specified')}")
        
        # Initialize SoT integration
        if self.config["use_sot"]:
            self.sot = SoTIntegration()
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
            # Try to connect to Ollama API to check if it's running
            response = requests.get(
                f"{self.config['ollama']['base_url']}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                # Check if the specified model is available
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                
                default_model = self.config['ollama'].get('default_model')
                if default_model and default_model not in model_names:
                    logger.warning(f"Ollama model '{default_model}' not found.")
                    logger.warning(f"Available models: {', '.join(model_names)}")
                    
                    # If no model available or specified, use the first available one
                    if model_names:
                        logger.warning(f"Using first available model: {model_names[0]}")
                        self.config['ollama']['model_to_use'] = model_names[0]
                    else:
                        logger.warning("No models available in Ollama")
                        return False
                else:
                    # Use the specified model
                    self.config['ollama']['model_to_use'] = default_model
                
                return True
            return False
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
        
        # Get the model to use
        model = self.config['ollama'].get('model_to_use', self.config['ollama'].get('default_model'))
        if not model:
            raise ValueError("No Ollama model specified")
        
        # Prepare the payload
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": self.config['ollama'].get('temperature', 0.7),
            "top_p": self.config['ollama'].get('top_p', 0.9),
            "stream": False,
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt
        
        # Implement retry logic
        retries = self.config['ollama'].get('retries', 3)
        timeout = self.config['ollama'].get('timeout', 60)
        
        for attempt in range(retries):
            try:
                logger.info(f"Calling Ollama API with model {model} (attempt {attempt+1}/{retries})")
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
    
    def _analyze_question(self, question: str) -> Dict:
        """Analyze a question"""
        # Use the analyze method from the base clarifier
        analysis = self.base_clarifier.analyze(question)
        return analysis.dict()
    
    def _generate_clarification_prompt(self, question: str, analysis: Dict) -> str:
        """Generate a prompt for the clarification step"""
        # Create a clarification prompt based on the analysis
        prompt = f"""
I need to clarify the following question:
"{question}"

I've analyzed the question and identified the following issues:
"""
        
        # Add issues details if available
        if "issues" in analysis and analysis["issues"]:
            for i, issue in enumerate(analysis["issues"], 1):
                issue_type = issue.get("type", "unknown")
                term = issue.get("term", "")
                confidence = issue.get("confidence", 0.0)
                prompt += f"{i}. {issue_type} issue with term '{term}' (confidence: {confidence:.2f})\n"
        else:
            prompt += "No specific issues identified.\n"
        
        # Add reasoning if available
        if "reasoning" in analysis and analysis["reasoning"]:
            prompt += f"\nReasoning:\n{analysis['reasoning']}\n"
        
        # Add instruction for response
        prompt += """
Based on this analysis, please clarify the question by:
1. Identifying any ambiguous, vague, or biased terms
2. Suggesting more precise alternatives
3. Posing Socratic questions that would help refine the original question

Please present your clarification in a clear, structured way that highlights the issues and suggests how to improve the question.
"""
        
        return prompt
    
    def _extract_socratic_questions(self, clarification_text: str) -> List[str]:
        """Extract Socratic questions from the clarification text"""
        # Simple heuristic to extract questions
        lines = clarification_text.split("\n")
        questions = []
        
        for line in lines:
            line = line.strip()
            # Check if the line looks like a question
            if line and line[-1] == "?" and len(line) > 10:
                questions.append(line)
        
        # If no questions were found with simple heuristic, try more patterns
        if not questions:
            import re
            # Find sentences ending with question marks
            question_pattern = re.compile(r'[A-Z][^.!?]*\?')
            questions = question_pattern.findall(clarification_text)
        
        return questions
    
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
                analysis = self.base_clarifier.analyze(question)
                return {
                    "original_question": question,
                    "analysis": analysis.dict(),
                    "clarification": "Ollama not available for clarification.",
                    "socratic_questions": analysis.questions,
                    "processed_with": "base"
                }
            else:
                raise Exception("Ollama is not available and fallback is disabled")
        
        try:
            # Analyze the question
            analysis = self._analyze_question(question)
            
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
                    clarification_response = future.result(timeout=self.config['ollama'].get('timeout', 60))
                except concurrent.futures.TimeoutError:
                    logger.error(f"Ollama processing timed out after {self.config['ollama'].get('timeout', 60)} seconds")
                    if self.config["fallback_to_base"]:
                        logger.warning("Falling back to base processing")
                        analysis = self.base_clarifier.analyze(question)
                        return {
                            "original_question": question,
                            "analysis": analysis.dict(),
                            "clarification": "Ollama processing timed out.",
                            "socratic_questions": analysis.questions,
                            "processed_with": "base"
                        }
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
                analysis = self.base_clarifier.analyze(question)
                return {
                    "original_question": question,
                    "analysis": analysis.dict(),
                    "clarification": f"Error in Ollama processing: {str(e)}",
                    "socratic_questions": analysis.questions,
                    "processed_with": "base"
                }
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
            analysis = self.base_clarifier.analyze(question)
            return {
                "original_question": question,
                "analysis": analysis.dict(),
                "clarification": "Processed with base clarifier.",
                "socratic_questions": analysis.questions,
                "processed_with": "base"
            }

# Example usage when run directly
if __name__ == "__main__":
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running")
            models = response.json().get("models", [])
            if models:
                print("Available models:")
                for model in models:
                    print(f"  - {model.get('name', 'Unknown')}")
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
