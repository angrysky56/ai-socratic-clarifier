"""
Advanced example showing Sketch-of-Thought integration with AI-Socratic-Clarifier.
This demonstrates how to leverage SoT reasoning paradigms for different types of questions.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from sketch_of_thought import SoT
    from socratic_clarifier import SocraticClarifier
    SOT_AVAILABLE = True
except ImportError:
    print("WARNING: Sketch-of-Thought package not found. Please install it to run this example.")
    print("You can get it from https://github.com/SimonAytes/SoT")
    SOT_AVAILABLE = False
    sys.exit(1)

def demonstrate_conceptual_chaining():
    """Show examples of conceptual chaining for bias in abstract reasoning."""
    clarifier = SocraticClarifier(mode="academic")
    
    print("\nConceptual Chaining Examples (Good for bias and abstract reasoning)")
    print("-" * 70)
    
    examples = [
        "All immigrants are a drain on the economy.",
        "Technology always improves people's lives.",
        "Women are naturally better caregivers than men."
    ]
    
    for text in examples:
        print(f"\nText: \"{text}\"")
        
        # Set the SoT reasoning paradigm
        clarifier.set_sot_paradigm("conceptual_chaining")
        
        # Analyze the text
        result = clarifier.analyze(text)
        
        print("\nSoT Reasoning:")
        print(f"  {result.reasoning}")
        
        print("\nSuggested Socratic Questions:")
        for question in result.questions:
            print(f"  - {question}")
        
        print("----")

def demonstrate_chunked_symbolism():
    """Show examples of chunked symbolism for numerical claims."""
    clarifier = SocraticClarifier(mode="academic")
    
    print("\nChunked Symbolism Examples (Good for numerical and quantitative claims)")
    print("-" * 70)
    
    examples = [
        "Our product is 50% more effective than leading competitors.",
        "The vast majority of experts agree with this position.",
        "This investment will give you significant returns."
    ]
    
    for text in examples:
        print(f"\nText: \"{text}\"")
        
        # Set the SoT reasoning paradigm
        clarifier.set_sot_paradigm("chunked_symbolism")
        
        # Analyze the text
        result = clarifier.analyze(text)
        
        print("\nSoT Reasoning:")
        print(f"  {result.reasoning}")
        
        print("\nSuggested Socratic Questions:")
        for question in result.questions:
            print(f"  - {question}")
        
        print("----")

def demonstrate_expert_lexicons():
    """Show examples of expert lexicons for domain-specific terms."""
    clarifier = SocraticClarifier(mode="legal")
    
    print("\nExpert Lexicons Examples (Good for domain-specific terminology)")
    print("-" * 70)
    
    examples = [
        "This treatment has been proven effective for most patients.",
        "Under the statute, the defendant's actions constitute gross negligence.",
        "The company has substantial market power in the relevant market."
    ]
    
    for text in examples:
        print(f"\nText: \"{text}\"")
        
        # Set the SoT reasoning paradigm
        clarifier.set_sot_paradigm("expert_lexicons")
        
        # Analyze the text
        result = clarifier.analyze(text)
        
        print("\nSoT Reasoning:")
        print(f"  {result.reasoning}")
        
        print("\nSuggested Socratic Questions:")
        for question in result.questions:
            print(f"  - {question}")
        
        print("----")

def demonstrate_automatic_paradigm_selection():
    """Show how the system can automatically select the right SoT paradigm."""
    clarifier = SocraticClarifier()
    sot = SoT()
    
    print("\nAutomatic Paradigm Selection")
    print("-" * 70)
    
    examples = [
        "The project will increase GDP by 2.5% over the next fiscal year.",
        "Western philosophy has historically neglected non-Western perspectives.",
        "The BRCA1 mutation significantly increases the risk of breast cancer."
    ]
    
    for text in examples:
        # Use SoT to classify the question type
        paradigm = sot.classify_question(text)
        
        print(f"\nText: \"{text}\"")
        print(f"Automatically selected paradigm: {paradigm}")
        
        # Analyze with automatic paradigm
        result = clarifier.analyze(text)
        
        print("\nSoT Reasoning:")
        print(f"  {result.reasoning}")
        
        print("\nSuggested Socratic Questions:")
        for question in result.questions:
            print(f"  - {question}")
        
        print("----")

def main():
    """Run the SoT integration examples."""
    if not SOT_AVAILABLE:
        return
    
    print("Sketch-of-Thought Integration with AI-Socratic-Clarifier")
    print("=" * 70)
    print("This example demonstrates how different SoT reasoning paradigms")
    print("can be applied to different types of clarification needs.")
    
    # Run different paradigm examples
    demonstrate_conceptual_chaining()
    demonstrate_chunked_symbolism()
    demonstrate_expert_lexicons()
    demonstrate_automatic_paradigm_selection()

if __name__ == "__main__":
    main()
