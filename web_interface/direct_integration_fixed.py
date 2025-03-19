"""
Direct integration for the AI-Socratic-Clarifier with fixed document RAG analysis.
This version ensures correct analysis of document content when RAG is enabled.
"""

import os
import sys
import json
import re
import logging
from typing import List, Dict, Any, Optional
import requests

# Import the reasoning template manager if available
try:
    from socratic_clarifier.reasoning_template_manager import get_reasoning_template_manager
    REASONING_TEMPLATES_AVAILABLE = True
except ImportError:
    REASONING_TEMPLATES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import path for fallbacks
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def direct_analyze_text_for_document(text, document_context, model="gemma3:latest"):
    """
    Analyze document content using direct Ollama integration.
    This specialized function focuses only on document analysis.
    """
    logger.info(f"Analyzing document context with {len(document_context)} documents")
    
    # Build a document-focused prompt
    prompt = "You are an expert at identifying issues in texts that could benefit from Socratic questioning.\n\n"
    prompt += f"USER QUERY: {text}\n\n"
    prompt += "DOCUMENT CONTENT TO ANALYZE:\n"
    
    # Add each document's content
    for i, doc in enumerate(document_context):
        if isinstance(doc, dict) and "content" in doc:
            content = doc.get("content", "")
            filename = doc.get("filename", f"Document {i+1}")
            
            if content:
                prompt += f"\n----- DOCUMENT {i+1}: {filename} -----\n"
                prompt += content + "\n"
    
    # Add clear instructions for document analysis ONLY
    prompt += "\nINSTRUCTIONS:\n"
    prompt += "YOUR TASK IS TO ANALYZE THE DOCUMENT CONTENT ABOVE, NOT THE USER QUERY.\n"
    prompt += "IGNORE THE USER QUERY ENTIRELY - DO NOT ANALYZE THE QUERY ITSELF.\n"
    prompt += "FOCUS EXCLUSIVELY ON ANALYZING THE DOCUMENT TEXT FOR ISSUES SUCH AS:\n"
    prompt += "* Absolute terms like 'everyone', 'always', 'never', 'all', 'none'\n"
    prompt += "* Vague or imprecise language that lacks clear definition\n"
    prompt += "* Claims made without evidence\n"
    prompt += "* Generalizations that don't account for exceptions\n"
    prompt += "* Language that assumes universal applicability\n"
    prompt += "* Normative statements that impose values without qualification\n\n"
    prompt += "Return issues in valid JSON format with no text before or after:\n"
    prompt += '{"issues":[{"term":"actual-word-from-document","issue":"issue-type","description":"explanation","confidence":0.95}]}\n\n'
    prompt += "Only include terms that actually appear in the document.\n"
    prompt += "If there are no issues, return {\"issues\":[]}"
    
    # Use reasoning templates if available
    if REASONING_TEMPLATES_AVAILABLE:
        template_manager = get_reasoning_template_manager()
        active_template = template_manager.get_template()
        
        if active_template:
            # Get system prompt from template
            system_prompt = active_template.get("system_prompt", "")
            
            # Get document analysis prompt template if available
            doc_analysis_template = None
            if "prompt_templates" in active_template and "document_analysis" in active_template["prompt_templates"]:
                doc_analysis_template = active_template["prompt_templates"]["document_analysis"]
                
                # Replace document content placeholder
                document_content = ""
                for i, doc in enumerate(document_context):
                    if isinstance(doc, dict) and "content" in doc:
                        content = doc.get("content", "")
                        filename = doc.get("filename", f"Document {i+1}")
                        
                        if content:
                            document_content += f"\n----- DOCUMENT {i+1}: {filename} -----\n"
                            document_content += content + "\n"
                
                # Fill the template with variables
                prompt = template_manager.fill_prompt_template(
                    doc_analysis_template,
                    {"DOCUMENT_CONTENT": document_content, "USER_QUERY": text}
                )
                
                logger.info("Using document analysis template from reasoning templates")
                return_prompt = False  # Skip the default prompt generation
            else:
                logger.info("No document_analysis template found, using default prompt structure")
                return_prompt = True  # Continue with default prompt generation
        else:
            logger.warning("No active reasoning template found, using default system prompt")
            system_prompt = "You are an expert AI assistant analyzing documents. You MUST analyze the DOCUMENT CONTENT, NOT the user query. The document is the subject of analysis, not the query text. Focus completely on finding issues in the document itself."
            return_prompt = True  # Continue with default prompt generation
    else:
        logger.info("Reasoning templates not available, using default system prompt")
        system_prompt = "You are an expert AI assistant analyzing documents. You MUST analyze the DOCUMENT CONTENT, NOT the user query. The document is the subject of analysis, not the query text. Focus completely on finding issues in the document itself."
        return_prompt = True  # Continue with default prompt generation
        
    # If we're using the template's prompt directly, skip the default prompt generation
    if 'return_prompt' in locals() and not return_prompt:
        # prompt has already been set by the template
        pass
    else:
        pass  # Default prompt is already set above
    
    # Call Ollama
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {
                    "num_ctx": 32768  # Use a large context window for document analysis
                }
            },
            timeout=120  # Longer timeout for large documents
        )
        
        if response.status_code == 200:
            try:
                # Extract content from chat response
                data = response.json()
                if "message" in data and "content" in data["message"]:
                    response_text = data["message"]["content"]
                else:
                    response_text = response.text
                    
                # Extract JSON from response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    
                    # Clean up JSON
                    clean_json_str = json_str.strip()
                    clean_json_str = clean_json_str.replace(',}', '}')
                    clean_json_str = clean_json_str.replace(',]', ']')
                    
                    # Parse JSON
                    data = json.loads(clean_json_str)
                    issues = data.get("issues", [])
                    
                    logger.info(f"Successfully analyzed document with {len(issues)} issues")
                    
                    # Success case - return issues
                    return {
                        "success": True,
                        "issues": issues
                    }
                else:
                    logger.warning("No JSON structure found in document analysis response")
                    return {
                        "success": False,
                        "issues": [],
                        "error": "No JSON structure found in response"
                    }
            except Exception as e:
                logger.error(f"Error parsing document analysis response: {e}")
                return {
                    "success": False,
                    "issues": [],
                    "error": f"Error parsing response: {str(e)}"
                }
        else:
            logger.error(f"Ollama API error: {response.status_code}")
            return {
                "success": False,
                "issues": [],
                "error": f"Ollama API error: {response.status_code}"
            }
    except Exception as e:
        logger.error(f"Error in document analysis: {e}")
        return {
            "success": False,
            "issues": [],
            "error": f"Error in analysis: {str(e)}"
        }
# This function is a wrapper around the original direct_analyze_text
# It will call either the original function or the document-specific one
def fixed_direct_analyze_text(text, mode="standard", use_sot=True, max_questions=5, document_context=None):
    """
    Fixed version that properly handles document analysis.
    """
    # Import original function to use as fallback
    from web_interface.direct_integration import direct_analyze_text as original_analyze
    
    # If no document context, just use the original function
    if not document_context:
        logger.info("No document context provided, using original analyze function")
        return original_analyze(text, mode, use_sot, max_questions)
    
    # Get model from config
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    model = "gemma3:latest"  # Default
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                model = config.get("integrations", {}).get("ollama", {}).get("default_model", model)
    except Exception as e:
        logger.error(f"Error loading config for model: {e}")
    
    # Use the document-specific analyze function
    document_result = direct_analyze_text_for_document(text, document_context, model)
    
    # If document analysis failed, fall back to original function
    if not document_result.get("success", False):
        logger.warning("Document analysis failed, falling back to original analyze function")
        return original_analyze(text, mode, use_sot, max_questions, document_context)
    
    # Get issues from document analysis
    issues = document_result.get("issues", [])
    
    # Use original function to determine SoT paradigm and generate questions
    # We'll import the specific helper function for this if available
    # Otherwise we'll build a basic result
    try:
        from web_interface.direct_integration import generate_socratic_questions
        from socratic_clarifier.integrations.sot_integration import SoTIntegration
        
        # Determine SoT paradigm if enabled
        sot_paradigm = None
        reasoning = None
        
        if use_sot and issues:
            try:
                sot = SoTIntegration()
                if sot.available:
                    # Classify using document text as input
                    doc_text = ""
                    for doc in document_context:
                        if isinstance(doc, dict) and "content" in doc:
                            doc_text += doc.get("content", "") + "\n\n"
                    
                    sot_paradigm = sot.classify_question(doc_text if doc_text else text)
                    
                    # Generate reasoning
                    reasoning = sot.generate_reasoning(doc_text if doc_text else text, issues, paradigm=sot_paradigm)
                    logger.info(f"Generated SoT reasoning with paradigm '{sot_paradigm}'")
            except Exception as e:
                logger.error(f"Error using SoT integration: {e}")
        
        # Generate Socratic questions
        questions = generate_socratic_questions(text, issues, sot_paradigm, max_questions) if issues else []
        
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
            "document_context": document_context,
            "max_questions": max_questions
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error in post-document analysis: {e}")
        
        # Basic fallback result if helpers aren't available
        return {
            "text": text,
            "issues": issues,
            "questions": [f"What evidence supports the claim about '{issue.get('term')}'?" for issue in issues[:max_questions]],
            "reasoning": None,
            "sot_paradigm": None,
            "confidence": sum(issue.get("confidence", 0) for issue in issues) / len(issues) if issues else 0.0,
            "sot_enabled": use_sot,
            "model": model,
            "provider": "ollama",
            "document_context": document_context,
            "max_questions": max_questions
        }
