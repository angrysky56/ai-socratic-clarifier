"""
Core module for the AI-Socratic-Clarifier system.
Provides the main SocraticClarifier class that coordinates the components.
"""

import os
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

# Import local SoT implementation directly
SOT_AVAILABLE = True
class SoT:
    """Local implementation of SoT functionality."""
    
    def __init__(self):
        pass
    
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
    
    def __init__(self, mode: str = "standard", use_sot: bool = True):
        """
        Initialize the SocraticClarifier.
        
        Args:
            mode: The operating mode (academic, legal, casual, etc.)
            use_sot: Whether to use Sketch-of-Thought integration
        """
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
        if use_sot and SOT_AVAILABLE:
            self.sot = SoT()
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
