# AI-Socratic-Clarifier Project Reorganization Plan

## Overview

This document outlines a comprehensive plan to reorganize the AI-Socratic-Clarifier project from its current state to a more modular, maintainable structure. The plan addresses the identified issues with monolithic scripts, code duplication, and integration problems between components.

## Current Issues

1. **Monolithic Structure**
   - Large scripts with many responsibilities
   - Tightly coupled components
   - Unclear separation of concerns

2. **Document Management Duplication**
   - Two separate implementations in `enhanced_integration/document_manager.py` and `web_interface/document_rag_routes.py`
   - Inconsistent API between components

3. **Fragmented UI**
   - Document library and chat interface not well integrated
   - Multiple similar but slightly different routes

4. **Integration Issues**
   - Document RAG not properly integrated with chat
   - Multiple fallbacks for compatibility issues

## Proposed Structure

```
ai_socratic_clarifier/
├── core/
│   ├── __init__.py
│   ├── clarifier.py               # Main clarifier class
│   ├── config.py                  # Configuration management
│   ├── detectors/                 # Issue detection modules
│   │   ├── __init__.py
│   │   ├── ambiguity.py
│   │   ├── bias.py
│   │   └── factory.py             # Detector factory
│   ├── reasoning/                 # Reasoning generators
│   │   ├── __init__.py
│   │   ├── sketch_of_thought.py   # SoT implementation
│   │   └── factory.py             # Reasoning factory
│   └── models/                    # Model integrations
│       ├── __init__.py
│       ├── ollama.py
│       ├── lm_studio.py
│       └── factory.py             # Model factory
├── document/                      # Document handling
│   ├── __init__.py
│   ├── manager.py                 # Unified document manager
│   ├── storage.py                 # Document storage
│   ├── processing.py              # Text extraction
│   ├── embedding.py               # Embedding generation and storage
│   └── retrieval.py               # Vector-based retrieval
├── web/                           # Web interface
│   ├── __init__.py
│   ├── app.py                     # Main Flask app
│   ├── routes/                    # Route modules
│   │   ├── __init__.py
│   │   ├── api.py                 # API endpoints
│   │   ├── document_routes.py     # Document management
│   │   ├── chat_routes.py         # Chat interface
│   │   ├── enhanced_routes.py     # Enhanced UI
│   │   └── reflection_routes.py   # Reflection routes
│   ├── static/                    # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/                 # Templates
│       ├── base.html
│       ├── chat.html
│       ├── document_library.html
│       └── reflection.html
├── utils/                         # Utilities
│   ├── __init__.py
│   ├── logging.py                 # Logging setup
│   └── errors.py                  # Error handling
├── __init__.py
├── config.example.json            # Example configuration
└── main.py                        # Application entry point
```

## Implementation Phases

### Phase 1: Immediate Improvements (1-2 weeks)

1. **Consolidate Document Management**
   - Update `document_rag_routes.py` to use the enhanced document manager
   - Add vector-based retrieval to the document manager
   - Fix document API endpoints to ensure consistent behavior

2. **Improve RAG Integration**
   - Update the chat API to properly incorporate document context
   - Fix UI components for document selection in chat

3. **Fix Error Handling**
   - Add proper error handling and logging
   - Improve user feedback for errors

### Phase 2: Core Component Refactoring (2-3 weeks)

1. **Create Core Package Structure**
   - Move core functionality to dedicated modules
   - Create factories for detectors, reasoners, and models
   - Implement clean interfaces between components

2. **Implement Unified Document Module**
   - Create dedicated document package
   - Implement improved manager, storage, and retrieval
   - Add proper vector store support

3. **Update Tests**
   - Create tests for core components
   - Ensure proper test coverage

### Phase 3: Web Interface Reorganization (1-2 weeks)

1. **Reorganize Web Interface**
   - Create modular route structure
   - Update templates to use components
   - Improve JavaScript code organization

2. **Implement Unified UI**
   - Create consistent styling
   - Improve document-chat integration
   - Add better error handling and user feedback

### Phase 4: Final Integration and Documentation (1 week)

1. **Update Main Application**
   - Create new entry point
   - Update configuration handling
   - Ensure all components work together

2. **Improve Documentation**
   - Add README with setup instructions
   - Create API documentation
   - Add code comments

3. **Final Testing**
   - End-to-end testing
   - Performance testing
   - Security review

## Key Improvements

### Document Management

1. **Unified Manager**
   - Single implementation in `document/manager.py`
   - Clean API for document operations
   - Proper error handling

2. **Vector-Based Retrieval**
   - Implement proper vector similarity search
   - Support for different embedding models
   - Fallback to keyword search when needed

3. **Improved Document Processing**
   - Better text extraction with multimodal support
   - Chunking for large documents
   - Metadata handling

### Web Interface

1. **Modular Routes**
   - Separate routes by functionality
   - Clear API definitions
   - Consistent error handling

2. **Improved UI**
   - Better document-chat integration
   - Consistent styling
   - Enhanced user experience

### Core Components

1. **Clean Interfaces**
   - Well-defined interfaces between components
   - Dependency injection
   - Factory patterns for extensibility

2. **Improved Configuration**
   - Centralized configuration
   - Environment-specific settings
   - Runtime configuration changes

## Migration Strategy

1. **Create New Structure**
   - Set up new package structure
   - Move code piece by piece to new locations
   - Keep backward compatibility during migration

2. **Update Dependencies**
   - Refactor one component at a time
   - Update dependencies gradually
   - Maintain full test coverage

3. **Switch Over**
   - Once everything is migrated, switch to new entry point
   - Deprecate old scripts
   - Release new version

## Conclusion

This reorganization will significantly improve the maintainability, extensibility, and reliability of the AI-Socratic-Clarifier project. By properly separating concerns, implementing clean interfaces, and improving error handling, the project will be easier to develop, test, and deploy.

The modular structure will also make it easier to add new features, such as additional document types, reasoning methods, or UI improvements, without affecting existing functionality.
