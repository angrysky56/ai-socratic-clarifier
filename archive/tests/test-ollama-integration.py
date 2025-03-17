#!/usr/bin/env python
"""
Test script for Ollama integration with Socratic Clarifier
"""
import os
import sys
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path to find our enhanced_clarifier module
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from enhanced_clarifier import EnhancedClarifier
    logger.info("Successfully imported EnhancedClarifier")
except ImportError as e:
    logger.error(f"Failed to import EnhancedClarifier: {e}")
    sys.exit(1)

def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running")
            return True
        else:
            print(f"✗ Ollama returned unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Ollama is not running: {e}")
        return False

def test_ollama_integration():
    """Test the Ollama integration"""
    print("Testing Ollama integration...")
    
    if not check_ollama():
        print("Please start Ollama first and try again")
        return
    
    try:
        # Create an enhanced clarifier with a longer timeout
        config = {
            "ollama": {
                "model": "llama3",  # Use the model you have installed
                "timeout": 60,  # Increase timeout for testing
            }
        }
        clarifier = EnhancedClarifier(config)
        
        # Test with a sample question
        question = "What is the relationship between temperature and pressure in a gas?"
        
        print(f"\nProcessing question: {question}")
        start_time = time.time()
        
        result = clarifier.process(question)
        
        end_time = time.time()
        print(f"Processing took {end_time - start_time:.2f} seconds\n")
        
        # Display the results
        print(f"Clarification:\n{result['clarification']}\n")
        print("Socratic Questions:")
        for i, q in enumerate(result['socratic_questions'], 1):
            print(f"{i}. {q}")
        
        print("\n✓ Ollama integration test successful")
        
    except Exception as e:
        print(f"✗ Ollama integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ollama_integration()
