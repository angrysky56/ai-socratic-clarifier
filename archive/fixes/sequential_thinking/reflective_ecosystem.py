"""
Reflective Ecosystem Module for AI-Socratic-Clarifier

This module implements a practical reflective ecosystem that enhances the Socratic questioning
by enabling:
1. Context-aware question generation
2. Coherence tracking between different reasoning paradigms
3. Adaptive feedback based on user interactions
4. Direct integration with LLM models through Ollama
"""

import os
import json
import logging
import time
import requests
from typing import List, Dict, Any, Optional, Union
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Load system configuration."""
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '../../../../../../../../config.json'))
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        else:
            logger.warning(f"Configuration file not found at {config_path}")
            return {}
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}

class OllamaConnector:
    """Connector for Ollama API to generate questions."""
    
    def __init__(self):
        """Initialize the Ollama connector."""
        self.config = load_config()
        ollama_config = self.config.get("integrations", {}).get("ollama", {})
        
        # Set up API configuration
        self.base_url = ollama_config.get("base_url", "http://localhost:11434/api")
        if not self.base_url.endswith("/api"):
            self.base_url += "/api"
            
        self.default_model = ollama_config.get("default_model", "deepseek-r1:7b")
        self.timeout = ollama_config.get("timeout", 30)
        self.temperature = ollama_config.get("temperature", 0.7)
        self.available = self._check_availability()
        
        if self.available:
            logger.info(f"Ollama connector initialized with model: {self.default_model}")
        else:
            logger.warning("Ollama not available. Reflective ecosystem will use template-based questions.")
    
    def _check_availability(self):
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url.replace('/api', '')}/api/tags", timeout=5)
            if response.status_code == 200:
                # Check if the configured model is available
                models = response.json().get("models", [])
                model_names = [model.get("name") for model in models]
                
                if self.default_model not in model_names and models:
                    logger.warning(f"Configured model {self.default_model} not available. Using {model_names[0]}")
                    self.default_model = model_names[0]
                elif not models:
                    logger.warning("No models available in Ollama")
                    return False
                
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking Ollama availability: {e}")
            return False
    
    def generate_questions(self, text: str, issues: List[Dict[str, Any]], 
                          paradigm: str, max_questions: int = 5) -> List[str]:
        """
        Generate questions using Ollama.
        
        Args:
            text: The text to analyze
            issues: Detected issues
            paradigm: Reasoning paradigm to use
            max_questions: Maximum number of questions
            
        Returns:
            List of generated questions
        """
        if not self.available:
            return []
            
        # Create the prompt
        prompt = self._create_prompt(text, issues, paradigm, max_questions)
        
        try:
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    "model": self.default_model,
                    "prompt": prompt,
                    "temperature": self.temperature,
                    "max_tokens": 500,
                    "stream": False
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "")
                
                # Extract questions from the response
                questions = self._extract_questions(generated_text)
                
                # Limit to max questions
                return questions[:max_questions]
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return []
    
    def _create_prompt(self, text: str, issues: List[Dict[str, Any]], 
                      paradigm: str, max_questions: int) -> str:
        """
        Create a prompt for generating questions.
        
        Args:
            text: The text to analyze
            issues: Detected issues
            paradigm: Reasoning paradigm
            max_questions: Maximum number of questions
            
        Returns:
            Prompt for the LLM
        """
        # Create the base prompt
        prompt = f"""
You are a master of Socratic questioning who helps people improve their critical thinking.

Please analyze this text: "{text}"

The following issues have been detected:
"""
        
        # Add issues
        for i, issue in enumerate(issues, 1):
            term = issue.get("term", "")
            issue_type = issue.get("issue", "unknown")
            confidence = issue.get("confidence", 0.0)
            prompt += f"{i}. Issue with term '{term}' - Type: {issue_type} (confidence: {confidence:.2f})\n"
        
        # Add instructions based on paradigm
        if paradigm == "conceptual_chaining":
            prompt += f"""
Please use the CONCEPTUAL CHAINING approach to generate {max_questions} Socratic questions.

In CONCEPTUAL CHAINING, your questions should:
- Focus on logical connections between ideas
- Ask how concepts relate to one another
- Explore the chains of reasoning from premises to conclusions
- Draw attention to conceptual relationships
"""
        elif paradigm == "chunked_symbolism":
            prompt += f"""
Please use the CHUNKED SYMBOLISM approach to generate {max_questions} Socratic questions.

In CHUNKED SYMBOLISM, your questions should:
- Focus on precise definitions and measurements
- Ask how abstract terms can be quantified
- Explore mathematical or symbolic relationships
- Break down complex concepts into measurable components
"""
        elif paradigm == "expert_lexicons":
            prompt += f"""
Please use the EXPERT LEXICONS approach to generate {max_questions} Socratic questions.

In EXPERT LEXICONS, your questions should:
- Focus on domain-specific terminology
- Ask about technical definitions and specialized usage
- Explore how experts in the field would interpret the terms
- Inquire about field-specific criteria or standards
"""
        else:
            prompt += f"""
Please generate {max_questions} thoughtful Socratic questions that will help the person clarify their thinking.

Your questions should:
- Address the specific issues identified
- Be open-ended rather than yes/no questions
- Promote deeper reflection
- Be genuinely helpful for improving the statement
"""
        
        prompt += """
IMPORTANT INSTRUCTIONS:
1. Return ONLY the questions, one per line
2. Do not number the questions
3. Do not include any explanations or commentary
4. Ensure each question directly addresses one of the identified issues
5. Format as clear, complete questions ending with question marks
"""
        
        return prompt
    
    def _extract_questions(self, text: str) -> List[str]:
        """
        Extract questions from generated text.
        
        Args:
            text: Generated text
            
        Returns:
            List of questions
        """
        lines = text.strip().split('\n')
        questions = []
        
        for line in lines:
            line = line.strip()
            # Remove numbering if present
            if len(line) > 2 and line[0].isdigit() and line[1:3] in ['. ', ') ']:
                line = line[3:].strip()
            elif line.startswith('- '):
                line = line[2:].strip()
                
            # Check if it's a question
            if line and line.endswith('?'):
                questions.append(line)
        
        return questions


class ReasoningNode:
    """
    A node representing a specific reasoning paradigm or thinking approach.
    
    Each node tracks its efficacy and can adapt based on feedback from user interactions.
    """
    def __init__(self, paradigm: str, description: str, initial_weight: float = 1.0):
        """
        Initialize a reasoning node.
        
        Args:
            paradigm: The reasoning paradigm this node represents
            description: Description of the reasoning approach
            initial_weight: Initial efficacy weight (0.0 to 1.0)
        """
        self.paradigm = paradigm
        self.description = description
        self.weight = initial_weight  # Efficacy weight
        self.feedback_history = []    # Track user feedback
        self.questions_generated = 0  # Count of questions generated
        self.questions_rated = 0      # Count of questions that received feedback
        self.positive_ratings = 0     # Count of positive ratings
    
    def update_weight(self, feedback: float):
        """
        Update the node's weight based on feedback.
        
        Args:
            feedback: Feedback value (-1.0 to 1.0)
        """
        # Track feedback
        self.feedback_history.append(feedback)
        
        # Update question counts
        self.questions_rated += 1
        if feedback > 0:
            self.positive_ratings += 1
        
        # Adjust weight using exponential moving average
        alpha = 0.2  # Learning rate
        self.weight = (1 - alpha) * self.weight + alpha * (1.0 + feedback) / 2.0
        
        # Ensure weight stays in valid range
        self.weight = max(0.1, min(self.weight, 1.0))
        
        logger.debug(f"Node {self.paradigm} weight updated to {self.weight:.2f}")
    
    def generate_questions(self, text: str, issues: List[Dict[str, Any]], 
                          question_templates: Dict[str, List[str]]) -> List[str]:
        """
        Generate questions based on this node's reasoning paradigm.
        
        Args:
            text: The text being analyzed
            issues: The detected issues in the text
            question_templates: Templates for question generation
            
        Returns:
            List of generated questions
        """
        # Get templates for this paradigm
        templates = question_templates.get(self.paradigm, [])
        if not templates:
            # Fallback to generic templates
            templates = question_templates.get("generic", [])
        
        questions = []
        for issue in issues:
            term = issue.get("term", "")
            issue_type = issue.get("issue", "unknown")
            
            # Replace placeholders in templates
            for template in templates:
                question = template.replace("{term}", term)
                questions.append(question)
        
        # Track the number of questions generated
        self.questions_generated += len(questions)
        
        return questions
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this reasoning node."""
        return {
            "paradigm": self.paradigm,
            "weight": self.weight,
            "questions_generated": self.questions_generated,
            "questions_rated": self.questions_rated,
            "positive_ratings": self.positive_ratings,
            "effectiveness": self.positive_ratings / max(1, self.questions_rated),
            "average_feedback": np.mean(self.feedback_history) if self.feedback_history else 0.0
        }


class ReflectiveEcosystem:
    """
    A reflective ecosystem that coordinates multiple reasoning nodes.
    
    The ecosystem tracks overall coherence and adapts questioning strategies
    based on feedback and context.
    """
    def __init__(self):
        """Initialize the reflective ecosystem."""
        # Initialize nodes for different reasoning paradigms
        self.nodes = {
            "conceptual_chaining": ReasoningNode(
                "conceptual_chaining",
                "Reasoning that connects concepts through logical steps"
            ),
            "chunked_symbolism": ReasoningNode(
                "chunked_symbolism",
                "Reasoning that breaks down complex ideas into symbolic representations"
            ),
            "expert_lexicons": ReasoningNode(
                "expert_lexicons",
                "Reasoning that utilizes domain-specific technical terminology"
            ),
            "socratic_questioning": ReasoningNode(
                "socratic_questioning",
                "Classic Socratic inquiry methods"
            )
        }
        
        # Define question templates for each paradigm
        self.question_templates = self._load_question_templates()
        
        # Initialize Ollama connector
        self.ollama = OllamaConnector()
        
        # Track global coherence metrics
        self.global_coherence = 1.0
        self.question_history = []
        
        # Settings for adaptation
        self.learning_rate = 0.2
        self.context_awareness = 0.5
    
    def _load_question_templates(self) -> Dict[str, List[str]]:
        """Load question templates for different reasoning paradigms."""
        templates = {
            "conceptual_chaining": [
                "How does {term} relate to the core concept?",
                "What is the logical connection between {term} and your conclusion?",
                "Can you trace the reasoning path from {term} to your final point?",
                "How would changing {term} affect the rest of your reasoning?",
                "What underlying principles connect {term} with your main argument?"
            ],
            "chunked_symbolism": [
                "How would you quantify or measure {term}?",
                "What are the defining variables or parameters for {term}?",
                "Can you express {term} as a more precise formula or relationship?",
                "How would you decompose {term} into its fundamental components?",
                "What mathematical relationships might exist between {term} and other elements?"
            ],
            "expert_lexicons": [
                "What is the technical definition of {term} in this domain?",
                "How do experts in this field operationalize {term}?",
                "What specialized criteria are used to evaluate {term}?",
                "How does the technical usage of {term} differ from everyday usage?",
                "What domain-specific nuances are associated with {term}?"
            ],
            "socratic_questioning": [
                "What do you mean by {term}?",
                "What is the evidence for your view about {term}?",
                "Is there an alternative perspective on {term}?",
                "What would be the consequences of {term} being true?",
                "How can we verify or test claims about {term}?"
            ],
            "generic": [
                "Could you clarify what you mean by {term}?",
                "How would you define {term} more precisely?",
                "What assumptions underlie your use of {term}?",
                "What evidence supports your claims about {term}?",
                "Have you considered alternative perspectives on {term}?"
            ]
        }
        
        # Check for custom templates
        templates_path = os.path.join(os.path.dirname(__file__), 'templates.json')
        if os.path.exists(templates_path):
            try:
                with open(templates_path, 'r') as f:
                    custom_templates = json.load(f)
                    # Merge custom templates with defaults
                    for paradigm, template_list in custom_templates.items():
                        if paradigm in templates:
                            templates[paradigm].extend(template_list)
                        else:
                            templates[paradigm] = template_list
                logger.info(f"Loaded custom question templates from {templates_path}")
            except Exception as e:
                logger.error(f"Error loading custom templates: {e}")
        
        return templates
    
    def select_paradigm(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Select the most appropriate reasoning paradigm for the current text.
        
        Args:
            text: The text to analyze
            context: Optional context information
            
        Returns:
            The selected paradigm name
        """
        # Simple keyword-based selection
        text_lower = text.lower()
        
        # Check for mathematical/numerical content
        math_keywords = ['calculate', 'compute', 'equation', 'number', 'equals', 
                         'solve', 'formula', 'math', 'plus', 'minus', 'percent', 
                         'equals', 'ratio', 'proportion', 'quantity']
        if any(keyword in text_lower for keyword in math_keywords):
            return "chunked_symbolism"
        
        # Check for technical/specialized content
        technical_keywords = ['technical', 'specialized', 'professional', 'field', 
                             'domain', 'discipline', 'methodology', 'experts', 
                             'technical term', 'jargon', 'terminology']
        if any(keyword in text_lower for keyword in technical_keywords):
            return "expert_lexicons"
        
        # Default to conceptual chaining for abstract reasoning
        conceptual_keywords = ['concept', 'principle', 'theory', 'idea', 'relationship',
                              'connection', 'association', 'link', 'correlation', 
                              'causation', 'interaction', 'framework']
        if any(keyword in text_lower for keyword in conceptual_keywords):
            return "conceptual_chaining"
        
        # Use context if available
        if context and 'domain' in context:
            domain = context['domain'].lower()
            if domain in ['math', 'physics', 'economics', 'statistics']:
                return "chunked_symbolism"
            elif domain in ['medicine', 'law', 'engineering', 'computer science']:
                return "expert_lexicons"
            else:
                return "conceptual_chaining"
        
        # Fallback to socratic questioning
        return "socratic_questioning"
    
    def generate_questions(self, text: str, issues: List[Dict[str, Any]], 
                          selected_paradigm: Optional[str] = None,
                          max_questions: int = 5) -> List[str]:
        """
        Generate Socratic questions using the reflective ecosystem.
        
        Args:
            text: The text to analyze
            issues: The detected issues in the text
            selected_paradigm: Optional specific paradigm to use
            max_questions: Maximum number of questions to generate
            
        Returns:
            List of generated questions
        """
        if not issues:
            return []
            
        # If no paradigm is specified, select one
        if not selected_paradigm:
            selected_paradigm = self.select_paradigm(text)
        
        # First try to generate questions using Ollama
        if self.ollama.available:
            logger.info(f"Generating questions using Ollama with paradigm: {selected_paradigm}")
            ollama_questions = self.ollama.generate_questions(
                text, issues, selected_paradigm, max_questions
            )
            
            # If we got good results from Ollama, use those
            if len(ollama_questions) >= 3:
                logger.info(f"Generated {len(ollama_questions)} questions with Ollama")
                return ollama_questions
            logger.warning(f"Ollama generated only {len(ollama_questions)} questions. Falling back to templates.")
        
        # Fallback to template-based generation
        logger.info(f"Generating questions using templates with paradigm: {selected_paradigm}")
        
        # Get the primary node for this paradigm
        primary_node = self.nodes.get(selected_paradigm)
        if not primary_node:
            # Fallback to conceptual chaining
            primary_node = self.nodes.get("conceptual_chaining")
        
        # Generate primary questions
        primary_questions = primary_node.generate_questions(
            text, issues, self.question_templates
        )
        
        # Generate some complementary questions from other paradigms
        complementary_questions = []
        
        # Use weighted random selection for other paradigms
        other_paradigms = [p for p in self.nodes.keys() if p != selected_paradigm]
        weights = [self.nodes[p].weight for p in other_paradigms]
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w/total_weight for w in weights]
            
            # Select 1-2 complementary paradigms
            num_complementary = min(2, len(other_paradigms))
            try:
                selected_complementary = np.random.choice(
                    other_paradigms,
                    size=num_complementary,
                    replace=False,
                    p=weights
                )
                
                # Generate questions from complementary paradigms
                for paradigm in selected_complementary:
                    node = self.nodes[paradigm]
                    complementary_questions.extend(
                        node.generate_questions(text, issues, self.question_templates)[:2]
                    )
            except ValueError:
                # Fallback if random choice fails
                for paradigm in other_paradigms[:num_complementary]:
                    node = self.nodes[paradigm]
                    complementary_questions.extend(
                        node.generate_questions(text, issues, self.question_templates)[:2]
                    )
        
        # Combine questions and limit to max_questions
        all_questions = primary_questions + complementary_questions
        
        # Remove any duplicates while preserving order
        unique_questions = []
        seen = set()
        for q in all_questions:
            if q not in seen:
                unique_questions.append(q)
                seen.add(q)
        
        return unique_questions[:max_questions]
    
    def process_feedback(self, question: str, helpful: bool, paradigm: Optional[str] = None):
        """
        Process feedback on a question.
        
        Args:
            question: The question that received feedback
            helpful: Whether the question was helpful
            paradigm: Optional paradigm that generated the question
        """
        # Convert boolean to numeric feedback
        feedback_value = 1.0 if helpful else -0.5
        
        # If paradigm is provided, update that specific node
        if paradigm and paradigm in self.nodes:
            self.nodes[paradigm].update_weight(feedback_value)
        else:
            # Otherwise, update all nodes with a smaller adjustment
            reduced_feedback = feedback_value * 0.2
            for node in self.nodes.values():
                node.update_weight(reduced_feedback)
        
        # Track in question history
        self.question_history.append({
            "question": question,
            "helpful": helpful,
            "paradigm": paradigm
        })
        
        # Update global coherence based on feedback
        if len(self.question_history) > 0:
            recent_feedbacks = [1.0 if q["helpful"] else 0.0 for q in self.question_history[-10:]]
            if recent_feedbacks:
                self.global_coherence = sum(recent_feedbacks) / len(recent_feedbacks)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get a performance report for the ecosystem."""
        node_metrics = {node.paradigm: node.get_performance_metrics() 
                       for node in self.nodes.values()}
        
        # Calculate overall effectiveness
        total_rated = sum(metrics["questions_rated"] for metrics in node_metrics.values())
        total_positive = sum(metrics["positive_ratings"] for metrics in node_metrics.values())
        
        return {
            "node_metrics": node_metrics,
            "global_coherence": self.global_coherence,
            "total_questions_generated": sum(metrics["questions_generated"] for metrics in node_metrics.values()),
            "total_questions_rated": total_rated,
            "total_positive_ratings": total_positive,
            "overall_effectiveness": total_positive / max(1, total_rated),
            "questions_history_length": len(self.question_history),
            "ollama_available": self.ollama.available,
            "ollama_model": self.ollama.default_model if self.ollama.available else None
        }
    
    def save_state(self, file_path: Optional[str] = None):
        """
        Save the current state of the ecosystem.
        
        Args:
            file_path: Optional file path to save the state
        """
        if not file_path:
            file_path = os.path.join(os.path.dirname(__file__), 'ecosystem_state.json')
        
        state = {
            "nodes": {
                name: {
                    "paradigm": node.paradigm,
                    "description": node.description,
                    "weight": node.weight,
                    "questions_generated": node.questions_generated,
                    "questions_rated": node.questions_rated,
                    "positive_ratings": node.positive_ratings,
                    "feedback_history": node.feedback_history
                } for name, node in self.nodes.items()
            },
            "global_coherence": self.global_coherence,
            "question_history": self.question_history
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Ecosystem state saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving ecosystem state: {e}")
            return False
    
    def load_state(self, file_path: Optional[str] = None):
        """
        Load a previously saved state.
        
        Args:
            file_path: Optional file path to load the state from
            
        Returns:
            Whether the state was successfully loaded
        """
        if not file_path:
            file_path = os.path.join(os.path.dirname(__file__), 'ecosystem_state.json')
        
        if not os.path.exists(file_path):
            logger.warning(f"No state file found at {file_path}")
            return False
        
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)
            
            # Restore nodes
            for name, node_state in state.get("nodes", {}).items():
                if name in self.nodes:
                    node = self.nodes[name]
                    node.weight = node_state.get("weight", 1.0)
                    node.questions_generated = node_state.get("questions_generated", 0)
                    node.questions_rated = node_state.get("questions_rated", 0)
                    node.positive_ratings = node_state.get("positive_ratings", 0)
                    node.feedback_history = node_state.get("feedback_history", [])
            
            # Restore global state
            self.global_coherence = state.get("global_coherence", 1.0)
            self.question_history = state.get("question_history", [])
            
            logger.info(f"Ecosystem state loaded from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading ecosystem state: {e}")
            return False
