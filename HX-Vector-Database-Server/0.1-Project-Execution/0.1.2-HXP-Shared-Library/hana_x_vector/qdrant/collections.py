"""
Qdrant Collections Manager
=========================

Collection management for Qdrant vector database.
Handles collection creation, configuration, and lifecycle management.
"""

from typing import Dict, Any, List, Optional
import asyncio
from ..utils.exceptions import QdrantError, CollectionError
from ..utils.validators import CollectionValidator


class CollectionManager:
    """
    Qdrant collection management.
    Handles collection creation, configuration, and lifecycle management.
    """
    
    def __init__(self, qdrant_client, config: Dict[str, Any]):
        self.qdrant_client = qdrant_client
        self.config = config
        
        # Collection configuration
        self.default_vector_size = config.get("default_vector_size", 384)
        self.default_distance = config.get("default_distance", "cosine")
        self.default_shard_number = config.get("default_shard_number", 1)
        self.default_replication_factor = config.get("default_replication_factor", 1)
        
        # Collection cache
        self.collection_cache = {}
        self.cache_ttl = config.get("cache_ttl", 300)  # 5 minutes
    
    async def create_collection(self, name: str, vector_size: int, 
                              distance: str = "cosine", **kwargs) -> Dict[str, Any]:
        """
        Create a new collection.
        
        Args:
            name: Collection name
            vector_size: Vector dimension
            distance: Distance metric
            **kwargs: Additional configuration
            
        Returns:
            Collection information
            
        Raises:
            CollectionError: If creation fails
        """
        # Validate collection name
        validated_name = CollectionValidator.validate_collection_name(name)
        validated_size = CollectionValidator.validate_vector_size(vector_size)
        validated_distance = CollectionValidator.validate_distance_metric(distance)
        
        try:
            # Create collection configuration
            config = {
                "vectors": {
                    "size": validated_size,
                    "distance": validated_distance
                },
                "shard_number": kwargs.get("shard_number", self.default_shard_number),
                "replication_factor": kwargs.get("replication_factor", self.default_replication_factor),
                "write_consistency_factor": kwargs.get("write_consistency_factor", 1)
            }
            
            # Create collection via Qdrant client
            result = await self.qdrant_client.create_collection(validated_name, config)
            
            # Cache collection info
            self.collection_cache[validated_name] = {
                "name": validated_name,
                "vector_size": validated_size,
                "distance": validated_distance,
                "config": config,
                "created_at": asyncio.get_event_loop().time()
            }
            
            return result
            
        except Exception as e:
            raise CollectionError(f"Failed to create collection {validated_name}: {str(e)}", validated_name)
    
    async def get_collection(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get collection information.
        
        Args:
            name: Collection name
            
        Returns:
            Collection information or None if not found
        """
        # Check cache first
        if name in self.collection_cache:
            cached = self.collection_cache[name]
            if asyncio.get_event_loop().time() - cached["created_at"] < self.cache_ttl:
                return cached
        
        try:
            # Get from Qdrant
            result = await self.qdrant_client.get_collection(name)
            
            # Update cache
            if result:
                self.collection_cache[name] = {
                    **result,
                    "created_at": asyncio.get_event_loop().time()
                }
            
            return result
            
        except Exception as e:
            raise CollectionError(f"Failed to get collection {name}: {str(e)}", name)
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections.
        
        Returns:
            List of collection information
        """
        try:
            return await self.qdrant_client.list_collections()
        except Exception as e:
            raise QdrantError(f"Failed to list collections: {str(e)}")
    
    async def delete_collection(self, name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            name: Collection name
            
        Returns:
            True if successful
            
        Raises:
            CollectionError: If deletion fails
        """
        try:
            result = await self.qdrant_client.delete_collection(name)
            
            # Remove from cache
            self.collection_cache.pop(name, None)
            
            return result
            
        except Exception as e:
            raise CollectionError(f"Failed to delete collection {name}: {str(e)}", name)
    
    async def update_collection(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update collection configuration.
        
        Args:
            name: Collection name
            config: New configuration
            
        Returns:
            Updated collection information
        """
        # Validate configuration
        validated_config = CollectionValidator.validate_collection_config(config)
        
        try:
            result = await self.qdrant_client.update_collection(name, validated_config)
            
            # Update cache
            if name in self.collection_cache:
                self.collection_cache[name].update({
                    "config": validated_config,
                    "created_at": asyncio.get_event_loop().time()
                })
            
            return result
            
        except Exception as e:
            raise CollectionError(f"Failed to update collection {name}: {str(e)}", name)
    
    async def collection_exists(self, name: str) -> bool:
        """
        Check if collection exists.
        
        Args:
            name: Collection name
            
        Returns:
            True if collection exists
        """
        try:
            result = await self.get_collection(name)
            return result is not None
        except CollectionError:
            return False
    
    async def get_collection_stats(self, name: str) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Args:
            name: Collection name
            
        Returns:
            Collection statistics
        """
        try:
            return await self.qdrant_client.get_collection_stats(name)
        except Exception as e:
            raise CollectionError(f"Failed to get collection stats for {name}: {str(e)}", name)
    
    def clear_cache(self):
        """Clear collection cache."""
        self.collection_cache.clear()
    
    def get_cached_collections(self) -> List[str]:
        """Get list of cached collection names."""
        return list(self.collection_cache.keys())
