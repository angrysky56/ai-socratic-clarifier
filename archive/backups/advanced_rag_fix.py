#!/usr/bin/env python3
"""
Advanced RAG Integration Fix for AI-Socratic-Clarifier.

This script enhances the RAG functionality by:
1. Leveraging the full context window of models like Gemma 3 (128k)
2. Enabling multimodal document processing using the configured LLM
3. Improving document content integration in prompts
4. Enhancing the retrieval mechanism beyond simple keyword matching
"""

import os
import sys
import json
import shutil
from pathlib import Path
import re
import time
import tempfile
import base64
import requests

def backup_file(file_path):
    """Create a backup of a file."""
    backup_path = f"{file_path}.advanced_rag_bak"
    if os.path.exists(file_path):
        print(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
    return backup_path

def update_config_for_advanced_rag():
    """Update config.json with advanced RAG settings."""
    config_path = os.path.join('config.json')
    
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found")
        return False
    
    backup_file(config_path)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Ensure RAG settings are present and optimized
        if "settings" not in config:
            config["settings"] = {}
        
        config["settings"]["use_document_rag"] = True
        config["settings"]["advanced_rag"] = True  # New setting for advanced RAG
        config["settings"]["rag_context_limit"] = 50000  # Higher limit for large context models
        config["settings"]["use_model_for_rag"] = True  # Use the main model for RAG
        
        # Ensure Ollama settings include necessary models and context length
        if "integrations" not in config:
            config["integrations"] = {}
        
        if "ollama" not in config["integrations"]:
            config["integrations"]["ollama"] = {}
        
        # Update context length for Gemma 3
        if config["integrations"]["ollama"].get("default_model") == "gemma3:latest":
            config["integrations"]["ollama"]["context_length"] = 128000
        else:
            config["integrations"]["ollama"]["context_length"] = 8192
        
        # Ensure embedding model is set
        if "default_embedding_model" not in config["integrations"]["ollama"]:
            config["integrations"]["ollama"]["default_embedding_model"] = "nomic-embed-text"
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print("✅ Updated config.json with advanced RAG settings")
        return True
    except Exception as e:
        print(f"Error updating config with advanced RAG settings: {e}")
        return False

def fix_direct_integration():
    """Enhance how document content is integrated into prompts."""
    file_path = os.path.join('web_interface', 'direct_integration.py')
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    backup_file(file_path)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the document context processing section
        doc_context_pattern = r"# Process any document context if provided\s*document_text = \"\"\s*if document_context:.*?document_text \+= f\"\\n\\nDocument content: \{content\[:500\]\}...\""
        
        # Improved document context processing with full context utilization
        improved_doc_context = """# Process any document context if provided
    document_text = ""
    if document_context:
        logger.info(f"Processing document context with {len(document_context)} documents")
        
        # Get config to check context limits
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        context_limit = 50000  # Default high limit
        use_model_for_rag = True
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                context_limit = config.get("settings", {}).get("rag_context_limit", 50000)
                use_model_for_rag = config.get("settings", {}).get("use_model_for_rag", True)
            except:
                pass
        
        # Format document content with clear structure and more content
        document_text = "\\n\\n===== REFERENCE DOCUMENTS =====\\n"
        total_chars = 0
        
        for i, doc in enumerate(document_context):
            if isinstance(doc, dict) and "content" in doc:
                content = doc.get("content", "")
                filename = doc.get("filename", f"Document {i+1}")
                relevance = doc.get("relevance", None)
                
                if content:
                    doc_header = f"\\n----- DOCUMENT {i+1}: {filename}"
                    if relevance:
                        doc_header += f" (Relevance: {relevance:.2f})"
                    doc_header += " -----\\n"
                    
                    document_text += doc_header
                    
                    # Add as much content as possible within the limits
                    content_to_add = content
                    # Check if adding this would exceed our context limit
                    if total_chars + len(content_to_add) > context_limit:
                        # Truncate to fit within limit
                        available_chars = max(0, context_limit - total_chars)
                        if available_chars > 100:  # Only add if we can add a meaningful amount
                            content_to_add = content[:available_chars] + "... [content truncated to fit context window]"
                        else:
                            # Skip this document if we can't add enough content
                            document_text += "Document content omitted to fit context window.\\n"
                            continue
                    
                    document_text += content_to_add + "\\n"
                    total_chars += len(doc_header) + len(content_to_add)
                    
                    # If we've exceeded our context limit, stop adding documents
                    if total_chars >= context_limit:
                        document_text += "\\n[Additional documents omitted to fit context window]"
                        break
        
        # Add clear instructions for the LLM
        document_text += "\\n\\n===== INSTRUCTIONS =====\\n"
        document_text += "1. Use the information from the REFERENCE DOCUMENTS above to inform your analysis\\n"
        document_text += "2. Cite specific information from documents when relevant to the analysis\\n"
        document_text += "3. Acknowledge if the information in the documents contradicts or supports the user statement\\n"
        document_text += "4. Do not fabricate information that is not in the documents or the user's statement\\n\\n"
        
        logger.info(f"Added {total_chars} characters of document context from {len(document_context)} documents")"""
        
        # Replace the document context processing section
        if re.search(doc_context_pattern, content, re.DOTALL):
            new_content = re.sub(doc_context_pattern, improved_doc_context, content, flags=re.DOTALL)
            
            # Write updated content
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            print("✅ Enhanced document context processing in direct_integration.py")
        else:
            print("⚠️ Could not find document context processing section in direct_integration.py")
            return False
        
        return True
    except Exception as e:
        print(f"Error fixing direct_integration.py: {e}")
        return False

def enhance_document_rag_routes():
    """Enhance the document RAG routes for better retrieval and processing."""
    file_path = os.path.join('web_interface', 'document_rag_routes.py')
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    backup_file(file_path)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Improve the retrieve_relevant_context function
        retrieve_pattern = r"def retrieve_relevant_context\(query: str, limit: int = 5\) -> List\[Dict\[str, Any\]\]:.*?return \[\]"
        
        # Enhanced retrieval function with better matching and content inclusion
        enhanced_retrieve = """def retrieve_relevant_context(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    \"\"\"
    Retrieve relevant document sections based on a query.
    Returns a list of relevant document chunks.
    \"\"\"
    try:
        # Get config to check for preferred approaches
        config = current_app.config.get('CLARIFIER_CONFIG', {})
        use_full_doc = config.get('settings', {}).get('advanced_rag', False)
        
        # Get all documents
        index_data = get_document_index()
        documents = index_data.get("documents", [])
        
        # If no documents, return empty results
        if not documents:
            logger.warning("No documents found in the index.")
            return []
        
        # For more advanced implementations, this would use vector embeddings
        # For now we'll use enhanced keyword matching and relevance scoring
        results = []
        
        # Extract important terms from query, excluding stopwords
        stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                    'of', 'for', 'in', 'to', 'with', 'on', 'at', 'from', 'by', 'about'}
        query_terms = [term.lower() for term in query.split() if term.lower() not in stopwords]
        
        for doc in documents:
            doc_path = doc.get("file_path")
            if not doc_path or not os.path.exists(doc_path):
                continue
                
            try:
                # Read text content from file
                text_file_path = f"{doc_path}.txt"
                if not os.path.exists(text_file_path):
                    logger.warning(f"Text file not found: {text_file_path}")
                    continue
                    
                with open(text_file_path, 'r') as f:
                    content = f.read()
                
                # Skip empty content
                if not content.strip():
                    continue
                
                # Calculate relevance score based on term frequency and position
                score = 0
                content_lower = content.lower()
                
                # Count term occurrences and weight by position (terms near beginning count more)
                for term in query_terms:
                    # Skip very short terms
                    if len(term) < 3:
                        continue
                        
                    # Find all occurrences
                    positions = [m.start() for m in re.finditer(re.escape(term), content_lower)]
                    
                    if positions:
                        # Calculate position-weighted score (earlier occurrences worth more)
                        position_scores = [1.0 - (pos / len(content_lower)) * 0.5 for pos in positions]
                        term_score = sum(position_scores) * len(term) / 5  # Longer term matches worth more
                        score += term_score
                
                # If any terms matched or we're using full doc mode, add to results
                if score > 0 or use_full_doc:
                    # Decide how much content to include
                    if use_full_doc:
                        # In advanced mode, include the full document
                        chunk_content = content
                    else:
                        # In regular mode, find the most relevant chunk
                        # Create chunks based on paragraphs
                        paragraphs = re.split(r'\\n\\n+', content)
                        
                        # Score each paragraph
                        paragraph_scores = []
                        for i, paragraph in enumerate(paragraphs):
                            para_score = 0
                            para_lower = paragraph.lower()
                            
                            for term in query_terms:
                                if len(term) >= 3 and term in para_lower:
                                    para_score += 1 * len(term) / 5
                            
                            paragraph_scores.append((i, para_score))
                        
                        # Sort by score
                        paragraph_scores.sort(key=lambda x: x[1], reverse=True)
                        
                        # Combine top paragraphs up to a reasonable size
                        combined_content = ""
                        total_length = 0
                        max_chunk_size = 2000  # Set a reasonable size
                        
                        for i, _ in paragraph_scores:
                            if total_length + len(paragraphs[i]) <= max_chunk_size:
                                combined_content += paragraphs[i] + "\\n\\n"
                                total_length += len(paragraphs[i]) + 2
                            else:
                                break
                        
                        chunk_content = combined_content.strip()
                    
                    # Add to results
                    results.append({
                        "document_id": doc.get("id"),
                        "filename": doc.get("filename"),
                        "content": chunk_content,
                        "relevance": score
                    })
            except Exception as inner_e:
                logger.error(f"Error processing document {doc.get('filename')}: {inner_e}")
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        # In advanced mode, we might want to return fewer documents but with more content
        if use_full_doc and limit > 3:
            limit = min(3, len(results))  # Return at most 3 full documents
            
        logger.info(f"Found {len(results)} relevant documents, returning top {limit}")
        
        return results[:limit]
    except Exception as e:
        logger.error(f"Error retrieving relevant context: {e}")
        return []"""
        
        # Replace the retrieve_relevant_context function
        if re.search(retrieve_pattern, content, re.DOTALL):
            new_content = re.sub(retrieve_pattern, enhanced_retrieve, content, flags=re.DOTALL)
            
            # Now improve process_document_for_rag to better utilize multimodal capabilities
            process_pattern = r"def process_document_for_rag\(file_path: str\) -> Tuple\[bool, str, Dict\[str, Any\]\]:.*?return False, \"\", \{\"error\": str\(e\)\}"
            
            # Enhanced document processing function
            enhanced_process = """def process_document_for_rag(file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
    \"\"\"
    Process a document for RAG by extracting text and generating embeddings.
    Returns (success, text_content, metadata)
    \"\"\"
    # Get config to check for preferred approaches
    config = current_app.config.get('CLARIFIER_CONFIG', {})
    use_model_for_rag = config.get('settings', {}).get('use_model_for_rag', False)
    
    if not MULTIMODAL_AVAILABLE:
        logger.error("Multimodal integration not available for document processing")
        return False, "", {"error": "Multimodal integration not available"}
    
    try:
        # Check file extension to determine processing approach
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # For image-based documents (scanned PDFs, images) try using multimodal capabilities
        is_image_document = file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']
        is_pdf = file_ext == '.pdf'
        
        # Determine if we should use the model for document processing
        if use_model_for_rag and (is_image_document or is_pdf):
            logger.info(f"Using primary LLM for document processing: {file_path}")
            try:
                # Use model to extract text with richer context
                result = process_file(file_path, use_multimodal=True)
                
                if result.get('success', False):
                    # If successful, return the results
                    extracted_text = result.get('text', '')
                    
                    # If content came from a multimodal model, it might be in the 'content' field
                    if not extracted_text and 'content' in result:
                        extracted_text = result.get('content', '')
                    
                    return True, extracted_text, {
                        "method": result.get('method', 'multimodal'),
                        "model": result.get('model', config.get('integrations', {}).get('ollama', {}).get('multimodal_model', 'unknown')),
                        "processing_time": result.get('processing_time', 0)
                    }
            except Exception as multimodal_error:
                logger.warning(f"Multimodal processing failed, falling back to OCR: {multimodal_error}")
                # Fall back to OCR approach
        
        # Use regular text extraction methods
        logger.info(f"Using standard OCR for document processing: {file_path}")
        result = process_file(file_path, use_multimodal=False)
        
        if not result.get('success', False):
            return False, "", {"error": result.get('error', 'Unknown error')}
        
        # Get the extracted text
        text_content = result.get('text', '')
        
        if not text_content.strip():
            return False, "", {"error": "No text could be extracted from the document"}
        
        return True, text_content, {
            "method": result.get('method', 'ocr'),
            "processing_time": result.get('processing_time', 0)
        }
    except Exception as e:
        logger.error(f"Error processing document for RAG: {e}")
        return False, "", {"error": str(e)}"""
            
            # Replace the process_document_for_rag function
            if re.search(process_pattern, new_content, re.DOTALL):
                new_content = re.sub(process_pattern, enhanced_process, new_content, flags=re.DOTALL)
                
                # Write updated content
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                print("✅ Enhanced document RAG routes")
            else:
                print("⚠️ Could not find process_document_for_rag function in document_rag_routes.py")
                return False
        else:
            print("⚠️ Could not find retrieve_relevant_context function in document_rag_routes.py")
            return False
        
        return True
    except Exception as e:
        print(f"Error enhancing document_rag_routes.py: {e}")
        return False

def update_multimodal_integration():
    """Update multimodal integration to better utilize the primary model for RAG."""
    file_path = os.path.join('multimodal_integration.py')
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    backup_file(file_path)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Update the process_file function to allow using the primary model
        process_file_pattern = r"def process_file\(file_path: str, use_multimodal: bool = True\) -> Dict\[str, Any\]:.*?return \{\s+\"success\": False,\s+\"error\": f\"Unsupported file type: \{file_ext\}\"\s+\}"
        
        # Enhanced process_file function
        enhanced_process_file = """def process_file(file_path: str, use_multimodal: bool = True) -> Dict[str, Any]:
    \"\"\"
    Process a file (image or PDF) and extract text or analyze with multimodal model.
    
    Args:
        file_path: Path to the file
        use_multimodal: Whether to use multimodal analysis
        
    Returns:
        Processing result
    \"\"\"
    # Ensure dependencies are installed
    if not check_dependencies():
        return {
            "success": False,
            "error": "Required dependencies are not available"
        }
    
    # Determine file type
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Get configuration to determine which model to use
    config = load_config()
    use_primary_model = config.get("settings", {}).get("use_model_for_rag", False)
    
    # If we're using the primary model, we'll need to check what it is
    primary_model = None
    multimodal_model = None
    
    if use_primary_model:
        primary_model = config.get("integrations", {}).get("ollama", {}).get("default_model", "gemma3:latest")
        multimodal_model = config.get("integrations", {}).get("ollama", {}).get("multimodal_model", "llava:latest")
        
        # Check if primary model supports multimodal
        primary_is_multimodal = any(mm in primary_model.lower() for mm in ["gemma", "llama3", "phi3", "qwen2"])
        
        if primary_is_multimodal:
            multimodal_model = primary_model  # Use primary model for multimodal if it supports it
    
    # For image files
    if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif']:
        if use_multimodal:
            # Use multimodal analysis
            start_time = time.time()
            
            # Use primary model if configured to do so and it's multimodal
            if use_primary_model and multimodal_model == primary_model:
                prompt = "Please analyze this image and extract all visible text content. Then, provide a detailed description of what you see in the image."
                result = analyze_image_with_multimodal(file_path, prompt, model=primary_model)
            else:
                # Use default multimodal model
                result = analyze_image_with_multimodal(file_path)
            
            # Add timing information
            if result.get("success", False):
                result["processing_time"] = time.time() - start_time
                result["method"] = "multimodal"
                result["model"] = multimodal_model
            
            return result
        else:
            # Use OCR
            try:
                start_time = time.time()
                text = perform_ocr(file_path)
                return {
                    "success": True,
                    "text": text,
                    "method": "ocr",
                    "processing_time": time.time() - start_time
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error performing OCR: {str(e)}"
                }
    
    # For PDF files
    elif file_ext == '.pdf':
        try:
            start_time = time.time()
            
            # First, try to extract text directly without OCR
            try:
                # Import PyPDF2 dynamically
                import PyPDF2
                
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text() + "\\n\\n"
                
                # If text extraction worked and returned significant content
                if len(text.strip()) > 100:
                    return {
                        "success": True,
                        "text": text,
                        "method": "pdf_text_extraction",
                        "processing_time": time.time() - start_time
                    }
            except Exception as pdf_error:
                print(f"PDF text extraction failed, falling back to OCR: {pdf_error}")
            
            # If direct extraction failed or returned too little text, try OCR
            text = extract_text_from_pdf(file_path)
            
            # If OCR returned too little text or has encoding issues, try multimodal
            if use_multimodal and (len(text.strip()) < 100 or "�" in text):
                # Try with multimodal model if enabled
                images = pdf2image.convert_from_path(file_path, first_page=1, last_page=3)  # Process first 3 pages
                all_content = ""
                
                for i, img in enumerate(images):
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
                        img.save(temp.name)
                        temp_path = temp.name
                    
                    # Process with the appropriate model
                    if use_primary_model and multimodal_model == primary_model:
                        prompt = f"This is page {i+1} of a PDF document. Please extract all visible text content from this image, preserving any formatting, tables, and structure as much as possible."
                        result = analyze_image_with_multimodal(temp_path, prompt, model=primary_model)
                    else:
                        result = analyze_image_with_multimodal(temp_path)
                    
                    # Remove temporary file
                    os.unlink(temp_path)
                    
                    # If successful, add to content
                    if result.get("success", False):
                        if "content" in result:
                            all_content += f"--- Page {i+1} ---\\n{result['content']}\\n\\n"
                        elif "text" in result:
                            all_content += f"--- Page {i+1} ---\\n{result['text']}\\n\\n"
                
                if all_content.strip():
                    return {
                        "success": True,
                        "text": all_content,
                        "method": "multimodal_pdf",
                        "model": multimodal_model,
                        "processing_time": time.time() - start_time
                    }
            
            # Return OCR result if it's valid
            if text.strip():
                return {
                    "success": True,
                    "text": text,
                    "method": "ocr_pdf",
                    "processing_time": time.time() - start_time
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to extract meaningful text from PDF"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing PDF: {str(e)}"
            }
    
    # For text-based documents
    elif file_ext in ['.txt', '.md', '.html', '.csv', '.json', '.xml', '.rst', '.tex']:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            return {
                "success": True,
                "text": text,
                "method": "text_extraction",
                "processing_time": 0
            }
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
                
                return {
                    "success": True,
                    "text": text,
                    "method": "text_extraction",
                    "processing_time": 0
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error reading text file: {str(e)}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing text file: {str(e)}"
            }
    
    # For MS Office documents, we'd need additional libraries like python-docx, etc.
    # This can be expanded as needed
    
    # Unsupported file type
    else:
        return {
            "success": False,
            "error": f"Unsupported file type: {file_ext}"
        }"""
        
        # Update the analyze_image_with_multimodal function to accept a model parameter
        analyze_pattern = r"def analyze_image_with_multimodal\(image_path: str, prompt: Optional\[str\] = None\) -> Dict\[str, Any\]:.*?return \{\s+\"success\": False,\s+\"error\": error_msg\s+\}"
        
        # Enhanced analyze_image_with_multimodal function
        enhanced_analyze = """def analyze_image_with_multimodal(image_path: str, prompt: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
    \"\"\"
    Analyze an image using a multimodal model through Ollama.
    
    Args:
        image_path: Path to the image file
        prompt: Optional prompt to guide the analysis
        model: Optional model override
        
    Returns:
        Analysis result
    \"\"\"
    # Get configuration
    config = load_config()
    
    # Check if multimodal models are defined
    if not model:
        model = config.get("integrations", {}).get("ollama", {}).get("multimodal_model", "llava:latest")
    
    # Prepare the prompt
    if not prompt:
        prompt = "Please analyze this image and extract the text content. Then, provide any insights about the content and its context."
    
    try:
        # Read the image and encode as base64
        with open(image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode("utf-8")
        
        # Call Ollama API for multimodal analysis
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt, "images": [base64_image]}
                ]
            }
        )
        
        # Process response safely
        if response.status_code == 200:
            try:
                result = response.json()
                return {
                    "success": True,
                    "content": result.get("message", {}).get("content", ""),
                    "model": model
                }
            except requests.exceptions.JSONDecodeError:
                # Handle the JSON decode error by parsing the raw text
                content = response.text
                # Basic parsing to extract content from malformed JSON
                content_start = content.find('"content":"')
                content_end = content.find('"}', content_start)
                if content_start > 0 and content_end > 0:
                    extracted_content = content[content_start+11:content_end].replace("\\n", "\\n").replace('\\"', '"')
                    return {
                        "success": True,
                        "content": extracted_content,
                        "model": model
                    }
                else:
                    # If we can't parse it, just return the raw text
                    return {
                        "success": True,
                        "content": f"Raw response: {content[:500]}...",
                        "model": model
                    }
        else:
            error_msg = f"Error calling multimodal model: {response.status_code} - {response.text}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    except Exception as e:
        error_msg = f"Error analyzing image with multimodal model: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return {
            "success": False,
            "error": error_msg
        }"""
        
        # Replace the functions
        new_content = content
        
        if re.search(process_file_pattern, content, re.DOTALL):
            new_content = re.sub(process_file_pattern, enhanced_process_file, new_content, flags=re.DOTALL)
        else:
            print("⚠️ Could not find process_file function in multimodal_integration.py")
            return False
            
        if re.search(analyze_pattern, new_content, re.DOTALL):
            new_content = re.sub(analyze_pattern, enhanced_analyze, new_content, flags=re.DOTALL)
        else:
            print("⚠️ Could not find analyze_image_with_multimodal function in multimodal_integration.py")
            return False
        
        # Write the updated content
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        print("✅ Enhanced multimodal integration")
        return True
    except Exception as e:
        print(f"Error updating multimodal_integration.py: {e}")
        return False

def create_advanced_rag_readme():
    """Create a README file explaining the advanced RAG integration."""
    readme_path = os.path.join('ADVANCED_RAG_README.md')
    
    readme_content = """# Advanced RAG Integration for AI-Socratic-Clarifier

## Overview

This enhancement improves the Retrieval-Augmented Generation (RAG) capabilities of the AI-Socratic-Clarifier by:

1. **Leveraging Large Context Windows**: Utilizes the full context window of models like Gemma 3 (128k tokens) for comprehensive document analysis.
2. **Enhanced Multimodal Document Processing**: Enables the primary model to process image-based documents directly when supported.
3. **Improved Document Content Integration**: Provides better structuring and more content from documents in prompts.
4. **Advanced Retrieval Mechanism**: Goes beyond simple keyword matching with improved relevance scoring.

## Features

### Full Context Utilization

- The system now properly formats document content with clear structure
- Documents are appropriately chunked to fit within context limits
- Clear instructions guide the LLM on how to use the document content

### Smarter Document Retrieval

- Improved relevance scoring based on:
  - Term frequency
  - Position weighting (terms appearing earlier in documents count more)
  - Term length (longer matching terms carry more weight)
- Paragraph-level relevance scoring for better chunk selection
- Advanced mode option to include full documents rather than chunks

### Enhanced Document Processing

- Auto-detection of document types and appropriate processing methods
- Fallback mechanisms for various document formats
- Integration with multimodal models for image-based documents
- Primary model utilization for improved analysis when the model supports multimodal input

### Configuration Options

Added settings in `config.json`:

- `advanced_rag`: Enable/disable advanced RAG features
- `rag_context_limit`: Control how much document content to include
- `use_model_for_rag`: Use the primary model for document processing when possible

## Usage

The advanced RAG capabilities are automatically enabled when the system processes documents. Documents can be uploaded through the document library interface, and the system will process them appropriately based on their format.

When you ask a question that requires document knowledge, the system will:

1. Retrieve the most relevant documents or sections
2. Include as much content as possible within context limits
3. Format the documents clearly for the LLM
4. Instruct the LLM on how to use the document information

## Technical Details

The implementation includes:

- Enhanced document retrieval with improved relevance scoring
- Better document processing for various formats (text, PDF, images)
- Multimodal capabilities for image-based documents
- Context management to maximize document content while respecting model limits

## Requirements

- Ollama with models like Gemma 3, Llava, or other LLMs with large context windows
- Python dependencies for document processing (OCR, PDF handling, etc.)
- Sufficient system memory to handle large context windows

## Limitations

- While the system uses enhanced relevance scoring, it does not yet implement full vector-based similarity search
- Document processing capabilities vary by format and quality
- Very large documents may still need to be truncated to fit context windows
"""
    
    try:
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"✅ Created {readme_path}")
        return True
    except Exception as e:
        print(f"Error creating README: {e}")
        return False

def apply_all_fixes():
    """Apply all advanced RAG fixes."""
    print("\n===== APPLYING ADVANCED RAG FIXES =====\n")
    
    # Update configuration
    print("\nUpdating configuration...")
    config_updated = update_config_for_advanced_rag()
    
    # Fix direct integration
    print("\nEnhancing document context integration...")
    direct_integration_fixed = fix_direct_integration()
    
    # Enhance document RAG routes
    print("\nEnhancing document RAG retrieval and processing...")
    rag_routes_enhanced = enhance_document_rag_routes()
    
    # Update multimodal integration
    print("\nUpdating multimodal integration...")
    multimodal_updated = update_multimodal_integration()
    
    # Create README
    print("\nCreating advanced RAG documentation...")
    readme_created = create_advanced_rag_readme()
    
    # Print summary
    print("\n===== ADVANCED RAG FIXES SUMMARY =====\n")
    print(f"✅ Configuration updated: {config_updated}")
    print(f"✅ Direct integration enhanced: {direct_integration_fixed}")
    print(f"✅ Document RAG routes enhanced: {rag_routes_enhanced}")
    print(f"✅ Multimodal integration updated: {multimodal_updated}")
    print(f"✅ Documentation created: {readme_created}")
    
    # Overall success
    all_succeeded = all([config_updated, direct_integration_fixed, rag_routes_enhanced, 
                         multimodal_updated, readme_created])
    
    if all_succeeded:
        print("\n✅ All advanced RAG fixes applied successfully!")
    else:
        print("\n⚠️ Some fixes could not be applied. Check the logs above for details.")
    
    return all_succeeded

if __name__ == "__main__":
    # Apply all fixes when run directly
    apply_all_fixes()
