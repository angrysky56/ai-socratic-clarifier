# Advanced RAG Configuration for AI-Socratic-Clarifier

## Overview

This configuration enhances the Retrieval-Augmented Generation (RAG) capabilities of the AI-Socratic-Clarifier by:

1. **Leveraging Large Context Windows**: Configures the system to use the full context window of models like Gemma 3 (128k tokens)
2. **Enabling Multimodal Document Processing**: Configures settings to use the primary model for document processing
3. **Optimizing Document Retrieval**: Sets parameters for better document context integration

## Configuration Changes

Added settings in `config.json`:

- `advanced_rag`: Enable/disable advanced RAG features
- `rag_context_limit`: Control how much document content to include
- `use_model_for_rag`: Use the primary model for document processing when possible
- Increased context length for Gemma 3 to 128k tokens
- Configured default embedding model for document retrieval

## Usage

The advanced RAG capabilities are automatically enabled when documents are processed. Additional code improvements for better RAG functionality may be added in future updates.

## Requirements

- Ollama with models like Gemma 3, Llava, or other LLMs with large context windows
- Python dependencies for document processing (OCR, PDF handling, etc.)
- Sufficient system memory to handle large context windows
