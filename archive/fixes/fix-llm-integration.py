#!/usr/bin/env python3
"""
Fix for LLM integration issues in the AI-Socratic-Clarifier.
"""
import os
from pathlib import Path
import re

def fix_direct_integration():
    """Fix direct_integration.py to properly handle document_context and ensure LLM integration."""
    file_path = Path(__file__).parent / "web_interface" / "direct_integration.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(file_path) + ".llm_fix_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Ensure the document_context parameter is in the right position
    # Find the function signature
    function_pattern = r"def direct_analyze_text\(.*?\):"
    function_match = re.search(function_pattern, content)
    
    if function_match:
        function_sig = function_match.group(0)
        
        # Check if document_context is already in the function signature
        if "document_context" in function_sig:
            print("document_context already in function signature, no change needed")
        else:
            # Add document_context parameter
            new_sig = function_sig.replace("max_questions=5):", "max_questions=5, document_context=None):")
            content = content.replace(function_sig, new_sig)
            print("Added document_context parameter to function signature")
    else:
        print("Could not find direct_analyze_text function signature")
    
    # Fix document content handling by adding it directly
    prompt_update_pattern = r'Please analyze this text: "{text}"'
    if prompt_update_pattern in content:
        new_prompt = 'Please analyze this text: "{text}"'
        if "{document_text}" not in content:
            # Add document_text to the prompt
            new_prompt_with_context = 'Please analyze this text: "{text}"{document_text}'
            content = content.replace(new_prompt, new_prompt_with_context)
            print("Added document_text to prompt")
    
    # Add document_context initialization if needed
    doc_context_init = """    # Initialize document_context if not provided
    if document_context is None:
        document_context = []
    
    # Process any document context if provided
    document_text = ""
    if document_context:
        logger.info(f"Processing document context with {len(document_context)} documents")
        for doc in document_context:
            if isinstance(doc, dict) and "content" in doc:
                doc_content = doc.get("content", "")
                if doc_content:
                    document_text += f"\\n\\nRelevant document context:\\n{doc_content[:1000]}..."
"""
    
    # Find suitable insertion point after the function definition
    if "def direct_analyze_text" in content:
        # Find the position after docstring
        function_start = content.find("def direct_analyze_text")
        docstring_start = content.find('"""', function_start)
        
        if docstring_start != -1:
            docstring_end = content.find('"""', docstring_start + 3)
            if docstring_end != -1:
                docstring_end += 3  # Move past the closing quotes
                
                # Check if we already have the document_context code
                if "# Initialize document_context if not provided" not in content[docstring_end:docstring_end+200]:
                    # Insert after docstring
                    content = content[:docstring_end] + "\n" + doc_context_init + content[docstring_end:]
                    print("Added document_context initialization code")
                else:
                    print("Document context initialization already exists")
        else:
            print("Could not find docstring in direct_analyze_text function")
    
    # Fix LLM call to ensure it works
    ollama_call_pattern = r"response = requests\.post\(\s*\"http://localhost:11434/api/chat\","
    if ollama_call_pattern in content:
        # Update the Ollama API call to be more robust
        improved_call = """
        try:
            # Try Ollama chat API
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
                # Success! Process the response
                try:
                    data = response.json()
                    if "message" in data and "content" in data["message"]:
                        response_text = data["message"]["content"]
                    else:
                        response_text = response.text
                except Exception as e:
                    logger.error(f"Error parsing Ollama response: {e}")
                    response_text = response.text
            else:
                # Fallback to generate API if chat fails
                logger.warning(f"Ollama chat API returned {response.status_code}, falling back to generate")
                response_text, _ = direct_ollama_generate(prompt, model=model, temperature=0.3, max_tokens=800)
        except Exception as e:
            # Network error or other issues
            logger.error(f"Error connecting to Ollama: {e}, falling back to generate")
            response_text, _ = direct_ollama_generate(prompt, model=model, temperature=0.3, max_tokens=800)
        """
        
        # Find the original try block and replace it
        try_block_start = content.find("try:")
        try_block_end = content.find("except Exception as e:", try_block_start)
        
        if try_block_start != -1 and try_block_end != -1:
            # Replace the entire try block
            content = content[:try_block_start] + "    # Use robust Ollama connection" + improved_call + content[try_block_end:]
            print("Replaced Ollama API call with more robust version")
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed direct_integration.py")
    return True

def fix_enhanced_routes():
    """Fix enhanced_routes.py to ensure proper LLM integration."""
    file_path = Path(__file__).parent / "web_interface" / "enhanced_routes.py"
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = str(file_path) + ".llm_fix_bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Enhance error handling for LLM calls
    api_call_pattern = r"result = direct_analyze_text\(message, mode, use_sot, document_context=document_context\)"
    if api_call_pattern in content:
        # Add detailed debug logging
        enhanced_call = """try:
                # Try with document_context parameter and detailed logging
                logger.info(f"Calling direct_analyze_text with: message='{message[:50]}...', mode='{mode}', use_sot={use_sot}, document_context={len(document_context)} items")
                result = direct_analyze_text(message, mode, use_sot, document_context=document_context)
                logger.info(f"LLM analysis completed successfully: {len(result.get('issues', []))} issues, {len(result.get('questions', []))} questions")
            except TypeError as e:
                if "document_context" in str(e):
                    # Fallback to call without document_context
                    logger.warning(f"document_context parameter error: {e}, falling back to version without document_context")
                    result = direct_analyze_text(message, mode, use_sot)
                    
                    # Add document context to the result manually
                    if document_context:
                        result["document_context"] = document_context
                else:
                    # Re-raise any other errors
                    logger.error(f"TypeError in direct_analyze_text: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error in direct_analyze_text: {e}")
                # Attempt basic fallback
                result = {
                    "text": message,
                    "issues": [],
                    "questions": ["Could you elaborate more on what you mean?", "Would you mind providing more details?"],
                    "reasoning": None,
                    "sot_paradigm": None,
                    "confidence": 0.0,
                    "sot_enabled": use_sot,
                    "model": "fallback",
                    "provider": "error_handler",
                    "document_context": document_context
                }
                logger.info("Using fallback response due to error")"""
        
        # Replace all occurrences of the direct call with enhanced version
        content = content.replace(api_call_pattern, enhanced_call)
        print("Enhanced error handling for LLM calls")
    
    # Write the updated content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed enhanced_routes.py")
    return True

def main():
    """Main function."""
    print("Fixing LLM integration issues...")
    
    # Fix direct_integration.py
    fix_direct_integration()
    
    # Fix enhanced_routes.py
    fix_enhanced_routes()
    
    print("Done!")

if __name__ == "__main__":
    main()
