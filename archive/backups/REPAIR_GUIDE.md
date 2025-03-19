# AI-Socratic-Clarifier Repair Guide

This guide explains how to repair and optimize the AI-Socratic-Clarifier application using the fix_project.py script.

## Overview of Issues

The AI-Socratic-Clarifier project currently has several issues that need to be addressed:

1. **Broken Multimodal Integration**: The multimodal functionality, which processes images and PDFs, is not working correctly.
2. **Sub-optimal Ollama Performance**: The Ollama LLM integration is not using optimal settings for performance.
3. **RAG System Issues**: The Retrieval-Augmented Generation system has implementation problems.
4. **UI Integration Problems**: Various UI components and integrations have issues.

## The Fix Script

The `fix_project.py` script automatically resolves these issues by:

1. **Updating Multimodal Integration**: Copies improved multimodal components from the ruined repo.
2. **Enhancing Ollama Support**: Adds optimized settings for better performance.
3. **Fixing RAG Integration**: Ensures the document management and retrieval system works correctly.
4. **Resolving UI Issues**: Applies necessary UI fixes to ensure components work together.

## How to Use

To repair your AI-Socratic-Clarifier installation:

1. Ensure both repositories are in their proper locations:
   - Working repo: `/home/ty/Repositories/ai-socratic-clarifier`
   - Ruined repo: `/home/ty/Repositories/ai_workspace/ai-socratic-clarifier-ruined`

2. Run the fix script:
   ```bash
   cd /home/ty/Repositories/ai-socratic-clarifier
   python fix_project.py
   ```

3. After the script completes successfully, you can start the application using the optimized start script:
   ```bash
   ./start_optimized.py
   ```

   Or use the Ollama optimized script:
   ```bash
   ./start_with_optimized_ollama.sh
   ```

## What Gets Fixed

### 1. Multimodal Integration

- Improved image and PDF processing
- Enhanced UI controls for question generation
- Better integration with Socratic Reasoning Engine (SRE)
- Support for multiple multimodal models

### 2. Ollama Optimization

- Increased context window size (8192 tokens)
- Flash Attention enabled for better memory usage
- KV Cache Quantization (8-bit) for more efficient memory utilization
- Configuration updates in `config.json`

### 3. RAG Integration

- Fixed document handling and deletion
- Enhanced document embeddings using Ollama
- Improved document search functionality
- Fixed API endpoints for document management

### 4. UI Integration

- Applied SRE and SoT integration fixes
- Resolved UI layout and CSS issues
- Fixed duplicate settings panels
- Improved UI components for document management

## After Running the Fix

After applying the fixes, you should be able to:

1. Upload and process documents (PDFs, images, text files)
2. Use uploaded documents as context for AI analysis
3. Process images using multimodal models
4. Experience better performance from Ollama with the optimized settings
5. See the Socratic reasoning visualization working correctly

## Backups

The fix script creates backups of all modified files with the extension `.fix_proj_bak`. If you need to revert any changes, you can restore from these backup files.

## Troubleshooting

If you encounter issues after running the fix script:

1. Check the log output for specific error messages
2. Ensure Ollama is running (`ollama serve`)
3. Make sure the required models are available:
   ```bash
   ollama list
   ```
4. Look for models like `gemma3:latest` (text) and `llava:latest` (multimodal)

If needed, install missing models:
```bash
ollama pull gemma3:latest
ollama pull llava:latest
```

## Performance Tuning

For additional performance tuning options, refer to the `OLLAMA_OPTIMIZATION.md` file that was created by the fix script.
