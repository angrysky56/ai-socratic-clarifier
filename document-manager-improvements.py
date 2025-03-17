"""
Enhanced Document Manager for AI-Socratic-Clarifier

This extension adds improved vector-based retrieval functionality to the DocumentManager class
to better support RAG (Retrieval-Augmented Generation).
"""

import numpy as np
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

def add_to_document_manager_class():
    """
    These functions should be added to the EnhancedDocumentManager class in 
    enhanced_integration/document_manager.py to improve vector-based retrieval.
    """
    
    def _calculate_similarity(self, query_embedding: List[float], document_embedding: List[float]) -> float:
        """
        Calculate cosine similarity between query and document embeddings.
        
        Args:
            query_embedding: Embedding vector for the query
            document_embedding: Embedding vector for the document
            
        Returns:
            Cosine similarity score
        """
        try:
            # Convert to numpy arrays for calculation
            query_array = np.array(query_embedding)
            doc_array = np.array(document_embedding)
            
            # Calculate cosine similarity
            dot_product = np.dot(query_array, doc_array)
            query_norm = np.linalg.norm(query_array)
            doc_norm = np.linalg.norm(doc_array)
            
            if query_norm == 0 or doc_norm == 0:
                return 0.0
                
            similarity = dot_product / (query_norm * doc_norm)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _load_embedding(self, embedding_path: str) -> Optional[List[float]]:
        """
        Load embedding vector from file.
        
        Args:
            embedding_path: Path to the embedding file
            
        Returns:
            Embedding vector or None if loading failed
        """
        try:
            if not os.path.exists(embedding_path):
                return None
                
            with open(embedding_path, 'r') as f:
                embedding = json.load(f)
            
            return embedding
        except Exception as e:
            logger.error(f"Error loading embedding from {embedding_path}: {e}")
            return None
    
    def vector_search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search documents using vector similarity if available, with fallback to keyword search.
        
        Args:
            query: Query text
            limit: Maximum number of results to return
            
        Returns:
            List of relevant documents with similarity scores
        """
        try:
            # Try to generate embeddings for the query
            query_embedding = None
            try:
                from socratic_clarifier.integrations.ollama import OllamaIntegration
                ollama = OllamaIntegration()
                if ollama.available:
                    query_embedding = ollama.generate_embeddings(query)
            except ImportError:
                logger.warning("Ollama integration not available for embedding generation")
            
            # If we couldn't generate embeddings, fall back to keyword search
            if not query_embedding:
                logger.info("Vector search not available, falling back to keyword search")
                return self.search_documents(query, limit)
            
            # Get all documents with embeddings
            results = []
            for doc in self.index["documents"]:
                if not doc.get("has_embeddings", False) or not doc.get("embedding_path"):
                    continue
                
                # Load document embedding
                doc_embedding = self._load_embedding(doc["embedding_path"])
                if not doc_embedding:
                    continue
                
                # Calculate similarity
                similarity = self._calculate_similarity(query_embedding, doc_embedding)
                
                # Add to results if similarity is above threshold
                if similarity > 0.5:  # Adjustable threshold
                    results.append({
                        "document": doc,
                        "score": similarity,
                        "match_type": "vector"
                    })
            
            # If we have few vector results, supplement with keyword search
            if len(results) < limit:
                keyword_results = self.search_documents(query, limit=(limit - len(results)))
                # Only add keyword results that aren't already in vector results
                doc_ids = {r["document"]["id"] for r in results}
                for kr in keyword_results:
                    if kr["document"]["id"] not in doc_ids:
                        kr["match_type"] = "keyword"  # Mark as keyword match
                        results.append(kr)
            
            # Sort by score and return
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            # Fall back to keyword search
            return self.search_documents(query, limit)
    
    def get_documents_for_rag(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get documents relevant for RAG based on a query.
        Uses vector search when available.
        
        Args:
            query: The query to match against
            limit: Maximum number of documents to return
            
        Returns:
            List of document contents with metadata
        """
        # Get relevant documents using vector search when available
        search_results = self.vector_search_documents(query, limit=limit)
        
        # Extract content for each document
        rag_documents = []
        for result in search_results:
            doc = result["document"]
            content = self.get_document_content(doc["id"])
            
            if content:
                rag_documents.append({
                    "document_id": doc["id"],
                    "filename": doc.get("name", "Unknown"),
                    "content": content,
                    "relevance": result["score"],
                    "match_type": result.get("match_type", "unknown")
                })
        
        return rag_documents
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and all its associated files.
        
        Args:
            doc_id: ID of the document to delete
            
        Returns:
            Whether deletion was successful
        """
        try:
            # Find document in index
            doc = self.get_document_by_id(doc_id)
            if not doc:
                logger.warning(f"Document not found for deletion: {doc_id}")
                return False
            
            # Get paths to document directories
            raw_dir = os.path.dirname(doc.get("raw_path", ""))
            processed_dir = os.path.dirname(doc.get("text_path", ""))
            embedding_dir = os.path.dirname(doc.get("embedding_path", "")) if doc.get("embedding_path") else None
            
            # Remove document from index
            self.index["documents"] = [d for d in self.index["documents"] if d["id"] != doc_id]
            self._save_index()
            
            # Delete directories if they exist
            import shutil
            if raw_dir and os.path.exists(raw_dir):
                shutil.rmtree(raw_dir)
                
            if processed_dir and os.path.exists(processed_dir) and processed_dir != raw_dir:
                shutil.rmtree(processed_dir)
                
            if embedding_dir and os.path.exists(embedding_dir) and embedding_dir != raw_dir and embedding_dir != processed_dir:
                shutil.rmtree(embedding_dir)
            
            logger.info(f"Document deleted successfully: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
