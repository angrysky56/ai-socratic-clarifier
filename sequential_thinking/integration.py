"""
Integration module for the Reflective Ecosystem with the Socratic Clarifier.

This module provides an easy way to integrate the reflective ecosystem into 
the existing Socratic Clarifier workflow.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional

# Add parent directory to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import reflective ecosystem
from sequential_thinking.reflective_ecosystem import ReflectiveEcosystem, load_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReflectiveEnhancer:
    """
    Integration class that enhances the Socratic Clarifier with reflective ecosystem capabilities.
    """
    
    def __init__(self):
        """Initialize the reflective enhancer."""
        self.ecosystem = ReflectiveEcosystem()
        self.initialized = True
        
        # Try to load existing state
        if not self.ecosystem.load_state():
            logger.info("No existing ecosystem state found. Starting with default settings.")
        
        # Load configuration
        self.config = load_config()
    
    def enhance_questions(self, 
                         text: str, 
                         issues: List[Dict[str, Any]], 
                         original_questions: List[str],
                         sot_paradigm: Optional[str] = None,
                         max_questions: int = 5) -> List[str]:
        """
        Enhance a set of questions using the reflective ecosystem.
        
        Args:
            text: The original text being analyzed
            issues: The detected issues
            original_questions: The original questions generated
            sot_paradigm: The SoT paradigm if available
            max_questions: Maximum number of questions
            
        Returns:
            Enhanced list of questions
        """
        # First, check if we have enough original questions
        if len(original_questions) >= max_questions:
            # Keep track of these questions in our ecosystem
            for q in original_questions:
                # Just track the questions - no feedback yet
                self.ecosystem.question_history.append({
                    "question": q,
                    "helpful": None,
                    "paradigm": sot_paradigm
                })
            return original_questions[:max_questions]
        
        # Generate additional questions with the ecosystem
        eco_paradigm = sot_paradigm if sot_paradigm else self.ecosystem.select_paradigm(text)
        
        # First, try to use Ollama if available
        if self.ecosystem.ollama.available:
            need_count = max_questions - len(original_questions)
            
            logger.info(f"Generating {need_count} additional questions with Ollama")
            ollama_questions = self.ecosystem.ollama.generate_questions(
                text=text,
                issues=issues,
                paradigm=eco_paradigm,
                max_questions=need_count
            )
            
            if ollama_questions:
                logger.info(f"Generated {len(ollama_questions)} questions with Ollama")
                # Combine with original questions
                combined_questions = original_questions + [
                    q for q in ollama_questions if q not in original_questions
                ]
                return combined_questions[:max_questions]
        
        # Fallback to template-based generation
        eco_questions = self.ecosystem.generate_questions(
            text=text,
            issues=issues,
            selected_paradigm=eco_paradigm,
            max_questions=max_questions - len(original_questions)
        )
        
        # Combine original questions with ecosystem questions
        enhanced_questions = original_questions + [
            q for q in eco_questions if q not in original_questions
        ]
        
        # Limit to max_questions
        return enhanced_questions[:max_questions]
    
    def process_feedback(self, question: str, helpful: bool, paradigm: Optional[str] = None):
        """
        Process feedback on a question.
        
        Args:
            question: The question that received feedback
            helpful: Whether the question was helpful
            paradigm: Optional paradigm that generated the question
        """
        self.ecosystem.process_feedback(question, helpful, paradigm)
        
        # Periodically save state
        if len(self.ecosystem.question_history) % 10 == 0:
            self.ecosystem.save_state()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get a performance report for the ecosystem.
        
        Returns:
            Dictionary with performance metrics
        """
        report = self.ecosystem.get_performance_report()
        return report
    
    def reset(self):
        """Reset the ecosystem to initial state."""
        self.ecosystem = ReflectiveEcosystem()
        self.initialized = True
        logger.info("Reflective enhancer reset to initial state.")

# Create a singleton instance
_enhancer = None

def get_enhancer() -> ReflectiveEnhancer:
    """
    Get the singleton ReflectiveEnhancer instance.
    
    Returns:
        ReflectiveEnhancer instance
    """
    global _enhancer
    if _enhancer is None:
        _enhancer = ReflectiveEnhancer()
    return _enhancer
