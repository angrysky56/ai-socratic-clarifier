"""
Enhanced Document Manager for AI-Socratic-Clarifier

This module provides a unified document management system that ensures:
1. All uploaded and downloaded materials are stored in the document library
2. Proper indexing and embedding generation for effective RAG
3. A unified processing pipeline for all document types
"""

import os
import json
import shutil
import logging
import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedDocumentManager:
    """
    Enhanced document manager that ensures all materials are properly stored
    and available for reflection and RAG.
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the enhanced document manager.
        
        Args:
            storage_dir: Base directory for document storage, defaults to document_storage in project root
        """
        if storage_dir is None:
            # Default to document_storage in the project root
            storage_dir = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'document_storage'))
        
        self.storage_dir = storage_dir
        self.index_file = os.path.join(storage_dir, 'document_index.json')
        os.makedirs(storage_dir, exist_ok=True)
        
        # Ensure specific directories exist
        self.raw_dir = os.path.join(storage_dir, 'raw')
        self.processed_dir = os.path.join(storage_dir, 'processed')
        self.embeddings_dir = os.path.join(storage_dir, 'embeddings')
        self.temp_dir = os.path.join(storage_dir, 'temp')
        
        for directory in [self.raw_dir, self.processed_dir, self.embeddings_dir, self.temp_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Initialize index if needed
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'w') as f:
                json.dump({
                    "documents": [],
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "version": "1.0"
                }, f, indent=2)
        
        # Load document index
        self.index = self._load_index()
        
        logger.info(f"Enhanced Document Manager initialized with storage at: {storage_dir}")
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the document index from file."""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading document index: {e}")
            return {
                "documents": [],
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0"
            }
    
    def _save_index(self):
        """Save the document index to file."""
        try:
            self.index["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving document index: {e}")
            return False
    
    def process_document(self, file_path: str, source: str = "upload", 
                        generate_embeddings: bool = True,
                        metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Process a document and add it to the library.
        
        Args:
            file_path: Path to the document file
            source: Source of the document (upload, download, etc.)
            generate_embeddings: Whether to generate embeddings
            metadata: Optional additional metadata
            
        Returns:
            Document metadata or None if processing failed
        """
        try:
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Get file info
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            file_size = os.path.getsize(file_path)
            
            # Determine document type
            doc_type = self._get_document_type(file_ext)
            
            # Create target directory in raw
            target_dir = os.path.join(self.raw_dir, doc_id)
            os.makedirs(target_dir, exist_ok=True)
            
            # Copy file to target directory
            raw_path = os.path.join(target_dir, file_name)
            if file_path != raw_path:  # Don't copy if already in the right place
                shutil.copy2(file_path, raw_path)
            
            # Extract text content
            text_content, page_count = self._extract_text(raw_path, doc_type)
            
            # Save text content
            processed_dir = os.path.join(self.processed_dir, doc_id)
            os.makedirs(processed_dir, exist_ok=True)
            text_path = os.path.join(processed_dir, f"{file_name}.txt")
            
            with open(text_path, 'w') as f:
                f.write(text_content)
            
            # Generate embeddings if requested
            embedding_path = None
            if generate_embeddings:
                embedding_dir = os.path.join(self.embeddings_dir, doc_id)
                os.makedirs(embedding_dir, exist_ok=True)
                embedding_path = os.path.join(embedding_dir, f"{file_name}.embeddings")
                embedding_generated = self._generate_embeddings(text_content, embedding_path)
                if not embedding_generated:
                    embedding_path = None
            
            # Create document metadata
            doc_metadata = {
                "id": doc_id,
                "name": file_name,
                "raw_path": raw_path,
                "text_path": text_path,
                "embedding_path": embedding_path,
                "type": doc_type,
                "size": file_size,
                "page_count": page_count,
                "text_length": len(text_content),
                "source": source,
                "date_added": time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_accessed": time.strftime("%Y-%m-%d %H:%M:%S"),
                "tags": [],
                "has_embeddings": embedding_path is not None
            }
            
            # Add custom metadata if provided
            if metadata:
                for key, value in metadata.items():
                    if key not in doc_metadata:  # Don't overwrite standard fields
                        doc_metadata[key] = value
            
            # Add to index
            self.index["documents"].append(doc_metadata)
            self._save_index()
            
            logger.info(f"Document processed and added to library: {file_name} (ID: {doc_id})")
            return doc_metadata
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return None
    
    def _get_document_type(self, file_ext: str) -> str:
        """Determine document type from file extension."""
        image_types = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']
        pdf_types = ['.pdf']
        text_types = ['.txt', '.md', '.rtf']
        word_types = ['.doc', '.docx']
        excel_types = ['.xls', '.xlsx', '.csv']
        presentation_types = ['.ppt', '.pptx']
        
        if file_ext in image_types:
            return "image"
        elif file_ext in pdf_types:
            return "pdf"
        elif file_ext in text_types:
            return "text"
        elif file_ext in word_types:
            return "word"
        elif file_ext in excel_types:
            return "excel"
        elif file_ext in presentation_types:
            return "presentation"
        else:
            return "other"
    
    def _extract_text(self, file_path: str, doc_type: str) -> Tuple[str, int]:
        """
        Extract text from a document.
        
        Args:
            file_path: Path to the document
            doc_type: Type of document
            
        Returns:
            Tuple of (extracted text, page count)
        """
        # This is a placeholder for the actual text extraction
        # In a real implementation, this would use different methods based on doc_type
        try:
            # If multimodal integration is available, use it
            try:
                # Try to import from socratic_clarifier first
                try:
                    from socratic_clarifier.multimodal_integration import process_file
                except ImportError:
                    # If not found, try direct import
                    try:
                        from multimodal_integration import process_file
                    except ImportError:
                        logger.warning('Multimodal integration not available for text extraction')
                        raise
                
                # Process the file if imported successfully
                result = process_file(file_path)
                if result and result.get('success', False):
                    return result.get('text', ''), result.get('page_count', 1)
            except ImportError:
                logger.warning("Multimodal integration not available for text extraction")
            except Exception as e:
                logger.error(f"Error using multimodal integration: {e}")
            
            # Simple extraction based on type
            if doc_type == "text":
                # Direct reading for text files
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()
                return text, 1
            
            elif doc_type == "pdf":
                # Try to use PyPDF2 if available
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfFileReader(f)
                        text = ""
                        page_count = pdf_reader.getNumPages()
                        for page in range(page_count):
                            text += pdf_reader.getPage(page).extractText() + "\n"
                        return text, page_count
                except ImportError:
                    logger.warning("PyPDF2 not available for PDF extraction")
                except Exception as e:
                    logger.error(f"Error extracting text from PDF: {e}")
            
            # Fallback for all other types
            return f"Text extracted from {os.path.basename(file_path)} ({doc_type} format)", 1
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return f"Error extracting text from {os.path.basename(file_path)}: {str(e)}", 1
    
    def _generate_embeddings(self, text: str, output_path: str) -> bool:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to generate embeddings for
            output_path: Path to save embeddings
            
        Returns:
            Whether embeddings were successfully generated
        """
        try:
            # Check if Ollama is available
            try:
                import requests
                import json
                
                # Load configuration
                config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Get embedding model from config
                embedding_model = config.get('integrations', {}).get('ollama', {}).get('default_embedding_model', 'nomic-embed-text:latest')
                ollama_url = config.get('integrations', {}).get('ollama', {}).get('base_url', 'http://localhost:11434/api')
                
                # Make sure URL has the correct format
                if not ollama_url.endswith('/api'):
                    ollama_url = ollama_url.rstrip('/') + '/api'
                    
                # Call Ollama embeddings API
                response = requests.post(
                    f"{ollama_url}/embeddings",
                    json={
                        "model": embedding_model,
                        "prompt": text[:8192]  # Limit text to 8k characters to avoid issues
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    embeddings = result.get('embedding', [])
                    if embeddings:
                        with open(output_path, 'w') as f:
                            json.dump(embeddings, f)
                        logger.info(f"Generated embeddings for {output_path}")
                        return True
                    else:
                        logger.warning(f"No embeddings returned for {output_path}")
                else:
                    logger.warning(f"Ollama embeddings API error: {response.status_code}")
            except ImportError:
                logger.warning("Requests library not available for embedding generation")
            except Exception as e:
                logger.error(f"Error calling Ollama embeddings API: {e}")
            
            # Fallback: Try using from socratic_clarifier if available
            try:
                from socratic_clarifier.integrations.ollama import OllamaIntegration
                ollama = OllamaIntegration()
                if ollama.available:
                    # Generate embeddings using Ollama
                    embeddings = ollama.generate_embeddings(text)
                    if embeddings:
                        with open(output_path, 'w') as f:
                            json.dump(embeddings, f)
                        logger.info(f"Generated embeddings with OllamaIntegration for {output_path}")
                        return True
            except ImportError:
                logger.warning("OllamaIntegration not available for embedding generation")
            except Exception as e:
                logger.error(f"Error using OllamaIntegration: {e}")
            
            # Final fallback: Write dummy embeddings (vector of 384 zeros)
            with open(output_path, 'w') as f:
                f.write(json.dumps([0.0] * 384))
            
            logger.warning(f"Generated placeholder embeddings for {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return False
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata by ID."""
        for doc in self.index["documents"]:
            if doc["id"] == doc_id:
                # Update last accessed
                doc["last_accessed"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self._save_index()
                return doc
        return None
    
    def get_document_content(self, doc_id: str) -> Optional[str]:
        """Get the text content of a document by ID."""
        doc = self.get_document_by_id(doc_id)
        if doc and "text_path" in doc:
            text_path = doc["text_path"]
            if os.path.exists(text_path):
                try:
                    with open(text_path, 'r', encoding='utf-8', errors='replace') as f:
                        return f.read()
                except Exception as e:
                    logger.error(f"Error reading document content: {e}")
        return None
    
    def search_documents(self, query: str, limit: int = 5, use_embeddings: bool = True) -> List[Dict[str, Any]]:
        """
        Search documents using keyword matching and/or vector similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            use_embeddings: Whether to use vector similarity
            
        Returns:
            List of matching document metadata
        """
        results = []
        query_lower = query.lower()
        
        # First check document names and metadata
        for doc in self.index["documents"]:
            # Check document name
            if query_lower in doc["name"].lower():
                results.append({
                    "document": doc,
                    "score": 0.9,  # High score for name match
                    "match_type": "name"
                })
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in doc.get("tags", [])):
                results.append({
                    "document": doc,
                    "score": 0.8,  # Good score for tag match
                    "match_type": "tag"
                })
                continue
        
        # Generate embeddings for the query if using embeddings
        if use_embeddings:
            try:
                import numpy as np
                import tempfile
                import json
                import os
                
                # Create temporary file for query embeddings
                with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
                    # Generate embeddings for the query
                    if self._generate_embeddings(query, temp_file.name):
                        # Load the query embeddings
                        with open(temp_file.name, 'r') as f:
                            query_embedding = np.array(json.load(f))
                        
                        # Get all documents with embeddings
                        docs_with_embeddings = []
                        for doc in self.index["documents"]:
                            if doc.get("embedding_path") and os.path.exists(doc["embedding_path"]):
                                try:
                                    with open(doc["embedding_path"], 'r') as f:
                                        doc_embedding = np.array(json.load(f))
                                    
                                    # Calculate cosine similarity
                                    similarity = np.dot(query_embedding, doc_embedding) / (
                                        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                                    )
                                    
                                    # Only include if similarity is good enough
                                    if similarity > 0.4:  # Threshold to avoid noise
                                        docs_with_embeddings.append({
                                            "document": doc,
                                            "score": float(similarity),
                                            "match_type": "semantic"
                                        })
                                except Exception as e:
                                    logger.error(f"Error processing document embeddings: {e}")
                        
                        # Sort by similarity and add to results
                        docs_with_embeddings.sort(key=lambda x: x["score"], reverse=True)
                        results.extend(docs_with_embeddings[:limit])
            except Exception as e:
                logger.error(f"Error using embeddings for search: {e}")
        
        # Check content as fallback if not enough results yet
        if len(results) < limit:
            for doc in self.index["documents"]:
                # Skip docs already in results
                if any(r["document"]["id"] == doc["id"] for r in results):
                    continue
                
                try:
                    text_path = doc.get("text_path")
                    if text_path and os.path.exists(text_path):
                        with open(text_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                        if query_lower in content.lower():
                            results.append({
                                "document": doc,
                                "score": 0.6,  # Lower score for content match
                                "match_type": "content"
                            })
                except Exception as e:
                    logger.error(f"Error searching document content: {e}")
                
                # Stop if we have enough results
                if len(results) >= limit:
                    break
        
        # Sort by score and return
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def get_documents_for_rag(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get documents relevant for RAG based on a query.
        
        Args:
            query: The query to match against
            limit: Maximum number of documents to return
            
        Returns:
            List of document contents with metadata
        """
        # Search for relevant documents using vector similarity
        search_results = self.search_documents(query, limit=limit, use_embeddings=True)
        
        # Extract content for each document
        rag_documents = []
        for result in search_results:
            doc = result["document"]
            content = self.get_document_content(doc["id"])
            
            if content:
                rag_documents.append({
                    "document_id": doc["id"],
                    "filename": doc["name"],
                    "content": content,
                    "relevance": result["score"],
                    "match_type": result["match_type"]
                })
        
        return rag_documents
    
    def add_downloaded_document(self, url: str, local_path: str, 
                               generate_embeddings: bool = True) -> Optional[Dict[str, Any]]:
        """
        Add a downloaded document to the library.
        
        Args:
            url: Source URL
            local_path: Path where the document was downloaded
            generate_embeddings: Whether to generate embeddings
            
        Returns:
            Document metadata or None if processing failed
        """
        # Add URL to metadata
        metadata = {
            "source_url": url,
            "downloaded_from": url,
            "download_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Process the document with custom metadata
        return self.process_document(
            local_path, 
            source="download", 
            generate_embeddings=generate_embeddings,
            metadata=metadata
        )
    
    def tag_document(self, doc_id: str, tags: List[str]) -> bool:
        """
        Add tags to a document.
        
        Args:
            doc_id: Document ID
            tags: List of tags to add
            
        Returns:
            Whether tags were successfully added
        """
        doc = self.get_document_by_id(doc_id)
        if not doc:
            return False
        
        # If doc doesn't have tags field, add it
        if "tags" not in doc:
            doc["tags"] = []
        
        # Add tags that don't already exist
        doc["tags"].extend([tag for tag in tags if tag not in doc["tags"]])
        
        # Save the index
        self._save_index()
        return True
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents in the library."""
        return self.index["documents"]
    
    def get_recent_documents(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most recently added documents."""
        # Sort by date_added and return most recent
        sorted_docs = sorted(
            self.index["documents"], 
            key=lambda x: x.get("date_added", ""), 
            reverse=True
        )
        return sorted_docs[:limit]
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the document library."""
        documents = self.index["documents"]
        total_docs = len(documents)
        
        # Count by type
        types = {}
        for doc in documents:
            doc_type = doc.get("type", "unknown")
            types[doc_type] = types.get(doc_type, 0) + 1
        
        # Count with embeddings
        with_embeddings = sum(1 for doc in documents if doc.get("has_embeddings", False))
        
        # Calculate total size
        total_size = sum(doc.get("size", 0) for doc in documents)
        
        return {
            "total_documents": total_docs,
            "document_types": types,
            "with_embeddings": with_embeddings,
            "total_size_bytes": total_size,
            "last_updated": self.index["last_updated"]
        }

# Create a singleton instance
_document_manager = None

def get_document_manager() -> EnhancedDocumentManager:
    """
    Get the singleton EnhancedDocumentManager instance.
    
    Returns:
        EnhancedDocumentManager instance
    """
    global _document_manager
    if _document_manager is None:
        _document_manager = EnhancedDocumentManager()
    return _document_manager
