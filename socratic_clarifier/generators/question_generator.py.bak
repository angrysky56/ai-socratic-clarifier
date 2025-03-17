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
        
        # High-quality question templates
        self.improved_templates = {
            "vague_term": [
                "Could you elaborate on what specific criteria define '{term}' in this context?",
                "What measurable indicators would help quantify or evaluate '{term}'?",
                "How would experts in this field operationalize the concept of '{term}'?",
                "What precise boundaries or thresholds distinguish '{term}' from related concepts?"
            ],
            "unclear_reference": [
                "Which specific entity or concept does '{term}' refer to in this context?",
                "Could you clarify the exact antecedent of '{term}' for precision?",
                "How would you disambiguate the reference '{term}' to avoid multiple interpretations?",
                "What explicit identification would make the reference '{term}' unambiguous?"
            ],
            "gender_bias": [
                "How might this statement read if we applied it equally across all genders?",
                "What underlying assumptions about gender roles are embedded in this phrasing?",
                "In what ways might this formulation inadvertently reinforce gender stereotypes?",
                "How could this be rephrased to maintain its core meaning while being gender-inclusive?"
            ],
            "stereotype": [
                "What specific evidence supports this generalization beyond anecdotal observation?",
                "How might individual variation within this group contradict this characterization?",
                "What contextual factors might better explain these observed patterns than group identity?",
                "How could this observation be reformulated to acknowledge the diversity within this group?"
            ],
            "non_inclusive": [
                "How might this terminology affect readers from different backgrounds or identities?",
                "What historical context makes this term potentially exclusionary for certain groups?",
                "What more universally accessible language could convey the same concept?",
                "How would you reframe this point using terminology that acknowledges diverse perspectives?"
            ],
            "absolute_statement": [
                "Under what specific conditions or circumstances might exceptions to this statement exist?",
                "What degree of certainty would be appropriate to assign to this claim based on available evidence?",
                "How might this statement be qualified to acknowledge potential limitations or exceptions?",
                "What evidence would be required to justify the absolute nature of this claim?"
            ],
            "unsupported_claim": [
                "What empirical evidence would strengthen the foundation of this assertion?",
                "How might this claim be revised to reflect the current state of evidence?",
                "What methodologies could be employed to test the validity of this claim?",
                "What specific sources or data points would need to be cited to substantiate this position?"
            ],
            "normative_statement": [
                "What underlying values or principles inform this normative judgment?",
                "How might this evaluation differ based on alternative ethical frameworks?",
                "How could this normative claim be distinguished from an empirical observation?",
                "What criteria are being applied to make this value judgment?"
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
            if issue_type in self.improved_templates and mode.get("question_style", "neutral") == "precise":
                # Use high-quality templates for precise question style
                templates = self.improved_templates[issue_type]
            elif issue_type in self.templates:
                # Use standard templates
                templates = self.templates[issue_type]
            else:
                # FIXED: Create a default question for unknown issue types
                default_question = f"Can you clarify what you mean by '{term}'?"
                questions.append(default_question)
                continue  # Skip to next issue after adding default question
                
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