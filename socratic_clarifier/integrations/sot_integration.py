"""
Integration module for Sketch-of-Thought (SoT) reasoning.

This module provides direct integration with the SoT model for reasoning
paradigm classification and structured reasoning.
"""

import os
import sys
import json
import copy
from typing import List, Dict, Any, Optional
from loguru import logger
import torch

# Try importing the required dependencies
try:
    from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers library not available. SoT functionality will be limited.")
    TRANSFORMERS_AVAILABLE = False


class SoTIntegration:
    """
    Integration class for Sketch-of-Thought reasoning.
    
    This class provides methods for using the SoT model for reasoning
    paradigm classification and structured reasoning.
    """
    
    def __init__(self):
        """Initialize the SoT integration."""
        self.available = False
        self.model = None
        self.tokenizer = None
        self.label_mapping = None
        self.label_mapping_reverse = None
        self.paradigms = ["conceptual_chaining", "chunked_symbolism", "expert_lexicons"]
        self.prompts = {}
        self.contexts = {}
        
        # Try to initialize the model
        if TRANSFORMERS_AVAILABLE:
            try:
                self._initialize_model()
                self.available = True
            except Exception as e:
                logger.error(f"Error initializing SoT model: {e}")
        else:
            logger.warning("SoT model initialization skipped due to missing dependencies.")
    
    def _initialize_model(self):
        """Initialize the SoT model and resources."""
        # Find SoT directory
        sot_dir = self._find_sot_directory()
        if not sot_dir:
            logger.warning("SoT directory not found. Trying to use HuggingFace model directly.")
            try:
                self.model = DistilBertForSequenceClassification.from_pretrained("saytes/SoT_DistilBERT")
                self.tokenizer = DistilBertTokenizer.from_pretrained("saytes/SoT_DistilBERT")
                
                # Create a simple label mapping
                self.label_mapping = {
                    "chunked_symbolism": 0,
                    "conceptual_chaining": 1,
                    "expert_lexicons": 2
                }
                self.label_mapping_reverse = {v: k for k, v in self.label_mapping.items()}
                return
            except Exception as e:
                logger.error(f"Error loading model from HuggingFace: {e}")
                raise
        
        # Load model from local directory
        model_path = "saytes/SoT_DistilBERT"  # Default HF path
        
        try:
            self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
            self.tokenizer = DistilBertTokenizer.from_pretrained(model_path)
            
            # Load label mapping
            label_mapping_path = os.path.join(sot_dir, "sketch_of_thought", "config", "label_mapping.json")
            if os.path.exists(label_mapping_path):
                with open(label_mapping_path, "r") as f:
                    self.label_mapping = json.load(f)
                self.label_mapping_reverse = {v: k for k, v in self.label_mapping.items()}
            
            # Load prompts
            prompts_dir = os.path.join(sot_dir, "sketch_of_thought", "config", "prompts", "EN")
            if os.path.exists(prompts_dir):
                self._load_prompts(prompts_dir)
            
            # Load contexts
            contexts_path = os.path.join(sot_dir, "sketch_of_thought", "config", "exemplars.json")
            if os.path.exists(contexts_path):
                with open(contexts_path, "r") as f:
                    contexts_data = json.load(f)
                    self.contexts = contexts_data.get("EN", {})
        except Exception as e:
            logger.error(f"Error loading SoT resources: {e}")
            raise
    
    def _find_sot_directory(self):
        """Find the SoT directory by searching the project folders."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
        
        # Look for SoT directories with specific pattern
        potential_dirs = []
        for item in os.listdir(project_dir):
            if item.startswith("sot_") or item == "SoT":
                sot_path = os.path.join(project_dir, item)
                if os.path.isdir(sot_path):
                    potential_dirs.append(sot_path)
        
        # Check each potential directory for the expected structure
        for sot_dir in potential_dirs:
            # Check if it has sketch_of_thought subdirectory
            sketch_dir = os.path.join(sot_dir, "sketch_of_thought")
            sot_subdir = os.path.join(sot_dir, "SoT", "sketch_of_thought")
            
            if os.path.isdir(sketch_dir):
                return sot_dir
            elif os.path.isdir(sot_subdir):
                return os.path.join(sot_dir, "SoT")
        
        return None
    
    def _load_prompts(self, prompts_dir):
        """Load all the prompt files for different paradigms."""
        prompt_files = {
            "conceptual_chaining": "EN_ConceptualChaining_SystemPrompt.md",
            "chunked_symbolism": "EN_ChunkedSymbolism_SystemPrompt.md",
            "expert_lexicons": "EN_ExpertLexicons_SystemPrompt.md"
        }
        
        for paradigm, filename in prompt_files.items():
            file_path = os.path.join(prompts_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    self.prompts[paradigm] = f.read()
    
    def classify_question(self, text: str) -> str:
        """
        Classify a question to determine the appropriate reasoning paradigm.
        
        Args:
            text: The text to classify
            
        Returns:
            The reasoning paradigm to use (conceptual_chaining, chunked_symbolism, or expert_lexicons)
        """
        if not self.available:
            logger.warning("SoT model not available. Using heuristic classification.")
            return self._heuristic_classification(text)
        
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
            outputs = self.model(**inputs)
            predicted_class = torch.argmax(outputs.logits, dim=1).item()
            
            if self.label_mapping_reverse:
                return self.label_mapping_reverse[predicted_class]
            else:
                # Fallback if mapping not available
                paradigms = ["chunked_symbolism", "conceptual_chaining", "expert_lexicons"]
                return paradigms[predicted_class % 3]
        except Exception as e:
            logger.error(f"Error classifying with SoT model: {e}")
            return self._heuristic_classification(text)
    
    def _heuristic_classification(self, text: str) -> str:
        """
        Use a simple heuristic to classify text if the model is not available.
        
        Args:
            text: The text to classify
            
        Returns:
            The predicted reasoning paradigm
        """
        text_lower = text.lower()
        
        # Check for math/numerical content
        math_keywords = ['math', 'calculate', 'compute', 'equation', 'number', 
                        'equals', 'solve', '%', '+', '-', '*', '/', '=']
        if any(keyword in text_lower for keyword in math_keywords):
            return "chunked_symbolism"
        
        # Check for technical/domain-specific content
        expert_keywords = ['technical', 'expert', 'medical', 'legal', 'specific',
                          'domain', 'professional', 'specialized', 'terminology']
        if any(keyword in text_lower for keyword in expert_keywords):
            return "expert_lexicons"
        
        # Default to conceptual chaining
        return "conceptual_chaining"
    
    def get_system_prompt(self, paradigm: str) -> str:
        """
        Get the system prompt for a specific reasoning paradigm.
        
        Args:
            paradigm: The reasoning paradigm
            
        Returns:
            The system prompt for the paradigm
        """
        return self.prompts.get(paradigm, "")
    
    def get_initialized_context(self, paradigm: str, question: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get an initialized context for a reasoning paradigm.
        
        Args:
            paradigm: The reasoning paradigm
            question: Optional question to include in the context
            
        Returns:
            Initialized context as a list of messages
        """
        if paradigm not in self.paradigms:
            logger.warning(f"Unknown paradigm: {paradigm}. Using conceptual_chaining.")
            paradigm = "conceptual_chaining"
        
        # Construct the context
        if paradigm in self.prompts:
            context = [{"role": "system", "content": self.prompts[paradigm]}]
        else:
            # Generic prompt if specific one not available
            context = [{"role": "system", "content": f"You are an expert at {paradigm} reasoning. Show step-by-step thinking."}]
        
        # Add exemplars if available
        if paradigm in self.contexts and len(self.contexts[paradigm]) > 0:
            for exemplar in self.contexts[paradigm]:
                context.append({"role": "user", "content": exemplar.get("question", "")})
                context.append({"role": "assistant", "content": exemplar.get("answer", "")})
        
        # Add the user's question if provided
        if question:
            context.append({"role": "user", "content": question})
        
        return context
    
    def avaliable_paradigms(self) -> List[str]:
        """
        Return the available reasoning paradigms.
        
        Returns:
            List of available paradigms
        """
        return self.paradigms
    
    def generate_reasoning(self, text: str, issues: List[Dict[str, Any]], paradigm: str = "conceptual_chaining") -> Optional[str]:
        """
        Generate structured reasoning based on the SoT paradigm and detected issues.
        
        Args:
            text: The original text
            issues: List of detected issues
            paradigm: The SoT paradigm to use
            
        Returns:
            Structured reasoning as a string, or None if unable to generate
        """
        if not issues:
            return None
        
        if paradigm == "conceptual_chaining":
            return self._generate_conceptual_chaining(text, issues)
        elif paradigm == "chunked_symbolism":
            return self._generate_chunked_symbolism(text, issues)
        elif paradigm == "expert_lexicons":
            return self._generate_expert_lexicons(text, issues)
        else:
            # Default to conceptual chaining
            return self._generate_conceptual_chaining(text, issues)
    
    def _generate_conceptual_chaining(self, text: str, issues: List[Dict[str, Any]]) -> str:
        """Generate reasoning using the conceptual chaining paradigm."""
        # Extract issue types and terms
        issue_types = [issue.get("issue", "unknown") for issue in issues]
        terms = [issue.get("term", "") for issue in issues]
        
        # Build chains based on the issues
        chains = []
        
        # Handle bias-related issues
        if any("bias" in issue_type for issue_type in issue_types):
            bias_terms = [term for i, term in enumerate(terms) if "bias" in issue_types[i]]
            if bias_terms:
                chains.append(f"#{bias_terms[0]} → #implicit_bias → #needs_neutrality")
        
        # Handle ambiguity/vagueness issues
        if any("vague" in issue_type for issue_type in issue_types):
            vague_terms = [term for i, term in enumerate(terms) if "vague" in issue_types[i]]
            if vague_terms:
                chains.append(f"#{vague_terms[0]} → #ambiguity → #requires_precision")
        
        # Handle reference issues
        if any("reference" in issue_type for issue_type in issue_types):
            ref_terms = [term for i, term in enumerate(terms) if "reference" in issue_types[i]]
            if ref_terms:
                chains.append(f"#{ref_terms[0]} → #unclear_antecedent → #needs_specificity")
        
        # Handle stereotype issues
        if any("stereotype" in issue_type for issue_type in issue_types):
            stereotype_terms = [term for i, term in enumerate(terms) if "stereotype" in issue_types[i]]
            if stereotype_terms:
                chains.append(f"#{stereotype_terms[0]} → #generalization → #requires_evidence")
        
        # If no specific chains were created, use a general one
        if not chains:
            # Use the first issue as a fallback
            first_term = terms[0] if terms else "text"
            first_issue = issue_types[0] if issue_types else "issue"
            chains.append(f"#{first_term} → #{first_issue} → #needs_clarification")
        
        # Combine all chains
        reasoning = "<think>\n" + "\n".join(chains) + "\n</think>"
        return reasoning
    
    def _generate_chunked_symbolism(self, text: str, issues: List[Dict[str, Any]]) -> str:
        """Generate reasoning using the chunked symbolism paradigm."""
        # Extract issue confidence values and counts
        confidences = [issue.get("confidence", 0) for issue in issues]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Count issue types
        issue_types = {}
        for issue in issues:
            issue_type = issue.get("issue", "unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        # Build symbolic representation
        lines = []
        lines.append("issues = {")
        for issue_type, count in issue_types.items():
            lines.append(f"  {issue_type}: {count},")
        lines.append("}")
        
        lines.append(f"confidence = {avg_confidence:.2f}")
        
        # Calculate an overall clarity score (inverse of issues)
        clarity_score = max(0, 1 - (len(issues) * 0.1))
        lines.append(f"clarity_score = {clarity_score:.2f}")
        
        # Add an assessment
        if clarity_score < 0.5:
            lines.append("assessment = 'major revision needed'")
        elif clarity_score < 0.8:
            lines.append("assessment = 'minor revision needed'")
        else:
            lines.append("assessment = 'acceptable'")
        
        # Combine all lines
        reasoning = "<think>\n" + "\n".join(lines) + "\n</think>"
        return reasoning
    
    def _generate_expert_lexicons(self, text: str, issues: List[Dict[str, Any]]) -> str:
        """Generate reasoning using the expert lexicons paradigm."""
        # Extract terms and issue types
        terms = [issue.get("term", "") for issue in issues]
        issue_types = [issue.get("issue", "unknown") for issue in issues]
        
        # Build expert notation
        lines = []
        
        # Create a set of issues
        if terms:
            terms_str = ", ".join(f"'{term}'" for term in terms)
            lines.append(f"I = {{{terms_str}}}")
        
        # Create logical symbols based on issue types
        if "bias" in "".join(issue_types):
            lines.append("bias(I) → ¬neutral")
        
        if "vague" in "".join(issue_types):
            lines.append("vague(I) → ¬precise")
        
        if "stereotype" in "".join(issue_types):
            lines.append("stereotype(I) → ¬evidence-based")
        
        # Add a conclusion
        issue_count = len(issues)
        if issue_count > 0:
            lines.append(f"∴ clarification_required({issue_count})")
        
        # Combine all lines
        reasoning = "<think>\n" + "\n".join(lines) + "\n</think>"
        return reasoning
