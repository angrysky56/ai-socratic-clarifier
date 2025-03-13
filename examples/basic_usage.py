"""
Basic usage example of the AI-Socratic-Clarifier system.
This demonstrates how to analyze text and get Socratic questions.
"""

import sys
import os
import subprocess

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_and_install_sot():
    """Check if Sketch-of-Thought is installed and install if not available."""
    try:
        # Try to import SoT
        from sketch_of_thought import SoT
        print("Sketch-of-Thought is already installed.")
        return True
    except ImportError:
        # SoT is not installed, attempt to install it
        print("Sketch-of-Thought not found. Attempting to install...")
        try:
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'install_sot.py'))
            if os.path.exists(script_path):
                result = subprocess.call([sys.executable, script_path])
                if result == 0:
                    print("Successfully installed Sketch-of-Thought!")
                    return True
                else:
                    print("Failed to install Sketch-of-Thought. Please install it manually.")
                    return False
            else:
                print(f"SoT installation script not found at {script_path}")
                return False
        except Exception as e:
            print(f"Error installing Sketch-of-Thought: {e}")
            return False

def main():
    """Run basic examples of the Socratic clarifier."""
    
    # Ensure SoT is installed before continuing
    if not check_and_install_sot():
        print("Cannot continue without Sketch-of-Thought. Please install it manually.")
        print("You can install it by running: python install_sot.py")
        return
    
    # Now import SocraticClarifier
    try:
        from socratic_clarifier import SocraticClarifier
    except ImportError as e:
        print(f"Failed to import SocraticClarifier: {e}")
        print("Make sure the package is properly installed.")
        return
    
    print("AI-Socratic-Clarifier Basic Usage Example")
    print("=" * 50)
    
    # Create a clarifier with the default mode
    clarifier = SocraticClarifier(mode="standard")
    
    # Example texts to analyze
    example_texts = [
        "Men are better leaders than women.",
        "These results were significant and show that our approach works.",
        "Most people think this is a good idea, but they haven't considered the implications.",
        "The chairman made a decision that impacted all policemen in the department."
    ]
    
    # Process each example
    for i, text in enumerate(example_texts):
        print(f"\nExample {i+1}: \"{text}\"")
        print("-" * 50)
        
        # Analyze the text
        result = clarifier.analyze(text)
        
        # Show the results
        print(f"Detected {len(result.issues)} issues:")
        for j, issue in enumerate(result.issues):
            print(f"  {j+1}. {issue['issue']} - '{issue['term']}' ({issue['confidence']:.2f})")
            print(f"     {issue['description']}")
        
        print("\nSuggested questions:")
        for j, question in enumerate(result.questions):
            print(f"  {j+1}. {question}")
        
        if result.reasoning:
            print("\nReasoning:")
            print(f"  {result.reasoning}")
            print(f"  SoT Paradigm: {result.sot_paradigm}")
    
    # Try different modes
    print("\n\nTrying different modes")
    print("=" * 50)
    
    text = "These results were significant and show that our approach works."
    
    for mode in ["academic", "casual"]:
        print(f"\nMode: {mode}")
        print("-" * 50)
        
        clarifier.set_mode(mode)
        result = clarifier.analyze(text)
        
        print(f"Detected {len(result.issues)} issues")
        print("\nSuggested questions:")
        for j, question in enumerate(result.questions):
            print(f"  {j+1}. {question}")

if __name__ == "__main__":
    main()
