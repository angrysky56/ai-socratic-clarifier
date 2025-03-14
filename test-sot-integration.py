#!/usr/bin/env python
"""
Test script for Sketch-of-Thought integration

This script verifies that the SoT package is properly integrated.
"""
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure we're in the right directory
project_root = Path(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, str(project_root))

# Try to import directly first
print("Testing direct import from sketch_of_thought...")
try:
    from sketch_of_thought import SoT
    sot = SoT()
    print(f"✓ Direct import successful - available paradigms: {sot.avaliable_paradigms()}")
except ImportError as e:
    print(f"✗ Direct import failed: {e}")
    print("  This is expected if the package is not installed")

# Try using our wrapper
print("\nTesting SoT wrapper...")
try:
    from sot_integration import SoTWrapper
    sot_wrapper = SoTWrapper()
    print(f"✓ SoT wrapper initialized successfully")
    
    # Test the wrapper functions
    question = "What causes the seasons to change on Earth?"
    paradigm = sot_wrapper.classify_question(question)
    print(f"✓ Question classified as: {paradigm}")
    
    system_prompt = sot_wrapper.get_system_prompt(paradigm)
    print(f"✓ Got system prompt for {paradigm} ({len(system_prompt)} chars)")
    
    context = sot_wrapper.get_initialized_context(paradigm, question)
    print(f"✓ Got initialized context with {len(context)} messages")
    
except Exception as e:
    print(f"✗ SoT wrapper test failed: {e}")
    print("  Check the sot_integration.py file for issues")

# Test integration with clarifier
print("\nTesting integration with SocraticClarifier...")
try:
    sys.path.insert(0, str(project_root))
    from socratic_clarifier.clarifier import SocraticClarifier
    from sot_integration import SoTWrapper
    
    # Initialize SoT wrapper
    sot = SoTWrapper()
    
    # Initialize clarifier with SoT
    clarifier = SocraticClarifier()
    
    # Use SoT to enhance processing
    question = "How does gravity work?"
    paradigm = sot.classify_question(question)
    system_prompt = sot.get_system_prompt(paradigm)
    
    print(f"✓ Question classified as '{paradigm}'")
    print(f"✓ Got system prompt for clarification")
    
    # Process the question with the clarifier
    result = clarifier.process(question)
    print(f"✓ Processed question with clarifier")
    print(f"  Generated {len(result['socratic_questions'])} socratic questions")
    
    print("\nSocratic Questions:")
    for i, q in enumerate(result['socratic_questions'], 1):
        print(f"{i}. {q}")
        
except Exception as e:
    print(f"✗ Clarifier integration test failed: {e}")
    print("  Check the clarifier implementation for issues")

print("\nTest completed.")
