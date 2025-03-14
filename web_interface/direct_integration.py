"""
Direct integration patch for the AI-Socratic-Clarifier.
This file adds direct integration with Ollama and SoT.
"""

import requests
import json
import os
import sys
from typing import List, Dict, Any, Optional
import re
from pathlib import Path

# Import fallback handlers
from web_interface.fallback_handlers import create_fallback_issue, extract_issues_via_patterns

# Add path for SoT integration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the reflective ecosystem
try:
    from sequential_thinking.integration import get_enhancer
    REFLECTIVE_ECOSYSTEM_AVAILABLE = True
except ImportError:
    REFLECTIVE_ECOSYSTEM_AVAILABLE = False

def direct_ollama_generate(prompt, model="deepseek-r1:7b", temperature=0.7, max_tokens=512):
    """
    Generate text using Ollama directly.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
        
        if response.status_code == 200:
            return response.json().get("response", ""), response.json()
        else:
            return f"Error: {response.status_code} - {response.text}", {}
    except Exception as e:
        return f"Error: {str(e)}", {}

def direct_ollama_chat(messages, model="deepseek-r1:7b", temperature=0.7, max_tokens=512):
    """
    Generate chat response using Ollama directly.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
        
        if response.status_code == 200:
            return response.json().get("message", {}).get("content", ""), response.json()
        else:
            return f"Error: {response.status_code} - {response.text}", {}
    except Exception as e:
        return f"Error: {str(e)}", {}

def generate_socratic_questions(text, issues, sot_paradigm=None):
    """
    Generate Socratic questions using direct Ollama integration.
    """
    # Try to use the reflective ecosystem if available
    if REFLECTIVE_ECOSYSTEM_AVAILABLE:
        try:
            enhancer = get_enhancer()
            # Start with no original questions and let the enhancer generate all
            enhanced_questions = enhancer.enhance_questions(
                text=text,
                issues=issues,
                original_questions=[],
                sot_paradigm=sot_paradigm,
                max_questions=5
            )
            if enhanced_questions:
                return enhanced_questions
        except Exception as e:
            print(f"Error using reflective ecosystem: {e}")
            # Fall back to standard generation
    
    # Standard Ollama generation as fallback
    # Create a system prompt for the LLM
    system_prompt = """
    You are a master of Socratic questioning who helps people improve their critical thinking.
    
    Your purpose is to craft precise, thoughtful questions that identify potential issues in people's statements.
    
    Based on the text and specific issues detected, create 3-5 thought-provoking questions that will:
    - Encourage the person to recognize their own assumptions
    - Help them examine whether generalizations account for exceptions
    - Prompt consideration of evidence for claims made
    - Lead them to clarify vague or imprecise language
    - Guide reflection on normative statements that impose values
    
    Make each question genuinely useful for deepening understanding, not rhetorical.  
    Each question should directly address a specific issue identified in the text.
    """
    
    # Create context from the text and issues
    context = f"Text: \"{text}\"\n\nDetected issues:\n"
    for i, issue in enumerate(issues):
        context += f"{i+1}. {issue.get('issue', 'Unknown issue')} - '{issue.get('term', '')}'\n"
        context += f"   {issue.get('description', '')}\n"
    
    # Add SoT format instructions if enabled
    if sot_paradigm:
        context += f"\nGenerate questions using the {sot_paradigm} format. Begin with analyzing the issues, then present 3-5 questions.\n"
    
    # Create messages for the chat API
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context}
    ]
    
    # Generate questions using direct Ollama integration
    # Get model from config
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    model = "deepseek-r1:7b"  # Default
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                model = config.get("integrations", {}).get("ollama", {}).get("default_model", model)
        except:
            pass
    
    generated_text, _ = direct_ollama_chat(messages, model=model)
    
    # Parse the response to extract questions
    questions = []
    for line in generated_text.strip().split("\n"):
        line = line.strip()
        if line and ("?" in line) and not line.startswith("#") and not line.startswith("<"):
            # Clean up numbering or bullet points
            clean_line = line
            if len(line) > 2 and line[0].isdigit() and line[1:3] in ['. ', ') ']:
                clean_line = line[3:].strip()
            elif line.startswith('- '):
                clean_line = line[2:].strip()
            
            questions.append(clean_line)
    
    if not questions and sot_paradigm:
        # Fallback question if none were extracted
        questions = [
            "How would you define or quantify the terms in your statement?",
            "What evidence supports your assertion?",
            "Have you considered alternative perspectives to this view?"
        ]
    
    return questions

def direct_analyze_text(text, mode="standard", use_sot=True):
    """
    Analyze text using direct Ollama integration and SoT.
    """
    # Use Ollama to detect issues
    prompt = f"""
    You are an expert at identifying issues in statements that could benefit from Socratic questioning.
    
    Please analyze this text: "{text}"
    
    INSTRUCTIONS:
    - If the statement contains any of the following issues, you MUST identify them:
      * Absolute terms like 'everyone', 'always', 'never', 'all', 'none'
      * Vague or imprecise language that lacks clear definition
      * Claims made without evidence 
      * Generalizations that don't account for exceptions
      * Language that assumes universal applicability 
      * Normative statements that impose values without qualification
    
    - For the specific example "Everyone should own a dog", you would definitely identify:
      * "Everyone" as an absolute term that fails to account for people with allergies, 
        housing restrictions, or different preferences
      * "should" as a normative claim that imposes values without acknowledging cultural 
        or personal differences
    
    YOUR RESPONSE MUST BE VALID JSON WITH NO TEXT BEFORE OR AFTER IT. USE THIS EXACT STRUCTURE:
    
    {{"issues":[{{"term":"word-here","issue":"label-here","description":"explanation-here","confidence":0.95}}]}}
    
    Important JSON formatting rules:
    1. Use double quotes (") for all strings and keys
    2. Do not use single quotes (')
    3. Do not include trailing commas
    4. Use a decimal between 0 and 1 for confidence (e.g., 0.8)
    5. Ensure all curly braces and square brackets match correctly
    6. Return ONLY the JSON with no text before or after
    
    If there are no issues, return {{"issues":[]}} with an empty array.
    """
    
    # Get model from config
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    model = "deepseek-r1:7b"  # Default
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                model = config.get("integrations", {}).get("ollama", {}).get("default_model", model)
        except:
            pass
    
    # Create a system prompt for the LLM that emphasizes JSON output
    system_prompt = """
    You are an expert AI assistant that analyzes statements to identify logical issues.
    You must respond in valid JSON format according to the instructions.
    """
    
    # Generate issues using direct Ollama integration - Include system prompt and focus on correct output format
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            try:
                # Parse the chat response format
                data = response.json()
                if "message" in data and "content" in data["message"]:
                    response = data["message"]["content"]
                else:
                    # If we didn't get a proper chat response, use the text
                    response = response.text
            except json.JSONDecodeError:
                # If we can't decode as JSON, use the text directly
                response = response.text
        else:
            # Fallback to generate API if chat fails
            response, _ = direct_ollama_generate(prompt, model=model, temperature=0.3, max_tokens=800)
            
    except Exception as e:
        print(f"Error using chat API: {e}, falling back to generate")
        # Fallback to original method
        response, _ = direct_ollama_generate(prompt, model=model, temperature=0.3, max_tokens=800)
    
    # Extract JSON from response
    try:
        # Handle streaming responses where each line might be a JSON object
        if '\n' in response and any('{' in line for line in response.split('\n')):
            print("Detected potential streaming response format")
            # Try to extract JSON from each line
            json_lines = [line for line in response.split('\n') if line.strip()]
            
            # Check if any line has a complete JSON object with issues array
            for line in json_lines:
                if '{"issues":' in line and '}' in line:
                    # Extract just this line to parse
                    json_start = line.find('{')
                    json_end = line.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        response = line[json_start:json_end]
                        print("Found complete JSON object in streaming response")
                        break
        
        # Standard JSON extraction
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            print(f"Extracted JSON structure starting with: {json_str[:50]}...")
            
            # Try to clean up and fix common JSON issues
            clean_json_str = json_str.strip()
            # Handle trailing commas
            clean_json_str = clean_json_str.replace(',}', '}')
            clean_json_str = clean_json_str.replace(',]', ']')
            
            try:
                data = json.loads(clean_json_str)
                issues = data.get("issues", [])
                print(f"Successfully parsed JSON with {len(issues)} issues")
            except json.JSONDecodeError as je:
                print(f"JSON decode error: {je}. Attempting simplified parsing...")
                
                # Check if we have a string that contains issue data but isn't valid JSON
                if '"issues"' in clean_json_str:
                    # Simplified parsing approach - just extract the issues array
                    issues_match = re.search(r'"issues"\s*:\s*(\[.*?\])', clean_json_str, re.DOTALL)
                    if issues_match:
                        issues_json = issues_match.group(1)
                        try:
                            issues = json.loads(issues_json)
                            print(f"Extracted issues array with {len(issues)} issues")
                        except json.JSONDecodeError:
                            # Still can't parse - create simple fallback issue
                            issues = [create_fallback_issue(response)]
                    else:
                        # Create a fallback issue if we can't extract the array
                        issues = [create_fallback_issue(response)]
                else:
                    # No issues keyword found - use fallback
                    issues = [create_fallback_issue(response)]
        else:
            print(f"No JSON structure found in response - using pattern matching")
            # Save debug info
            with open("/tmp/ai_debug_response.txt", "w") as f:
                f.write(f"Original response:\n{response}\n\n")
            # Use pattern matching to find potential issues
            issues = extract_issues_via_patterns(response, text)
            if not issues:
                # If nothing found, create a general fallback issue
                issues = [create_fallback_issue(response)]
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        # Save problematic response for debugging
        with open("/tmp/ai_debug_response.txt", "w") as f:
            f.write(f"Error: {str(e)}\n\nOriginal response:\n{response}\n\n")
        issues = [create_fallback_issue(response)]
        
    # Ensure there's always a full result structure returned
    if 'return' in locals():
        # This means we've already returned from the function
        return locals()['return']
        
    
    # Determine SoT paradigm if enabled
    sot_paradigm = None
    reasoning = None
    
    if use_sot and issues:  # Only try to use SoT if we actually found issues
        try:
            from socratic_clarifier.integrations.sot_integration import SoTIntegration
            sot = SoTIntegration()
            
            if sot.available:
                # Classify the text
                sot_paradigm = sot.classify_question(text)
                
                # Generate reasoning
                reasoning = sot.generate_reasoning(text, issues, paradigm=sot_paradigm)
                print(f"Generated SoT reasoning with paradigm '{sot_paradigm}'")
        except Exception as e:
            print(f"Error using SoT integration: {e}")
            # No fallback - if it doesn't work, we don't want artificial reasoning
    
    # Generate Socratic questions only if there are actual issues detected
    questions = generate_socratic_questions(text, issues, sot_paradigm) if issues else []
    
    # Build the result
    result = {
        "text": text,
        "issues": issues,
        "questions": questions,
        "reasoning": reasoning,
        "sot_paradigm": sot_paradigm,
        "confidence": sum(issue.get("confidence", 0) for issue in issues) / len(issues) if issues else 0.0,
        "sot_enabled": use_sot,
        "model": model,
        "provider": "ollama",
        "reflective_ecosystem_used": REFLECTIVE_ECOSYSTEM_AVAILABLE
    }
    
    return result

def process_feedback(question: str, helpful: bool, paradigm: Optional[str] = None):
    """
    Process feedback on question effectiveness through the reflective ecosystem if available.
    
    Args:
        question: The question that received feedback
        helpful: Whether the question was helpful
        paradigm: Optional paradigm that generated the question
        
    Returns:
        Success status
    """
    if not REFLECTIVE_ECOSYSTEM_AVAILABLE:
        return False
    
    try:
        enhancer = get_enhancer()
        enhancer.process_feedback(question, helpful, paradigm)
        return True
    except Exception as e:
        print(f"Error processing feedback: {e}")
        return False

def get_reflective_ecosystem_status():
    """
    Get information about the reflective ecosystem.
    
    Returns:
        Dictionary with status information
    """
    if not REFLECTIVE_ECOSYSTEM_AVAILABLE:
        return {
            "available": False,
            "reason": "Reflective ecosystem module not available"
        }
    
    try:
        enhancer = get_enhancer()
        report = enhancer.get_performance_report()
        
        return {
            "available": True,
            "report": report,
            "global_coherence": report.get("global_coherence", 0.0),
            "ollama_available": report.get("ollama_available", False),
            "ollama_model": report.get("ollama_model", None)
        }
    except Exception as e:
        return {
            "available": False,
            "reason": f"Error getting status: {e}"
        }
