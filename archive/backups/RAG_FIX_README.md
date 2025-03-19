# RAG Context Fix for AI-Socratic-Clarifier

This fix addresses an issue with the Retrieval-Augmented Generation (RAG) functionality in the AI-Socratic-Clarifier where the system was analyzing the user's query instead of properly analyzing the document content.

## The Problem

When a document is loaded and a query is entered, the system should:
1. Use the document content as the primary text for Socratic analysis
2. Generate questions and identify issues based on the document content
3. Consider the user's query to provide context for the analysis

Instead, the system was:
1. Using the user's query as the primary text for analysis
2. Appending document content to the prompt but not instructing the LLM to focus on it
3. Generating questions about the user's query rather than about the document content

## The Fix

The fix modifies two main files:

1. `web_interface/direct_integration.py`:
   - Changes how the prompt for the LLM is constructed
   - Instructs the LLM to analyze the document content in relation to the user's query
   - Increases the document context length included in the prompt (from 2000 to 4000 chars)
   - Adds clear instructions for the LLM to focus on the document content

2. `web_interface/enhanced_routes.py`:
   - Improves how document content is retrieved and prepared
   - Adds a check for documents with insufficient content

## How to Apply the Fix

1. Make sure the AI-Socratic-Clarifier server is not running
2. Run the fix script:

```bash
python fix_rag_context.py
```

3. Restart the server:

```bash
python start.py
```

## Testing the Fix

To verify that the fix has been applied successfully, you can run the test script:

```bash
python test_rag_fix.py
```

This script will:
1. Create a test document with known issues (absolute terms, etc.)
2. Submit a simple user query
3. Check if the system correctly identifies issues from the document content
4. Report whether the test passes or fails

## Manual Testing

You can also test the fix manually:

1. Start the AI-Socratic-Clarifier server
2. Upload a document with some clear issues (absolute terms, vague language, etc.)
3. Select the document from the library
4. Enter a simple query like "Analyze this document" or "What issues can you find?"
5. Verify that the response addresses issues in the document content, not in your query

## Understanding the Changes

The key improvements in this fix:

1. Changed prompt structure:
```python
# Before
prompt = f"""
Please analyze this text: "{text}"{document_text}
...
"""

# After
prompt = f"""
{document_text if document_context else f'Please analyze this text: "{text}"'}

{'If document context is provided, analyze the document content in relation to the user query: "' + text + '"' if document_context else ''}
...
"""
```

2. Improved document context integration:
```python
# Before
document_text += "Use the document information to inform your analysis.\n"

# After
document_text += "1. Analyze the DOCUMENT CONTENT above in relation to the USER QUERY.\n"
document_text += "2. Identify issues in the document content, not in the user's query.\n"
document_text += "3. Focus on analyzing the actual document text rather than the query itself.\n"
```

## Rollback (If Needed)

If you need to revert the changes, you can restore the backup files:

```bash
# Restore direct_integration.py
cp web_interface/direct_integration.py.rag_fix_bak web_interface/direct_integration.py

# Restore enhanced_routes.py
cp web_interface/enhanced_routes.py.rag_fix_bak web_interface/enhanced_routes.py
```
