"""
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
4. Present your final answer clearly using \boxed{answer} notation

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
            example_a = "<think>\nx = 5\ny = 3\nx + y = 8\n</think>\n\n\\boxed{8}"
        elif paradigm == 'conceptual_chaining':
            example_q = "Why does ice float on water?"
            example_a = "<think>\n- Water molecules form crystal structure when freezing\n- Crystal structure has more space between molecules\n- More space → lower density\n- Ice is less dense than liquid water\n- Less dense objects float on more dense liquids\n</think>\n\nIce floats on water because it's less dense."
        else:  # expert_lexicons
            example_q = "Explain photosynthesis briefly."
            example_a = "<think>\nPhotosynthesis: Light → Chemical Energy\nReactants: CO₂ + H₂O + photons\nProducts: C₆H₁₂O₆ + O₂\nLocation: Chloroplasts\nKey processes: Light-dependent rxns + Calvin cycle\n</think>\n\nPhotosynthesis: conversion of light energy to chemical energy in plants via CO₂ + H₂O + light → glucose + O₂."
        
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
