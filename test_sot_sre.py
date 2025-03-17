#!/usr/bin/env python3
"""
Test script for SoT and SRE functionality in AI-Socratic-Clarifier.
"""

import os
import sys
import json
from loguru import logger

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_sot():
    """Test the SoT functionality."""
    logger.info("Testing SoT integration...")
    
    # Import SoT from socratic_clarifier
    try:
        from socratic_clarifier.core import import_sot
        sot_available, SoT_class = import_sot()
        
        if not sot_available:
            logger.error("SoT not available")
            return False
        
        # Create a SoT instance
        sot = SoT_class()
        
        # Test classification
        test_text = "What are the key factors in economic growth?"
        paradigm = sot.classify_question(test_text)
        
        logger.info(f"Classified '{test_text}' as paradigm: {paradigm}")
        
        # Get available paradigms
        paradigms = sot.avaliable_paradigms()
        logger.info(f"Available paradigms: {paradigms}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing SoT: {e}")
        return False

def test_sre():
    """Test the SRE functionality."""
    logger.info("Testing SRE integration...")
    
    try:
        # Import the enhancer
        from enhanced_integration.integration import get_enhanced_enhancer
        
        # Get the enhancer
        enhancer = get_enhanced_enhancer()
        
        if not enhancer.initialized:
            logger.error("Enhancer not initialized")
            return False
        
        # Test getting reasoning context
        test_text = "All people are always happy."
        issues = [
            {
                "issue": "absolute_language",
                "term": "All",
                "description": "Using absolute terms like 'all' often oversimplifies complex situations.",
                "confidence": 0.9
            },
            {
                "issue": "vague_language",
                "term": "happy",
                "description": "The term 'happy' is subjective and needs more precise definition.",
                "confidence": 0.8
            }
        ]
        
        # Get reasoning context
        context = enhancer.get_reasoning_context(test_text, issues)
        
        # Log the keys
        logger.info(f"Reasoning context keys: {list