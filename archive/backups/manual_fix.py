#!/usr/bin/env python3
"""
Manual fix for direct_integration.py string literal issue.
This script fixes the syntax error in the direct_integration.py file.
"""

import re
import os

def fix_direct_integration_syntax():
    file_path = "web_interface/direct_integration.py"
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the document context processing section
    doc_context_pattern = r"# Process any document context if provided\s*document_text = \"\"\s*if document_context:"
    
    # The correctly formatted improved document context section
    improved_doc_context = """# Process any document context if provided
    document_text = ""
    if document_context:
        logger.info(f"Processing document context with {len(document_context)} documents")
        
        # Get config to check context limits
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        context_limit = 50000  # Default high limit
        use_model_for_rag = True
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                context_limit = config.get("settings", {}).get("rag_context_limit", 50000)
                use_model_for_rag = config.get("settings", {}).get("use_model_for_rag", True)
            except:
                pass
        
        # Format document content with clear structure and more content
        document_text = "\\n\\n===== REFERENCE DOCUMENTS =====\\n"
        total_chars = 0
        
        for i, doc in enumerate(document_context):
            if isinstance(doc, dict) and "content" in doc:
                content = doc.get("content", "")
                filename = doc.get("filename", f"Document {i+1}")
                relevance = doc.get("relevance", None)
                
                if content:
                    doc_header = f"\\n----- DOCUMENT {i+1}: {filename}"
                    if relevance:
                        doc_header += f" (Relevance: {relevance:.2f})"
                    doc_header += " -----\\n"
                    
                    document_text += doc_header
                    
                    # Add as much content as possible within the limits
                    content_to_add = content
                    # Check if adding this would exceed our context limit
                    if total_chars + len(content_to_add) > context_limit:
                        # Truncate to fit within limit
                        available_chars = max(0, context_limit - total_chars)
                        if available_chars > 100:  # Only add if we can add a meaningful amount
                            content_to_add = content[:available_chars] + "... [content truncated to fit context window]"
                        else:
                            # Skip this document if we can't add enough content
                            document_text += "Document content omitted to fit context window.\\n"
                            continue
                    
                    document_text += content_to_add + "\\n"
                    total_chars += len(doc_header) + len(content_to_add)
                    
                    # If we've exceeded our context limit, stop adding documents
                    if total_chars >= context_limit:
                        document_text += "\\n[Additional documents omitted to fit context window]"
                        break
        
        # Add clear instructions for the LLM
        document_text += "\\n\\n===== INSTRUCTIONS =====\\n"
        document_text += "1. Use the information from the REFERENCE DOCUMENTS above to inform your analysis\\n"
        document_text += "2. Cite specific information from documents when relevant to the analysis\\n"
        document_text += "3. Acknowledge if the information in the documents contradicts or supports the user statement\\n"
        document_text += "4. Do not fabricate information that is not in the documents or the user's statement\\n\\n"
        
        logger.info(f"Added {total_chars} characters of document context from {len(document_context)} documents")"""
    
    # Find the starting point of the section we want to replace
    match = re.search(doc_context_pattern, content)
    if not match:
        print("Could not find the document context processing section")
        return False
    
    # Find the end of the section we want to replace
    start_pos = match.start()
    
    # Find the next section after this block
    next_section_match = re.search(r"\n\s*# (?!Process any document context)", content[start_pos:])
    if next_section_match:
        end_pos = start_pos + next_section_match.start()
    else:
        # If we can't find the next section, just use a simple pattern to find the end of this block
        end_match = re.search(r"document_text \+= .+?\n", content[start_pos:])
        if end_match:
            end_pos = start_pos + end_match.end()
        else:
            print("Could not determine the end of the document context section")
            return False
    
    # Replace the content
    new_content = content[:start_pos] + improved_doc_context + content[end_pos:]
    
    # Write the fixed content
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Fixed syntax error in {file_path}")
    return True

if __name__ == "__main__":
    # Apply the fix
    fix_direct_integration_syntax()
