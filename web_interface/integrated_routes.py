"""
Integrated UI routes for AI-Socratic-Clarifier.

This module provides the API endpoints for the integrated user interface,
centralizing all features in a single page application.
"""

import os
import json
import traceback
from pathlib import Path
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from loguru import logger

from web_interface import direct_integration
from web_interface.app import load_custom_patterns

# Create blueprint
integrated_bp = Blueprint('integrated', __name__, url_prefix='/api')

@integrated_bp.route('/chat', methods=['POST'])
def api_chat():
    """Process chat message and return a response."""
    try:
        # Get the data from the request
        data = request.get_json()
        message = data.get('message', '')
        mode = data.get('mode', 'standard')
        use_sot = data.get('use_sot', True)
        use_sre = data.get('use_sre', False)
        use_rag = data.get('use_rag', False)
        document_context = data.get('document_context', [])
        
        logger.info(f"Integrated UI - Chat request: '{message}' with mode: {mode}, use_sot: {use_sot}, use_rag: {use_rag}")
        
        # Get the Flask app to access config
        from web_interface.app import app, clarifier, config
        
        # If RAG is enabled, retrieve relevant document context
        rag_context = []
        if use_rag and config.get('settings', {}).get('use_document_rag', False):
            try:
                # Include provided document context
                rag_context = document_context
                
                # If no specific documents were provided, search for relevant context
                if not rag_context and message:
                    from web_interface.document_rag_routes import retrieve_relevant_context
                    results = retrieve_relevant_context(message, limit=3)
                    if results:
                        rag_context = [
                            {
                                "document_id": result.get("document_id"),
                                "filename": result.get("filename"),
                                "content": result.get("content"),
                                "relevance": result.get("relevance", 0.0)
                            }
                            for result in results
                        ]
                        logger.info(f"Retrieved {len(rag_context)} relevant document chunks for RAG")
            except Exception as rag_error:
                logger.error(f"Error retrieving RAG context: {rag_error}")
        
        # Use direct integration to analyze the text
        result = direct_integration.direct_analyze_text(
            message, 
            mode, 
            use_sot, 
            document_context=rag_context
        )
        
        # Generate a response based on the analysis
        if result['issues'] and result['questions']:
            # Craft a response that includes one of the Socratic questions
            reply = f"I've analyzed your statement and have some thoughts to share. {result['questions'][0]}"
            
            # If there are more questions, include a followup
            if len(result['questions']) > 1:
                reply += f" I also wonder: {result['questions'][1]}"
                
            # If we used document context, mention that
            if rag_context:
                reply += f"\n\n(Analysis included context from {len(rag_context)} document(s))"
        else:
            # Default response if no issues detected
            reply = "I've considered your statement. It seems clear and well-formed. Do you have any other thoughts you'd like to explore?"
        
        # SRE metrics (if available)
        sre_metrics = {}
        if use_sre:
            try:
                # Try to get enhanced ecosystem state first
                try:
                    from enhanced_integration.enhanced_reflective_ecosystem import get_enhanced_ecosystem
                    ecosystem = get_enhanced_ecosystem()
                    
                    # Get IntelliSynth metrics
                    intellisynth = ecosystem.intellisynth
                    
                    # Get Meta-Meta Framework stage
                    meta_meta_stage = 'stageWhy'  # Default value
                    for loop in ecosystem.meta_meta_components["feedback_loops"]:
                        if loop["name"] == "Question effectiveness" and loop["current_value"] > 0.7:
                            meta_meta_stage = 'stageWhatNow'
                        elif loop["name"] == "Paradigm selection accuracy" and loop["current_value"] > 0.7:
                            meta_meta_stage = 'stageWhatNext'
                        elif ecosystem.global_coherence > 0.7:
                            meta_meta_stage = 'stageHowElse'
                    
                    # Get reasoning paths from enhancement
                    enhancement = ecosystem.apply_enhancement(
                        text=message,
                        issues=result.get('issues', []),
                        paradigm=result.get('sot_paradigm', 'conceptual_chaining')
                    )
                    
                    reasoning_paths = enhancement.get('reasoning_paths', [])
                    
                    sre_metrics = {
                        'global_coherence': ecosystem.global_coherence,
                        'advancement': {
                            'truth_value': intellisynth.get('truth_value', 0.7),
                            'scrutiny_value': intellisynth.get('scrutiny_value', 0.6),
                            'improvement_value': intellisynth.get('improvement_value', 0.5),
                            'advancement': intellisynth.get('advancement', 0.65)
                        },
                        'reasoning_paths': reasoning_paths,
                        'meta_meta_stage': meta_meta_stage
                    }
                except ImportError:
                    # Fallback to regular reflective ecosystem
                    from sequential_thinking.reflective_ecosystem import ReflectiveEcosystem
                    ecosystem = ReflectiveEcosystem()
                    ecosystem.load_state()
                    
                    # Simple metrics for fallback
                    sre_metrics = {
                        'global_coherence': ecosystem.global_coherence,
                        'advancement': {
                            'truth_value': 0.7,
                            'scrutiny_value': 0.6,
                            'improvement_value': 0.5,
                            'advancement': 0.65
                        },
                        'reasoning_paths': [],
                        'meta_meta_stage': 'stageWhy'
                    }
            except Exception as sre_error:
                logger.warning(f"Could not get SRE metrics: {sre_error}")
        
        # Prepare the response data
        response = {
            'reply': reply,
            'text': message,
            'issues': result['issues'],
            'questions': result['questions'],
            'reasoning': result['reasoning'],
            'sot_paradigm': result['sot_paradigm'],
            'confidence': result['confidence'],
            'sot_enabled': result['sot_enabled'],
            'model': result['model'],
            'provider': result['provider'],
            'document_context': rag_context,
            **sre_metrics
        }
        
        return jsonify(response)
    
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error processing integrated chat message: {e}\n{error_traceback}")
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500
