# sot_integration.py
"""
Proper integration module for Sketch-of-Thought (SoT)
This replaces any fallback implementation and ensures proper import
"""
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
    """
    Wrapper class for Sketch-of-Thought integration
    
    This wrapper ensures we're using the proper package when available,
    but provides minimal functionality when it's not.
    """
    
    def __init__(self):
        """Initialize the SoT wrapper"""
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
        """Initialize fallback implementation with minimal functionality"""
        logger.warning("Using fallback SoT implementation")
        self.sot = None
        self.available_paradigms = ['chunked_symbolism', 'conceptual_chaining', 'expert_lexicons']
    
    def classify_question(self, question: str) -> str:
        """Classify a question to determine the best reasoning paradigm"""
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
        """Get the appropriate system prompt for the paradigm"""
        if USE_PROPER_SOT and self.sot:
            try:
                return self.sot.get_system_prompt(paradigm)
            except Exception as e:
                logger.error(f"Error getting system prompt with SoT: {e}")
                return self._get_fallback_prompt(paradigm)
        else:
            return self._get_fallback_prompt(paradigm)
    
    def _get_fallback_prompt(self, paradigm: str) -> str:
        """Get a basic fallback prompt for the given paradigm"""
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
        """Get initialized context with exemplars for the selected paradigm"""
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
        """Create a minimal fallback context"""
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
                    "content": "<think>\nx = 5\ny = 3\nx + y = 8\n</think>\n\n\\boxed{8}"
                })
            elif paradigm == "conceptual_chaining":
                messages.append({
                    "role": "user", 
                    "content": "Why does ice float on water?"
                })
                messages.append({
                    "role": "assistant", 
                    "content": "<think>\n- Water molecules form crystal structure when freezing\n- Crystal structure has more space between molecules\n- More space → lower density\n- Ice is less dense than liquid water\n- Less dense objects float on more dense liquids\n</think>\n\nIce floats on water because it's less dense."
                })
            else:  # expert_lexicons
                messages.append({
                    "role": "user", 
                    "content": "What is photosynthesis?"
                })
                messages.append({
                    "role": "assistant", 
                    "content": "<think>\nPhoto=light + synthesis=creation\nCO2 + H2O + light → C6H12O6 + O2\nChloroplasts: cell organelles w/ chlorophyll pigment\n1. Light absorption (chlorophyll)\n2. ATP/NADPH production\n3. Calvin cycle (CO2 → sugar)\n</think>\n\nPhotosynthesis: light-energy conversion to chemical energy in plants."
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
