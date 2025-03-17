"""
Core module for the AI-Socratic-Clarifier system.
Provides the main SocraticClarifier class that coordinates the components.
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional, Union, Tuple
from loguru import logger
from pydantic import BaseModel

# Import components
from socratic_clarifier.detectors.ambiguity import AmbiguityDetector
from socratic_clarifier.detectors.bias import BiasDetector
from socratic_clarifier.generators.question_generator import QuestionGenerator
try:
    from socratic_clarifier.generators.sot_reasoning_generator import SoTReasoningGenerator
    SOT_REASONING_AVAILABLE = True
except ImportError:
    from socratic_clarifier.fallback_reasoning import FallbackReasoningGenerator
    SOT_REASONING_AVAILABLE = False
from socratic_clarifier.modes.mode_manager import ModeManager

# Try to import SoT
def import_sot():
    """Try to import SoT and handle any import errors."""
    try:
        # First try to import our custom SoT integration
        from socratic_clarifier.integrations.sot_integration import SoTIntegration
        logger.info("Successfully imported SoT integration")
        return True, SoTIntegration
    except ImportError as e:
        logger.warning(f"Could not import SoT integration: {e}")
            
        # Finally, try to import the original Sketch-of-Thought package
        try:
            # Ensure module is not cached if previous import failed
            if "sketch_of_thought" in sys.modules:
                del sys.modules["sketch_of_thought"]
                
            from sketch_of_thought import SoT
            logger.info("Successfully imported Sketch-of-Thought package")
            return True, SoT
        except ImportError as e:
            logger.warning(f"Could not import Sketch-of-Thought: {e}")
            return False, None

# Try to import SoT
SOT_AVAILABLE, SoT_class = import_sot()

# Create a local fallback implementation if neither is available
if not SOT_AVAILABLE:
    
    class SoT:
        """Local implementation of SoT functionality when neither the package is available."""
        
        def __init__(self):
            logger.warning("Using fallback SoT implementation. For full functionality, ensure the SoT package is available.")
        
        def classify_question(self, text):
            """Classify question to determine reasoning paradigm."""
            # Simple heuristic-based classification as a fallback
            if any(word in text.lower() for word in ['math', 'calculate', 'compute', 'equation', 'number']):
                return "chunked_symbolism"
            elif any(word in text.lower() for word in ['technical', 'expert', 'medical', 'legal', 'specific']):
                return "expert_lexicons"
            else:
                return "conceptual_chaining"
        
        def avaliable_paradigms(self):
            """Return the available reasoning paradigms."""
            return ["conceptual_chaining", "chunked_symbolism", "expert_lexicons"]
        
        def get_initialized_context(self, paradigm, question=None, format="llm", include_system_prompt=True):
            """Placeholder for context initialization."""
            return []


class AnalysisResult(BaseModel):
    """Results of the text analysis and question generation."""
    text: str
    issues: List[Dict[str, Any]]
    questions: List[str]
    reasoning: Optional[str] = None
    sot_paradigm: Optional[str] = None
    confidence: float


def load_config():
    """Load configuration from config.json."""
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
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


class SocraticClarifier:
    """
    Main class that coordinates the detection, reasoning, and question generation.
    
    Attributes:
        mode (str): The operating mode (academic, legal, casual, etc.)
        detectors (dict): Dictionary of loaded detector modules
        question_generator (QuestionGenerator): The question generation module
        reasoning_generator (SoTReasoningGenerator): The reasoning generation module
        sot (Optional[SoT]): The Sketch-of-Thought module, if available
    """
    
    def __init__(self, mode: str = "standard", use_sot: bool = True, config: Dict[str, Any] = None):
        """
        Initialize the SocraticClarifier.
        
        Args:
            mode: The operating mode (academic, legal, casual, etc.)
            use_sot: Whether to use Sketch-of-Thought integration
            config: Optional configuration dictionary
        """
        # Load config if not provided
        if config is None:
            self.config = load_config()
        else:
            self.config = config
        
        # Use config settings if available
        if not use_sot and "settings" in self.config and "use_sot" in self.config["settings"]:
            use_sot = self.config["settings"]["use_sot"]
        
        self.mode_manager = ModeManager()
        self.mode = self.mode_manager.get_mode(mode)
        
        # Initialize detectors
        self.detectors = {
            "ambiguity": AmbiguityDetector(),
            "bias": BiasDetector(),
            # More detectors can be added here
        }
        
        # Initialize generators
        self.question_generator = QuestionGenerator()
        
        # Initialize the appropriate reasoning generator
        if SOT_REASONING_AVAILABLE:
            self.reasoning_generator = SoTReasoningGenerator()
            logger.info("Using SoT reasoning generator.")
        else:
            self.reasoning_generator = FallbackReasoningGenerator()
            logger.info("Using fallback reasoning generator.")
        
        # Initialize SoT if available and enabled
        self.sot = None
        self.sot_paradigm_override = None
        self.use_sot = use_sot
        if use_sot:
            # Check for SoT availability
            if not SOT_AVAILABLE:
                logger.warning("Sketch-of-Thought not available. Try running 'python install_sot.py' to install it.")
                logger.warning("Using fallback SoT implementation with limited functionality.")
                self.sot = SoT()
            else:
                # Use the imported SoT class
                self.sot = SoT_class()
            
            logger.info("Sketch-of-Thought integration activated.")
    
    def get_detector_issues(self, text: str) -> List[Dict[str, Any]]:
        """
        Run detectors on text and return discovered issues.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of detected issues
        """
        # Apply mode-specific settings
        threshold = self.mode.get("threshold", 0.7)
        
        # Detect issues
        issues = []
        for detector_name, detector in self.detectors.items():
            detector_issues = detector.detect(text, threshold=threshold)
            for issue in detector_issues:
                issue["type"] = detector_name
                issues.append(issue)
        
        return issues
    
    def analyze(self, text: str) -> AnalysisResult:
        """
        Analyze text for issues and generate Socratic questions.
        
        Args:
            text: The text to analyze
            
        Returns:
            AnalysisResult: Object containing detected issues, questions, and reasoning
        """
        # Detect issues using detectors
        issues = self.get_detector_issues(text)
        
        # If no issues detected, return empty result
        if not issues:
            return AnalysisResult(
                text=text,
                issues=[],
                questions=[],
                confidence=0.0
            )
        
        # Determine reasoning paradigm using SoT if available
        sot_paradigm = self.sot_paradigm_override  # Use override if set
        reasoning = None
        
        if self.sot and not sot_paradigm:
            # Use SoT to classify the question type
            try:
                sot_paradigm = self.sot.classify_question(text)
            except Exception as e:
                logger.error(f"Error classifying with SoT: {e}")
                sot_paradigm = "conceptual_chaining"  # Default fallback
        elif not sot_paradigm:
            # If SoT not available, use default paradigm
            sot_paradigm = "conceptual_chaining"
        
        # Generate reasoning based on the paradigm and issues
        if sot_paradigm:
            reasoning = self.reasoning_generator.generate(
                text=text,
                issues=issues,
                paradigm=sot_paradigm
            )
        
        # Generate questions based on detected issues
        questions = self.question_generator.generate(
            text=text,
            issues=issues,
            mode=self.mode,
            sot_paradigm=sot_paradigm
        )
        
        # Calculate overall confidence
        confidence = sum(issue.get("confidence", 0) for issue in issues) / len(issues)
        
        return AnalysisResult(
            text=text,
            issues=issues,
            questions=questions,
            reasoning=reasoning,
            sot_paradigm=sot_paradigm,
            confidence=confidence
        )
    
    def analyze_question(self, text: str) -> Dict:
        """Analyze a question and return the results as a dictionary."""
        analysis = self.analyze(text)
        return analysis.dict()
    
    def available_modes(self) -> List[str]:
        """Return a list of available operating modes."""
        return self.mode_manager.available_modes()
    
    def set_mode(self, mode: str) -> None:
        """
        Change the current operating mode.
        
        Args:
            mode: The new mode to set
        """
        self.mode = self.mode_manager.get_mode(mode)
        logger.info(f"Mode changed to: {mode}")
    
    def set_sot_paradigm(self, paradigm: Optional[str]) -> None:
        """
        Override the SoT paradigm selection.
        
        Args:
            paradigm: The paradigm to use, or None to use automatic selection
        """
        if paradigm and self.sot:
            available_paradigms = self.sot.avaliable_paradigms()
            if paradigm not in available_paradigms:
                raise ValueError(f"Invalid paradigm: {paradigm}. Available paradigms: {', '.join(available_paradigms)}")
        
        self.sot_paradigm_override = paradigm
        logger.info(f"SoT paradigm override set to: {paradigm}")
    
    def process(self, question: str) -> Dict:
        """Process a question and return comprehensive results."""
        analysis = self.analyze(question)
        
        return {
            "original_question": question,
            "analysis": analysis.dict(),
            "clarification": "Processed with base clarifier.",
            "socratic_questions": analysis.questions,
            "processed_with": "base"
        }
