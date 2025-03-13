"""
Module for detecting ambiguity in text.
"""

from typing import List, Dict, Any
import re


class AmbiguityDetector:
    """
    Detects ambiguous statements, vague terms, and unclear references in text.
    
    This detector identifies:
    - Pronouns without clear antecedents
    - Vague quantifiers (some, many, few)
    - Broad, undefined terms
    - Multiple possible interpretations
    """
    
    def __init__(self):
        """Initialize the ambiguity detector."""
        # Patterns for detecting common ambiguity issues
        self.vague_terms = [
            r'\b(?:significant|substantial|several|various|most|many|some|few)\b',
            r'\b(?:recently|soon|later|earlier|sometimes|occasionally|often|frequently)\b',
            r'\b(?:good|bad|better|worse|best|worst|improved|effective)\b'
        ]
        
        self.unclear_references = [
            r'\b(?:this|that|these|those|it|they|them)\b(?!\s+\w+)',  # Demonstratives without a noun
            r'\b(?:the (?:former|latter))\b'
        ]
        
        # Compile patterns
        self.vague_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.vague_terms]
        self.reference_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.unclear_references]
    
    def detect(self, text: str, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Detect ambiguity issues in the provided text.
        
        Args:
            text: The text to analyze
            threshold: Confidence threshold for reporting issues
        
        Returns:
            List of detected ambiguity issues
        """
        issues = []
        
        # Check for vague terms
        for pattern in self.vague_patterns:
            for match in pattern.finditer(text):
                term = match.group(0)
                issues.append({
                    "term": term,
                    "span": (match.start(), match.end()),
                    "issue": "vague_term",
                    "description": f"The term '{term}' may be too vague or subjective",
                    "confidence": 0.8  # Fixed confidence for now
                })
        
        # Check for unclear references
        for pattern in self.reference_patterns:
            for match in pattern.finditer(text):
                term = match.group(0)
                issues.append({
                    "term": term,
                    "span": (match.start(), match.end()),
                    "issue": "unclear_reference",
                    "description": f"The reference '{term}' may be unclear",
                    "confidence": 0.75  # Fixed confidence for now
                })
        
        # Filter by confidence threshold
        issues = [issue for issue in issues if issue["confidence"] >= threshold]
        
        return issues
