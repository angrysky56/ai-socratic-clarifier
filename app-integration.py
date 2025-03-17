"""
Flask App Document RAG Integration Improvements

This file contains the key updates needed for better document RAG integration in the Flask app.
These changes should be applied to the appropriate files (app.py, enhanced_routes.py).
"""

#
# Updates for app.py
#

def app_py_init_document_manager():
    """
    Add this to the app.py initialization section to ensure document manager is available.
    Should be placed after app initialization but before route registration.
    """
    # Initialize document manager and make it available to the app
    from enhanced_integration.document_manager import get_document_manager
    document_manager = get_document_manager()
    app.config['DOCUMENT_MANAGER'] = document_manager
    
    # Initialize document directories if they don't exist
    storage_dir = document_manager.storage_dir
    if not os.path.exists(storage_dir):
        logger.warning(f"Document storage directory not found, creating: {storage_dir}")
        os.makedirs(storage_dir, exist_ok=True)
    
    # Check for document index
    index_file = os.path.join(storage_dir, 'document_index.json')
    if not os.path.exists(index_file):
        logger.warning("Document index not found, will be created on startup")
    else:
        # Log some stats about the document library
        try:
            stats = document_manager.get_document_stats()
            logger.info(f"Document library stats: {stats['total_documents']} documents, " +
                      f"{stats['with_embeddings']} with embeddings")
        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
    
    # Log success
    logger.info(f"Document manager initialized with storage at: {storage_dir}")

#
# Updates for enhanced_routes.py chat endpoint
#

def enhanced_chat_with_rag(message, mode, use_sot, use_rag, document_context=None):
    """
    An improved version of the chat message handler that better integrates document RAG.
    This should replace or be integrated into the existing chat_message function in enhanced_routes.py.
    """
    # Get document content for RAG
    if use_rag:
        # Get document manager
        document_manager = get_document_manager()
        
        if document_context:
            # Ensure documents in context have content
            for i, doc in enumerate(document_context):
                if "document_id" in doc and "content" not in doc:
                    content = document_manager.get_document_content(doc["document_id"])
                    if content:
                        document_context[i]["content"] = content
                        document_context[i]["relevance"] = 0.95  # High relevance for manually selected docs
        else:
            # If no specific documents provided, automatically retrieve relevant ones
            document_context = document_manager.get_documents_for_rag(message, limit=3)
            if document_context:
                logger.info(f"Retrieved {len(document_context)} relevant documents for RAG")
    else:
        document_context = []
    
    # Process with direct integration, handling document context
    from web_interface.direct_integration import direct_analyze_text
    try:
        # Try with document_context parameter
        result = direct_analyze_text(message, mode, use_sot, document_context=document_context)
    except TypeError as e:
        if "document_context" in str(e):
            # Fallback to call without document_context
            logger.warning("direct_analyze_text() doesn't support document_context, falling back")
            result = direct_analyze_text(message, mode, use_sot)
            
            # Add document context to the result manually
            result["document_context"] = document_context
        else:
            # Re-raise any other errors
            raise
    
    # Generate a response based on the analysis
    if result['issues'] and result['questions']:
        # Craft a response that includes one of the Socratic questions
        reply = f"I've analyzed your statement and have some thoughts to share. {result['questions'][0]}"
        
        # If there are more questions, include a followup
        if len(result['questions']) > 1:
            reply += f" I also wonder: {result['questions'][1]}"
            
        # If we used document context, mention that
        if document_context:
            reply += f"\n\n(Analysis included context from {len(document_context)} document(s))"
    else:
        # Default response if no issues detected
        reply = "I've considered your statement. It seems clear and well-formed. Do you have any other thoughts you'd like to explore?"
    
    # Prepare the response data with document context
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
        'document_context': document_context
    }
    
    return response

#
# Updates for direct_integration.py
#

def improved_direct_analyze_text(text, mode='standard', use_sot=True, document_context=None):
    """
    Improved version of direct_analyze_text that properly handles document context.
    This should replace or be integrated into the existing function in direct_integration.py.
    """
    # Initialize result data
    result = {
        'text': text,
        'issues': [],
        'questions': [],
        'reasoning': '',
        'sot_paradigm': None,
        'confidence': 0.0,
        'sot_enabled': use_sot,
        'model': 'unknown',
        'provider': 'unknown',
        'document_context': document_context or []
    }
    
    try:
        # Get the clarifier instance
        from flask import current_app
        clarifier = current_app.clarifier
        
        # Prepare context from documents if available
        context = ""
        if document_context:
            context = "Context from documents:\n\n"
            for i, doc in enumerate(document_context):
                if "content" in doc and doc["content"]:
                    content = doc["content"]
                    # Truncate if too long
                    if len(content) > 1000:
                        content = content[:1000] + "..."
                    context += f"Document {i+1} ({doc.get('filename', 'unnamed')}): {content}\n\n"
        
        # Add context to the text if available
        analysis_text = text
        if context:
            # Prepend context for analysis
            analysis_text = f"{context}\n\nUser query: {text}"
        
        # Analyze the text
        if mode == 'deep':
            # Use deep analysis mode
            issues = clarifier.analyze_deep(analysis_text)
        else:
            # Use standard mode
            issues = clarifier.analyze(analysis_text)
        
        # Generate Socratic questions based on the issues
        questions = []
        if issues:
            questions = clarifier.generate_questions(analysis_text, issues, use_sot=use_sot)
        
        # Generate reasoning if SoT is enabled
        reasoning = ""
        sot_paradigm = None
        if use_sot and issues:
            reasoning_result = clarifier.generate_reasoning(analysis_text, issues)
            reasoning = reasoning_result.get('reasoning', '')
            sot_paradigm = reasoning_result.get('paradigm')
        
        # Update the result
        result.update({
            'issues': issues,
            'questions': questions,
            'reasoning': reasoning,
            'sot_paradigm': sot_paradigm,
            'confidence': 0.85 if issues else 0.95,  # Simplified confidence score
            'model': clarifier.get_model_info().get('model', 'unknown'),
            'provider': clarifier.get_model_info().get('provider', 'unknown')
        })
        
        return result
    except Exception as e:
        # Log the error and return a basic result
        from loguru import logger
        import traceback
        logger.error(f"Error in direct_analyze_text: {e}\n{traceback.format_exc()}")
        
        # Include error in result
        result['error'] = str(e)
        return result
