"""
Direct integration patch for the AI-Socratic-Clarifier.
This file adds direct integration with Ollama and SoT.

Fixed version includes:
- Better document RAG handling with direct chat responses
- Mode selection for analysis vs answer
- Improved prompt formatting for documents
"""

import requests
import json
import os
import sys
from typing import List, Dict, Any, Optional
import re
from pathlib import Path
from loguru import logger  # Added import for logger

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

# Added initialize_clarifier function
def initialize_clarifier():
    """
    Initialize and return a SocraticClarifier instance.
    
    Returns:
        SocraticClarifier instance or None if not available
    """
    try:
        from socratic_clarifier import SocraticClarifier
        return SocraticClarifier()
    except ImportError:
        logger.warning("SocraticClarifier not available. Using direct integration.")
        return None

def direct_ollama_generate(prompt, model="deepseek-r1:7b", temperature=0.7, max_tokens=512):
    """
    Generate text using Ollama directly.
    
    Args:
        prompt (str): The prompt to send to Ollama
        model (str): The model to use
        temperature (float): Temperature parameter for generation
        max_tokens (int): Maximum tokens to generate
        
    Returns:
        tuple: (generated_text, full_response)
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

def direct_ollama_chat(messages, model="deepseek-r1:7b", temperature=0.7, max_tokens=512, system_prompt=None):
    """
    Generate chat response using Ollama directly.
    
    Args:
        messages (list): List of message dictionaries with role and content
        model (str): The model to use
        temperature (float): Temperature parameter for generation
        max_tokens (int): Maximum tokens to generate
        system_prompt (str, optional): System prompt to override the first message
        
    Returns:
        tuple: (generated_text, full_response)
    """
    try:
        # If system_prompt is provided and the first message is a system message,
        # replace its content
        if system_prompt and messages and messages[0]["role"] == "system":
            messages = [{"role": "system", "content": system_prompt}] + messages[1:]
        elif system_prompt:
            # Insert system prompt at the beginning
            messages = [{"role": "system", "content": system_prompt}] + messages
        
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

def generate_socratic_questions(text, issues, sot_paradigm=None, max_questions=5):
    """
    Generate Socratic questions using direct Ollama integration.
    
    Args:
        text (str): The text to analyze
        issues (list): List of detected issues
        sot_paradigm (str, optional): SOT paradigm to use if available
        max_questions (int, optional): Maximum number of questions to generate
        
    Returns:
        list: Generated questions
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
                max_questions=max_questions
            )
            if enhanced_questions:
                return enhanced_questions
        except Exception as e:
            logger.error(f"Error using reflective ecosystem: {e}")
            # Fall back to standard generation
    
    # Standard Ollama generation as fallback
    # Create a system prompt for the LLM
    system_prompt = f"""
    You are a master of Socratic questioning who helps people improve their critical thinking.
    
    Your purpose is to craft precise, thoughtful questions that identify potential issues in people's statements.
    
    Based on the text and specific issues detected, create {max_questions} thought-provoking questions that will:
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
        context += f"\nGenerate questions using the {sot_paradigm} format. Begin with analyzing the issues, then present {max_questions} questions.\n"
    
    # Create messages for the chat API
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context}
    ]
    
    # Generate questions using direct Ollama integration
    # Get model from config
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    model = "gemma3:latest"  # Default
    
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
        fallback_questions = [
            "How would you define or quantify the terms in your statement?",
            "What evidence supports your assertion?",
            "Have you considered alternative perspectives to this view?"
        ]
        questions = fallback_questions[:max_questions]
    
    # Limit to the requested number of questions
    return questions[:max_questions]

def direct_analyze_text(text, mode="standard", use_sot=True, max_questions=5, document_context=None, chat_mode="analyze"):
    """
    Analyze text using direct Ollama integration and SoT.
    
    Args:
        text (str): The text to analyze
        mode (str, optional): Analysis mode (standard or reflective)
        use_sot (bool, optional): Whether to use SOT if available
        max_questions (int, optional): Maximum number of questions to generate
        document_context (list, optional): List of documents to use as context
        chat_mode (str, optional): "analyze" for Socratic analysis or "answer" for direct answers
        
    Returns:
        dict: Analysis results
    """
    # Initialize document_context if not provided
    if document_context is None:
        document_context = []
    
    # Process any document context if provided
    document_text = ""
    formatted_context = ""
    if document_context:
        logger.info(f"Processing document context with {len(document_context)} documents")
        
        formatted_context = "Context from documents:\n\n"
        for idx, doc in enumerate(document_context):
            if isinstance(doc, dict) and "content" in doc:
                # Add document content to formatted context
                content = doc.get("content", "")
                filename = doc.get("filename", f"Document {idx+1}")
                if content:
                    formatted_context += f"--- {filename} ---\n{content}\n\n"
                    # Also keep the old format for backward compatibility
                    document_text += f"\n\nDocument content: {content[:500]}..."
    
    # If chat_mode is "answer", skip issue detection and directly generate an answer
    if chat_mode == "answer" and document_context:
        logger.info("Using direct answer mode with document context")
        
        # Create a system prompt for direct answers
        system_prompt = """
        You are a helpful AI assistant answering questions based on provided document context. 
        Your role is to:
        
        1. Carefully read the document context provided
        2. Answer the user's question directly and accurately based on this context
        3. If the answer isn't in the context, acknowledge this and provide your best general answer
        4. Be concise but comprehensive, focusing on the most relevant information
        5. Include specific details, quotes, or references from the document when appropriate
        
        Do not analyze the user's question itself - focus only on answering it based on the document context.
        """
        
        # Format the user query with context
        user_message = f"Question: {text}\n\n{formatted_context}\n\nPlease answer my question based on the document context provided."
        
        # Create messages for chat
        messages = [
            {"role": "user", "content": user_message}
        ]
        
        # Get model from config
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        model = "gemma3:latest"  # Default
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    model = config.get("integrations", {}).get("ollama", {}).get("default_model", model)
            except:
                pass
        
        # Generate direct answer
        answer, _ = direct_ollama_chat(messages, model=model, system_prompt=system_prompt)
        
        # Return a simplified result with the direct answer
        return {
            "text": text,
            "answer": answer,
            "issues": [],
            "questions": [],
            "reasoning": None,
            "sot_paradigm": None,
            "confidence": 1.0,  # High confidence for direct answers
            "sot_enabled": False,
            "model": model,
            "provider": "ollama",
            "reflective_ecosystem_used": False,
            "max_questions": 0,
            "chat_mode": "answer",
            "document_context": document_context
        }

    # For analysis mode, continue with the original flow but with improved prompting
    # Use Ollama to detect issues
    analysis_prompt = f"""
    You are an expert at identifying issues in statements that could benefit from Socratic questioning.
    
    Please analyze this text: "{text}"{document_text}
    
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
    model = "gemma3:latest"  # Default
    
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
                    {"role": "user", "content": analysis_prompt}
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
            response, _ = direct_ollama_generate(analysis_prompt, model=model, temperature=0.3, max_tokens=800)
            
    except Exception as e:
        logger.error(f"Error using chat API: {e}, falling back to generate")
        # Fallback to original method
        response, _ = direct_ollama_generate(analysis_prompt, model=model, temperature=0.3, max_tokens=800)
    
    # Extract JSON from response
    try:
        # Handle streaming responses where each line might be a JSON object
        if '\n' in response and any('{' in line for line in response.split('\n')):
            logger.debug("Detected potential streaming response format")
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
                        logger.debug("Found complete JSON object in streaming response")
                        break
        
        # Standard JSON extraction
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            logger.debug(f"Extracted JSON structure starting with: {json_str[:50]}...")
            
            # Try to clean up and fix common JSON issues
            clean_json_str = json_str.strip()
            # Handle trailing commas
            clean_json_str = clean_json_str.replace(',}', '}')
            clean_json_str = clean_json_str.replace(',]', ']')
            
            try:
                data = json.loads(clean_json_str)
                issues = data.get("issues", [])
                logger.info(f"Successfully parsed JSON with {len(issues)} issues")
            except json.JSONDecodeError as je:
                logger.error(f"JSON decode error: {je}. Attempting simplified parsing...")
                
                # Check if we have a string that contains issue data but isn't valid JSON
                if '"issues"' in clean_json_str:
                    # Simplified parsing approach - just extract the issues array
                    issues_match = re.search(r'"issues"\s*:\s*(\[.*?\])', clean_json_str, re.DOTALL)
                    if issues_match:
                        issues_json = issues_match.group(1)
                        try:
                            issues = json.loads(issues_json)
                            logger.info(f"Extracted issues array with {len(issues)} issues")
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
            logger.warning(f"No JSON structure found in response - using pattern matching")
            # Save debug info
            with open("/tmp/ai_debug_response.txt", "w") as f:
                f.write(f"Original response:\n{response}\n\n")
            # Use pattern matching to find potential issues
            issues = extract_issues_via_patterns(response, text)
            if not issues:
                # If nothing found, create a general fallback issue
                issues = [create_fallback_issue(response)]
    except Exception as e:
        logger.error(f"Error extracting JSON: {e}")
        # Save problematic response for debugging
        with open("/tmp/ai_debug_response.txt", "w") as f:
            f.write(f"Error: {str(e)}\n\nOriginal response:\n{response}\n\n")
        issues = [create_fallback_issue(response)]
    
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
                logger.info(f"Generated SoT reasoning with paradigm '{sot_paradigm}'")
        except Exception as e:
            logger.error(f"Error using SoT integration: {e}")
            # No fallback - if it doesn't work, we don't want artificial reasoning
    
    # Generate Socratic questions only if there are actual issues detected
    questions = generate_socratic_questions(text, issues, sot_paradigm, max_questions) if issues else []
    
    # Generate direct answer if requested, even in analysis mode
    direct_answer = None
    if document_context and (chat_mode == "mixed" or (chat_mode == "analyze" and not issues)):
        # If in mixed mode or if in analyze mode but no issues were found, generate a direct answer
        logger.info("Generating direct answer from document context")
        
        # Create a system prompt for direct answers
        answer_system_prompt = """
        You are a helpful AI assistant answering questions based on provided document context. 
        Be concise, accurate, and directly reference the document content when answering.
        If the answer isn't in the context, say so clearly before providing your best general answer.
        """
        
        # Format the user query with context
        user_message = f"Question: {text}\n\n{formatted_context}\n\nPlease answer my question based on the document context provided."
        
        # Create messages for chat
        messages = [
            {"role": "user", "content": user_message}
        ]
        
        # Generate direct answer
        direct_answer, _ = direct_ollama_chat(messages, model=model, system_prompt=answer_system_prompt)
    
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
        "reflective_ecosystem_used": REFLECTIVE_ECOSYSTEM_AVAILABLE,
        "max_questions": max_questions,
        "chat_mode": chat_mode,
        "direct_answer": direct_answer
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
    # Try using the SocraticClarifier first
    try:
        clarifier = initialize_clarifier()
        if clarifier and hasattr(clarifier, 'process_feedback'):
            logger.info(f"Processing feedback via SocraticClarifier")
            success = clarifier.process_feedback(question, helpful, paradigm)
            return success
    except Exception as e:
        logger.error(f"Error processing feedback via SocraticClarifier: {e}")
        # Fall back to direct processing
    
    # Direct integration fallback
    if not REFLECTIVE_ECOSYSTEM_AVAILABLE:
        logger.warning("Reflective ecosystem not available. Feedback not processed.")
        return False
    
    try:
        enhancer = get_enhancer()
        enhancer.process_feedback(question, helpful, paradigm)
        logger.info(f"Feedback processed successfully via direct enhancer")
        return True
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        return False

def get_reflective_ecosystem_status():
    """
    Get information about the reflective ecosystem.
    
    Returns:
        Dictionary with status information
    """
    # Try using the SocraticClarifier first
    try:
        clarifier = initialize_clarifier()
        if clarifier and hasattr(clarifier, 'get_reflective_ecosystem_status'):
            logger.info(f"Getting reflective ecosystem status via SocraticClarifier")
            status = clarifier.get_reflective_ecosystem_status()
            return status
    except Exception as e:
        logger.error(f"Error getting reflective ecosystem status via SocraticClarifier: {e}")
        # Fall back to direct status check
    
    # Direct integration fallback
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

def process_image(image_path: str, text: Optional[str] = None, mode: str = "standard", 
                 use_sot: bool = True, max_questions: int = 5) -> Dict[str, Any]:
    """
    Process an image using the SocraticClarifier.
    
    Args:
        image_path (str): Path to the image file
        text (str, optional): Additional text context for the image
        mode (str, optional): Analysis mode (standard or reflective)
        use_sot (bool, optional): Whether to use SOT if available
        max_questions (int, optional): Maximum number of questions to generate
        
    Returns:
        dict: Analysis results
    """
    try:
        # Initialize the clarifier
        clarifier = initialize_clarifier()
        if clarifier and hasattr(clarifier, 'analyze_image'):
            logger.info(f"Processing image via SocraticClarifier: {image_path}")
            
            # Process the image
            if mode == "reflective" and hasattr(clarifier, 'analyze_image_reflective'):
                issues, questions, reasoning = clarifier.analyze_image_reflective(
                    image_path=image_path,
                    text=text,
                    use_sot=use_sot,
                    max_questions=max_questions
                )
            else:
                issues, questions, reasoning = clarifier.analyze_image(
                    image_path=image_path,
                    text=text,
                    use_sot=use_sot,
                    max_questions=max_questions
                )
            
            # Build result dict
            sot_paradigm = clarifier.sot_paradigm if hasattr(clarifier, 'sot_paradigm') else None
            model = clarifier.model if hasattr(clarifier, 'model') else "llama3"
            provider = clarifier.provider if hasattr(clarifier, 'provider') else "ollama"
            
            result = {
                "image_path": image_path,
                "text": text or "",
                "issues": issues,
                "questions": questions,
                "reasoning": reasoning,
                "sot_paradigm": sot_paradigm,
                "confidence": sum(issue.get("confidence", 0) for issue in issues) / len(issues) if issues else 0.0,
                "sot_enabled": use_sot,
                "model": model,
                "provider": provider,
                "reflective_ecosystem_used": REFLECTIVE_ECOSYSTEM_AVAILABLE,
                "max_questions": max_questions
            }
            
            return result
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        
    # For image processing, we don't have a complete direct fallback
    # Return an error response
    return {
        "error": "Image processing failed. Multimodal capabilities may not be available.",
        "success": False,
        "image_path": image_path,
        "text": text or "",
        "issues": [],
        "questions": [],
        "reasoning": None,
        "sot_paradigm": None,
        "confidence": 0.0,
        "sot_enabled": use_sot,
        "provider": "none",
        "reflective_ecosystem_used": False,
        "max_questions": max_questions
    }

def process_document(document_path: str, query: Optional[str] = None, mode: str = "standard",
                    use_sot: bool = True, max_questions: int = 5) -> Dict[str, Any]:
    """
    Process a document using the SocraticClarifier.
    
    Args:
        document_path (str): Path to the document file
        query (str, optional): Query to apply to the document content
        mode (str, optional): Analysis mode (standard or reflective)
        use_sot (bool, optional): Whether to use SOT if available
        max_questions (int, optional): Maximum number of questions to generate
        
    Returns:
        dict: Analysis results
    """
    try:
        # Initialize the clarifier
        clarifier = initialize_clarifier()
        
        if clarifier and hasattr(clarifier, 'analyze_document'):
            logger.info(f"Processing document via SocraticClarifier: {document_path}")
            
            # Process the document
            if mode == "reflective" and hasattr(clarifier, 'analyze_document_reflective'):
                issues, questions, reasoning, content = clarifier.analyze_document_reflective(
                    document_path=document_path,
                    query=query,
                    use_sot=use_sot,
                    max_questions=max_questions
                )
            else:
                issues, questions, reasoning, content = clarifier.analyze_document(
                    document_path=document_path,
                    query=query,
                    use_sot=use_sot,
                    max_questions=max_questions
                )
            
            # Build result dict
            sot_paradigm = clarifier.sot_paradigm if hasattr(clarifier, 'sot_paradigm') else None
            model = clarifier.model if hasattr(clarifier, 'model') else "llama3"
            provider = clarifier.provider if hasattr(clarifier, 'provider') else "ollama"
            
            result = {
                "document_path": document_path,
                "query": query or "",
                "content": content,
                "issues": issues,
                "questions": questions,
                "reasoning": reasoning,
                "sot_paradigm": sot_paradigm,
                "confidence": sum(issue.get("confidence", 0) for issue in issues) / len(issues) if issues else 0.0,
                "sot_enabled": use_sot,
                "model": model,
                "provider": provider,
                "reflective_ecosystem_used": REFLECTIVE_ECOSYSTEM_AVAILABLE,
                "max_questions": max_questions
            }
            
            return result
    except Exception as e:
        logger.error(f"Error processing document: {e}")
    
    # For document processing, we don't have a complete direct fallback
    # Return an error response
    return {
        "error": "Document processing failed. Document RAG capabilities may not be available.",
        "success": False,
        "document_path": document_path,
        "query": query or "",
        "content": "",
        "issues": [],
        "questions": [],
        "reasoning": None,
        "sot_paradigm": None,
        "confidence": 0.0,
        "sot_enabled": use_sot,
        "provider": "none",
        "reflective_ecosystem_used": False,
        "max_questions": max_questions
    }

def get_supported_modes() -> List[str]:
    """
    Get a list of supported analysis modes.
    
    Returns:
        list: List of supported mode names
    """
    try:
        # Initialize the clarifier
        clarifier = initialize_clarifier()
        
        if clarifier and hasattr(clarifier, 'get_supported_modes'):
            modes = clarifier.get_supported_modes()
            return modes
        else:
            # Default modes if method not available
            return ["standard", "reflective"]
    except Exception as e:
        logger.error(f"Error getting supported modes: {e}")
        # Return default modes if the clarifier fails
        return ["standard", "reflective"]

def get_system_status() -> Dict[str, Any]:
    """
    Get the status of the Socratic Clarifier system.
    
    Returns:
        dict: System status information
    """
    try:
        # Initialize the clarifier
        clarifier = initialize_clarifier()
        
        if clarifier and hasattr(clarifier, 'get_system_status'):
            status = clarifier.get_system_status()
            return status
        else:
            # Create a basic status if method not available
            return {
                "version": "1.0.0",
                "success": True,
                "providers": {
                    "ollama": {"available": True},
                    "sot": {"available": REFLECTIVE_ECOSYSTEM_AVAILABLE},
                    "multimodal": {"available": False},
                    "document_rag": {"available": False}
                },
                "features": {
                    "text_analysis": True,
                    "image_analysis": False,
                    "document_analysis": False,
                    "reflective_ecosystem": REFLECTIVE_ECOSYSTEM_AVAILABLE
                }
            }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        # Create a basic status response if the clarifier fails
        return {
            "error": str(e),
            "success": False,
            "version": "unknown",
            "providers": {
                "ollama": {"available": False},
                "sot": {"available": False},
                "multimodal": {"available": False},
                "document_rag": {"available": False}
            },
            "features": {
                "text_analysis": True,
                "image_analysis": False,
                "document_analysis": False,
                "reflective_ecosystem": False
            }
        }
