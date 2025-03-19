#!/usr/bin/env python3
"""
Minimal fix script for the direct_integration.py file.
This script makes specific and limited changes to fix the advanced RAG functionality.
"""

import os

def minimal_fix():
    """Apply a minimal fix to direct_integration.py without extensive rewrites."""
    file_path = os.path.join('web_interface', 'direct_integration.py')
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Find the start of the document context section
    start_idx = -1
    for i, line in enumerate(lines):
        if "document_text = \"\"" in line:
            start_idx = i
            break
    
    if start_idx == -1:
        print("Could not find document context section")
        return False
    
    # Find the end of the section (where the document context is actually used)
    end_idx = -1
    for i in range(start_idx, len(lines)):
        if "document_text += f" in lines[i]:
            end_idx = i
            break
    
    if end_idx == -1:
        print("Could not find document context usage")
        return False
    
    # Create the replacement content
    replacement = [
        "    document_text = \"\"\n",
        "    if document_context:\n",
        "        logger.info(f\"Processing document context with {len(document_context)} documents\")\n",
        "        # Basic document integration - just include the first portion of each document\n",
        "        document_text = \"\\n\\n===== REFERENCE DOCUMENTS =====\\n\"\n",
        "        \n",
        "        for i, doc in enumerate(document_context):\n",
        "            if isinstance(doc, dict) and \"content\" in doc:\n",
        "                content = doc.get(\"content\", \"\")\n",
        "                filename = doc.get(\"filename\", f\"Document {i+1}\")\n",
        "                \n",
        "                if content:\n",
        "                    document_text += f\"\\n----- DOCUMENT {i+1}: {filename} -----\\n\"\n",
        "                    document_text += f\"{content[:2000]}\" + (\"...\" if len(content) > 2000 else \"\") + \"\\n\"\n",
        "        \n",
        "        # Add basic instructions\n",
        "        document_text += \"\\n\\n===== INSTRUCTIONS =====\\n\"\n",
        "        document_text += \"Use the document information to inform your analysis.\\n\"\n"
    ]
    
    # Replace the section with our simplified version
    new_lines = lines[:start_idx] + replacement + lines[end_idx+1:]
    
    # Write the modified file
    with open(file_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Applied minimal fix to {file_path}")
    return True

if __name__ == "__main__":
    minimal_fix()
