"""
Module for managing different operating modes of the system.
"""

from typing import Dict, Any, List


class ModeManager:
    """
    Manages different operating modes for the clarifier system.
    
    Each mode defines:
    - Sensitivity thresholds for detectors
    - Question styles and limits
    - Domain-specific behavior
    """
    
    def __init__(self):
        """Initialize the mode manager with predefined modes."""
        self.modes = {
            "standard": {
                "name": "Standard",
                "description": "Balanced detection and questioning suitable for general text",
                "threshold": 0.7,
                "question_style": "neutral",
                "question_limit": 3,
                "feedback_sensitivity": "medium"
            },
            "academic": {
                "name": "Academic",
                "description": "Strict standards suitable for academic or scholarly writing",
                "threshold": 0.6,  # Lower threshold means more sensitivity
                "question_style": "formal",
                "question_limit": 5,
                "feedback_sensitivity": "high"
            },
            "legal": {
                "name": "Legal",
                "description": "Focused on precision and clarity for legal documents",
                "threshold": 0.65,
                "question_style": "precise",
                "question_limit": 4,
                "feedback_sensitivity": "high"
            },
            "medical": {
                "name": "Medical",
                "description": "Tailored for medical documentation and communications",
                "threshold": 0.65,
                "question_style": "precise",
                "question_limit": 4,
                "feedback_sensitivity": "high"
            },
            "business": {
                "name": "Business",
                "description": "Balanced approach for professional communications",
                "threshold": 0.7,
                "question_style": "professional",
                "question_limit": 3,
                "feedback_sensitivity": "medium"
            },
            "casual": {
                "name": "Casual",
                "description": "Relaxed standards for informal communications",
                "threshold": 0.8,  # Higher threshold means less sensitivity
                "question_style": "conversational",
                "question_limit": 2,
                "feedback_sensitivity": "low"
            },
            "chat": {
                "name": "Chat",
                "description": "Minimal intervention for conversational exchanges",
                "threshold": 0.85,
                "question_style": "friendly",
                "question_limit": 1,
                "feedback_sensitivity": "low"
            }
        }
    
    def get_mode(self, mode_name: str) -> Dict[str, Any]:
        """
        Get the configuration for a specific mode.
        
        Args:
            mode_name: The name of the mode to retrieve
        
        Returns:
            The mode configuration dict
        
        Raises:
            ValueError: If the requested mode doesn't exist
        """
        mode_name = mode_name.lower()
        if mode_name not in self.modes:
            raise ValueError(f"Mode '{mode_name}' is not recognized. Available modes: {', '.join(self.modes.keys())}")
        
        return self.modes[mode_name]
    
    def available_modes(self) -> List[str]:
        """
        Get a list of all available mode names.
        
        Returns:
            List of mode names
        """
        return list(self.modes.keys())
    
    def add_custom_mode(self, name: str, config: Dict[str, Any]) -> None:
        """
        Add a new custom mode.
        
        Args:
            name: The name for the new mode
            config: The configuration dictionary
        
        Raises:
            ValueError: If the mode name already exists
        """
        name = name.lower()
        if name in self.modes:
            raise ValueError(f"Mode '{name}' already exists. Use a different name or update the existing mode.")
        
        # Validate required fields
        required_fields = ["threshold", "question_style", "question_limit"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Custom mode must include '{field}' field")
        
        self.modes[name] = config
