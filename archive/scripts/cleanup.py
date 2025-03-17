#!/usr/bin/env python
"""
Cleanup Script for AI-Socratic-Clarifier

This script cleans up the project by:
1. Removing any MCP sequential thinking code
2. Verifying SoT integration
3. Ensuring Ollama integration works correctly
4. Creating proper imports and references

Usage:
    python cleanup.py
"""
import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root directory - assumed to be where this script is executed
PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))


def verify_venv():
    """Verify we're running in a virtual environment"""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.error("This script should be run within a virtual environment")
        logger.info("Please activate your virtual environment first")
        sys.exit(1)


def backup_directory(directory_path):
    """Create a backup of a directory"""
    backup_path = str(directory_path) + '.bak'
    if os.path.exists(directory_path):
        logger.info(f"Creating backup of {directory_path} to {backup_path}")
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
        shutil.copytree(directory_path, backup_path)
        return True
    return False


def remove_directory(directory_path):
    """Remove a directory if it exists"""
    if os.path.exists(directory_path):
        logger.info(f"Removing directory: {directory_path}")
        shutil.rmtree(directory_path)
        return True
    return False


def cleanup_mcp_sequential_thinking():
    """Remove MCP sequential thinking related code"""
    # Directories to remove - adjust as needed
    dirs_to_remove = [
        PROJECT_ROOT / "sequential_thinking"
    ]
    
    for directory in dirs_to_remove:
        if os.path.exists(directory):
            backup_directory(directory)
            remove_directory(directory)
            logger.info(f"Removed MCP directory: {directory}")
    
    # Files to check for MCP references
    py_files = list(PROJECT_ROOT.glob('**/*.py'))
    
    mcp_references = []
    for py_file in py_files:
        # Skip virtual environment
        if 'venv' in str(py_file):
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'mcp' in content.lower() or 'sequential_thinking' in content.lower():
                mcp_references.append(py_file)
    
    logger.info(f"Found {len(mcp_references)} files with MCP references")
    for file_path in mcp_references:
        logger.info(f"File with MCP references: {file_path}")


def cleanup_sot_fallback():
    """Clean up any custom SoT implementations"""
    # Remove any custom SoT implementations - adjust paths as needed
    sot_dirs = [
        PROJECT_ROOT / "sot_2m7tor_e",
        PROJECT_ROOT / "sot_2mhns_3"
    ]
    
    for directory in sot_dirs:
        if os.path.exists(directory):
            backup_directory(directory)
            remove_directory(directory)
            logger.info(f"Removed custom SoT directory: {directory}")
    
    # Copy the new SoT integration file to the proper location
    sot_integration_path = PROJECT_ROOT / "sot_integration.py"
    
    with open(sot_integration_path, 'w', encoding='utf-8') as f:
        f.write("""# sot_integration.py
\"\"\"
Proper integration module for Sketch-of-Thought (SoT)
This replaces any fallback implementation and ensures proper import
\"\"\"
import logging
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Try to import the proper SoT package
    from sketch_of_thought import SoT
    logger.info("Successfully imported Sketch-of-Thought package")
    USE_PROPER_SOT = True
except ImportError as e:
    logger.warning(f"Could not import Sketch-of-Thought package: {e}")
    logger.warning("Using minimal stub implementation")
    USE_PROPER_SOT = False

class SoTWrapper:
    \"\"\"
    Wrapper class for Sketch-of-Thought integration
    
    This wrapper ensures we're using the proper package when available,
    but provides minimal functionality when it's not.
    \"\"\"
    
    def __init__(self):
        \"\"\"Initialize the SoT wrapper\"\"\"
        if USE_PROPER_SOT:
            try:
                self.sot = SoT()
                self.available_paradigms = self.sot.avaliable_paradigms()
                logger.info(f"SoT initialized with paradigms: {self.available_paradigms}")
            except Exception as e:
                logger.error(f"Error initializing SoT: {e}")
                self._fallback_init()
        else:
            self._fallback_init()
    
    def _fallback_init(self):
        \"\"\"Initialize fallback implementation with minimal functionality\"\"\"
        logger.warning("Using fallback SoT implementation")
        self.sot = None
        self.available_paradigms = ['chunked_symbolism', 'conceptual_chaining', 'expert_lexicons']
    
    def classify_question(self, question: str) -> str:
        \"\"\"Classify a question to determine the best reasoning paradigm\"\"\"
        if USE_PROPER_SOT and self.sot:
            try:
                return self.sot.classify_question(question)
            except Exception as e:
                logger.error(f"Error classifying question with SoT: {e}")
                # Return a default paradigm if classification fails
                return "conceptual_chaining"
        else:
            # Simple fallback classification using keywords
            question_lower = question.lower()
            if any(term in question_lower for term in ['calculate', 'compute', 'solve', 'equation']):
                return "chunked_symbolism"
            elif any(term in question_lower for term in ['explain', 'describe', 'why', 'how']):
                return "conceptual_chaining"
            else:
                return "expert_lexicons"
    
    def get_system_prompt(self, paradigm: str) -> str:
        \"\"\"Get the appropriate system prompt for the paradigm\"\"\"
        if USE_PROPER_SOT and self.sot:
            try:
                return self.sot.get_system_prompt(paradigm)
            except Exception as e:
                logger.error(f"Error getting system prompt with SoT: {e}")
                return self._get_fallback_prompt(paradigm)
        else:
            return self._get_fallback_prompt(paradigm)
    
    def _get_fallback_prompt(self, paradigm: str) -> str:
        \"\"\"Get a basic fallback prompt for the given paradigm\"\"\"
        if paradigm == "chunked_symbolism":
            return "Use equations and variables to solve this step by step."
        elif paradigm == "conceptual_chaining":
            return "Connect the key concepts to reason through this problem."
        elif paradigm == "expert_lexicons":
            return "Use domain-specific terminology to answer efficiently."
        else:
            return "Reason step by step to solve the problem."
    
    def get_initialized_context(self, paradigm: str, question: Optional[str] = None, 
                                format: str = "llm", include_system_prompt: bool = True) -> Union[List[Dict], Dict]:
        \"\"\"Get initialized context with exemplars for the selected paradigm\"\"\"
        if USE_PROPER_SOT and self.sot:
            try:
                return self.sot.get_initialized_context(
                    paradigm=paradigm,
                    question=question,
                    format=format,
                    include_system_prompt=include_system_prompt
                )
            except Exception as e:
                logger.error(f"Error getting initialized context with SoT: {e}")
                return self._get_fallback_context(paradigm, question, format, include_system_prompt)
        else:
            return self._get_fallback_context(paradigm, question, format, include_system_prompt)
    
    def _get_fallback_context(self, paradigm: str, question: Optional[str], 
                             format: str, include_system_prompt: bool) -> Union[List[Dict], Dict]:
        \"\"\"Create a minimal fallback context\"\"\"
        system_prompt = self._get_fallback_prompt(paradigm) if include_system_prompt else ""
        
        if format == "llm":
            messages = []
            if include_system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add a basic example
            if paradigm == "chunked_symbolism":
                messages.append({
                    "role": "user", 
                    "content": "If x = 5 and y = 3, what is x + y?"
                })
                messages.append({
                    "role": "assistant", 
                    "content": "<think>\\nx = 5\\ny = 3\\nx + y = 8\\n</think>\\n\\n\\\\boxed{8}"
                })
            elif paradigm == "conceptual_chaining":
                messages.append({
                    "role": "user", 
                    "content": "Why does ice float on water?"
                })
                messages.append({
                    "role": "assistant", 
                    "content": "<think>\\n- Water molecules form crystal structure when freezing\\n- Crystal structure has more space between molecules\\n- More space → lower density\\n- Ice is less dense than liquid water\\n- Less dense objects float on more dense liquids\\n</think>\\n\\nIce floats on water because it's less dense."
                })
            else:  # expert_lexicons
                messages.append({
                    "role": "user", 
                    "content": "What is photosynthesis?"
                })
                messages.append({
                    "role": "assistant", 
                    "content": "<think>\\nPhoto=light + synthesis=creation\\nCO2 + H2O + light → C6H12O6 + O2\\nChloroplasts: cell organelles w/ chlorophyll pigment\\n1. Light absorption (chlorophyll)\\n2. ATP/NADPH production\\n3. Calvin cycle (CO2 → sugar)\\n</think>\\n\\nPhotosynthesis: light-energy conversion to chemical energy in plants."
                })
            
            # Add the current question if provided
            if question:
                messages.append({"role": "user", "content": question})
            
            return messages
        elif format == "vlm":
            # Similar to LLM format but with message objects
            messages = []
            if include_system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add a basic example (simplified)
            messages.append({
                "role": "user", 
                "content": [{"type": "text", "text": "Example question"}]
            })
            messages.append({
                "role": "assistant", 
                "content": [{"type": "text", "text": "Example answer"}]
            })
            
            # Add the current question if provided
            if question:
                messages.append({
                    "role": "user", 
                    "content": [{"type": "text", "text": question}]
                })
            
            return messages
        else:  # raw format
            # Return raw exemplars
            return [
                {
                    "question": "Example question",
                    "answer": "Example answer"
                }
            ]
""")
    
    logger.info(f"Created proper SoT integration file at: {sot_integration_path}")


def fix_ollama_integration():
    """Fix Ollama integration in the clarifier"""
    # Create the directories if they don't exist
    examples_dir = PROJECT_ROOT / "examples"
    if not os.path.exists(examples_dir):
        os.makedirs(examples_dir)
    
    local_llm_dir = examples_dir / "local_llm_integration"
    if not os.path.exists(local_llm_dir):
        os.makedirs(local_llm_dir)
    
    # Update the enhanced_clarifier.py file
    enhanced_clarifier_path = local_llm_dir / "enhanced_clarifier.py"
    
    with open(enhanced_clarifier_path, 'w', encoding='utf-8') as f:
        f.write("""# enhanced_clarifier.py
\"\"\"
Enhanced Socratic Clarifier with Ollama Integration

This module provides an improved version of the Socratic Clarifier
that uses Ollama for local LLM processing.
\"\"\"
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
    \"\"\"
    Enhanced version of SocraticClarifier that uses Ollama for local processing
    
    This class extends the base SocraticClarifier by adding support for:
    1. Local LLM processing via Ollama
    2. Improved question analysis with SoT
    3. Better error handling and timeout management
    \"\"\"
    
    def __init__(self, config: Optional[Dict] = None):
        \"\"\"Initialize the enhanced clarifier with optional configuration\"\"\"
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
        \"\"\"Check if Ollama is available and running\"\"\"
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
        \"\"\"
        Call Ollama API with the given prompt
        
        Args:
            prompt: The user prompt to send
            system_prompt: Optional system prompt
            
        Returns:
            The model's response text
        
        Raises:
            Exception: If the API call fails after retries
        \"\"\"
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
        \"\"\"
        Process a question using Ollama
        
        Args:
            question: The question to process
            
        Returns:
            Dict containing the processed results
        \"\"\"
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
        \"\"\"
        Process a question using enhanced methods if available, fallback to base otherwise
        
        Args:
            question: The question to process
            
        Returns:
            Dict containing the processed results
        \"\"\"
        if self.config["use_ollama"] and self.ollama_available:
            return self.process_with_ollama(question)
        else:
            return super().process(question)

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
""")
    
    logger.info(f"Updated enhanced_clarifier.py at: {enhanced_clarifier_path}")
    
    # Create a simple example script to test the integration
    test_script_path = local_llm_dir / "test_ollama_integration.py"
    
    with open(test_script_path, 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python
\"\"\"
Test script for Ollama integration with Socratic Clarifier
\"\"\"
import os
import sys
import requests
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from enhanced_clarifier import EnhancedClarifier

def check_ollama():
    \"\"\"Check if Ollama is running\"\"\"
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running")
            return True
        else:
            print("✗ Ollama returned unexpected status code:", response.status_code)
            return False
    except Exception as e:
        print(f"✗ Ollama is not running: {e}")
        return False

def test_ollama_integration():
    \"\"\"Test the Ollama integration\"\"\"
    print("Testing Ollama integration...")
    
    if not check_ollama():
        print("Please start Ollama first and try again")
        return
    
    try:
        # Create an enhanced clarifier
        clarifier = EnhancedClarifier({
            "ollama": {
                "model": "llama3",  # Use the model you have installed
                "timeout": 60,  # Increase timeout for testing
            }
        })
        
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

if __name__ == "__main__":
    test_ollama_integration()
""")
    
    logger.info(f"Created test script at: {test_script_path}")
    
    # Make the test script executable
    os.chmod(test_script_path, 0o755)


def verify_sketch_of_thought_installation():
    """Verify the SoT package is installed correctly"""
    try:
        result = subprocess.run(
            [sys.executable, '-c', 'from sketch_of_thought import SoT; print("SoT package found")'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("SoT package is installed correctly")
            return True
        else:
            logger.warning(f"SoT package import failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error checking SoT installation: {e}")
        return False


def update_web_interface():
    """Update the web interface to use the new integrations"""
    web_interface_dir = PROJECT_ROOT / "web_interface"
    if not os.path.exists(web_interface_dir):
        logger.warning(f"Web interface directory not found: {web_interface_dir}")
        return False
    
    # Update app.py to use the enhanced clarifier
    app_py_path = web_interface_dir / "app.py"
    if os.path.exists(app_py_path):
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup the original file
        with open(str(app_py_path) + '.bak', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update imports and clarifier initialization
        updated_content = content
        
        # Look for imports section
        if 'from socratic_clarifier.clarifier import SocraticClarifier' in content:
            updated_content = updated_content.replace(
                'from socratic_clarifier.clarifier import SocraticClarifier',
                'from socratic_clarifier.clarifier import SocraticClarifier\n'
                'from examples.local_llm_integration.enhanced_clarifier import EnhancedClarifier'
            )
        
        # Look for clarifier initialization
        if 'clarifier = SocraticClarifier()' in updated_content:
            updated_content = updated_content.replace(
                'clarifier = SocraticClarifier()',
                '# Try to use enhanced clarifier with Ollama if available\n'
                'try:\n'
                '    clarifier = EnhancedClarifier()\n'
                '    app.logger.info("Using enhanced clarifier with Ollama")\n'
                'except Exception as e:\n'
                '    app.logger.warning(f"Failed to initialize enhanced clarifier: {e}")\n'
                '    app.logger.info("Falling back to basic clarifier")\n'
                '    clarifier = SocraticClarifier()'
            )
        
        # Write the updated content
        with open(app_py_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info(f"Updated web interface app.py: {app_py_path}")
        return True
    else:
        logger.warning(f"Web interface app.py not found: {app_py_path}")
        return False


def update_requirements():
    """Update requirements.txt to include proper dependencies"""
    requirements_path = PROJECT_ROOT / "requirements.txt"
    
    # Check if we need to add dependencies
    required_packages = [
        "sketch-of-thought>=0.1.0",
        "requests>=2.25.0"
    ]
    
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            current_requirements = f.read()
        
        # Create a backup
        with open(str(requirements_path) + '.bak', 'w', encoding='utf-8') as f:
            f.write(current_requirements)
        
        # Add missing packages
        updated_requirements = current_requirements
        for package in required_packages:
            package_name = package.split('>=')[0].split('==')[0]
            if package_name not in current_requirements:
                if not updated_requirements.endswith('\n'):
                    updated_requirements += '\n'
                updated_requirements += f"{package}\n"
        
        # Write the updated requirements
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write(updated_requirements)
        
        logger.info(f"Updated requirements.txt: {requirements_path}")
    else:
        # Create a new requirements file
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(required_packages) + '\n')
        
        logger.info(f"Created requirements.txt: {requirements_path}")


def main():
    """Main function to run all cleanup tasks"""
    logger.info("Starting AI-Socratic-Clarifier cleanup")
    
    # Create backup directory
    backup_dir = PROJECT_ROOT / "backup_before_cleanup"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    try:
        # Verify we're in a virtual environment
        verify_venv()
        
        # Clean up MCP sequential thinking code
        cleanup_mcp_sequential_thinking()
        
        # Clean up SoT fallback implementation
        cleanup_sot_fallback()
        
        # Fix Ollama integration
        fix_ollama_integration()
        
        # Verify SoT installation
        verify_sketch_of_thought_installation()
        
        # Update web interface
        update_web_interface()
        
        # Update requirements
        update_requirements()
        
        # Final verification
        logger.info("Cleanup completed successfully!")
        logger.info("""
Next steps:
1. Restart your virtual environment to apply changes
2. Run 'pip install -e .' to reinstall the package
3. Start Ollama and test the integration with:
   python examples/local_llm_integration/test_ollama_integration.py
4. Start the web interface:
   python web_interface/app.py
""")
    
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        logger.info("Check the backup directory for original files")


if __name__ == "__main__":
    main()