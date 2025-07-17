"""
Qdrant Indexing Optimizer
=========================

Index optimization and management for Qdrant vector database.
Handles index creation, optimization, and performance tuning.
"""

from typing import Dict, Any, List, Optional
import asyncio
from ..utils.exceptions import QdrantError


class IndexOptimizer:
    """
    Qdrant index optimization and management.
    Handles index creation, optimization, and performance tuning.
    """
    
    def __init__(self, qdrant_client, config: Dict[str, Any]):
        self.qdrant_client = qdrant_client
        self.config = config
        
        # Optimization configuration
        self.auto_optimize = config.get("auto_optimize", True)
        self.optimization_threshold = config.get("optimization_threshold", 10000)
        self.optimization_interval = config.get("optimization_interval", 3600)  # 1 hour
        
        # Index configuration
        self.index_config = config.get("index", {})
        self.hnsw_config = self.index_config.get("hnsw", {})
        
        # Optimization state
        self.optimization_tasks = {}
        self.last_optimization = {}
    
    async def optimize_collection(self, collection_name: str, 
                                force: bool = False) -> Dict[str, Any]:
        """
        Optimize collection index.
        
        Args:
            collection_name: Collection to optimize
            force: Force optimization regardless of threshold
            
        Returns:
            Optimization result
        """
        try:
            # Check if optimization is needed
            if not force and not await self._should_optimize(collection_name):
                return {
                    "collection": collection_name,
                    "optimized": False,
                    "reason": "Optimization not needed"
                }
            
            # Start optimization
            result = await self.qdrant_client.optimize_collection(collection_name)
            
            # Update optimization state
            self.last_optimization[collection_name] = asyncio.get_event_loop().time()
            
            return {
                "collection": collection_name,
                "optimized": True,
                "result": result
            }
            
        except Exception as e:
            raise QdrantError(f"Failed to optimize collection {collection_name}: {str(e)}")
    
    async def get_optimization_status(self, collection_name: str) -> Dict[str, Any]:
        """
        Get optimization status for collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Optimization status
        """
        try:
            # Get collection info
            collection_info = await self.qdrant_client.get_collection(collection_name)
            
            if not collection_info:
                raise QdrantError(f"Collection {collection_name} not found")
            
            # Get optimizer status
            optimizer_status = collection_info.get("optimizer_status", {})
            
            return {
                "collection": collection_name,
                "status": optimizer_status.get("status", "unknown"),
                "indexing_threshold": optimizer_status.get("indexing_threshold", 0),
                "max_segment_size": optimizer_status.get("max_segment_size", 0),
                "memmap_threshold": optimizer_status.get("memmap_threshold", 0),
                "last_optimization": self.last_optimization.get(collection_name, 0)
            }
            
        except Exception as e:
            raise QdrantError(f"Failed to get optimization status for {collection_name}: {str(e)}")
    
    async def configure_index(self, collection_name: str, 
                            index_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure index parameters for collection.
        
        Args:
            collection_name: Collection name
            index_config: Index configuration
            
        Returns:
            Configuration result
        """
        try:
            # Validate index configuration
            validated_config = self._validate_index_config(index_config)
            
            # Update collection configuration
            result = await self.qdrant_client.update_collection(
                collection_name, 
                {"optimizer_config": validated_config}
            )
            
            return {
                "collection": collection_name,
                "configured": True,
                "config": validated_config,
                "result": result
            }
            
        except Exception as e:
            raise QdrantError(f"Failed to configure index for {collection_name}: {str(e)}")
    
    async def start_auto_optimization(self, collection_name: str):
        """
        Start automatic optimization for collection.
        
        Args:
            collection_name: Collection name
        """
        if collection_name in self.optimization_tasks:
            return  # Already running
        
        task = asyncio.create_task(self._auto_optimization_loop(collection_name))
        self.optimization_tasks[collection_name] = task
    
    async def stop_auto_optimization(self, collection_name: str):
        """
        Stop automatic optimization for collection.
        
        Args:
            collection_name: Collection name
        """
        if collection_name in self.optimization_tasks:
            task = self.optimization_tasks.pop(collection_name)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    async def get_index_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get index statistics for collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Index statistics
        """
        try:
            # Get collection info
            collection_info = await self.qdrant_client.get_collection(collection_name)
            
            if not collection_info:
                raise QdrantError(f"Collection {collection_name} not found")
            
            # Extract index statistics
            stats = {
                "collection": collection_name,
                "points_count": collection_info.get("points_count", 0),
                "indexed_vectors_count": collection_info.get("indexed_vectors_count", 0),
                "segments_count": collection_info.get("segments_count", 0),
                "vector_data_type": collection_info.get("config", {}).get("params", {}).get("vectors", {}).get("datatype"),
                "distance": collection_info.get("config", {}).get("params", {}).get("vectors", {}).get("distance"),
                "optimizer_status": collection_info.get("optimizer_status", {})
            }
            
            return stats
            
        except Exception as e:
            raise QdrantError(f"Failed to get index stats for {collection_name}: {str(e)}")
    
    async def rebuild_index(self, collection_name: str) -> Dict[str, Any]:
        """
        Rebuild index for collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Rebuild result
        """
        try:
            # This would trigger a full index rebuild
            # Implementation depends on Qdrant API capabilities
            result = await self.qdrant_client.recreate_collection_index(collection_name)
            
            return {
                "collection": collection_name,
                "rebuilt": True,
                "result": result
            }
            
        except Exception as e:
            raise QdrantError(f"Failed to rebuild index for {collection_name}: {str(e)}")
    
    async def _should_optimize(self, collection_name: str) -> bool:
        """Check if collection should be optimized."""
        try:
            # Get collection stats
            stats = await self.get_index_stats(collection_name)
            
            # Check point count threshold
            points_count = stats.get("points_count", 0)
            if points_count < self.optimization_threshold:
                return False
            
            # Check time since last optimization
            last_opt = self.last_optimization.get(collection_name, 0)
            current_time = asyncio.get_event_loop().time()
            
            if current_time - last_opt < self.optimization_interval:
                return False
            
            # Check optimizer status
            optimizer_status = stats.get("optimizer_status", {})
            if optimizer_status.get("status") == "ok":
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_index_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate index configuration."""
        validated = {}
        
        # HNSW configuration
        if "hnsw" in config:
            hnsw = config["hnsw"]
            validated["hnsw"] = {
                "m": max(4, min(64, hnsw.get("m", 16))),
                "ef_construct": max(4, min(512, hnsw.get("ef_construct", 100))),
                "full_scan_threshold": max(1000, hnsw.get("full_scan_threshold", 10000))
            }
        
        # Optimization thresholds
        if "indexing_threshold" in config:
            validated["indexing_threshold"] = max(0, config["indexing_threshold"])
        
        if "max_segment_size" in config:
            validated["max_segment_size"] = max(1000, config["max_segment_size"])
        
        if "memmap_threshold" in config:
            validated["memmap_threshold"] = max(0, config["memmap_threshold"])
        
        return validated
    
    async def _auto_optimization_loop(self, collection_name: str):
        """Automatic optimization loop for collection."""
        while True:
            try:
                # Wait for optimization interval
                await asyncio.sleep(self.optimization_interval)
                
                # Check if optimization is needed
                if await self._should_optimize(collection_name):
                    await self.optimize_collection(collection_name)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue
                print(f"Auto-optimization error for {collection_name}: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def cleanup(self):
        """Cleanup optimization tasks."""
        for collection_name in list(self.optimization_tasks.keys()):
            await self.stop_auto_optimization(collection_name)
