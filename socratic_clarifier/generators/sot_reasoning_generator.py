"""
Module for generating Sketch-of-Thought reasoning based on detected issues.
"""

from typing import List, Dict, Any, Optional


class SoTReasoningGenerator:
    """
    Generates structured Sketch-of-Thought reasoning based on detected issues.
    
    This generator creates reasoning in three different paradigms:
    - Conceptual Chaining: For connecting ideas in logical sequences
    - Chunked Symbolism: For numerical and symbolic reasoning
    - Expert Lexicons: For domain-specific terminology
    """
    
    def __init__(self):
        """Initialize the SoT reasoning generator."""
    
    def generate(self, text: str, issues: List[Dict[str, Any]], 
                 paradigm: str = "conceptual_chaining") -> Optional[str]:
        """
        Generate SoT reasoning based on the paradigm and detected issues.
        
        Args:
            text: The original text
            issues: List of detected issues
            paradigm: The SoT paradigm to use
        
        Returns:
            Structured reasoning as a string, or None if unable to generate
        """
        if not issues:
            return None
        
        # Use local implementation
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
