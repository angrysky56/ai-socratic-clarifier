"""
Module for generating Socratic questions based on detected issues.
"""

from typing import List, Dict, Any
import random


class QuestionGenerator:
    """
    Generates Socratic questions based on detected issues in text.
    
    This generator creates questions that:
    - Prompt clarification of ambiguous terms
    - Challenge biased assumptions
    - Request evidence for unsupported claims
    - Identify logical inconsistencies
    """
    
    def __init__(self):
        """Initialize the question generator."""
        # Templates for different issue types
        self.templates = {
            "vague_term": [
                "What exactly do you mean by '{term}'?",
                "Could you define '{term}' more precisely?",
                "How would you measure or quantify '{term}'?",
                "Can you provide a specific example of '{term}'?"
            ],
            "unclear_reference": [
                "What does '{term}' refer to specifically?",
                "Could you clarify what '{term}' points to?",
                "Which specific entity or concept does '{term}' refer to?",
                "How might someone else interpret what '{term}' refers to?"
            ],
            "gender_bias": [
                "Would this statement apply equally if we changed the gender referenced?",
                "How might this be rephrased to be more gender-inclusive?",
                "What assumptions about gender roles might be embedded in this phrasing?",
                "Are there gender-neutral alternatives to '{term}'?"
            ],
            "stereotype": [
                "What evidence supports this generalization?",
                "Are there notable exceptions to this statement?",
                "How might individual variations be overlooked in this claim?",
                "What factors beyond group membership might influence this observation?"
            ],
            "non_inclusive": [
                "How might this terminology affect different readers?",
                "Are there more inclusive alternatives to '{term}'?",
                "What historical context might make this term problematic for some?",
                "How does this phrasing align with current inclusive language practices?"
            ]
        }
        
        # SoT paradigm-specific question structures
        self.sot_question_structures = {
            "conceptual_chaining": [
                "Can you trace the logical connection between {term_a} and {term_b}?",
                "What key concepts bridge the gap between {term_a} and the conclusion?",
                "How does {term_a} lead to or relate to {term_b}?"
            ],
            "chunked_symbolism": [
                "Can you break down {term} into measurable components?",
                "What variables would we need to quantify {term}?",
                "How would you express {term} in more concrete terms?"
            ],
            "expert_lexicons": [
                "In the context of this domain, what precise meaning does {term} have?",
                "How might experts in this field operationalize {term}?",
                "What technical criteria define {term} in this context?"
            ]
        }
    
    def generate(self, text: str, issues: List[Dict[str, Any]], 
                 mode: Dict[str, Any], sot_paradigm: str = None) -> List[str]:
        """
        Generate Socratic questions based on detected issues.
        
        Args:
            text: The original text
            issues: List of detected issues
            mode: Current operating mode configuration
            sot_paradigm: The Sketch-of-Thought paradigm if available
        
        Returns:
            List of generated questions
        """
        questions = []
        
        # Apply mode-specific adjustments
        question_style = mode.get("question_style", "neutral")
        question_limit = mode.get("question_limit", 3)
        
        # Process each issue
        for issue in issues:
            issue_type = issue.get("issue")
            term = issue.get("term", "")
            
            # Get templates for this issue type
            if issue_type in self.templates:
                templates = self.templates[issue_type]
                
                # Select a template
                template = random.choice(templates)
                
                # Format the question with the term
                question = template.format(term=term)
                
                # Add SoT structure if available
                if sot_paradigm and sot_paradigm in self.sot_question_structures:
                    # For demonstration, we'll just use a random term from the issues as term_b
                    # In a real implementation, this would be more sophisticated
                    other_terms = [i.get("term", "") for i in issues if i.get("term") != term]
                    term_b = random.choice(other_terms) if other_terms else "the conclusion"
                    
                    # Select a SoT structure
                    sot_structure = random.choice(self.sot_question_structures[sot_paradigm])
                    
                    # Format with terms
                    sot_question = sot_structure.format(term=term, term_a=term, term_b=term_b)
                    
                    # Add both the standard and SoT questions
                    questions.append(question)
                    questions.append(sot_question)
                else:
                    questions.append(question)
        
        # Ensure uniqueness
        questions = list(set(questions))
        
        # Limit the number of questions based on mode
        questions = questions[:question_limit]
        
        return questions
