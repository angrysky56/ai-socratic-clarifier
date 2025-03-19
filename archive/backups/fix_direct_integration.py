#!/usr/bin/env python3
"""
Fix script for direct_integration.py to implement Advanced RAG functionality.
This script properly modifies the file without causing syntax errors.
"""

import os
import re

def fix_direct_integration():
    """Enhance how document content is integrated into prompts in direct_integration.py."""
    file_path = os.path.join('web_interface', 'direct_integration.py')
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    # Create a backup just to be safe
    backup_path = f"{file_path}.safe_fix_bak"
    try:
        with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        print(f"Created backup of {file_path} to {backup_path}")
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
    try:
        # Read the file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the section to replace - from the document context processing to the next major section
        section_start = content.find("# Process any document context if provided")
        if section_start == -1:
            print("Could not find document context processing section")
            return False
        
        # Find where to end the replacement
        # Look for either the next function or the next top-level comment after our section
        section_text = content[section_start:]
        next_section_match = re.search(r"\n\s*# [^#\n]+", section_text[50:])  # Skip a bit to avoid matching our own comment
        
        if next_section_match:
            section_end = section_start + 50 + next_section_match.start()
        else:
            # If no next section, look for lines that might be part of the next logic block
            document_text_end = section_text.find("    prompt = f")
            if document_text_end > 0:
                section_end = section_start + document_text_end
            else:
                # Fallback - just replace until we find a blank line followed by a non-comment, non-whitespace line
                match = re.search(r"\n\s*\n\s*[^#\s]", section_text)
                if match:
                    section_end = section_start + match.start()
                else:
                    print("Could not determine the end of the document context section")
                    return False
        
        # The improved document context processing code
        improved_section = """# Process any document context if provided
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
        
        # Replace the section
        new_content = content[:section_start] + improved_section + content[section_end:]
        
        # Write the updated content
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        # Validate the syntax of the Python file
        try:
            import py_compile
            py_compile.compile(file_path, doraise=True)
            print(f"✅ Successfully fixed and validated {file_path}")
            return True
        except py_compile.PyCompileError as e:
            print(f"Syntax error in fixed file: {e}")
            # Restore from backup
            with open(backup_path, 'r') as src, open(file_path, 'w') as dst:
                dst.write(src.read())
            print(f"Restored from backup due to syntax error")
            return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        # Try to restore from backup
        try:
            with open(backup_path, 'r') as src, open(file_path, 'w') as dst:
                dst.write(src.read())
            print(f"Restored from backup due to error")
        except Exception as restore_error:
            print(f"Error restoring from backup: {restore_error}")
        return False

if __name__ == "__main__":
    fix_direct_integration()
