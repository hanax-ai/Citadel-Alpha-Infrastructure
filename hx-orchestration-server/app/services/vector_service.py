"""
Qdrant Vector Database Service
Enterprise-grade vector operations for RAG pipeline
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, CreateCollection, PointStruct, 
    Filter, FieldCondition, Match, SearchRequest, 
    UpdateCollection, OptimizersConfigDiff, QuantizationConfig,
    ScalarQuantization, ScalarType
)
from qdrant_client.http.exceptions import UnexpectedResponse
import numpy as np

from app.utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

class QdrantService:
    """Enterprise Qdrant vector database service for RAG operations"""
    
    def __init__(self, 
                 url: str = "http://192.168.10.30:6333",
                 timeout: int = 30,
                 prefer_grpc: bool = False):
        """
        Initialize Qdrant service
        
        Args:
            url: Qdrant server URL
            timeout: Request timeout in seconds
            prefer_grpc: Use gRPC instead of HTTP
        """
        self.url = url
        self.timeout = timeout
        self.client = QdrantClient(
            url=url,
            timeout=timeout,
            prefer_grpc=prefer_grpc
        )
        self.performance_monitor = PerformanceMonitor()
        
        # Default collection configurations
        self.default_vector_config = VectorParams(
            size=1024,  # Default for nomic-embed-text
            distance=Distance.COSINE
        )
        
        # Collection templates for different use cases
        self.collection_templates = {
            "rag_documents": {
                "vector_size": 1024,
                "distance": Distance.COSINE,
                "description": "RAG document embeddings"
            },
            "rag_conversations": {
                "vector_size": 1024, 
                "distance": Distance.COSINE,
                "description": "Conversation context embeddings"
            },
            "business_knowledge": {
                "vector_size": 1024,
                "distance": Distance.COSINE,
                "description": "Business domain knowledge base"
            },
            "code_snippets": {
                "vector_size": 1024,
                "distance": Distance.COSINE,
                "description": "Code and technical documentation"
            }
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Check Qdrant service health"""
        try:
            # Test basic connectivity and get collections
            collections = await asyncio.to_thread(self.client.get_collections)
            
            # Try a simple operation to verify the service is working
            collection_names = [c.name for c in collections.collections]
            
            return {
                "status": "healthy",
                "total_collections": len(collections.collections),
                "collections": collection_names,
                "timestamp": datetime.utcnow().isoformat(),
                "url": self.url
            }
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "url": self.url
            }
    
    async def create_rag_collection(self, 
                                  collection_name: str,
                                  vector_size: int = 1024,
                                  distance: Distance = Distance.COSINE,
                                  optimize_for_performance: bool = True) -> Dict[str, Any]:
        """
        Create optimized collection for RAG operations
        
        Args:
            collection_name: Name for the collection
            vector_size: Dimension of vectors
            distance: Distance metric
            optimize_for_performance: Enable performance optimizations
        """
        try:
            # Check if collection exists
            collections = await asyncio.to_thread(self.client.get_collections)
            existing_names = [c.name for c in collections.collections]
            
            if collection_name in existing_names:
                logger.info(f"Collection '{collection_name}' already exists")
                return {"status": "exists", "collection": collection_name}
            
            # Create collection with optimizations
            vector_config = VectorParams(
                size=vector_size,
                distance=distance
            )
            
            create_params = {
                "collection_name": collection_name,
                "vectors_config": vector_config
            }
            
            # Add performance optimizations
            if optimize_for_performance:
                create_params["optimizers_config"] = OptimizersConfigDiff(
                    default_segment_number=2,
                    max_segment_size=200000,
                    memmap_threshold=20000,
                    indexing_threshold=20000,
                    flush_interval_sec=5,
                    max_optimization_threads=0  # Use all available threads
                )
                
                # Enable quantization for better performance
                create_params["quantization_config"] = QuantizationConfig(
                    scalar=ScalarQuantization(
                        type=ScalarType.INT8,
                        quantile=0.99,
                        always_ram=True
                    )
                )
            
            # Create collection
            result = await asyncio.to_thread(
                self.client.create_collection,
                **create_params
            )
            
            logger.info(f"Created RAG collection '{collection_name}' with {vector_size}D vectors")
            return {
                "status": "created",
                "collection": collection_name,
                "vector_size": vector_size,
                "distance": distance.value,
                "optimized": optimize_for_performance
            }
            
        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {e}")
            raise Exception(f"Collection creation failed: {e}")
    
    async def upsert_documents(self, 
                             collection_name: str,
                             documents: List[Dict[str, Any]],
                             batch_size: int = 100) -> Dict[str, Any]:
        """
        Upsert documents with embeddings into collection
        
        Args:
            collection_name: Target collection
            documents: List of documents with embeddings and metadata
            batch_size: Batch size for upsert operations
        """
        try:
            total_docs = len(documents)
            processed = 0
            errors = []
            
            # Process in batches
            for i in range(0, total_docs, batch_size):
                batch = documents[i:i + batch_size]
                points = []
                
                for doc in batch:
                    # Generate UUID if not provided
                    doc_id = doc.get('id', str(uuid.uuid4()))
                    vector = doc.get('vector', doc.get('embedding'))
                    payload = doc.get('metadata', {})
                    
                    # Add document text and timestamp to payload
                    payload.update({
                        'text': doc.get('text', ''),
                        'timestamp': doc.get('timestamp', datetime.utcnow().isoformat()),
                        'document_type': doc.get('document_type', 'unknown'),
                        'source': doc.get('source', 'unknown')
                    })
                    
                    if vector is None:
                        errors.append(f"Document {doc_id}: Missing vector/embedding")
                        continue
                    
                    points.append(PointStruct(
                        id=doc_id,
                        vector=vector,
                        payload=payload
                    ))
                
                if points:
                    # Upsert batch
                    await asyncio.to_thread(
                        self.client.upsert,
                        collection_name=collection_name,
                        points=points
                    )
                    processed += len(points)
                    
                    logger.info(f"Upserted batch {i//batch_size + 1}: {len(points)} documents")
            
            return {
                "status": "success",
                "collection": collection_name,
                "total_documents": total_docs,
                "processed": processed,
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to upsert documents to '{collection_name}': {e}")
            raise Exception(f"Document upsert failed: {e}")
    
    async def similarity_search(self,
                              collection_name: str,
                              query_vector: List[float],
                              limit: int = 5,
                              score_threshold: float = 0.0,
                              filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform similarity search for RAG retrieval
        
        Args:
            collection_name: Collection to search
            query_vector: Query embedding vector
            limit: Maximum results to return
            score_threshold: Minimum similarity score
            filters: Optional metadata filters
        """
        try:
            start_time = datetime.utcnow()
            
            # Build search request
            search_params = {
                "collection_name": collection_name,
                "query_vector": query_vector,
                "limit": limit,
                "score_threshold": score_threshold,
                "with_payload": True,
                "with_vectors": False  # Don't return vectors by default
            }
            
            # Add filters if provided
            if filters:
                filter_conditions = []
                for field, value in filters.items():
                    if isinstance(value, list):
                        # Multiple values - OR condition
                        for v in value:
                            filter_conditions.append(
                                FieldCondition(key=field, match=Match(value=v))
                            )
                    else:
                        filter_conditions.append(
                            FieldCondition(key=field, match=Match(value=value))
                        )
                
                if filter_conditions:
                    search_params["query_filter"] = Filter(should=filter_conditions)
            
            # Perform search
            results = await asyncio.to_thread(
                self.client.search,
                **search_params
            )
            
            # Process results
            search_results = []
            for result in results:
                search_results.append({
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"},
                    "document_type": result.payload.get("document_type", "unknown"),
                    "source": result.payload.get("source", "unknown"),
                    "timestamp": result.payload.get("timestamp")
                })
            
            search_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "status": "success",
                "collection": collection_name,
                "query_stats": {
                    "total_results": len(search_results),
                    "search_time_seconds": search_time,
                    "score_threshold": score_threshold,
                    "filters_applied": filters is not None
                },
                "results": search_results
            }
            
        except Exception as e:
            logger.error(f"Similarity search failed in '{collection_name}': {e}")
            raise Exception(f"Search operation failed: {e}")
    
    async def hybrid_search(self,
                          collection_name: str, 
                          query_vector: List[float],
                          query_text: str,
                          limit: int = 10,
                          vector_weight: float = 0.7,
                          text_weight: float = 0.3) -> Dict[str, Any]:
        """
        Hybrid search combining vector similarity and text matching
        
        Args:
            collection_name: Collection to search
            query_vector: Query embedding
            query_text: Query text for keyword matching
            limit: Maximum results
            vector_weight: Weight for vector similarity
            text_weight: Weight for text matching
        """
        try:
            # Perform vector search
            vector_results = await self.similarity_search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit * 2,  # Get more results for hybrid ranking
                score_threshold=0.0
            )
            
            # Perform text-based filtering
            text_tokens = query_text.lower().split()
            hybrid_results = []
            
            for result in vector_results["results"]:
                text_content = result["text"].lower()
                
                # Calculate text matching score
                text_matches = sum(1 for token in text_tokens if token in text_content)
                text_score = text_matches / len(text_tokens) if text_tokens else 0
                
                # Combine scores
                vector_score = result["score"]
                hybrid_score = (vector_weight * vector_score) + (text_weight * text_score)
                
                hybrid_results.append({
                    **result,
                    "hybrid_score": hybrid_score,
                    "vector_score": vector_score,
                    "text_score": text_score
                })
            
            # Sort by hybrid score and limit results
            hybrid_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
            final_results = hybrid_results[:limit]
            
            return {
                "status": "success",
                "collection": collection_name,
                "search_type": "hybrid",
                "query_stats": {
                    "total_results": len(final_results),
                    "vector_weight": vector_weight,
                    "text_weight": text_weight,
                    "query_text": query_text
                },
                "results": final_results
            }
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            raise Exception(f"Hybrid search failed: {e}")
    
    async def delete_documents(self,
                             collection_name: str,
                             document_ids: List[str]) -> Dict[str, Any]:
        """Delete documents by IDs"""
        try:
            await asyncio.to_thread(
                self.client.delete,
                collection_name=collection_name,
                points_selector=document_ids
            )
            
            return {
                "status": "success",
                "collection": collection_name,
                "deleted_count": len(document_ids),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise Exception(f"Document deletion failed: {e}")
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get detailed collection information"""
        try:
            info = await asyncio.to_thread(
                self.client.get_collection,
                collection_name=collection_name
            )
            
            return {
                "name": collection_name,
                "status": info.status.value,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": info.config.params.vectors.distance.value
                },
                "payload_schema": info.payload_schema
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise Exception(f"Collection info retrieval failed: {e}")
    
    async def initialize_rag_collections(self) -> Dict[str, Any]:
        """Initialize standard RAG collections"""
        try:
            results = {}
            
            for collection_name, config in self.collection_templates.items():
                result = await self.create_rag_collection(
                    collection_name=collection_name,
                    vector_size=config["vector_size"],
                    distance=config["distance"],
                    optimize_for_performance=True
                )
                results[collection_name] = result
                
            return {
                "status": "success",
                "initialized_collections": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG collections: {e}")
            raise Exception(f"RAG collections initialization failed: {e}")

# Global instance
qdrant_service = QdrantService()
