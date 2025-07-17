"""
Batch Processor
==============

High-performance batch processing for vector operations.
Handles bulk insertions, updates, and deletions with optimization.
"""

from typing import List, Dict, Any, Optional, AsyncGenerator
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from ..qdrant.client import QdrantClient
from ..monitoring.metrics import MetricsCollector
from ..utils.exceptions import VectorOperationError
from ..utils.validators import validate_vector_data


class BatchProcessor:
    """
    High-performance batch processor for vector operations.
    Optimizes bulk operations with parallel processing and chunking.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.qdrant_client = QdrantClient(config)
        self.metrics = MetricsCollector()
        
        # Batch processing configuration
        batch_config = config.get("batch", {})
        self.default_batch_size = batch_config.get("batch_size", 1000)
        self.max_batch_size = batch_config.get("max_batch_size", 10000)
        self.parallel_batches = batch_config.get("parallel_batches", 4)
        self.batch_timeout = batch_config.get("timeout", 300.0)  # 5 minutes
        
        # Performance optimization
        self.use_parallel_processing = batch_config.get("parallel_processing", True)
        self.chunk_size = batch_config.get("chunk_size", 100)
        self.max_retries = batch_config.get("max_retries", 3)
        self.retry_delay = batch_config.get("retry_delay", 1.0)
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=self.parallel_batches)
    
    async def startup(self):
        """Initialize batch processor."""
        await self.qdrant_client.startup()
    
    async def shutdown(self):
        """Cleanup batch processor."""
        await self.qdrant_client.shutdown()
        self.thread_pool.shutdown(wait=True)
    
    async def process_batch(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a batch of mixed operations.
        
        Args:
            operations: List of operation dictionaries
            
        Returns:
            Dict with batch processing results
        """
        start_time = time.time()
        
        try:
            # Group operations by type
            grouped_ops = self._group_operations(operations)
            
            # Process each operation type
            results = {}
            
            if "insert" in grouped_ops:
                insert_result = await self._process_insert_batch(grouped_ops["insert"])
                results["insert"] = insert_result
            
            if "update" in grouped_ops:
                update_result = await self._process_update_batch(grouped_ops["update"])
                results["update"] = update_result
            
            if "delete" in grouped_ops:
                delete_result = await self._process_delete_batch(grouped_ops["delete"])
                results["delete"] = delete_result
            
            # Calculate totals
            total_processed = sum(r.get("processed_count", 0) for r in results.values())
            total_errors = sum(r.get("error_count", 0) for r in results.values())
            
            duration = time.time() - start_time
            self.metrics.record_histogram("batch_processing_duration", duration)
            self.metrics.increment_counter("batch_operations_processed", total_processed)
            
            return {
                "total_processed": total_processed,
                "total_errors": total_errors,
                "duration": duration,
                "results": results,
                "success_rate": (total_processed - total_errors) / total_processed if total_processed > 0 else 0
            }
            
        except Exception as e:
            self.metrics.increment_counter("batch_processing_errors")
            raise VectorOperationError(f"Batch processing failed: {str(e)}")
    
    async def insert_batch(
        self,
        collection_name: str,
        vectors: List[Dict[str, Any]],
        batch_size: int = None
    ) -> Dict[str, Any]:
        """
        Insert vectors in batches with optimization.
        
        Args:
            collection_name: Name of the collection
            vectors: List of vector data
            batch_size: Size of each batch
            
        Returns:
            Dict with insertion results
        """
        start_time = time.time()
        
        try:
            # Validate input
            validate_vector_data(vectors)
            batch_size = min(batch_size or self.default_batch_size, self.max_batch_size)
            
            # Process in batches
            total_inserted = 0
            total_errors = 0
            batch_results = []
            
            if self.use_parallel_processing and len(vectors) > batch_size * 2:
                # Use parallel processing for large datasets
                result = await self._parallel_insert_batches(
                    collection_name, vectors, batch_size
                )
                total_inserted = result["inserted_count"]
                total_errors = result["error_count"]
                batch_results = result["batch_results"]
            else:
                # Use sequential processing
                async for batch_result in self._sequential_insert_batches(
                    collection_name, vectors, batch_size
                ):
                    total_inserted += batch_result["inserted_count"]
                    total_errors += batch_result["error_count"]
                    batch_results.append(batch_result)
            
            duration = time.time() - start_time
            self.metrics.record_histogram("batch_insert_duration", duration)
            self.metrics.increment_counter("batch_vectors_inserted", total_inserted)
            
            return {
                "inserted_count": total_inserted,
                "error_count": total_errors,
                "batch_count": len(batch_results),
                "duration": duration,
                "collection": collection_name,
                "batch_results": batch_results
            }
            
        except Exception as e:
            self.metrics.increment_counter("batch_insert_errors")
            raise VectorOperationError(f"Batch insertion failed: {str(e)}")
    
    async def update_batch(
        self,
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update vectors in batches.
        
        Args:
            operations: List of update operations
            
        Returns:
            Dict with update results
        """
        start_time = time.time()
        
        try:
            # Group by collection for efficiency
            collection_groups = {}
            for op in operations:
                collection = op["collection"]
                if collection not in collection_groups:
                    collection_groups[collection] = []
                collection_groups[collection].append(op)
            
            # Process each collection
            total_updated = 0
            total_errors = 0
            
            for collection_name, collection_ops in collection_groups.items():
                result = await self._process_collection_updates(
                    collection_name, collection_ops
                )
                total_updated += result["updated_count"]
                total_errors += result["error_count"]
            
            duration = time.time() - start_time
            self.metrics.record_histogram("batch_update_duration", duration)
            self.metrics.increment_counter("batch_vectors_updated", total_updated)
            
            return {
                "updated_count": total_updated,
                "error_count": total_errors,
                "duration": duration,
                "collections_processed": len(collection_groups)
            }
            
        except Exception as e:
            self.metrics.increment_counter("batch_update_errors")
            raise VectorOperationError(f"Batch update failed: {str(e)}")
    
    async def delete_batch(
        self,
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Delete vectors in batches.
        
        Args:
            operations: List of delete operations
            
        Returns:
            Dict with deletion results
        """
        start_time = time.time()
        
        try:
            # Group by collection for efficiency
            collection_groups = {}
            for op in operations:
                collection = op["collection"]
                if collection not in collection_groups:
                    collection_groups[collection] = []
                collection_groups[collection].append(op["vector_id"])
            
            # Process each collection
            total_deleted = 0
            total_errors = 0
            
            for collection_name, vector_ids in collection_groups.items():
                result = await self._process_collection_deletions(
                    collection_name, vector_ids
                )
                total_deleted += result["deleted_count"]
                total_errors += result["error_count"]
            
            duration = time.time() - start_time
            self.metrics.record_histogram("batch_delete_duration", duration)
            self.metrics.increment_counter("batch_vectors_deleted", total_deleted)
            
            return {
                "deleted_count": total_deleted,
                "error_count": total_errors,
                "duration": duration,
                "collections_processed": len(collection_groups)
            }
            
        except Exception as e:
            self.metrics.increment_counter("batch_delete_errors")
            raise VectorOperationError(f"Batch deletion failed: {str(e)}")
    
    async def stream_insert(
        self,
        collection_name: str,
        vector_stream: AsyncGenerator[Dict[str, Any], None],
        batch_size: int = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream insert vectors with real-time processing.
        
        Args:
            collection_name: Name of the collection
            vector_stream: Async generator of vector data
            batch_size: Size of each batch
            
        Yields:
            Dict with batch results
        """
        batch_size = batch_size or self.default_batch_size
        current_batch = []
        
        try:
            async for vector_data in vector_stream:
                current_batch.append(vector_data)
                
                if len(current_batch) >= batch_size:
                    # Process current batch
                    result = await self._insert_single_batch(
                        collection_name, current_batch
                    )
                    yield result
                    current_batch = []
            
            # Process remaining vectors
            if current_batch:
                result = await self._insert_single_batch(
                    collection_name, current_batch
                )
                yield result
                
        except Exception as e:
            self.metrics.increment_counter("stream_insert_errors")
            raise VectorOperationError(f"Stream insertion failed: {str(e)}")
    
    def _group_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group operations by type."""
        grouped = {}
        
        for op in operations:
            op_type = op.get("type", "insert")
            if op_type not in grouped:
                grouped[op_type] = []
            grouped[op_type].append(op)
        
        return grouped
    
    async def _process_insert_batch(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process insert operations."""
        # Group by collection
        collection_groups = {}
        for op in operations:
            collection = op["collection"]
            if collection not in collection_groups:
                collection_groups[collection] = []
            collection_groups[collection].append(op["data"])
        
        # Process each collection
        total_inserted = 0
        total_errors = 0
        
        for collection_name, vectors in collection_groups.items():
            result = await self.insert_batch(collection_name, vectors)
            total_inserted += result["inserted_count"]
            total_errors += result["error_count"]
        
        return {
            "processed_count": total_inserted,
            "error_count": total_errors,
            "collections_processed": len(collection_groups)
        }
    
    async def _process_update_batch(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process update operations."""
        result = await self.update_batch(operations)
        return {
            "processed_count": result["updated_count"],
            "error_count": result["error_count"]
        }
    
    async def _process_delete_batch(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process delete operations."""
        result = await self.delete_batch(operations)
        return {
            "processed_count": result["deleted_count"],
            "error_count": result["error_count"]
        }
    
    async def _parallel_insert_batches(
        self,
        collection_name: str,
        vectors: List[Dict[str, Any]],
        batch_size: int
    ) -> Dict[str, Any]:
        """Insert vectors using parallel batch processing."""
        # Split vectors into chunks for parallel processing
        chunks = [vectors[i:i + batch_size] for i in range(0, len(vectors), batch_size)]
        
        # Create tasks for parallel processing
        tasks = []
        for chunk in chunks:
            task = self._insert_single_batch(collection_name, chunk)
            tasks.append(task)
        
        # Process batches in parallel (with concurrency limit)
        semaphore = asyncio.Semaphore(self.parallel_batches)
        
        async def process_with_semaphore(task):
            async with semaphore:
                return await task
        
        # Execute tasks
        batch_results = await asyncio.gather(
            *[process_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # Aggregate results
        total_inserted = 0
        total_errors = 0
        successful_batches = []
        
        for result in batch_results:
            if isinstance(result, Exception):
                total_errors += batch_size  # Assume entire batch failed
            else:
                total_inserted += result["inserted_count"]
                total_errors += result["error_count"]
                successful_batches.append(result)
        
        return {
            "inserted_count": total_inserted,
            "error_count": total_errors,
            "batch_results": successful_batches
        }
    
    async def _sequential_insert_batches(
        self,
        collection_name: str,
        vectors: List[Dict[str, Any]],
        batch_size: int
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Insert vectors using sequential batch processing."""
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            result = await self._insert_single_batch(collection_name, batch)
            yield result
    
    async def _insert_single_batch(
        self,
        collection_name: str,
        vectors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Insert a single batch of vectors with retry logic."""
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                # Perform the insertion
                result = await self.qdrant_client.insert_vectors(
                    collection_name=collection_name,
                    vectors=vectors
                )
                
                duration = time.time() - start_time
                
                return {
                    "inserted_count": len(vectors),
                    "error_count": 0,
                    "duration": duration,
                    "batch_size": len(vectors)
                }
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    # Final attempt failed
                    return {
                        "inserted_count": 0,
                        "error_count": len(vectors),
                        "duration": 0,
                        "batch_size": len(vectors),
                        "error": str(e)
                    }
                
                # Wait before retry
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        # Should never reach here
        return {
            "inserted_count": 0,
            "error_count": len(vectors),
            "duration": 0,
            "batch_size": len(vectors),
            "error": "Max retries exceeded"
        }
    
    async def _process_collection_updates(
        self,
        collection_name: str,
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process updates for a specific collection."""
        updated_count = 0
        error_count = 0
        
        # Process updates in chunks
        for i in range(0, len(operations), self.chunk_size):
            chunk = operations[i:i + self.chunk_size]
            
            # Process chunk
            chunk_tasks = []
            for op in chunk:
                task = self.qdrant_client.update_vector(
                    collection_name=collection_name,
                    vector_id=op["vector_id"],
                    vector=op.get("vector"),
                    metadata=op.get("metadata")
                )
                chunk_tasks.append(task)
            
            # Execute chunk updates
            chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
            
            # Count results
            for result in chunk_results:
                if isinstance(result, Exception):
                    error_count += 1
                else:
                    updated_count += 1 if result.get("updated") else 0
        
        return {
            "updated_count": updated_count,
            "error_count": error_count
        }
    
    async def _process_collection_deletions(
        self,
        collection_name: str,
        vector_ids: List[str]
    ) -> Dict[str, Any]:
        """Process deletions for a specific collection."""
        deleted_count = 0
        error_count = 0
        
        # Process deletions in chunks
        for i in range(0, len(vector_ids), self.chunk_size):
            chunk = vector_ids[i:i + self.chunk_size]
            
            # Process chunk
            chunk_tasks = []
            for vector_id in chunk:
                task = self.qdrant_client.delete_vector(
                    collection_name=collection_name,
                    vector_id=vector_id
                )
                chunk_tasks.append(task)
            
            # Execute chunk deletions
            chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
            
            # Count results
            for result in chunk_results:
                if isinstance(result, Exception):
                    error_count += 1
                else:
                    deleted_count += 1 if result.get("deleted") else 0
        
        return {
            "deleted_count": deleted_count,
            "error_count": error_count
        }
