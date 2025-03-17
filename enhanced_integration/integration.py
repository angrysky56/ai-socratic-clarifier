"""
Integration module for the Enhanced Reflective Ecosystem with the Socratic Clarifier.

This module provides a drop-in replacement for the existing integration module
while adding enhanced capabilities.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional

# Add parent directory to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import enhanced reflective ecosystem
from enhanced_integration.enhanced_reflective_ecosystem import EnhancedReflectiveEcosystem, get_enhanced_ecosystem

# Import original integration for compatibility
from sequential_thinking.integration import ReflectiveEnhancer as OriginalEnhancer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedReflectiveEnhancer(OriginalEnhancer):
    """
    Enhanced integration class that extends the original ReflectiveEnhancer
    with additional capabilities from EnhancedReflectiveEcosystem.
    """
    
    def __init__(self):
        """Initialize the enhanced reflective enhancer."""
        # Skip calling parent's __init__ to avoid creating a standard ecosystem
        self.ecosystem = get_enhanced_ecosystem()
        self.initialized = True
        
        # Try to load existing state
        if not self.ecosystem.load_state():
            logger.info("No existing ecosystem state found. Starting with default settings.")
        
        # Load configuration (as in original enhancer)
        self.config = self.ecosystem.config if hasattr(self.ecosystem, 'config') else {}
        
        logger.info("Enhanced Reflective Enhancer initialized")
    
    def enhance_questions(self, 
                         text: str, 
                         issues: List[Dict[str, Any]], 
                         original_questions: List[str],
                         sot_paradigm: Optional[str] = None,
                         max_questions: int = 5) -> List[str]:
        """
        Enhance a set of questions using the enhanced reflective ecosystem.
        
        Args:
            text: The original text being analyzed
            issues: The detected issues
            original_questions: The original questions generated
            sot_paradigm: The SoT paradigm if available
            max_questions: Maximum number of questions
            
        Returns:
            Enhanced list of questions
        """
        # Using the enhanced ecosystem's method
        return self.ecosystem.enhance_questions(
            text=text,
            issues=issues,
            original_questions=original_questions,
            sot_paradigm=sot_paradigm,
            max_questions=max_questions
        )
    
    def get_reasoning_context(self, 
                            text: str, 
                            issues: List[Dict[str, Any]],
                            paradigm: Optional[str] = None) -> Dict[str, Any]:
        """
        Get enhanced reasoning context for visualization and explanation.
        
        Args:
            text: The text being analyzed
            issues: The detected issues
            paradigm: Optional specific paradigm to use
            
        Returns:
            Dictionary with reasoning context
        """
        # Select paradigm if not provided
        if not paradigm:
            paradigm = self.ecosystem.select_paradigm(text)
        
        # Apply enhancements to get rich reasoning context
        context = self.ecosystem.apply_enhancement(text, issues, paradigm)
        
        # Add advancement metrics from IntelliSynth
        context["advancement"] = {
            "truth_value": self.ecosystem.intellisynth["truth_value"],
            "scrutiny_value": self.ecosystem.intellisynth["scrutiny_value"],
            "improvement_value": self.ecosystem.intellisynth["improvement_value"],
            "advancement": self.ecosystem.intellisynth["advancement"]
        }
        
        # Add Meta-Meta Framework information
        context["meta_meta_stage"] = self._determine_meta_meta_stage(text, issues)
        
        return context
    
    def _determine_meta_meta_stage(self, text: str, issues: List[Dict[str, Any]]) -> str:
        """Determine the current stage in the Meta-Meta Framework."""
        # Simplified determination based on issues
        if not issues:
            return "stageWhy"  # Start with Why if no issues
        
        issue_count = len(issues)
        if issue_count == 1:
            return "stageWhat"  # Identifying dimensions with 1 issue
        elif issue_count <= 3:
            return "stageHow"   # Designing frameworks with 2-3 issues
        elif issue_count <= 5:
            return "stageWhatIf"  # Leveraging constraints with 4-5 issues
        elif issue_count <= 7:
            return "stageHowElse"  # Controlled emergence with 6-7 issues
        elif issue_count <= 9:
            return "stageWhatNext"  # Feedback loops with 8-9 issues
        else:
            return "stageWhatNow"  # Adaptive flexibility with 10+ issues
    
    def process_feedback(self, question: str, helpful: bool, paradigm: Optional[str] = None):
        """
        Process enhanced feedback on a question.
        
        Args:
            question: The question that received feedback
            helpful: Whether the question was helpful
            paradigm: Optional paradigm that generated the question
        """
        # Use the enhanced ecosystem's method
        self.ecosystem.process_feedback(question, helpful, paradigm)
        
        # Periodically save state (as in original enhancer)
        if len(self.ecosystem.question_history) % 10 == 0:
            self.ecosystem.save_state()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get an enhanced performance report for the ecosystem.
        
        Returns:
            Dictionary with enhanced performance metrics
        """
        # Using the enhanced ecosystem's method
        return self.ecosystem.get_performance_report()
    
    def reset(self):
        """Reset the ecosystem to initial state."""
        self.ecosystem = EnhancedReflectiveEcosystem()
        self.initialized = True
        logger.info("Enhanced Reflective Enhancer reset to initial state.")

# Create a singleton instance
_enhanced_enhancer = None

def get_enhanced_enhancer() -> EnhancedReflectiveEnhancer:
    """
    Get the singleton EnhancedReflectiveEnhancer instance.
    
    Returns:
        EnhancedReflectiveEnhancer instance
    """
    global _enhanced_enhancer
    if _enhanced_enhancer is None:
        _enhanced_enhancer = EnhancedReflectiveEnhancer()
    return _enhanced_enhancer
