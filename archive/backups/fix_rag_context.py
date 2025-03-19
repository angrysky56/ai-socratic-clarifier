#!/usr/bin/env python3
"""
Fix for RAG context usage in the AI-Socratic-Clarifier.

This script patches the direct_integration.py file to ensure that when document context
is provided, the RAG document content is used as the primary text for analysis, not just
the user's query text.
"""

import os
import sys
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.rag_fix_bak"
    try:
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup at {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False

def fix_direct_integration():
    """
    Fix the direct_integration.py file to properly use RAG document content.
    """
    direct_integration_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'web_interface', 'direct_integration.py'))
    
    if not os.path.exists(direct_integration_path):
        logger.error(f"File not found: {direct_integration_path}")
        return False
    
    # Create backup
    if not backup_file(direct_integration_path):
        logger.error("Failed to create backup, aborting.")
        return False
    
    try:
        with open(direct_integration_path, 'r') as f:
            content = f.read()
        
        # The key issue is in the prompt construction
        # We need to change how the document context is used
        
        # Find the section that constructs the prompt
        prompt_section = re.search(r'prompt\s*=\s*f""".*?"""', content, re.DOTALL)
        
        if prompt_section:
            original_prompt = prompt_section.group(0)
            
            # Create the new prompt that properly uses document context
            new_prompt = r'''prompt = f"""
    You are an expert at identifying issues in statements that could benefit from Socratic questioning.
    
    {document_text if document_context else f'Please analyze this text: "{text}"'}
    
    {'If no document context is provided, analyze the user query. If document context is provided, analyze the document content in relation to the user query. The user query is: "' + text + '"' if document_context else ''}
    
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
    """'''
            
            # Replace the original prompt with the new one
            updated_content = content.replace(original_prompt, new_prompt)
            
            # Also modify the document_text construction to make instructions clearer
            doc_context_section = re.search(r'document_text = "".*?document_text \+= "Use the document information to inform your analysis\.\n"', content, re.DOTALL)
            
            if doc_context_section:
                original_doc_section = doc_context_section.group(0)
                
                # Create improved document context construction
                new_doc_section = '''document_text = ""
    if document_context:
        logger.info(f"Processing document context with {len(document_context)} documents")
        # Basic document integration - include document content for analysis
        document_text = f"USER QUERY: {text}\\n\\n"
        document_text += "DOCUMENT CONTENT TO ANALYZE:\\n"
        
        for i, doc in enumerate(document_context):
            if isinstance(doc, dict) and "content" in doc:
                content = doc.get("content", "")
                filename = doc.get("filename", f"Document {i+1}")
                
                if content:
                    document_text += f"\\n----- DOCUMENT {i+1}: {filename} -----\\n"
                    document_text += f"{content[:4000]}" + ("..." if len(content) > 4000 else "") + "\\n"
        
        # Add clear analysis instructions
        document_text += "\\n\\nINSTRUCTIONS FOR ANALYSIS:\\n"
        document_text += "1. Analyze the DOCUMENT CONTENT above in relation to the USER QUERY.\\n"
        document_text += "2. Identify issues in the document content, not in the user's query.\\n"
        document_text += "3. Focus on analyzing the actual document text rather than the query itself.\\n"'''
                
                # Replace the original document context section with the new one
                updated_content = updated_content.replace(original_doc_section, new_doc_section)
            
            # Write the updated content back to the file
            with open(direct_integration_path, 'w') as f:
                f.write(updated_content)
            
            logger.info(f"Successfully patched {direct_integration_path}")
            return True
        else:
            logger.error("Could not find prompt section in the file")
            return False
            
    except Exception as e:
        logger.error(f"Error fixing direct_integration.py: {e}")
        return False

def fix_document_content_access():
    """
    Fix the document content access in the enhanced_routes.py file.
    """
    enhanced_routes_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'web_interface', 'enhanced_routes.py'))
    
    if not os.path.exists(enhanced_routes_path):
        logger.error(f"File not found: {enhanced_routes_path}")
        return False
    
    # Create backup
    if not backup_file(enhanced_routes_path):
        logger.error("Failed to create backup, aborting.")
        return False
    
    try:
        with open(enhanced_routes_path, 'r') as f:
            content = f.read()
        
        # Find the section that processes document context
        doc_context_section = re.search(r'# Get document content for RAG.*?document_context\[i\]\["relevance"\] = 0\.95', content, re.DOTALL)
        
        if doc_context_section:
            original_section = doc_context_section.group(0)
            
            # Create improved document context handling
            new_section = '''# Get document content for RAG
        if use_rag:
            manager = get_document_manager()
            
            # Add content to document context
            for i, doc in enumerate(document_context):
                if "document_id" in doc and "content" not in doc:
                    content = manager.get_document_content(doc["document_id"])
                    if content:
                        document_context[i]["content"] = content
                        document_context[i]["relevance"] = 0.95  # High relevance for manually selected docs
                        
            # Ensure document content is substantial for analysis
            for i, doc in enumerate(document_context):
                if "content" in doc and len(doc["content"].strip()) < 50:
                    logger.warning(f"Document {i} has very short content ({len(doc['content'])} chars). This may not provide enough context.")'''
            
            # Replace the original section with the new one
            updated_content = content.replace(original_section, new_section)
            
            # Write the updated content back to the file
            with open(enhanced_routes_path, 'w') as f:
                f.write(updated_content)
            
            logger.info(f"Successfully patched {enhanced_routes_path}")
            return True
        else:
            logger.error("Could not find document context section in the file")
            return False
            
    except Exception as e:
        logger.error(f"Error fixing enhanced_routes.py: {e}")
        return False

def main():
    """Run the fixes."""
    print("\n" + "="*70)
    print("   AI-Socratic-Clarifier RAG Context Fix")
    print("="*70 + "\n")
    
    logger.info("Starting RAG context fix...")
    
    # Fix direct_integration.py
    if fix_direct_integration():
        logger.info("✅ Successfully fixed direct_integration.py")
    else:
        logger.error("❌ Failed to fix direct_integration.py")
    
    # Fix enhanced_routes.py
    if fix_document_content_access():
        logger.info("✅ Successfully fixed enhanced_routes.py")
    else:
        logger.error("❌ Failed to fix enhanced_routes.py")
    
    print("\n" + "="*70)
    print("   Fix completed! Please restart the server to apply changes.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
