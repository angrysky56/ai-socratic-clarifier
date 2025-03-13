"""
Module for detecting bias in text.
"""

from typing import List, Dict, Any
import re


class BiasDetector:
    """
    Detects potentially biased language, stereotypes, and non-inclusive terms.
    
    This detector identifies:
    - Gender-biased language
    - Stereotypical statements
    - Non-inclusive terminology
    - Generalizations about groups
    """
    
    def __init__(self):
        """Initialize the bias detector."""
        # Patterns for detecting common bias issues
        self.gender_bias = [
            r'\b(?:mankind|manpower|manmade|chairman|policeman|fireman|stewardess|mailman)\b',
            r'\b(?:he|his|him)\b(?:\s+or\s+(?:she|her))?'  # Male default
        ]
        
        self.stereotypes = [
            r'\ball\s+(?:\w+\s+)*(?:women|men|asians|africans|latinos|elderly|millennials)\s+(?:are|have|do)\b',
            r'\b(?:women|men)\s+(?:are better|are worse|can\'t|always|never)\b'
        ]
        
        self.non_inclusive = [
            r'\b(?:blacklist|whitelist|master|slave|crazy|insane|lame|retarded|crippled)\b',
            r'\b(?:illegal alien|colored people|oriental|gypped|jewed|ghetto)\b'
        ]
        
        # Compile patterns
        self.gender_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.gender_bias]
        self.stereotype_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.stereotypes]
        self.non_inclusive_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.non_inclusive]
    
    def detect(self, text: str, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Detect bias issues in the provided text.
        
        Args:
            text: The text to analyze
            threshold: Confidence threshold for reporting issues
        
        Returns:
            List of detected bias issues
        """
        issues = []
        
        # Check for gender bias
        for pattern in self.gender_patterns:
            for match in pattern.finditer(text):
                term = match.group(0)
                issues.append({
                    "term": term,
                    "span": (match.start(), match.end()),
                    "issue": "gender_bias",
                    "description": f"The term '{term}' may contain gender bias",
                    "confidence": 0.8  # Fixed confidence for now
                })
        
        # Check for stereotypes
        for pattern in self.stereotype_patterns:
            for match in pattern.finditer(text):
                term = match.group(0)
                issues.append({
                    "term": term,
                    "span": (match.start(), match.end()),
                    "issue": "stereotype",
                    "description": f"The statement '{term}' may contain stereotyping",
                    "confidence": 0.9  # Fixed confidence for now
                })
        
        # Check for non-inclusive language
        for pattern in self.non_inclusive_patterns:
            for match in pattern.finditer(text):
                term = match.group(0)
                issues.append({
                    "term": term,
                    "span": (match.start(), match.end()),
                    "issue": "non_inclusive",
                    "description": f"The term '{term}' may be non-inclusive",
                    "confidence": 0.85  # Fixed confidence for now
                })
        
        # Filter by confidence threshold
        issues = [issue for issue in issues if issue["confidence"] >= threshold]
        
        return issues
