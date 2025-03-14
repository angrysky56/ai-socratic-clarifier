"""
Fallback handlers for when JSON parsing fails.
This module provides helpers to extract meaningful issues from unstructured responses.
"""
import re
from typing import List, Dict, Any

def create_fallback_issue(response: str) -> Dict[str, Any]:
    """
    Create a basic fallback issue when JSON parsing fails.
    This ensures we always have at least one issue to work with.
    
    Args:
        response: The raw response from the model
        
    Returns:
        A fallback issue dictionary
    """
    # Try to extract something meaningful from the response
    if len(response) > 300:
        # If response is long, use a snippet
        description = response[:250] + "..."
    else:
        description = response
    
    # Create a generic fallback issue
    return {
        "term": "statement",
        "issue": "potential_issues",
        "description": f"The statement may contain logical or factual issues that merit questioning",
        "confidence": 0.5
    }

def extract_issues_via_patterns(response: str, text: str) -> List[Dict[str, Any]]:
    """
    Extract issues from text response using pattern matching.
    This is used when JSON parsing fails completely.
    
    Args:
        response: Model response
        text: Original text being analyzed
        
    Returns:
        List of extracted issues
    """
    issues = []
    
    # Extract quoted terms as potential issues
    quoted_terms = re.findall(r'["\']([^"\']{3,})["\']', response)
    
    # Look for terms from the original text that are mentioned in the response
    words = text.split()
    significant_words = [word for word in words if len(word) > 3 and word.lower() not in [
        "this", "that", "these", "those", "there", "their", "they", "them",
        "have", "does", "will", "would", "could", "should", "about", "with"
    ]]
    
    for word in significant_words:
        if word in response:
            # Found a term from the original text mentioned in the response
            term = word
            
            # Try to find a sentence containing this term
            pattern = fr'[.!?]\s+([^.!?]*{re.escape(term)}[^.!?]*[.!?])'
            context_match = re.search(pattern, response)
            description = context_match.group(1).strip() if context_match else "This term may require clarification"
            
            issues.append({
                "term": term,
                "issue": "potential_concern",
                "description": description,
                "confidence": 0.6
            })
    
    # If we found quoted terms, use those as well
    for term in quoted_terms:
        if len(term) > 2 and term not in [issue["term"] for issue in issues]:
            issues.append({
                "term": term,
                "issue": "quoted_term",
                "description": "This term was specifically noted in the analysis",
                "confidence": 0.7
            })
    
    # Extract words like "vague", "absolute", "evidence", "claim" and associate with terms
    issue_indicators = {
        "vague": "vague_term",
        "unclear": "vague_term", 
        "ambiguous": "vague_term",
        "absolute": "absolute_statement",
        "always": "absolute_statement",
        "never": "absolute_statement",
        "evidence": "unsupported_claim",
        "claim": "unsupported_claim",
        "assumption": "assumption",
    }
    
    for indicator, issue_type in issue_indicators.items():
        if indicator in response.lower():
            # Try to find a sentence containing this issue indicator
            pattern = fr'[.!?]\s+([^.!?]*{indicator}[^.!?]*[.!?])'
            context_match = re.search(pattern, response, re.IGNORECASE)
            if context_match:
                sentence = context_match.group(1).strip()
                
                # Try to extract a term from the sentence
                term_match = re.search(r'["\']([^"\']+)["\']', sentence)
                if term_match:
                    term = term_match.group(1)
                else:
                    # Just use the most significant word from the original text
                    term = significant_words[0] if significant_words else "statement"
                
                # Check if we already have this term
                if not any(issue["term"] == term for issue in issues):
                    issues.append({
                        "term": term,
                        "issue": issue_type,
                        "description": sentence,
                        "confidence": 0.65
                    })
    
    # If we still don't have any issues, create a generic one
    if not issues:
        issues.append(create_fallback_issue(response))
    
    return issues[:3]  # Limit to top 3 issues
