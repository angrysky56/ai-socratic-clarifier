#!/usr/bin/env python3
"""
Test script for the RAG context fix in AI-Socratic-Clarifier.

This script performs a simple test to verify that the RAG document content
is correctly used as the primary text for analysis.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_rag_analysis():
    """Test direct_analyze_text with document context."""
    try:
        # Import the direct_integration module
        from web_interface.direct_integration import direct_analyze_text
        
        # Create a simple test document
        test_document = {
            "document_id": "test-doc-1",
            "filename": "test_document.txt",
            "content": """
            Everyone needs to follow these exact protocols without deviation.
            All users must always use the system between 9am and 5pm only.
            The system is never wrong and should be trusted completely.
            """,
            "relevance": 0.95
        }
        
        # Simple user query
        user_query = "Analyze this document for issues"
        
        # Call direct_analyze_text with document context
        logger.info("Testing direct_analyze_text with document context...")
        result = direct_analyze_text(user_query, mode="standard", use_sot=True, document_context=[test_document])
        
        # Print the result
        logger.info(f"Analysis result:")
        logger.info(f"Text: {result.get('text')}")
        logger.info(f"Issues found: {len(result.get('issues', []))}")
        
        for i, issue in enumerate(result.get('issues', [])):
            logger.info(f"Issue {i+1}: {issue.get('term')} - {issue.get('issue')}")
            logger.info(f"  Description: {issue.get('description')}")
        
        logger.info(f"Questions generated: {len(result.get('questions', []))}")
        for i, question in enumerate(result.get('questions', [])):
            logger.info(f"Question {i+1}: {question}")
        
        # Verify that the issues found are from the document content, not the user query
        document_terms = ["Everyone", "All", "always", "never", "completely"]
        issues_found = [issue.get('term') for issue in result.get('issues', [])]
        
        # Check if any document terms were found in the issues
        document_issues_found = any(term in issues_found for term in document_terms)
        
        if document_issues_found:
            logger.info("✅ SUCCESS: Issues from document content were correctly identified")
            return True
        else:
            logger.error("❌ FAILURE: No issues from document content were identified")
            logger.error("This suggests the system is still analyzing the user query instead of document content")
            return False
        
    except Exception as e:
        logger.error(f"Error running test: {e}")
        return False

def main():
    """Run the test."""
    print("\n" + "="*70)
    print("   AI-Socratic-Clarifier RAG Context Fix Test")
    print("="*70 + "\n")
    
    # Check if the fix has been applied
    direct_integration_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'web_interface', 'direct_integration.py'))
    backup_path = f"{direct_integration_path}.rag_fix_bak"
    
    if os.path.exists(backup_path):
        logger.info("RAG context fix appears to have been applied (backup file exists)")
    else:
        logger.warning("RAG context fix may not have been applied yet (no backup file found)")
        logger.warning("Please run fix_rag_context.py first")
    
    # Run the test
    success = test_rag_analysis()
    
    print("\n" + "="*70)
    if success:
        print("   Test PASSED! RAG context is correctly used for analysis.")
    else:
        print("   Test FAILED! RAG context is not correctly used for analysis.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
