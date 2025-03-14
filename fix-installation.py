#!/usr/bin/env python
"""
Fix installation script for AI-Socratic-Clarifier

This script:
1. Identifies and fixes the module structure
2. Installs the proper SoT integration
3. Updates the Ollama integration
4. Removes unnecessary MCP sequential thinking code

Usage:
    python fix_installation.py
"""
import os
import sys
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root directory (where this script is located)
PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))

def remove_mcp_sequential_thinking():
    """Remove MCP sequential thinking code"""
    logger.info("Checking for MCP sequential thinking code...")
    
    # Look for the sequential_thinking directory
    sequential_thinking_dir = PROJECT_ROOT / "sequential_thinking"
    
    if sequential_thinking_dir.exists() and sequential_thinking_dir.is_dir():
        logger.info(f"Found sequential_thinking directory: {sequential_thinking_dir}")
        
        # Create backup
        backup_dir = PROJECT_ROOT / "backup_sequential_thinking"
        backup_dir.mkdir(exist_ok=True)
        
        try:
            shutil.copytree(sequential_thinking_dir, backup_dir / "sequential_thinking")
            logger.info(f"Backed up sequential_thinking to {backup_dir}")
            
            # Remove the directory
            shutil.rmtree(sequential_thinking_dir)
            logger.info("Removed sequential_thinking directory")
        except Exception as e:
            logger.error(f"Error processing sequential_thinking: {e}")
    else:
        logger.info("No sequential_thinking directory found")
    
    return True

def main():
    """Main execution function"""
    logger.info("Starting AI-Socratic-Clarifier installation fix")
    
    try:
        # Check module structure
        if not check_module_structure():
            logger.warning("Module structure check failed, but continuing...")
        
        # Remove custom SoT folders
        if not remove_custom_sot_folders():
            logger.warning("Custom SoT folder removal failed, but continuing...")
        
        # Remove MCP sequential thinking
        if not remove_mcp_sequential_thinking():
            logger.warning("MCP sequential thinking removal failed, but continuing...")
        
        # Install SoT integration
        if not install_sot_integration():
            logger.error("Failed to install SoT integration")
            return False
        
        # Update Ollama integration
        if not update_ollama_integration():
            logger.error("Failed to update Ollama integration")
            return False
        
        logger.info("Installation fix completed successfully!")
        logger.info("""
Next steps:
1. If you were having issues with SoT installation:
   pip install sketch-of-thought

2. Test the Ollama integration:
   python examples/local_llm_integration/test_ollama_integration.py

3. Make sure Ollama is running before testing:
   ollama serve  # in a separate terminal

This fix has:
- Removed any custom SoT folders
- Installed a proper SoT integration
- Updated the Ollama integration
- Removed MCP sequential thinking code
""")
        return True
        
    except Exception as e:
        logger.error(f"Error during installation fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()

def check_module_structure():
    """Check the module structure and report issues"""
    logger.info("Checking module structure...")
    
    socratic_clarifier_dir = PROJECT_ROOT / "socratic_clarifier"
    if not socratic_clarifier_dir.exists():
        logger.warning(f"socratic_clarifier directory not found at: {socratic_clarifier_dir}")
        
        # Look for alternative locations
        candidates = list(PROJECT_ROOT.glob("**/socratic_clarifier"))
        if candidates:
            logger.info(f"Found potential socratic_clarifier directories: {candidates}")
        else:
            logger.error("Could not find socratic_clarifier directory anywhere")
            return False
    
    # Check for core files that should exist
    core_files = [
        socratic_clarifier_dir / "__init__.py",
        # Look for either core.py or clarifier.py
        [socratic_clarifier_dir / "core.py", socratic_clarifier_dir / "clarifier.py"],
        # Look for either analysis.py or question_analysis.py
        [socratic_clarifier_dir / "analysis.py", socratic_clarifier_dir / "question_analysis.py"]
    ]
    
    for file_or_alternatives in core_files:
        if isinstance(file_or_alternatives, list):
            # Check if at least one of the alternatives exists
            if not any(alt.exists() for alt in file_or_alternatives):
                logger.warning(f"None of the alternative files exist: {file_or_alternatives}")
        else:
            if not file_or_alternatives.exists():
                logger.warning(f"Required file not found: {file_or_alternatives}")
    
    return True

def remove_custom_sot_folders():
    """Remove any custom SoT folders"""
    logger.info("Checking for custom SoT folders...")
    
    # Patterns for custom SoT folders
    patterns = ["sot_*", "**/sot_*", "SoT"]
    
    custom_folders = []
    for pattern in patterns:
        custom_folders.extend(list(PROJECT_ROOT.glob(pattern)))
    
    custom_folders = [folder for folder in custom_folders if folder.is_dir()]
    
    if custom_folders:
        logger.info(f"Found {len(custom_folders)} custom SoT folders: {custom_folders}")
        
        # Backup folders before removing
        backup_dir = PROJECT_ROOT / "backup_custom_sot"
        backup_dir.mkdir(exist_ok=True)
        
        for folder in custom_folders:
            try:
                # Create backup
                folder_name = folder.name
                backup_path = backup_dir / folder_name
                if backup_path.exists():
                    # If backup already exists, add a number
                    i = 1
                    while (backup_dir / f"{folder_name}_{i}").exists():
                        i += 1
                    backup_path = backup_dir / f"{folder_name}_{i}"
                
                shutil.copytree(folder, backup_path)
                logger.info(f"Backed up {folder} to {backup_path}")
                
                # Remove the folder
                shutil.rmtree(folder)
                logger.info(f"Removed custom SoT folder: {folder}")
            except Exception as e:
                logger.error(f"Error processing folder {folder}: {e}")
    else:
        logger.info("No custom SoT folders found")
    
    return True

def update_ollama_integration():
    """Update Ollama integration"""
    logger.info("Updating Ollama integration...")
    
    # Create the directory structure if needed
    examples_dir = PROJECT_ROOT / "examples"
    if not examples_dir.exists():
        examples_dir.mkdir(exist_ok=True)
    
    local_llm_dir = examples_dir / "local_llm_integration"
    if not local_llm_dir.exists():
        local_llm_dir.mkdir(exist_ok=True)
    
    # Path to the enhanced clarifier file
    enhanced_clarifier_path = local_llm_dir / "enhanced_clarifier.py"
    
    # Create the enhanced clarifier file (with proper imports)
    with open(enhanced_clarifier_path, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python
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
    print(f"\\nQuestion: {result['original_question']}\\n")
    print(f"Clarification:\\n{result['clarification']}\\n")
    print("Socratic Questions:")
    for i, q in enumerate(result['socratic_questions'], 1):
        print(f"{i}. {q}")
''')
    
    logger.info(f"Created enhanced clarifier file at: {enhanced_clarifier_path}")
    
    # Create a test script for Ollama integration
    test_script_path = local_llm_dir / "test_ollama_integration.py"
    
    with open(test_script_path, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python
"""
Test script for Ollama integration with Socratic Clarifier
"""
import os
import sys
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path to find our enhanced_clarifier module
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from enhanced_clarifier import EnhancedClarifier
    logger.info("Successfully imported EnhancedClarifier")
except ImportError as e:
    logger.error(f"Failed to import EnhancedClarifier: {e}")
    sys.exit(1)

def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running")
            return True
        else:
            print(f"✗ Ollama returned unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Ollama is not running: {e}")
        return False

def test_ollama_integration():
    """Test the Ollama integration"""
    print("Testing Ollama integration...")
    
    if not check_ollama():
        print("Please start Ollama first and try again")
        return
    
    try:
        # Create an enhanced clarifier with a longer timeout
        config = {
            "ollama": {
                "model": "llama3",  # Use the model you have installed
                "timeout": 60,  # Increase timeout for testing
            }
        }
        clarifier = EnhancedClarifier(config)
        
        # Test with a sample question
        question = "What is the relationship between temperature and pressure in a gas?"
        
        print(f"\\nProcessing question: {question}")
        start_time = time.time()
        
        result = clarifier.process(question)
        
        end_time = time.time()
        print(f"Processing took {end_time - start_time:.2f} seconds\\n")
        
        # Display the results
        print(f"Clarification:\\n{result['clarification']}\\n")
        print("Socratic Questions:")
        for i, q in enumerate(result['socratic_questions'], 1):
            print(f"{i}. {q}")
        
        print("\\n✓ Ollama integration test successful")
        
    except Exception as e:
        print(f"✗ Ollama integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ollama_integration()
''')
    
    # Make the test script executable
    os.chmod(test_script_path, 0o755)
    
    logger.info(f"Created test script at: {test_script_path}")
    return True

def install_sot_integration():
    """Install proper SoT integration"""
    logger.info("Installing proper SoT integration...")
    
    sot_integration_path = PROJECT_ROOT / "sot_integration.py"
    
    # Write the simplified SoT integration
    with open(sot_integration_path, 'w', encoding='utf-8') as f:
        f.write('''"""
Minimal SoT (Sketch-of-Thought) integration for the AI-Socratic-Clarifier
"""
import os
import sys
import logging
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we can import SoT properly
try:
    import sketch_of_thought
    from sketch_of_thought import SoT
    has_sot_package = True
    logger.info("Successfully imported Sketch-of-Thought package")
except ImportError:
    has_sot_package = False
    logger.warning("Could not import Sketch-of-Thought package, using minimal implementation")

class SoTWrapper:
    """
    Wrapper for Sketch-of-Thought
    
    This is a minimal wrapper that either uses the proper SoT package
    if available, or provides basic functionality if not.
    """
    
    def __init__(self):
        """Initialize the wrapper"""
        if has_sot_package:
            try:
                self.sot = SoT()
                self.available_paradigms = self.sot.avaliable_paradigms()
                logger.info(f"Using SoT with paradigms: {self.available_paradigms}")
            except Exception as e:
                logger.error(f"Error initializing SoT: {e}")
                self._init_minimal()
        else:
            self._init_minimal()
    
    def _init_minimal(self):
        """Initialize with minimal functionality"""
        self.sot = None
        self.available_paradigms = ['chunked_symbolism', 'conceptual_chaining', 'expert_lexicons']
        logger.info("Using minimal SoT implementation")
    
    def classify_question(self, question: str) -> str:
        """Classify a question to determine the best reasoning paradigm"""
        if has_sot_package and self.sot:
            try:
                return self.sot.classify_question(question)
            except Exception as e:
                logger.error(f"Error classifying question with SoT: {e}")
                return self._minimal_classify(question)
        else:
            return self._minimal_classify(question)
    
    def _minimal_classify(self, question: str) -> str:
        """Simple classification based on keywords"""
        question_lower = question.lower()
        
        # Mathematical or calculation questions
        if any(term in question_lower for term in [
            'calculate', 'compute', 'solve', 'equation', 'math', 'formula',
            'plus', 'minus', 'add', 'subtract', 'multiply', 'divide'
        ]):
            return 'chunked_symbolism'
        
        # Explanatory questions
        elif any(term in question_lower for term in [
            'explain', 'why', 'how', 'what is', 'describe', 'elaborate', 
            'reason', 'cause', 'effect', 'relationship'
        ]):
            return 'conceptual_chaining'
        
        # Technical or domain-specific questions
        elif any(term in question_lower for term in [
            'technical', 'specific', 'domain', 'field', 'expert',
            'science', 'engineering', 'medicine', 'law', 'finance'
        ]):
            return 'expert_lexicons'
        
        # Default to conceptual chaining for most questions
        else:
            return 'conceptual_chaining'
    
    def get_system_prompt(self, paradigm: str) -> str:
        """Get the appropriate system prompt for the paradigm"""
        if has_sot_package and self.sot:
            try:
                return self.sot.get_system_prompt(paradigm)
            except Exception as e:
                logger.error(f"Error getting system prompt with SoT: {e}")
                return self._get_minimal_prompt(paradigm)
        else:
            return self._get_minimal_prompt(paradigm)
    
    def _get_minimal_prompt(self, paradigm: str) -> str:
        """Get a minimal prompt for the specified paradigm"""
        if paradigm == 'chunked_symbolism':
            return """
You are a helpful AI assistant specializing in mathematical and symbolic reasoning.
When solving problems, use the following structured approach:
1. Organize your reasoning into clear, step-by-step equations
2. Define variables clearly at each step
3. Show your work using mathematical notation
4. Present your final answer clearly using \\boxed{answer} notation

Enclose your step-by-step reasoning in <think> </think> tags.
"""
        elif paradigm == 'conceptual_chaining':
            return """
You are a helpful AI assistant specializing in clear conceptual explanations.
When answering questions, use the following structured approach:
1. Break down complex ideas into key concepts
2. Connect concepts in a logical sequence using clear transitions
3. Focus on the essential relationships between ideas
4. Avoid unnecessary details while preserving accuracy

Enclose your step-by-step reasoning in <think> </think> tags.
"""
        elif paradigm == 'expert_lexicons':
            return """
You are a helpful AI assistant specializing in technical and domain-specific communication.
When answering questions, use the following structured approach:
1. Use precise technical terminology appropriate to the field
2. Define specialized terms concisely when necessary
3. Use standard notation and abbreviations
4. Maximize information density while maintaining clarity

Enclose your step-by-step reasoning in <think> </think> tags.
"""
        else:
            return """
You are a helpful AI assistant. Think step by step to solve problems clearly and accurately.
Enclose your step-by-step reasoning in <think> </think> tags.
"""
    
    def get_initialized_context(self, paradigm: str, question: Optional[str] = None, 
                               format: str = "llm", include_system_prompt: bool = True) -> Union[List[Dict], Dict]:
        """Get initialized context with exemplars for the selected paradigm"""
        if has_sot_package and self.sot:
            try:
                return self.sot.get_initialized_context(
                    paradigm=paradigm,
                    question=question,
                    format=format,
                    include_system_prompt=include_system_prompt
                )
            except Exception as e:
                logger.error(f"Error getting initialized context with SoT: {e}")
                return self._get_minimal_context(paradigm, question, format, include_system_prompt)
        else:
            return self._get_minimal_context(paradigm, question, format, include_system_prompt)
    
    def _get_minimal_context(self, paradigm: str, question: Optional[str], 
                            format: str, include_system_prompt: bool) -> Union[List[Dict], Dict]:
        """Create a minimal context for the specified paradigm"""
        system_prompt = self._get_minimal_prompt(paradigm) if include_system_prompt else ""
        
        # Create examples based on the paradigm
        if paradigm == 'chunked_symbolism':
            example_q = "If x = 5 and y = 3, what is x + y?"
            example_a = "<think>\\nx = 5\\ny = 3\\nx + y = 8\\n</think>\\n\\n\\\\boxed{8}"
        elif paradigm == 'conceptual_chaining':
            example_q = "Why does ice float on water?"
            example_a = "<think>\\n- Water molecules form crystal structure when freezing\\n- Crystal structure has more space between molecules\\n- More space → lower density\\n- Ice is less dense than liquid water\\n- Less dense objects float on more dense liquids\\n</think>\\n\\nIce floats on water because it's less dense."
        else:  # expert_lexicons
            example_q = "Explain photosynthesis briefly."
            example_a = "<think>\\nPhotosynthesis: Light → Chemical Energy\\nReactants: CO₂ + H₂O + photons\\nProducts: C₆H₁₂O₆ + O₂\\nLocation: Chloroplasts\\nKey processes: Light-dependent rxns + Calvin cycle\\n</think>\\n\\nPhotosynthesis: conversion of light energy to chemical energy in plants via CO₂ + H₂O + light → glucose + O₂."
        
        # Format the context based on the requested format
        if format == "llm":
            messages = []
            if include_system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add example
            messages.append({"role": "user", "content": example_q})
            messages.append({"role": "assistant", "content": example_a})
            
            # Add current question if provided
            if question:
                messages.append({"role": "user", "content": question})
            
            return messages
        
        elif format == "vlm":
            # Visual language model format
            messages = []
            if include_system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add example
            messages.append({
                "role": "user", 
                "content": [{"type": "text", "text": example_q}]
            })
            messages.append({
                "role": "assistant", 
                "content": [{"type": "text", "text": example_a}]
            })
            
            # Add current question if provided
            if question:
                messages.append({
                    "role": "user", 
                    "content": [{"type": "text", "text": question}]
                })
            
            return messages
        
        else:  # raw format
            return [
                {
                    "question": example_q,
                    "answer": example_a
                }
            ]
''')
    
    logger.info(f"Created SoT integration file at: {sot_integration_path}")
    return True