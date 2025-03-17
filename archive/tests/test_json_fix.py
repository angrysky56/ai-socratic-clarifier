#!/usr/bin/env python3
"""
Test script to verify the JSON parsing fixes in the direct_integration.py file.
"""
import os
import sys
import json
from web_interface.direct_integration import direct_analyze_text

def test_analysis(text):
    """Test analyzing text and print the result."""
    print(f"Testing analysis of: '{text}'")
    print("-" * 40)
    
    try:
        # Save the original stdout to restore it later
        import sys
        original_stdout = sys.stdout
        from io import StringIO
        # Capture stdout to get the debug messages
        debug_output = StringIO()
        sys.stdout = debug_output
        
        # Run the analysis
        result = direct_analyze_text(text, mode="standard", use_sot=True)
        
        # Restore stdout
        sys.stdout = original_stdout
        
        # Print the captured debug output
        print("Debug output:")
        print(debug_output.getvalue())
        
        print("\nAnalysis result:")
        print(f"Detected issues: {len(result.get('issues', []))}")
        
        for i, issue in enumerate(result.get("issues", [])):
            print(f"\nIssue {i+1}:")
            print(f"  Term: {issue.get('term', 'Unknown')}")
            print(f"  Issue: {issue.get('issue', 'Unknown')}")
            print(f"  Confidence: {issue.get('confidence', 0)}")
            
        print(f"\nGenerated questions: {len(result.get('questions', []))}")
        for i, question in enumerate(result.get("questions", [])):
            print(f"  {i+1}. {question}")
        
        return True
    except Exception as e:
        print(f"Analysis failed with error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """Main function to run tests."""
    test_inputs = [
        "Cheese is the best food.",
        "Everyone should own a dog.",
        "Technology always improves people's lives.",
        "This statement is completely correct.",
        "The world would be better if people just followed my advice."
    ]
    
    success_count = 0
    for test_input in test_inputs:
        success = test_analysis(test_input)
        if success:
            success_count += 1
        print("\n" + "=" * 60 + "\n")
    
    print(f"Test results: {success_count} of {len(test_inputs)} tests passed.")

if __name__ == "__main__":
    main()
