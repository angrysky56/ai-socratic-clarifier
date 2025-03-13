"""
Example showing how to enhance the AI-Socratic-Clarifier with local LLMs.

This example demonstrates:
1. Automatic detection of available LLM providers (LM Studio, Ollama)
2. Using local LLMs to enhance question generation
3. Checking for multimodal capabilities
4. Using SoT reasoning with LLM-enhanced insights
"""

import sys
import os
import json
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from socratic_clarifier import SocraticClarifier
from socratic_clarifier.integrations.integration_manager import IntegrationManager
from socratic_clarifier.integrations.lm_studio import LMStudioProvider
from socratic_clarifier.integrations.ollama import OllamaProvider

from loguru import logger
import argparse


def load_config():
    """Load configuration from config.json."""
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json'))
    default_config = {
        "integrations": {
            "lm_studio": {
                "enabled": True,
                "base_url": "http://localhost:1234/v1",
                "api_key": None,
                "default_model": "default",
                "timeout": 60
            },
            "ollama": {
                "enabled": True,
                "base_url": "http://localhost:11434/api",
                "api_key": None,
                "default_model": "llama3",
                "default_embedding_model": "nomic-embed-text",
                "timeout": 60
            }
        },
        "settings": {
            "prefer_provider": "auto",
            "use_llm_questions": True,
            "use_llm_reasoning": True,
            "use_sot": True,
            "use_multimodal": True
        }
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        else:
            logger.warning(f"Configuration file not found at {config_path}. Using default configuration.")
            return default_config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}. Using default configuration.")
        return default_config


class EnhancedClarifier(SocraticClarifier):
    """
    Enhanced version of SocraticClarifier that leverages local LLMs
    while preserving the core SoT functionality.
    """
    
    def __init__(self, mode: str = "standard", config: dict = None):
        """Initialize the enhanced clarifier."""
        super().__init__(mode=mode)
        
        # Load config if not provided
        if config is None:
            config = load_config()
        
        # Initialize the integration manager with the config
        self.integration_manager = IntegrationManager(config=config)
        
        # Add a timeout for Ollama operations to prevent hanging
        if "integrations" in config and "ollama" in config["integrations"]:
            if "timeout" not in config["integrations"]["ollama"]:
                config["integrations"]["ollama"]["timeout"] = 10  # Set a shorter timeout
        
        # Check available providers
        llm_providers = self.integration_manager.get_available_llm_providers()
        if llm_providers:
            logger.info(f"Local LLM providers available: {', '.join(llm_providers)}")
            self.has_llm = True
        else:
            logger.info("No local LLM providers detected. Using base SoT functionality only.")
            self.has_llm = False
        
        # Check multimodal support
        self.multimodal_available = self.integration_manager.is_multimodal_available()
        if self.multimodal_available:
            logger.info("Multimodal capabilities detected!")
    
    def analyze(self, text: str, use_local_llm: bool = True):
        """
        Analyze text with enhanced capabilities when local LLM is available.
        
        Args:
            text: The text to analyze
            use_local_llm: Whether to use local LLM enhancement if available
            
        Returns:
            AnalysisResult with enhanced questions and reasoning
        """
        # First, use the base clarifier to detect issues and get SoT paradigm
        result = super().analyze(text)
        
        # If no issues detected or LLM enhancement not requested, return base result
        if not result.issues or not use_local_llm or not self.has_llm:
            return result
        
        # Enhance with local LLM if available
        if self.has_llm and use_local_llm:
            # Generate enhanced questions
            enhanced_questions = self.integration_manager.generate_socratic_questions(
                text=text,
                issues=result.issues,
                use_sot=(result.sot_paradigm is not None)
            )
            
            # If we got enhanced questions, use them
            if enhanced_questions:
                result.questions = enhanced_questions
            
            # Enhance reasoning if we have a paradigm
            if result.sot_paradigm:
                enhanced_reasoning = self.integration_manager.enhance_reasoning(
                    text=text,
                    issues=result.issues,
                    sot_paradigm=result.sot_paradigm
                )
                
                # If we got enhanced reasoning, use it
                if enhanced_reasoning:
                    result.reasoning = enhanced_reasoning
        
        return result
    
    def analyze_multimodal(self, text: str, image_path: str):
        """
        Analyze text and image together using multimodal capabilities.
        
        Args:
            text: The text to analyze
            image_path: Path to the image file
            
        Returns:
            AnalysisResult with multimodal insights
        """
        if not self.multimodal_available:
            logger.warning("Multimodal analysis requested but no multimodal provider available.")
            return super().analyze(text)
        
        logger.info(f"Performing multimodal analysis with image: {image_path}")
        
        # Get a multimodal-capable provider
        provider = self.integration_manager.get_multimodal_provider()
        if not provider:
            logger.error("Failed to get a multimodal provider.")
            return super().analyze(text)
        
        # First, analyze the text as normal
        result = super().analyze(text)
        
        # Then, enhance with multimodal insights if we have issues
        if result.issues:
            # Create messages for multimodal analysis
            system_prompt = """
            Analyze both the text and image together. Look for:
            1. Any inconsistencies between the text and image
            2. Visual elements that might clarify or contradict ambiguous text
            3. Visual bias that might reinforce or contradict textual bias
            
            Generate Socratic questions that help clarify meaning, considering both textual and visual content.
            """
            
            # Create context from the detected issues
            context = f"Text: \"{text}\"\n\nDetected issues:\n"
            for i, issue in enumerate(result.issues):
                context += f"{i+1}. {issue.get('issue', 'Unknown issue')} - '{issue.get('term', '')}'\n"
                context += f"   {issue.get('description', '')}\n"
            
            context += "\nAnalyze the image and provide multimodal insights that might address these issues."
            
            # Create messages for the multimodal API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": context},
                    {"type": "image", "image_url": {"url": image_path}}
                ]}
            ]
            
            # Generate multimodal insights
            generated_text, _ = provider.generate_multimodal(
                messages=messages,
                max_tokens=768,
                temperature=0.7
            )
            
            # Extract questions from the response
            multimodal_questions = []
            for line in generated_text.strip().split("\n"):
                line = line.strip()
                if line and ("?" in line) and not line.startswith("#") and not line.startswith("<"):
                    # Clean up numbering or bullet points
                    clean_line = line
                    if line[0].isdigit() and line[1:3] in ['. ', ') ']:
                        clean_line = line[3:].strip()
                    elif line.startswith('- '):
                        clean_line = line[2:].strip()
                    
                    multimodal_questions.append(clean_line)
            
            # Add multimodal questions to results
            if multimodal_questions:
                result.questions.extend(multimodal_questions)
                
                # Add a note about multimodal analysis
                if result.reasoning:
                    multimodal_note = "\n#image_analysis → #multimodal_context → #enhanced_understanding"
                    result.reasoning = result.reasoning.replace("</think>", f"{multimodal_note}\n</think>")
        
        return result


def main():
    """Run the enhanced clarifier example."""
    parser = argparse.ArgumentParser(description="Enhanced Socratic Clarifier Example")
    parser.add_argument("--text", type=str, help="Text to analyze")
    parser.add_argument("--image", type=str, help="Optional image path for multimodal analysis")
    parser.add_argument("--mode", type=str, default="standard", help="Operating mode")
    parser.add_argument("--base-only", action="store_true", help="Use only base SoT functionality")
    parser.add_argument("--config", type=str, help="Path to custom config.json file")
    args = parser.parse_args()
    
    # Load configuration
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
            logger.info(f"Using custom configuration from {args.config}")
        except Exception as e:
            logger.error(f"Error loading custom configuration: {e}. Using default configuration.")
            config = load_config()
    else:
        config = load_config()
    
    # Define example texts if none provided
    example_texts = [
        "Men are better leaders than women.",
        "These results were significant and prove our approach works.",
        "Most people think this is a good idea, but they haven't considered the implications.",
        "The chairman made a decision that impacted all policemen in the department."
    ]
    
    # Create the enhanced clarifier with the loaded config
    clarifier = EnhancedClarifier(mode=args.mode, config=config)
    
    # If text provided, use it; otherwise, use examples
    if args.text:
        texts = [args.text]
    else:
        texts = example_texts
    
    # Process each text
    for i, text in enumerate(texts):
        print(f"\nExample {i+1}: \"{text}\"")
        print("-" * 70)
        
        # Analyze with multimodal if image provided, otherwise standard analysis
        if args.image and i == 0 and clarifier.multimodal_available:
            result = clarifier.analyze_multimodal(text, args.image)
            print(f"Multimodal analysis with image: {args.image}")
        else:
            result = clarifier.analyze(text, use_local_llm=not args.base_only)
        
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


if __name__ == "__main__":
    main()
