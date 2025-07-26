"""
Celery tasks for asynchronous embedding processing.

This module defines background tasks for processing large embedding
requests that would otherwise timeout in synchronous endpoints.
"""

import asyncio
import time
from typing import List, Union, Optional
from celery import current_task
from celery_app import celery_app

from app.core.embeddings.ollama_client import OllamaClient
from app.core.embeddings.cache_manager import CacheManager
from app.core.embeddings.batch_processor import BatchProcessor
from app.utils.performance_monitor import PerformanceMonitor


@celery_app.task(bind=True, name="process_embeddings_async")
def process_embeddings_async(
    self, 
    texts: List[str], 
    model: str, 
    user: Optional[str] = None
):
    """
    Process embeddings asynchronously for large batches.
    
    Args:
        self: Celery task instance
        texts: List of texts to embed
        model: Model to use for embeddings
        user: Optional user identifier
        
    Returns:
        dict: OpenAI-compatible embedding response
    """
    start_time = time.time()
    
    try:
        # Update task state
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': len(texts), 'status': 'Initializing...'}
        )
        
        # Initialize services (synchronous context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def process_async():
            ollama_client = OllamaClient()
            cache_manager = CacheManager()
            batch_processor = BatchProcessor()
            
            # Update progress
            current_task.update_state(
                state='PROGRESS',
                meta={'current': 0, 'total': len(texts), 'status': 'Checking cache...'}
            )
            
            # Check cache
            cached_results = await cache_manager.get_embeddings(texts, model)
            uncached_texts = [text for text, embedding in zip(texts, cached_results) if embedding is None]
            
            uncached_count = len(uncached_texts)
            cached_count = len(texts) - uncached_count
            
            # Update progress
            current_task.update_state(
                state='PROGRESS',
                meta={
                    'current': cached_count, 
                    'total': len(texts), 
                    'status': f'Found {cached_count} cached embeddings, processing {uncached_count}...'
                }
            )
            
            if uncached_texts:
                # Create progress callback
                def progress_callback(processed: int, total: int):
                    current_task.update_state(
                        state='PROGRESS',
                        meta={
                            'current': cached_count + processed,
                            'total': len(texts),
                            'status': f'Processing embeddings: {processed}/{total}'
                        }
                    )
                
                # Process embeddings with progress updates
                new_embeddings = await batch_processor.process_batch(
                    uncached_texts,
                    model,
                    ollama_client,
                    progress_callback=progress_callback
                )
                
                # Cache new embeddings (background)
                await cache_manager.cache_embeddings(uncached_texts, new_embeddings, model)
            else:
                new_embeddings = []
            
            # Combine results
            embeddings = []
            new_idx = 0
            for cached in cached_results:
                if cached is not None:
                    embeddings.append(cached)
                else:
                    embeddings.append(new_embeddings[new_idx])
                    new_idx += 1
            
            # Build response data
            data = [
                {
                    "object": "embedding",
                    "embedding": emb,
                    "index": i
                }
                for i, emb in enumerate(embeddings)
            ]
            
            # Calculate usage
            total_tokens = sum(len(text.split()) for text in texts)
            usage = {
                "prompt_tokens": total_tokens,
                "total_tokens": total_tokens
            }
            
            # Record performance
            processing_time = time.time() - start_time
            perf_monitor = PerformanceMonitor()
            await perf_monitor.record_embedding_request(
                texts_count=len(texts),
                model=model,
                processing_time=processing_time,
                cache_hits=cached_count,
                is_async=True
            )
            
            return {
                "object": "list",
                "data": data,
                "model": model,
                "usage": usage,
                "processing_time": processing_time,
                "cache_stats": {
                    "hits": cached_count,
                    "misses": uncached_count,
                    "hit_rate": cached_count / len(texts) if len(texts) > 0 else 0.0
                }
            }
        
        # Run async processing
        result = loop.run_until_complete(process_async())
        
        # Final progress update
        current_task.update_state(
            state='SUCCESS',
            meta={
                'current': len(texts),
                'total': len(texts),
                'status': 'Completed successfully',
                'result': result
            }
        )
        
        return result
        
    except Exception as e:
        # Update task state with error
        current_task.update_state(
            state='FAILURE',
            meta={
                'current': 0,
                'total': len(texts),
                'status': f'Failed: {str(e)}',
                'error': str(e)
            }
        )
        raise e
    
    finally:
        if 'loop' in locals():
            loop.close()


@celery_app.task(name="warm_embedding_cache")
def warm_embedding_cache(texts: List[str], models: List[str]):
    """
    Pre-warm the embedding cache with common texts.
    
    Args:
        texts: List of common texts to cache
        models: List of models to warm cache for
        
    Returns:
        dict: Cache warming statistics
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def warm_cache_async():
        ollama_client = OllamaClient()
        cache_manager = CacheManager()
        batch_processor = BatchProcessor()
        
        stats = {
            "total_texts": len(texts),
            "total_models": len(models),
            "embeddings_generated": 0,
            "cache_entries": 0,
            "processing_time": 0
        }
        
        start_time = time.time()
        
        for model in models:
            try:
                # Check what's already cached
                cached_results = await cache_manager.get_embeddings(texts, model)
                uncached_texts = [text for text, embedding in zip(texts, cached_results) if embedding is None]
                
                if uncached_texts:
                    # Generate embeddings for uncached texts
                    new_embeddings = await batch_processor.process_batch(
                        uncached_texts,
                        model,
                        ollama_client
                    )
                    
                    # Cache the results
                    await cache_manager.cache_embeddings(uncached_texts, new_embeddings, model)
                    
                    stats["embeddings_generated"] += len(new_embeddings)
                    stats["cache_entries"] += len(new_embeddings)
                
            except Exception as e:
                print(f"Error warming cache for model {model}: {e}")
                continue
        
        stats["processing_time"] = time.time() - start_time
        return stats
    
    try:
        result = loop.run_until_complete(warm_cache_async())
        return result
    finally:
        loop.close()


@celery_app.task(name="cleanup_embedding_cache")
def cleanup_embedding_cache(max_age_hours: int = 24):
    """
    Clean up old embedding cache entries.
    
    Args:
        max_age_hours: Maximum age of cache entries in hours
        
    Returns:
        dict: Cleanup statistics
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def cleanup_async():
        cache_manager = CacheManager()
        
        # Perform cleanup
        cleanup_stats = await cache_manager.cleanup_expired_entries(max_age_hours)
        
        return cleanup_stats
    
    try:
        result = loop.run_until_complete(cleanup_async())
        return result
    finally:
        loop.close()
