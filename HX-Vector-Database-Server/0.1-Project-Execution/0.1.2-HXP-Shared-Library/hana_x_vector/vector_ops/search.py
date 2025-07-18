"""
Search Engine
============

Advanced similarity search algorithms and optimization for vector operations.
Provides multiple search strategies and performance optimizations.
"""

from typing import List, Dict, Any, Optional, Tuple
import time
import numpy as np
from ..qdrant.client import QdrantClient
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import VectorOperationError


class SearchEngine:
    """
    Advanced search engine for vector similarity operations.
    Supports multiple search algorithms and optimization strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.qdrant_client = QdrantClient(config)
        self.metrics = MetricsCollector()
        
        # Search configuration
        self.search_config = config.get("search", {})
        self.default_limit = self.search_config.get("default_limit", 10)
        self.max_limit = self.search_config.get("max_limit", 1000)
        self.default_score_threshold = self.search_config.get("score_threshold", 0.0)
        
        # Performance optimization settings
        self.use_approximate_search = self.search_config.get("approximate_search", True)
        self.search_timeout = self.search_config.get("timeout", 30.0)
        self.parallel_search_threshold = self.search_config.get("parallel_threshold", 100)
    
    async def startup(self):
        """Initialize search engine."""
        await self.qdrant_client.startup()
    
    async def shutdown(self):
        """Cleanup search engine."""
        await self.qdrant_client.shutdown()
    
    async def similarity_search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = None,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None,
        search_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform similarity search with advanced optimization.
        
        Args:
            collection_name: Name of the collection to search
            query_vector: Query vector for similarity search
            limit: Maximum number of results
            filters: Metadata filters
            score_threshold: Minimum similarity score
            search_params: Additional search parameters
            
        Returns:
            Dict with search results and metadata
        """
        start_time = time.time()
        
        try:
            # Validate and normalize parameters
            limit = min(limit or self.default_limit, self.max_limit)
            score_threshold = score_threshold or self.default_score_threshold
            
            # Optimize search parameters based on query characteristics
            optimized_params = self._optimize_search_params(
                query_vector, limit, filters, search_params
            )
            
            # Perform the search
            if limit > self.parallel_search_threshold:
                # Use parallel search for large result sets
                results = await self._parallel_search(
                    collection_name, query_vector, limit, filters, 
                    score_threshold, optimized_params
                )
            else:
                # Use standard search for smaller result sets
                results = await self._standard_search(
                    collection_name, query_vector, limit, filters,
                    score_threshold, optimized_params
                )
            
            # Post-process results
            processed_results = self._post_process_results(
                results, score_threshold
            )
            
            # Record metrics
            duration = time.time() - start_time
            self.metrics.record_histogram("search_duration", duration)
            self.metrics.record_histogram("search_result_count", len(processed_results))
            
            return {
                "results": processed_results,
                "duration": duration,
                "collection": collection_name,
                "query_params": {
                    "limit": limit,
                    "score_threshold": score_threshold,
                    "filters": filters
                }
            }
            
        except Exception as e:
            self.metrics.increment_counter("search_errors")
            raise VectorOperationError(f"Search failed: {str(e)}")
    
    async def multi_vector_search(
        self,
        collection_name: str,
        query_vectors: List[List[float]],
        limit: int = None,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None,
        aggregation_method: str = "average"
    ) -> Dict[str, Any]:
        """
        Perform multi-vector search with result aggregation.
        
        Args:
            collection_name: Name of the collection to search
            query_vectors: List of query vectors
            limit: Maximum number of results
            filters: Metadata filters
            score_threshold: Minimum similarity score
            aggregation_method: Method for aggregating results
            
        Returns:
            Dict with aggregated search results
        """
        start_time = time.time()
        
        try:
            # Perform individual searches
            individual_results = []
            for query_vector in query_vectors:
                result = await self.similarity_search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=limit,
                    filters=filters,
                    score_threshold=score_threshold
                )
                individual_results.append(result["results"])
            
            # Aggregate results
            aggregated_results = self._aggregate_search_results(
                individual_results, aggregation_method, limit
            )
            
            duration = time.time() - start_time
            self.metrics.record_histogram("multi_vector_search_duration", duration)
            
            return {
                "results": aggregated_results,
                "duration": duration,
                "collection": collection_name,
                "query_count": len(query_vectors),
                "aggregation_method": aggregation_method
            }
            
        except Exception as e:
            self.metrics.increment_counter("multi_vector_search_errors")
            raise VectorOperationError(f"Multi-vector search failed: {str(e)}")
    
    async def hybrid_search(
        self,
        collection_name: str,
        query_vector: List[float],
        text_query: Optional[str] = None,
        limit: int = None,
        filters: Optional[Dict[str, Any]] = None,
        vector_weight: float = 0.7,
        text_weight: float = 0.3
    ) -> Dict[str, Any]:
        """
        Perform hybrid search combining vector and text search.
        
        Args:
            collection_name: Name of the collection to search
            query_vector: Query vector for similarity search
            text_query: Text query for keyword search
            limit: Maximum number of results
            filters: Metadata filters
            vector_weight: Weight for vector search results
            text_weight: Weight for text search results
            
        Returns:
            Dict with hybrid search results
        """
        start_time = time.time()
        
        try:
            # Perform vector search
            vector_results = await self.similarity_search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit * 2,  # Get more results for better hybrid ranking
                filters=filters
            )
            
            # Perform text search if text query provided
            text_results = []
            if text_query:
                text_results = await self._text_search(
                    collection_name, text_query, limit * 2, filters
                )
            
            # Combine and rank results
            hybrid_results = self._combine_hybrid_results(
                vector_results["results"], text_results, 
                vector_weight, text_weight, limit
            )
            
            duration = time.time() - start_time
            self.metrics.record_histogram("hybrid_search_duration", duration)
            
            return {
                "results": hybrid_results,
                "duration": duration,
                "collection": collection_name,
                "search_type": "hybrid",
                "weights": {"vector": vector_weight, "text": text_weight}
            }
            
        except Exception as e:
            self.metrics.increment_counter("hybrid_search_errors")
            raise VectorOperationError(f"Hybrid search failed: {str(e)}")
    
    async def _standard_search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int,
        filters: Optional[Dict[str, Any]],
        score_threshold: float,
        search_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Perform standard vector search."""
        return await self.qdrant_client.search_vectors(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            filters=filters,
            score_threshold=score_threshold,
            search_params=search_params
        )
    
    async def _parallel_search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int,
        filters: Optional[Dict[str, Any]],
        score_threshold: float,
        search_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Perform parallel search for large result sets."""
        # Split search into multiple smaller searches and combine results
        chunk_size = self.parallel_search_threshold
        num_chunks = (limit + chunk_size - 1) // chunk_size
        
        # Create search tasks
        search_tasks = []
        for i in range(num_chunks):
            chunk_limit = min(chunk_size, limit - i * chunk_size)
            if chunk_limit > 0:
                task = self._standard_search(
                    collection_name, query_vector, chunk_limit,
                    filters, score_threshold, search_params
                )
                search_tasks.append(task)
        
        # Execute searches in parallel
        import asyncio
        chunk_results = await asyncio.gather(*search_tasks)
        
        # Combine and sort results
        all_results = []
        for chunk in chunk_results:
            all_results.extend(chunk)
        
        # Sort by score and return top results
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return all_results[:limit]
    
    async def _text_search(
        self,
        collection_name: str,
        text_query: str,
        limit: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Perform text-based search on metadata."""
        # Implement text search using Qdrant's payload filtering
        text_filter = {
            "must": [
                {
                    "key": "text_content",
                    "match": {
                        "text": text_query
                    }
                }
            ]
        }
        
        # Combine with existing filters
        if filters:
            if "must" in filters:
                text_filter["must"].extend(filters["must"])
            else:
                text_filter.update(filters)
        
        # Perform search with text filter
        return await self.qdrant_client.scroll_points(
            collection_name=collection_name,
            filters=text_filter,
            limit=limit
        )
    
    def _optimize_search_params(
        self,
        query_vector: List[float],
        limit: int,
        filters: Optional[Dict[str, Any]],
        search_params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Optimize search parameters based on query characteristics."""
        params = search_params or {}
        
        # Adjust search parameters based on limit
        if limit > 100:
            params["hnsw_ef"] = min(limit * 2, 512)
        else:
            params["hnsw_ef"] = max(limit * 4, 64)
        
        # Adjust for filtered searches
        if filters:
            params["exact"] = False  # Use approximate search for filtered queries
        
        # Vector-specific optimizations
        vector_norm = np.linalg.norm(query_vector)
        if vector_norm < 0.1:  # Very small vector
            params["rescore"] = True
        
        return params
    
    def _post_process_results(
        self,
        results: List[Dict[str, Any]],
        score_threshold: float
    ) -> List[Dict[str, Any]]:
        """Post-process search results."""
        processed_results = []
        
        for result in results:
            # Apply score threshold
            if result.get("score", 0) >= score_threshold:
                # Add additional metadata
                result["search_timestamp"] = time.time()
                processed_results.append(result)
        
        return processed_results
    
    def _aggregate_search_results(
        self,
        individual_results: List[List[Dict[str, Any]]],
        aggregation_method: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Aggregate results from multiple searches."""
        if aggregation_method == "average":
            return self._average_aggregation(individual_results, limit)
        elif aggregation_method == "max":
            return self._max_aggregation(individual_results, limit)
        elif aggregation_method == "weighted":
            return self._weighted_aggregation(individual_results, limit)
        else:
            raise VectorOperationError(f"Unknown aggregation method: {aggregation_method}")
    
    def _average_aggregation(
        self,
        individual_results: List[List[Dict[str, Any]]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Aggregate results using average scoring."""
        # Collect all unique results
        result_map = {}
        
        for results in individual_results:
            for result in results:
                result_id = result["id"]
                if result_id not in result_map:
                    result_map[result_id] = {
                        "id": result_id,
                        "scores": [],
                        "metadata": result.get("metadata", {}),
                        "vector": result.get("vector")
                    }
                result_map[result_id]["scores"].append(result["score"])
        
        # Calculate average scores
        aggregated_results = []
        for result_data in result_map.values():
            avg_score = sum(result_data["scores"]) / len(result_data["scores"])
            aggregated_results.append({
                "id": result_data["id"],
                "score": avg_score,
                "metadata": result_data["metadata"],
                "vector": result_data["vector"]
            })
        
        # Sort by average score and return top results
        aggregated_results.sort(key=lambda x: x["score"], reverse=True)
        return aggregated_results[:limit]
    
    def _max_aggregation(
        self,
        individual_results: List[List[Dict[str, Any]]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Aggregate results using maximum scoring."""
        # Similar to average but use max score
        result_map = {}
        
        for results in individual_results:
            for result in results:
                result_id = result["id"]
                if result_id not in result_map:
                    result_map[result_id] = result
                else:
                    # Keep result with higher score
                    if result["score"] > result_map[result_id]["score"]:
                        result_map[result_id] = result
        
        # Sort by score and return top results
        aggregated_results = list(result_map.values())
        aggregated_results.sort(key=lambda x: x["score"], reverse=True)
        return aggregated_results[:limit]
    
    def _weighted_aggregation(
        self,
        individual_results: List[List[Dict[str, Any]]],
        limit: int,
        weights: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """Aggregate results using weighted scoring."""
        if weights is None:
            weights = [1.0] * len(individual_results)
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Collect weighted results
        result_map = {}
        
        for i, results in enumerate(individual_results):
            weight = weights[i]
            for result in results:
                result_id = result["id"]
                weighted_score = result["score"] * weight
                
                if result_id not in result_map:
                    result_map[result_id] = {
                        "id": result_id,
                        "score": weighted_score,
                        "metadata": result.get("metadata", {}),
                        "vector": result.get("vector")
                    }
                else:
                    result_map[result_id]["score"] += weighted_score
        
        # Sort by weighted score and return top results
        aggregated_results = list(result_map.values())
        aggregated_results.sort(key=lambda x: x["score"], reverse=True)
        return aggregated_results[:limit]
    
    def _combine_hybrid_results(
        self,
        vector_results: List[Dict[str, Any]],
        text_results: List[Dict[str, Any]],
        vector_weight: float,
        text_weight: float,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Combine vector and text search results."""
        # Normalize scores and combine
        result_map = {}
        
        # Add vector results
        for result in vector_results:
            result_id = result["id"]
            result_map[result_id] = {
                "id": result_id,
                "score": result["score"] * vector_weight,
                "metadata": result.get("metadata", {}),
                "vector": result.get("vector"),
                "sources": ["vector"]
            }
        
        # Add text results
        for result in text_results:
            result_id = result["id"]
            text_score = result.get("score", 1.0) * text_weight
            
            if result_id in result_map:
                result_map[result_id]["score"] += text_score
                result_map[result_id]["sources"].append("text")
            else:
                result_map[result_id] = {
                    "id": result_id,
                    "score": text_score,
                    "metadata": result.get("metadata", {}),
                    "vector": result.get("vector"),
                    "sources": ["text"]
                }
        
        # Sort by combined score and return top results
        hybrid_results = list(result_map.values())
        hybrid_results.sort(key=lambda x: x["score"], reverse=True)
        return hybrid_results[:limit]
