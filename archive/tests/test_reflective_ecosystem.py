#!/usr/bin/env python3
"""
Test script for the reflective ecosystem implementation.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sequential_thinking.reflective_ecosystem import ReflectiveEcosystem
from sequential_thinking.integration import get_enhancer

def test_ollama_connector():
    """Test the Ollama connector functionality."""
    print("\n=== Testing Ollama Connector ===")
    ecosystem = ReflectiveEcosystem()
    
    print(f"Ollama available: {ecosystem.ollama.available}")
    if ecosystem.ollama.available:
        print(f"Using model: {ecosystem.ollama.default_model}")
        
        # Test question generation with Ollama
        text = "Artificial intelligence will inevitably lead to human obsolescence."
        issues = [
            {"term": "artificial intelligence", "issue": "vague_term", "confidence": 0.85},
            {"term": "inevitably", "issue": "stereotype", "confidence": 0.75},
            {"term": "human obsolescence", "issue": "unclear_reference", "confidence": 0.8}
        ]
        
        print("\nGenerating questions with Ollama...")
        questions = ecosystem.ollama.generate_questions(
            text=text,
            issues=issues,
            paradigm="conceptual_chaining",
            max_questions=5
        )
        
        print(f"Generated {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
    else:
        print("Ollama not available. Skipping question generation test.")

def test_basic_functionality():
    """Test basic functionality of the reflective ecosystem."""
    print("\n=== Testing Basic Functionality ===")
    ecosystem = ReflectiveEcosystem()
    
    # Test paradigm selection
    text1 = "The equation x^2 + 5x + 6 = 0 can be solved using factoring."
    paradigm1 = ecosystem.select_paradigm(text1)
    print(f"Text: '{text1}'")
    print(f"Selected paradigm: {paradigm1}")
    
    text2 = "The legal interpretation of this clause has evolved over time."
    paradigm2 = ecosystem.select_paradigm(text2)
    print(f"\nText: '{text2}'")
    print(f"Selected paradigm: {paradigm2}")
    
    text3 = "Democracy represents the ideals of freedom and equality."
    paradigm3 = ecosystem.select_paradigm(text3)
    print(f"\nText: '{text3}'")
    print(f"Selected paradigm: {paradigm3}")
    
    # Test question generation
    print("\n=== Testing Question Generation ===")
    issues = [
        {"term": "democracy", "issue": "vague_term", "confidence": 0.8},
        {"term": "freedom", "issue": "unclear_reference", "confidence": 0.7}
    ]
    
    questions = ecosystem.generate_questions(text3, issues)
    print(f"Generated questions for '{text3}':")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")

def test_integration():
    """Test integration with the enhancer."""
    print("\n=== Testing Integration with Enhancer ===")
    enhancer = get_enhancer()
    
    text = "All students should be required to learn programming."
    issues = [
        {"term": "all students", "issue": "stereotype", "confidence": 0.85},
        {"term": "programming", "issue": "vague_term", "confidence": 0.7},
        {"term": "required", "issue": "non_inclusive", "confidence": 0.6}
    ]
    
    original_questions = [
        "What do you mean by 'all students'?",
        "How would you define 'programming' in this context?"
    ]
    
    enhanced_questions = enhancer.enhance_questions(
        text=text,
        issues=issues,
        original_questions=original_questions,
        sot_paradigm="conceptual_chaining",
        max_questions=5
    )
    
    print(f"Original questions ({len(original_questions)}):")
    for i, q in enumerate(original_questions, 1):
        print(f"{i}. {q}")
    
    print(f"\nEnhanced questions ({len(enhanced_questions)}):")
    for i, q in enumerate(enhanced_questions, 1):
        print(f"{i}. {q}")
    
    # Test feedback
    print("\n=== Testing Feedback Processing ===")
    for i, question in enumerate(enhanced_questions):
        # Alternate between positive and negative feedback
        helpful = (i % 2 == 0)
        enhancer.process_feedback(question, helpful, "conceptual_chaining")
        print(f"Processed feedback for question {i+1}: {'Helpful' if helpful else 'Not helpful'}")
    
    # Get performance report
    report = enhancer.get_performance_report()
    print("\nPerformance Report:")
    print(f"- Global coherence: {report['global_coherence']:.2f}")
    print(f"- Total questions generated: {report['total_questions_generated']}")
    print(f"- Total questions rated: {report['total_questions_rated']}")
    print(f"- Overall effectiveness: {report['overall_effectiveness']:.2f}")
    print(f"- Ollama available: {report.get('ollama_available', False)}")
    if report.get('ollama_model'):
        print(f"- Using Ollama model: {report.get('ollama_model')}")
    
    # Print metrics for each paradigm
    print("\nParadigm Metrics:")
    for paradigm, metrics in report['node_metrics'].items():
        print(f"- {paradigm}: weight={metrics['weight']:.2f}, effectiveness={metrics.get('effectiveness', 0):.2f}")

def test_with_socratic_clarifier():
    """Test with a real instance of the Socratic Clarifier (if available)."""
    print("\n=== Testing with Socratic Clarifier ===")
    try:
        from socratic_clarifier.core import SocraticClarifier
        
        # Initialize the clarifier
        clarifier = SocraticClarifier()
        
        # Get the enhancer
        enhancer = get_enhancer()
        
        # Text to analyze
        text = "Everyone knows that artificial intelligence will take over all jobs."
        
        # First, get the regular analysis
        regular_analysis = clarifier.analyze(text)
        
        print(f"Analysis identified {len(regular_analysis.issues)} issues:")
        for i, issue in enumerate(regular_analysis.issues, 1):
            print(f"{i}. Issue with '{issue.get('term', '')}' - {issue.get('type', 'unknown')}")
        
        print("\nRegular Socratic Questions:")
        for i, question in enumerate(regular_analysis.questions, 1):
            print(f"{i}. {question}")
        
        # Now enhance the questions
        enhanced_questions = enhancer.enhance_questions(
            text=text,
            issues=regular_analysis.issues,
            original_questions=regular_analysis.questions,
            sot_paradigm=regular_analysis.sot_paradigm,
            max_questions=5
        )
        
        print("\nEnhanced Questions:")
        for i, question in enumerate(enhanced_questions, 1):
            print(f"{i}. {question}")
        
    except ImportError:
        print("Socratic Clarifier not available in this environment. Skipping test.")

def main():
    """Main test function."""
    print("==================================================")
    print("  Testing Reflective Ecosystem Implementation")
    print("==================================================")
    
    # First test Ollama connector
    test_ollama_connector()
    
    # Test basic functionality
    test_basic_functionality()
    
    # Test integration
    test_integration()
    
    # Test with Socratic Clarifier
    test_with_socratic_clarifier()
    
    print("\n==================================================")
    print("  All tests completed")
    print("==================================================")

if __name__ == "__main__":
    main()
