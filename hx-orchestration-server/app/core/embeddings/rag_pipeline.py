"""
RAG Pipeline Core Implementation
Enterprise-grade Retrieval-Augmented Generation
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import uuid

import httpx
import numpy as np

from app.services.vector_service import qdrant_service
from app.utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Enterprise RAG pipeline with Qdrant integration"""
    
    def __init__(self, 
                 ollama_url: str = "http://localhost:11434",
                 embedding_model: str = "nomic-embed-text",
                 default_collection: str = "rag_documents"):
        """
        Initialize RAG pipeline
        
        Args:
            ollama_url: Ollama server URL for embeddings
            embedding_model: Default embedding model
            default_collection: Default Qdrant collection
        """
        self.ollama_url = ollama_url
        self.embedding_model = embedding_model
        self.default_collection = default_collection
        self.performance_monitor = PerformanceMonitor()
        
        # RAG configuration
        self.config = {
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "max_chunks_per_document": 50,
            "similarity_threshold": 0.5,
            "max_context_length": 8000,
            "rerank_top_k": 20,
            "final_top_k": 5
        }
    
    async def generate_embeddings(self, 
                                text: Union[str, List[str]], 
                                model: Optional[str] = None) -> List[List[float]]:
        """
        Generate embeddings using Ollama
        
        Args:
            text: Text or list of texts to embed
            model: Embedding model (defaults to instance model)
        """
        try:
            model = model or self.embedding_model
            texts = [text] if isinstance(text, str) else text
            
            embeddings = []
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                for txt in texts:
                    response = await client.post(
                        f"{self.ollama_url}/api/embeddings",
                        json={
                            "model": model,
                            "prompt": txt
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    embeddings.append(result["embedding"])
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise Exception(f"Embedding generation failed: {e}")
    
    def chunk_document(self, 
                      text: str, 
                      chunk_size: Optional[int] = None,
                      overlap: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Chunk document into overlapping segments
        
        Args:
            text: Document text
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
        """
        chunk_size = chunk_size or self.config["chunk_size"]
        overlap = overlap or self.config["chunk_overlap"]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]
            
            # Try to break at sentence boundaries
            if end < len(text):
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.7:  # Only break if we don't lose too much text
                    end = start + break_point + 1
                    chunk_text = text[start:end]
            
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text.strip(),
                "start_pos": start,
                "end_pos": end,
                "size": len(chunk_text)
            })
            
            chunk_id += 1
            start = end - overlap
            
            # Prevent infinite loops
            if start >= end:
                start = end
        
        return chunks
    
    async def ingest_document(self,
                            document: Dict[str, Any],
                            collection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest document into RAG pipeline
        
        Args:
            document: Document with text, metadata, etc.
            collection_name: Target collection
        """
        try:
            collection_name = collection_name or self.default_collection
            doc_id = document.get("id", str(uuid.uuid4()))
            text = document.get("text", "")
            metadata = document.get("metadata", {})
            
            # Chunk the document
            chunks = self.chunk_document(text)
            
            # Generate embeddings for chunks
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = await self.generate_embeddings(chunk_texts)
            
            # Prepare documents for Qdrant
            qdrant_documents = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_doc = {
                    "id": f"{doc_id}_chunk_{i}",
                    "vector": embedding,
                    "text": chunk["text"],
                    "metadata": {
                        **metadata,
                        "document_id": doc_id,
                        "chunk_id": chunk["chunk_id"],
                        "start_pos": chunk["start_pos"],
                        "end_pos": chunk["end_pos"],
                        "chunk_size": chunk["size"],
                        "total_chunks": len(chunks)
                    },
                    "document_type": document.get("document_type", "text"),
                    "source": document.get("source", "unknown"),
                    "timestamp": datetime.utcnow().isoformat()
                }
                qdrant_documents.append(chunk_doc)
            
            # Upsert to Qdrant
            result = await qdrant_service.upsert_documents(
                collection_name=collection_name,
                documents=qdrant_documents
            )
            
            return {
                "status": "success",
                "document_id": doc_id,
                "collection": collection_name,
                "chunks_created": len(chunks),
                "chunks_stored": result["processed"],
                "ingestion_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            raise Exception(f"Document ingestion failed: {e}")
    
    async def retrieve_context(self,
                             query: str,
                             collection_name: Optional[str] = None,
                             top_k: Optional[int] = None,
                             similarity_threshold: Optional[float] = None,
                             filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve relevant context for RAG
        
        Args:
            query: Search query
            collection_name: Collection to search
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            filters: Metadata filters
        """
        try:
            collection_name = collection_name or self.default_collection
            top_k = top_k or self.config["final_top_k"]
            similarity_threshold = similarity_threshold or self.config["similarity_threshold"]
            
            # Generate query embedding
            query_embeddings = await self.generate_embeddings(query)
            query_vector = query_embeddings[0]
            
            # Perform similarity search
            search_result = await qdrant_service.similarity_search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=similarity_threshold,
                filters=filters
            )
            
            # Process results for RAG context
            context_chunks = []
            for result in search_result["results"]:
                context_chunks.append({
                    "text": result["text"],
                    "score": result["score"],
                    "document_id": result["metadata"].get("document_id"),
                    "chunk_id": result["metadata"].get("chunk_id"),
                    "source": result["source"]
                })
            
            # Combine chunks into context
            combined_context = "\n\n".join([chunk["text"] for chunk in context_chunks])
            
            return {
                "status": "success",
                "query": query,
                "collection": collection_name,
                "context": combined_context,
                "chunks": context_chunks,
                "retrieval_stats": {
                    "total_chunks": len(context_chunks),
                    "avg_score": np.mean([c["score"] for c in context_chunks]) if context_chunks else 0,
                    "min_score": min([c["score"] for c in context_chunks]) if context_chunks else 0,
                    "max_score": max([c["score"] for c in context_chunks]) if context_chunks else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            raise Exception(f"Context retrieval failed: {e}")
    
    async def rag_query(self,
                       query: str,
                       llm_url: str,
                       collection_name: Optional[str] = None,
                       model: str = "phi3",
                       max_tokens: int = 1000,
                       temperature: float = 0.7) -> Dict[str, Any]:
        """
        Complete RAG query with retrieval and generation
        
        Args:
            query: User query
            llm_url: LLM server URL
            collection_name: Vector collection to search
            model: LLM model to use
            max_tokens: Maximum response tokens
            temperature: LLM temperature
        """
        try:
            start_time = datetime.utcnow()
            
            # Retrieve relevant context
            retrieval_result = await self.retrieve_context(
                query=query,
                collection_name=collection_name
            )
            
            context = retrieval_result["context"]
            
            # Construct RAG prompt
            rag_prompt = f"""Based on the following context, please answer the question.

Context:
{context}

Question: {query}

Answer: Please provide a comprehensive answer based on the context above. If the context doesn't contain relevant information, please state that clearly."""
            
            # Generate response using LLM
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{llm_url}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "user", "content": rag_prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "stream": False
                    }
                )
                response.raise_for_status()
                llm_result = response.json()
            
            # Extract generated text
            generated_text = llm_result["choices"][0]["message"]["content"]
            
            total_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "status": "success",
                "query": query,
                "answer": generated_text,
                "context_used": context,
                "retrieval_info": retrieval_result["retrieval_stats"],
                "source_chunks": retrieval_result["chunks"],
                "generation_stats": {
                    "model": model,
                    "tokens_used": llm_result.get("usage", {}),
                    "total_time_seconds": total_time
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            raise Exception(f"RAG query failed: {e}")
    
    async def batch_ingest(self,
                         documents: List[Dict[str, Any]],
                         collection_name: Optional[str] = None,
                         batch_size: int = 10) -> Dict[str, Any]:
        """
        Batch ingest multiple documents
        
        Args:
            documents: List of documents to ingest
            collection_name: Target collection
            batch_size: Processing batch size
        """
        try:
            collection_name = collection_name or self.default_collection
            total_docs = len(documents)
            processed = 0
            errors = []
            
            # Process documents in batches
            for i in range(0, total_docs, batch_size):
                batch = documents[i:i + batch_size]
                
                # Process batch concurrently
                tasks = [
                    self.ingest_document(doc, collection_name) 
                    for doc in batch
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        errors.append(f"Document {i+j}: {str(result)}")
                    else:
                        processed += 1
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(total_docs-1)//batch_size + 1}")
            
            return {
                "status": "completed",
                "collection": collection_name,
                "total_documents": total_docs,
                "processed": processed,
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Batch ingestion failed: {e}")
            raise Exception(f"Batch ingestion failed: {e}")

# Global instance
rag_pipeline = RAGPipeline()
