"""
Enhanced Reflective Ecosystem Module for AI-Socratic-Clarifier

This module extends the existing ReflectiveEcosystem with:
1. Meta-Meta Framework integration
2. IntelliSynth framework components
3. AI_Reasoner integration

It preserves all existing functionality while adding enhanced capabilities.
"""

import os
import json
import logging
import time
import numpy as np
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import sys

# Add parent directory to path to import original ReflectiveEcosystem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sequential_thinking.reflective_ecosystem import ReflectiveEcosystem, ReasoningNode, load_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedReflectiveEcosystem(ReflectiveEcosystem):
    """
    Enhanced version of the ReflectiveEcosystem that integrates:
    - Meta-Meta Framework
    - IntelliSynth framework components
    - AI_Reasoner capabilities
    
    This preserves all original functionality while adding new features.
    """
    
    def __init__(self):
        """Initialize the enhanced reflective ecosystem."""
        # Initialize the parent class
        super().__init__()
        
        # Meta-Meta Framework components
        self.meta_meta_components = {
            "principle_of_inquiry": "Improve critical thinking through effective Socratic questioning",  # Core "why" question
            "dimensional_axes": {
                "reasoning_approach": {
                    "description": "Reasoning approach to use",
                    "values": ["conceptual_chaining", "chunked_symbolism", "expert_lexicons", "socratic_questioning"]
                },
                "question_focus": {
                    "description": "Focus area for generated questions",
                    "values": ["definitions", "evidence", "assumptions", "implications", "alternatives"]
                },
                "complexity_level": {
                    "description": "Complexity level of exploration",
                    "values": ["simple", "moderate", "complex"]
                }
            },
            "recursive_frameworks": [],    # Nested frameworks
            "constraints": [
                {"constraint": "Questions must be genuinely helpful", "purpose": "Ensure practical value"},
                {"constraint": "Questions must address specific issues", "purpose": "Maintain relevance"},
                {"constraint": "Questions should be open-ended", "purpose": "Encourage deeper thinking"}
            ],
            "controlled_emergence": 0.3,   # Level of emergence (0.0-1.0)
            "feedback_loops": [],          # Active feedback mechanisms
            "adaptive_flexibility": 0.5    # Adaptation level (0.0-1.0)
        }
        
        # IntelliSynth components
        self.intellisynth = {
            "truth_value": 0.7,            # Base truth assessment
            "scrutiny_value": 0.0,         # Initial scrutiny level
            "improvement_value": 0.0,      # Initial improvement level
            "advancement": 0.0,            # Overall advancement metric
            "alpha": 0.5,                  # Scrutiny weight
            "beta": 0.5                    # Improvement weight
        }
        
        # AI_Reasoner components
        self.reasoner_capabilities = {
            "data_analysis": True,
            "hypothesis_generation": True,
            "probabilistic_reasoning": True,
            "hypothesis_testing": False,  # Requires additional implementation
            "continuous_learning": True,
            "explainability": True,
            "uncertainty_management": True,
            "contextual_awareness": True
        }
        
        # Enhanced capabilities
        self.enhanced_capabilities = {
            "consequences": True,
            "imagination": True,
            "creativity": True,
            "logic": True,
            "visualization": True,
            "eloquence": True,
            "elucidation": True
        }
        
        # Initialize feedback loops from Meta-Meta Framework
        self._initialize_feedback_loops()
        
        # Calculate initial advancement value
        self.calculate_advancement()
        
        logger.info("Enhanced Reflective Ecosystem initialized")
    
    def _initialize_feedback_loops(self):
        """Initialize feedback loops for the Meta-Meta Framework."""
        self.meta_meta_components["feedback_loops"] = [
            {
                "name": "Question effectiveness",
                "metric": "user_feedback",
                "current_value": 0.0,
                "target_value": 0.8,
                "update_function": lambda current, new: current * 0.8 + new * 0.2  # Exponential moving average
            },
            {
                "name": "Reasoning coherence",
                "metric": "global_coherence",
                "current_value": self.global_coherence,
                "target_value": 0.9,
                "update_function": lambda current, new: current * 0.9 + new * 0.1  # Slower moving average
            },
            {
                "name": "Paradigm selection accuracy",
                "metric": "paradigm_accuracy",
                "current_value": 0.5,
                "target_value": 0.85,
                "update_function": lambda current, new: current * 0.7 + new * 0.3  # Moderate moving average
            }
        ]
    
    def set_principle_of_inquiry(self, principle: str):
        """
        Set the core principle that guides the reflection process.
        
        Args:
            principle: The core "why" that drives the process
        """
        self.meta_meta_components["principle_of_inquiry"] = principle
        logger.info(f"Principle of inquiry set to: {principle}")
    
    def add_dimensional_axis(self, name: str, description: str, values: List[str]):
        """
        Add a dimensional axis for exploration.
        
        Args:
            name: Name of the axis
            description: Description of what this dimension represents
            values: Possible values along this dimension
        """
        self.meta_meta_components["dimensional_axes"][name] = {
            "description": description,
            "values": values
        }
        logger.info(f"Added dimensional axis: {name}")
    
    def add_constraint(self, constraint: str, purpose: str):
        """
        Add a useful constraint to focus exploration.
        
        Args:
            constraint: The constraint to add
            purpose: Why this constraint is useful
        """
        self.meta_meta_components["constraints"].append({
            "constraint": constraint,
            "purpose": purpose
        })
        logger.info(f"Added constraint: {constraint}")
    
    def calculate_advancement(self):
        """
        Calculate the overall advancement value using IntelliSynth formula.
        
        Returns:
            The calculated advancement value
        """
        alpha = self.intellisynth["alpha"]
        beta = self.intellisynth["beta"]
        
        # Update scrutiny value based on question history
        if len(self.question_history) > 0:
            # Count questions that received feedback
            rated_questions = sum(1 for q in self.question_history if q.get("helpful") is not None)
            if rated_questions > 0:
                # Calculate scrutiny as proportion of questions with feedback
                self.intellisynth["scrutiny_value"] = rated_questions / len(self.question_history)
        
        # Update improvement value based on positive feedback
        positive_feedback = sum(1 for q in self.question_history 
                              if q.get("helpful") is True)
        if len(self.question_history) > 0:
            self.intellisynth["improvement_value"] = positive_feedback / len(self.question_history)
        
        # Calculate advancement using formula: truth + alpha*scrutiny + beta*improvement
        advancement = (
            self.intellisynth["truth_value"] + 
            alpha * self.intellisynth["scrutiny_value"] + 
            beta * self.intellisynth["improvement_value"]
        )
        
        # Update the stored advancement value
        self.intellisynth["advancement"] = advancement
        
        logger.debug(f"Calculated advancement: {advancement}")
        return advancement
    
    def generate_hypothesis(self, text: str, issues: List[Dict[str, Any]]) -> str:
        """
        Generate a hypothesis about the text using AI_Reasoner capabilities.
        
        Args:
            text: The text to analyze
            issues: Detected issues in the text
            
        Returns:
            A generated hypothesis
        """
        if not self.reasoner_capabilities["hypothesis_generation"]:
            return ""
            
        # Simple hypothesis generation based on identified issues
        if not issues:
            return "The text appears to be logically sound with no obvious issues."
            
        # Use most significant issue (highest confidence) for hypothesis
        issues_sorted = sorted(issues, key=lambda x: x.get("confidence", 0), reverse=True)
        primary_issue = issues_sorted[0]
        
        issue_type = primary_issue.get("issue", "unknown").lower()
        term = primary_issue.get("term", "")
        
        if "absolute" in issue_type:
            return f"The use of absolute terms like '{term}' may indicate overgeneralization."
        elif "vague" in issue_type:
            return f"The term '{term}' lacks precise definition, reducing clarity."
        elif "norm" in issue_type:
            return f"The claim involving '{term}' makes a value judgment without qualification."
        elif "evidence" in issue_type or "support" in issue_type:
            return f"The assertion about '{term}' lacks sufficient supporting evidence."
        else:
            return f"The statement contains potential issues, particularly around the term '{term}'."
    
    def apply_enhancement(self, text: str, issues: List[Dict[str, Any]], paradigm: str) -> Dict[str, Any]:
        """
        Apply all enhancement capabilities to generate rich reasoning context.
        
        Args:
            text: The text to analyze
            issues: Detected issues
            paradigm: Selected reasoning paradigm
            
        Returns:
            Enhanced context with reasoning elements
        """
        # Generate a hypothesis
        hypothesis = self.generate_hypothesis(text, issues)
        
        # Calculate probabilities for issues (probabilistic reasoning)
        issue_probabilities = []
        for issue in issues:
            confidence = issue.get("confidence", 0.5)
            issue_probabilities.append({
                "issue": issue.get("issue", "unknown"),
                "term": issue.get("term", ""),
                "probability": confidence,
                "impact": self._calculate_impact(issue, text)
            })
        
        # Generate alternative perspectives (imagination capability)
        alternative_perspectives = []
        if self.enhanced_capabilities["imagination"]:
            for issue in issues[:2]:  # Limit to top 2 issues
                term = issue.get("term", "")
                issue_type = issue.get("issue", "").lower()
                
                if "absolute" in issue_type:
                    alternative_perspectives.append({
                        "perspective": f"What if '{term}' applied only in specific circumstances?",
                        "relevance": issue.get("confidence", 0.5)
                    })
                elif "vague" in issue_type:
                    alternative_perspectives.append({
                        "perspective": f"What if '{term}' were defined more precisely?",
                        "relevance": issue.get("confidence", 0.5)
                    })
                elif "norm" in issue_type:
                    alternative_perspectives.append({
                        "perspective": f"What if the value judgment behind '{term}' were made explicit?",
                        "relevance": issue.get("confidence", 0.5)
                    })
                else:
                    alternative_perspectives.append({
                        "perspective": f"What if '{term}' were interpreted differently?",
                        "relevance": issue.get("confidence", 0.5)
                    })
        
        # Create reasoning paths based on paradigm
        reasoning_paths = self._generate_reasoning_paths(text, issues, paradigm)
        
        # Return enhanced context
        return {
            "hypothesis": hypothesis,
            "issue_probabilities": issue_probabilities,
            "alternative_perspectives": alternative_perspectives,
            "reasoning_paths": reasoning_paths,
            "confidence": sum(issue.get("confidence", 0.5) for issue in issues) / max(1, len(issues))
        }
    
    def _calculate_impact(self, issue: Dict[str, Any], text: str) -> float:
        """Calculate potential impact of an issue."""
        # Simple impact calculation based on issue type and confidence
        confidence = issue.get("confidence", 0.5)
        issue_type = issue.get("issue", "").lower()
        
        # Adjust based on issue type
        multiplier = 1.0
        if "absolute" in issue_type:
            multiplier = 1.2
        elif "vague" in issue_type:
            multiplier = 1.0
        elif "norm" in issue_type:
            multiplier = 1.3
        elif "evidence" in issue_type:
            multiplier = 1.4
        
        # Calculate impact score (0.0-1.0)
        impact = min(1.0, confidence * multiplier)
        return impact
    
    def _generate_reasoning_paths(self, text: str, issues: List[Dict[str, Any]], paradigm: str) -> List[Dict[str, Any]]:
        """Generate reasoning paths based on paradigm."""
        paths = []
        
        if paradigm == "conceptual_chaining":
            # Create conceptual chain for each issue
            for issue in issues:
                term = issue.get("term", "")
                steps = [
                    f"Identify the concept '{term}'",
                    f"Analyze how '{term}' connects to other concepts",
                    f"Examine logical relationships",
                    "Identify potential disconnects or weaknesses",
                    "Suggest clarifications or improvements"
                ]
                paths.append({
                    "name": f"Conceptual chain for '{term}'",
                    "steps": steps
                })
                
        elif paradigm == "chunked_symbolism":
            # Create symbolic representation for each issue
            for issue in issues:
                term = issue.get("term", "")
                steps = [
                    f"Define variable(s) for '{term}'",
                    "Identify measurement criteria",
                    "Establish relationships between variables",
                    "Analyze boundary conditions",
                    "Formulate precise definition"
                ]
                paths.append({
                    "name": f"Symbolic representation of '{term}'",
                    "steps": steps
                })
                
        elif paradigm == "expert_lexicons":
            # Create domain analysis for each issue
            for issue in issues:
                term = issue.get("term", "")
                steps = [
                    f"Identify domain context for '{term}'",
                    "Apply specialized terminology",
                    "Reference field-specific standards",
                    "Compare against established definitions",
                    "Suggest domain-appropriate refinements"
                ]
                paths.append({
                    "name": f"Domain analysis of '{term}'",
                    "steps": steps
                })
                
        else:  # Default Socratic questioning
            # Create question sequence for each issue
            for issue in issues:
                term = issue.get("term", "")
                steps = [
                    f"What is meant by '{term}'?",
                    f"What evidence supports claims about '{term}'?",
                    f"What alternatives to '{term}' exist?",
                    f"What assumptions underlie '{term}'?",
                    f"What implications follow from '{term}'?"
                ]
                paths.append({
                    "name": f"Socratic inquiry about '{term}'",
                    "steps": steps
                })
        
        return paths
    
    def enhance_questions(self, 
                        text: str, 
                        issues: List[Dict[str, Any]], 
                        original_questions: List[str],
                        sot_paradigm: Optional[str] = None,
                        max_questions: int = 5) -> List[str]:
        """
        Enhanced version of the question generation that incorporates
        Meta-Meta Framework and IntelliSynth components.
        
        Args:
            text: The original text being analyzed
            issues: The detected issues
            original_questions: The original questions generated
            sot_paradigm: The SoT paradigm if available
            max_questions: Maximum number of questions
            
        Returns:
            Enhanced list of questions
        """
        # First use the original method to get base questions
        questions = super().enhance_questions(
            text=text,
            issues=issues,
            original_questions=original_questions,
            sot_paradigm=sot_paradigm,
            max_questions=max_questions
        )
        
        # Apply Meta-Meta Framework to refine questions
        if questions and self.meta_meta_components["dimensional_axes"]:
            # Get the focus area for questions
            focus_values = self.meta_meta_components["dimensional_axes"].get("question_focus", {}).get("values", [])
            
            if focus_values:
                # Choose a focus based on issues
                focus = "definitions"  # Default
                if issues:
                    issue_type = issues[0].get("issue", "").lower()
                    if "absolute" in issue_type:
                        focus = "alternatives"
                    elif "vague" in issue_type:
                        focus = "definitions"
                    elif "evidence" in issue_type:
                        focus = "evidence"
                    elif "norm" in issue_type:
                        focus = "assumptions"
                
                # Adjust one question to better match the focus
                if len(questions) > 1:
                    # Select a question to modify
                    modify_index = min(1, len(questions) - 1)  # Modify the second question if possible
                    original = questions[modify_index]
                    
                    if focus == "definitions" and "mean by" not in original.lower():
                        term = issues[0].get("term", "") if issues else ""
                        questions[modify_index] = f"What exactly do you mean by '{term}'?"
                    elif focus == "evidence" and "evidence" not in original.lower():
                        questions[modify_index] = f"What evidence supports this assertion?"
                    elif focus == "assumptions" and "assum" not in original.lower():
                        questions[modify_index] = f"What assumptions underlie this perspective?"
                    elif focus == "alternatives" and "alternative" not in original.lower():
                        questions[modify_index] = f"What alternative viewpoints exist?"
        
        # Update advancement values
        self.calculate_advancement()
        
        return questions
    
    def process_feedback(self, question: str, helpful: bool, paradigm: Optional[str] = None):
        """
        Enhanced feedback processing that updates Meta-Meta Framework
        and IntelliSynth components.
        
        Args:
            question: The question that received feedback
            helpful: Whether the question was helpful
            paradigm: Optional paradigm that generated the question
        """
        # Use the original method first
        super().process_feedback(question, helpful, paradigm)
        
        # Update Meta-Meta Framework feedback loops
        feedback_value = 1.0 if helpful else 0.0
        
        for loop in self.meta_meta_components["feedback_loops"]:
            if loop["name"] == "Question effectiveness":
                loop["current_value"] = loop["update_function"](
                    loop["current_value"], 
                    feedback_value
                )
            elif loop["name"] == "Paradigm selection accuracy" and paradigm:
                # If the paradigm has node and feedback was positive, it was likely a good selection
                if paradigm in self.nodes and helpful:
                    accuracy = 1.0
                elif paradigm in self.nodes and not helpful:
                    accuracy = 0.0
                else:
                    accuracy = 0.5  # Unknown paradigm, neutral score
                    
                loop["current_value"] = loop["update_function"](
                    loop["current_value"], 
                    accuracy
                )
        
        # Update the global coherence
        self.global_coherence = self.meta_meta_components["feedback_loops"][1]["current_value"]
        
        # Update IntelliSynth values
        self.calculate_advancement()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Enhanced performance report that includes Meta-Meta Framework
        and IntelliSynth metrics.
        
        Returns:
            Dictionary with enhanced performance metrics
        """
        # Get base report
        report = super().get_performance_report()
        
        # Add Meta-Meta Framework metrics
        report["meta_meta_framework"] = {
            "principle_of_inquiry": self.meta_meta_components["principle_of_inquiry"],
            "dimensional_axes": list(self.meta_meta_components["dimensional_axes"].keys()),
            "constraints": len(self.meta_meta_components["constraints"]),
            "controlled_emergence": self.meta_meta_components["controlled_emergence"],
            "feedback_loops": [
                {
                    "name": loop["name"],
                    "current_value": loop["current_value"],
                    "target_value": loop["target_value"]
                }
                for loop in self.meta_meta_components["feedback_loops"]
            ],
            "adaptive_flexibility": self.meta_meta_components["adaptive_flexibility"]
        }
        
        # Add IntelliSynth metrics
        report["intellisynth"] = {
            "truth_value": self.intellisynth["truth_value"],
            "scrutiny_value": self.intellisynth["scrutiny_value"],
            "improvement_value": self.intellisynth["improvement_value"],
            "advancement": self.intellisynth["advancement"],
            "alpha": self.intellisynth["alpha"],
            "beta": self.intellisynth["beta"]
        }
        
        # Add AI_Reasoner capabilities
        report["ai_reasoner"] = {
            "capabilities": self.reasoner_capabilities,
            "enhanced_capabilities": self.enhanced_capabilities
        }
        
        return report
    
    def save_state(self, file_path: Optional[str] = None):
        """
        Enhanced state saving that includes Meta-Meta Framework
        and IntelliSynth components.
        
        Args:
            file_path: Optional file path to save the state
        """
        # Use the original method first
        result = super().save_state(file_path)
        
        if not file_path:
            file_path = os.path.join(os.path.dirname(__file__), 'ecosystem_state.json')
        
        # Load the state to enhance it
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)
            
            # Add enhanced components
            state["meta_meta_framework"] = self.meta_meta_components
            state["intellisynth"] = self.intellisynth
            state["ai_reasoner"] = {
                "capabilities": self.reasoner_capabilities,
                "enhanced_capabilities": self.enhanced_capabilities
            }
            
            # Save the enhanced state
            with open(file_path, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"Enhanced ecosystem state saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving enhanced ecosystem state: {e}")
            return result  # Return original result if enhanced saving fails
    
    def load_state(self, file_path: Optional[str] = None):
        """
        Enhanced state loading that includes Meta-Meta Framework
        and IntelliSynth components.
        
        Args:
            file_path: Optional file path to load the state from
            
        Returns:
            Whether the state was successfully loaded
        """
        # Use the original method first
        result = super().load_state(file_path)
        
        if not file_path:
            file_path = os.path.join(os.path.dirname(__file__), 'ecosystem_state.json')
        
        if not os.path.exists(file_path):
            return result
        
        # Load enhanced components
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)
            
            # Load Meta-Meta Framework components if present
            if "meta_meta_framework" in state:
                self.meta_meta_components = state["meta_meta_framework"]
            
            # Load IntelliSynth components if present
            if "intellisynth" in state:
                self.intellisynth = state["intellisynth"]
            
            # Load AI_Reasoner components if present
            if "ai_reasoner" in state:
                if "capabilities" in state["ai_reasoner"]:
                    self.reasoner_capabilities = state["ai_reasoner"]["capabilities"]
                if "enhanced_capabilities" in state["ai_reasoner"]:
                    self.enhanced_capabilities = state["ai_reasoner"]["enhanced_capabilities"]
            
            logger.info(f"Enhanced ecosystem state loaded from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading enhanced ecosystem state: {e}")
            return result  # Return original result if enhanced loading fails

# Create a singleton instance
_enhanced_ecosystem = None

def get_enhanced_ecosystem() -> EnhancedReflectiveEcosystem:
    """
    Get the singleton EnhancedReflectiveEcosystem instance.
    
    Returns:
        EnhancedReflectiveEcosystem instance
    """
    global _enhanced_ecosystem
    if _enhanced_ecosystem is None:
        _enhanced_ecosystem = EnhancedReflectiveEcosystem()
    return _enhanced_ecosystem
