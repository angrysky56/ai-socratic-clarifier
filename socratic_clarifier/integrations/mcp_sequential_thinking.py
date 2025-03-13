"""
MCP Sequential Thinking integration for the Socratic Clarifier.

This module provides an adapter between the Socratic Clarifier and the MCP Sequential Thinking server.
"""

import json
import requests
from typing import List, Dict, Any, Optional
from loguru import logger


class MCPSequentialThinking:
    """
    Adapter for the MCP Sequential Thinking server.
    
    This class provides methods for using the MCP Sequential Thinking server for reasoning
    in the Socratic Clarifier.
    """
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        Initialize the MCP Sequential Thinking adapter.
        
        Args:
            base_url: The base URL of the MCP Sequential Thinking server
        """
        self.base_url = base_url
        self.endpoint = f"{base_url}/mcp/sequentialthinking"
        self.headers = {"Content-Type": "application/json"}
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if the MCP Sequential Thinking server is available."""
        try:
            response = requests.get(self.base_url, timeout=2)
            if response.status_code == 200:
                logger.info("MCP Sequential Thinking server is available.")
                return True
            else:
                logger.warning(f"MCP Sequential Thinking server returned status code {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.warning(f"MCP Sequential Thinking server not available: {e}")
            return False
    
    def classify_question(self, text: str) -> str:
        """
        Classify a question to determine the appropriate reasoning paradigm.
        
        Args:
            text: The text to classify
            
        Returns:
            The reasoning paradigm to use (conceptual_chaining, chunked_symbolism, or expert_lexicons)
        """
        if not self.available:
            logger.warning("MCP Sequential Thinking server not available. Using default paradigm.")
            return "conceptual_chaining"
        
        try:
            # Initial thought to classify the text
            payload = {
                "thought": f"Analyzing the following text to determine the most appropriate reasoning paradigm: '{text[:200]}...' if longer than 200 chars",
                "nextThoughtNeeded": True,
                "thoughtNumber": 1,
                "totalThoughts": 3
            }
            
            response = requests.post(self.endpoint, json=payload, headers=self.headers)
            if response.status_code == 200:
                # Process the response
                result = response.json()
                
                # Second thought to consider paradigms
                payload = {
                    "thought": "Based on the text, I need to determine if it's more suited for conceptual_chaining (connecting ideas logically), chunked_symbolism (numerical/mathematical reasoning), or expert_lexicons (domain-specific terminology).",
                    "nextThoughtNeeded": True,
                    "thoughtNumber": 2,
                    "totalThoughts": 3
                }
                
                response = requests.post(self.endpoint, json=payload, headers=self.headers)
                if response.status_code == 200:
                    # Final thought to determine the paradigm
                    result = response.json()
                    
                    # Check for mathematical/numerical content
                    if any(word in text.lower() for word in ['math', 'calculate', 'compute', 'equation', 'number', '%', '+', '-', '*', '/', '=', 'percentage']):
                        paradigm = "chunked_symbolism"
                    # Check for technical/domain-specific content
                    elif any(word in text.lower() for word in ['technical', 'expert', 'medical', 'legal', 'specific', 'jargon']):
                        paradigm = "expert_lexicons"
                    # Default to conceptual chaining
                    else:
                        paradigm = "conceptual_chaining"
                    
                    payload = {
                        "thought": f"After analyzing the text, the most appropriate reasoning paradigm is {paradigm}.",
                        "nextThoughtNeeded": False,
                        "thoughtNumber": 3,
                        "totalThoughts": 3
                    }
                    
                    response = requests.post(self.endpoint, json=payload, headers=self.headers)
                    if response.status_code == 200:
                        return paradigm
            
            # If we reach here, something went wrong
            logger.warning("Error communicating with MCP Sequential Thinking server. Using default paradigm.")
            return "conceptual_chaining"
            
        except Exception as e:
            logger.error(f"Error classifying with MCP Sequential Thinking: {e}")
            return "conceptual_chaining"
    
    def avaliable_paradigms(self) -> List[str]:
        """
        Return the available reasoning paradigms.
        
        Returns:
            List of available paradigms
        """
        return ["conceptual_chaining", "chunked_symbolism", "expert_lexicons"]
    
    def get_initialized_context(self, 
                             paradigm: str, 
                             question: Optional[str] = None, 
                             format: str = "llm", 
                             include_system_prompt: bool = True) -> List[Dict[str, Any]]:
        """
        Get an initialized context for a reasoning paradigm.
        
        Args:
            paradigm: The reasoning paradigm to use
            question: Optional question to include in the context
            format: The format of the output (llm, json, etc.)
            include_system_prompt: Whether to include a system prompt
            
        Returns:
            Initialized context as a list of messages
        """
        if not self.available:
            logger.warning("MCP Sequential Thinking server not available. Using empty context.")
            return []
        
        # Create a basic context based on the paradigm
        context = []
        
        if include_system_prompt:
            if paradigm == "conceptual_chaining":
                system_prompt = "You are an expert at connecting concepts in logical chains. Use the format #concept1 → #concept2 → #conclusion."
            elif paradigm == "chunked_symbolism":
                system_prompt = "You are an expert at numerical and symbolic reasoning. Use mathematical notation and structured representations."
            elif paradigm == "expert_lexicons":
                system_prompt = "You are an expert in domain-specific terminology. Use precise terminology and logical symbols to represent relationships."
            else:
                system_prompt = "You are an expert at structured reasoning. Analyze issues step by step."
            
            context.append({"role": "system", "content": system_prompt})
        
        if question:
            context.append({"role": "user", "content": question})
        
        return context
    
    def generate_reasoning(self, 
                        text: str, 
                        issues: List[Dict[str, Any]], 
                        paradigm: str = "conceptual_chaining") -> Optional[str]:
        """
        Generate structured reasoning using the MCP Sequential Thinking server.
        
        Args:
            text: The original text
            issues: List of detected issues
            paradigm: The reasoning paradigm to use
            
        Returns:
            Structured reasoning as a string, or None if unable to generate
        """
        if not self.available or not issues:
            logger.warning("MCP Sequential Thinking server not available or no issues to process.")
            return None
        
        try:
            # Extract issue information
            issue_descriptions = []
            for issue in issues:
                issue_type = issue.get("issue", "unknown")
                term = issue.get("term", "")
                confidence = issue.get("confidence", 0)
                description = issue.get("description", "")
                
                issue_descriptions.append(f"Issue: {issue_type}, Term: '{term}', Confidence: {confidence:.2f}, Description: {description}")
            
            issues_text = "\n".join(issue_descriptions)
            
            # Initial thought
            payload = {
                "thought": f"Analyzing the following text: '{text[:150]}...' if longer. I've detected several issues:\n{issues_text[:200]}...",
                "nextThoughtNeeded": True,
                "thoughtNumber": 1,
                "totalThoughts": 3
            }
            
            response = requests.post(self.endpoint, json=payload, headers=self.headers)
            if response.status_code == 200:
                # Process the response
                result = response.json()
                
                # Second thought - generate reasoning based on paradigm
                reasoning_content = ""
                
                if paradigm == "conceptual_chaining":
                    # Extract key terms from issues
                    terms = [issue.get("term", "") for issue in issues]
                    issue_types = [issue.get("issue", "unknown") for issue in issues]
                    
                    # Build chains
                    chains = []
                    for i, term in enumerate(terms):
                        if i < len(issue_types):
                            issue_type = issue_types[i]
                            if "bias" in issue_type:
                                chains.append(f"#{term} → #implicit_bias → #needs_neutrality")
                            elif "vague" in issue_type:
                                chains.append(f"#{term} → #ambiguity → #requires_precision")
                            elif "stereotype" in issue_type:
                                chains.append(f"#{term} → #generalization → #requires_evidence")
                            else:
                                chains.append(f"#{term} → #{issue_type} → #needs_clarification")
                    
                    reasoning_content = "<think>\n" + "\n".join(chains) + "\n</think>"
                    
                elif paradigm == "chunked_symbolism":
                    # Build symbolic representation
                    lines = []
                    lines.append("issues = {")
                    
                    issue_counts = {}
                    for issue in issues:
                        issue_type = issue.get("issue", "unknown")
                        issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
                    
                    for issue_type, count in issue_counts.items():
                        lines.append(f"  {issue_type}: {count},")
                    
                    lines.append("}")
                    
                    # Calculate confidence
                    confidences = [issue.get("confidence", 0) for issue in issues]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    lines.append(f"confidence = {avg_confidence:.2f}")
                    
                    reasoning_content = "<think>\n" + "\n".join(lines) + "\n</think>"
                    
                elif paradigm == "expert_lexicons":
                    # Build expert notation
                    lines = []
                    
                    terms = [issue.get("term", "") for issue in issues]
                    if terms:
                        terms_str = ", ".join(f"'{term}'" for term in terms)
                        lines.append(f"I = {{{terms_str}}}")
                    
                    # Add logical relations
                    issue_types = [issue.get("issue", "unknown") for issue in issues]
                    issue_types_str = " ".join(issue_types)
                    
                    if "bias" in issue_types_str:
                        lines.append("bias(I) → ¬neutral")
                    
                    if "vague" in issue_types_str:
                        lines.append("vague(I) → ¬precise")
                    
                    if "stereotype" in issue_types_str:
                        lines.append("stereotype(I) → ¬evidence-based")
                    
                    reasoning_content = "<think>\n" + "\n".join(lines) + "\n</think>"
                
                else:
                    # Default simple reasoning
                    reasoning_content = "<think>\nAnalyzing text for issues...\nDetected multiple issues that need clarification.\n</think>"
                
                # Set up second thought with the reasoning
                payload = {
                    "thought": f"Using the {paradigm} paradigm, I'll structure my reasoning as follows:\n\n{reasoning_content}",
                    "nextThoughtNeeded": True,
                    "thoughtNumber": 2,
                    "totalThoughts": 3
                }
                
                response = requests.post(self.endpoint, json=payload, headers=self.headers)
                if response.status_code == 200:
                    # Final thought - conclusion
                    payload = {
                        "thought": f"Based on the {paradigm} analysis, this text contains {len(issues)} issues that need clarification. The structured reasoning provides a framework for generating effective Socratic questions.",
                        "nextThoughtNeeded": False,
                        "thoughtNumber": 3,
                        "totalThoughts": 3
                    }
                    
                    response = requests.post(self.endpoint, json=payload, headers=self.headers)
                    if response.status_code == 200:
                        return reasoning_content
            
            # If we reach here, something went wrong
            logger.warning("Error communicating with MCP Sequential Thinking server.")
            return None
            
        except Exception as e:
            logger.error(f"Error generating reasoning with MCP Sequential Thinking: {e}")
            return None
