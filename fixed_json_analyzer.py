#!/usr/bin/env python3
"""
Standalone script for analyzing text with more robust JSON handling.
This can be integrated into the main application once validated.
"""
import os
import sys
import json
import re
import requests
from typing import Dict, List, Any, Optional, Union

def load_config():
    """Load configuration from the config file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Configuration file not found at {config_path}")
            return {}
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {}

def call_ollama_api(model: str, prompt: str, temperature: float = 0.7, max_tokens: int = 800):
    """
    Call the Ollama API directly with simpler parameters.
    
    Args:
        model: Model name
        prompt: The prompt to send
        temperature: Generation temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text
    """
    config = load_config()
    base_url = config.get("integrations", {}).get("ollama", {}).get("base_url", "http://localhost:11434/api")
    
    if not base_url.endswith("/api"):
        base_url += "/api"
    
    try:
        response = requests.post(
            f"{base_url}/generate",
            json={
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=60
        )
        
        if response.status_code == 200:
            try:
                # Try to parse the JSON response
                response_json = response.json()
                return response_json.get("response", "")
            except json.JSONDecodeError as je:
                # Handle JSON parsing errors
                print(f"JSON decoding error: {je}. Checking for plain text response.")
                
                # Save the raw response for debugging
                with open("/tmp/ollama_response_raw.txt", "wb") as f:
                    f.write(response.content)
                
                # Try to extract text directly from the response
                text_content = response.text
                
                # Look for a 'response' field in raw text
                match = re.search(r'"response"\s*:\s*"([^"]+)"', text_content)
                if match:
                    return match.group(1)
                
                # If nothing else works, return the raw text
                return text_content
        else:
            print(f"Error calling Ollama API: {response.status_code} - {response.text}")
            return ""
    except Exception as e:
        print(f"Exception calling Ollama API: {e}")
        return ""

def call_ollama_chat(model: str, prompt: str, temperature: float = 0.7, max_tokens: int = 800):
    """
    Call the Ollama chat API which may provide better formatting.
    
    Args:
        model: Model name
        prompt: The prompt to send
        temperature: Generation temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text
    """
    config = load_config()
    base_url = config.get("integrations", {}).get("ollama", {}).get("base_url", "http://localhost:11434/api")
    
    if not base_url.endswith("/api"):
        base_url += "/api"
    
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant"}, 
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "num_predict": max_tokens
            },
            timeout=60
        )
        
        # Save the raw response for debugging
        with open("/tmp/ollama_chat_response_raw.txt", "wb") as f:
            f.write(response.content)
        
        if response.status_code == 200:
            try:
                # Try to parse the JSON response
                response_json = response.json()
                content = response_json.get("message", {}).get("content", "")
                return content
            except json.JSONDecodeError as je:
                # Handle JSON parsing errors
                print(f"JSON decoding error in chat response: {je}")
                return response.text
        else:
            print(f"Error calling Ollama chat API: {response.status_code} - {response.text}")
            # Try generate API as fallback
            return call_ollama_api(model, prompt, temperature, max_tokens)
    except Exception as e:
        print(f"Exception calling Ollama chat API: {e}")
        # Try generate API as fallback
        return call_ollama_api(model, prompt, temperature, max_tokens)

def create_analysis_prompt(text: str) -> str:
    """
    Create a prompt for analysis that minimizes JSON formatting issues.
    
    Args:
        text: Text to analyze
        
    Returns:
        Prompt for the model
    """
    return f"""You are an expert at identifying issues in statements that could benefit from Socratic questioning.

Analyze this text: "{text}"

INSTRUCTIONS:
Look for these issues:
* Absolute terms like 'everyone', 'always', 'never', 'all', 'none'
* Vague or imprecise language that lacks clear definition
* Claims made without evidence 
* Generalizations that don't account for exceptions
* Language that assumes universal applicability 
* Normative statements that impose values without qualification

For example, in "Everyone should own a dog":
* "Everyone" is an absolute term that fails to account for people with allergies, housing restrictions, or different preferences
* "should" is a normative claim that imposes values without acknowledging cultural or personal differences

PROVIDE YOUR ANALYSIS AS A SIMPLE LIST OF ISSUES.
For each issue:
1. The problematic term
2. The type of issue
3. A brief explanation

DO NOT FORMAT AS JSON. 
Just list the issues one by one with clear labels.

If there are no issues, simply write "No issues found."
"""

def extract_issues_from_text(response: str) -> List[Dict[str, Any]]:
    """
    Extract issues from a text response rather than trying to parse JSON.
    
    Args:
        response: Model response
        
    Returns:
        List of extracted issues
    """
    issues = []
    
    # Save the response for debugging
    with open("/tmp/ai_debug_response.txt", "w") as f:
        f.write(f"Original response:\n{response}\n\n")
    
    # Check if no issues were found
    if "no issues found" in response.lower():
        print("No issues found in the text")
        return []
    
    # Try to extract issues using pattern matching
    # Look for patterns like:
    # - Term: "something"
    # - Issue/Problem/Type: description
    # - Explanation/Description/Reason: text
    
    # Split into potential issue blocks
    blocks = re.split(r'\n\s*\n|\n[-*•]\s+', response)
    
    for block in blocks:
        # Skip empty blocks
        if not block.strip():
            continue
            
        # Initialize issue components
        term = None
        issue_type = None
        description = None
        confidence = 0.8  # Default confidence value
        
        # Look for term
        term_match = re.search(r'(?:Term|Word|Phrase)[^\w]*[:]*\s*["\']?([^"\']+)["\']?', block, re.IGNORECASE)
        if term_match:
            term = term_match.group(1).strip()
        
        # Look for issue type
        issue_match = re.search(r'(?:Issue|Type|Problem)[^\w]*[:]*\s*([^\n]+)', block, re.IGNORECASE)
        if issue_match:
            issue_type = issue_match.group(1).strip()
            
        # Look for description
        desc_match = re.search(r'(?:Description|Explanation|Reason)[^\w]*[:]*\s*([^\n]+(?:\n\s+[^\n]+)*)', block, re.IGNORECASE)
        if desc_match:
            description = desc_match.group(1).strip()
        
        # If we couldn't find structured parts, try to use the whole block
        if not term and not issue_type and not description:
            # Look for any quoted text as a term
            quoted_term = re.search(r'["\']([^"\']+)["\']', block)
            if quoted_term:
                term = quoted_term.group(1).strip()
                
            # If still no term, look for capitalized words
            if not term:
                capitalized = re.search(r'\b([A-Z][a-z]+)\b', block)
                if capitalized:
                    term = capitalized.group(1).strip()
            
            # If still no term, just use the first few words
            if not term:
                words = block.split()
                if words:
                    term = " ".join(words[:2]).strip()
            
            # Use the rest as description
            if term and not description:
                description = block.replace(term, "", 1).strip()
        
        # Only add if we have at least a term
        if term:
            issues.append({
                "term": term,
                "issue": issue_type or "unspecified issue",
                "description": description or "No explanation provided",
                "confidence": confidence
            })
    
    # If no structured issues were found, try a simpler approach
    if not issues:
        # Look for any quoted terms
        quoted_terms = re.findall(r'["\']([^"\']+)["\']', response)
        for term in quoted_terms:
            if len(term) > 1:  # Skip single-character terms
                issues.append({
                    "term": term,
                    "issue": "possible issue",
                    "description": "Quoted term that may be problematic",
                    "confidence": 0.5
                })
    
    return issues

def generate_questions(issues: List[Dict[str, Any]], text: str) -> List[str]:
    """
    Generate questions for the issues.
    
    Args:
        issues: List of extracted issues
        text: Original text
        
    Returns:
        List of questions
    """
    if not issues:
        return []
    
    # Create a simple template-based question for each issue
    questions = []
    templates = [
        "What do you mean by {term}?",
        "Could you clarify what {term} means in this context?",
        "What evidence supports your claim about {term}?",
        "Are there exceptions to your statement about {term}?",
        "How do you define {term} precisely?"
    ]
    
    for issue in issues:
        term = issue.get("term", "")
        if not term:
            continue
            
        # Get a question template based on the issue type
        issue_type = issue.get("issue", "").lower()
        
        if "absolute" in issue_type or "general" in issue_type:
            template = "Are there exceptions or cases where {term} might not apply?"
        elif "vague" in issue_type or "imprecise" in issue_type:
            template = "Could you clarify what you mean by {term}?"
        elif "evidence" in issue_type or "support" in issue_type:
            template = "What evidence supports your claim about {term}?"
        elif "normative" in issue_type or "value" in issue_type:
            template = "Why do you believe {term} is appropriate in this context?"
        else:
            # Use a random template from the list
            import random
            template = random.choice(templates)
        
        # Create the question
        question = template.replace("{term}", term)
        
        # Only add if it's not already in the list
        if question not in questions:
            questions.append(question)
    
    return questions[:5]  # Limit to 5 questions

def analyze_text(text: str) -> Dict[str, Any]:
    """
    Analyze text to identify issues without relying on JSON.
    
    Args:
        text: Text to analyze
        
    Returns:
        Analysis result
    """
    # Get configuration
    config = load_config()
    model = config.get("integrations", {}).get("ollama", {}).get("default_model", "gemma3")
    
    print(f"Analyzing text with model: {model}")
    
    # Create prompt and call model
    prompt = create_analysis_prompt(text)
    
    # First try using the chat API
    print("Trying chat API first...")
    response = call_ollama_chat(model, prompt, temperature=0.3)
    
    # If chat API failed or returned empty, fall back to the regular API
    if not response.strip():
        print("Chat API returned empty response, trying generate API...")
        response = call_ollama_api(model, prompt, temperature=0.3)
    
    # Extract issues using pattern matching instead of JSON
    issues = extract_issues_from_text(response)
    
    # Generate simple questions
    questions = generate_questions(issues, text)
    
    # Create the result
    result = {
        "text": text,
        "issues": issues,
        "questions": questions,
        "reasoning": None,
        "sot_paradigm": None,
        "confidence": sum(issue.get("confidence", 0) for issue in issues) / max(1, len(issues)) if issues else 0.0,
        "sot_enabled": config.get("settings", {}).get("use_sot", True),
        "model": model,
        "provider": "ollama",
        "reflective_ecosystem_used": False
    }
    
    return result

def test_analysis():
    """Test the analysis with some example texts."""
    test_inputs = [
        "Cheese is the best food.",
        "Everyone should own a dog.",
        "Technology always improves people's lives.",
        "This statement is completely correct.",
        "The world would be better if people just followed my advice."
    ]
    
    for i, text in enumerate(test_inputs):
        print(f"\n{'=' * 60}")
        print(f"Test {i+1}: '{text}'")
        print('-' * 40)
        
        try:
            result = analyze_text(text)
            
            print(f"Detected issues: {len(result['issues'])}")
            for j, issue in enumerate(result["issues"]):
                print(f"\nIssue {j+1}:")
                print(f"  Term: {issue.get('term', 'Unknown')}")
                print(f"  Issue: {issue.get('issue', 'Unknown')}")
                print(f"  Description: {issue.get('description', '')}")
                print(f"  Confidence: {issue.get('confidence', 0)}")
            
            print(f"\nGenerated questions: {len(result['questions'])}")
            for j, question in enumerate(result["questions"]):
                print(f"  {j+1}. {question}")
        
        except Exception as e:
            print(f"Error analyzing text: {e}")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    test_analysis()
