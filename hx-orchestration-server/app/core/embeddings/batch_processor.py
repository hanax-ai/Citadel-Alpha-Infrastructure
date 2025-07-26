"""
Batch Processor for High-Performance Embedding Operations
Optimizes throughput for large-scale embedding generation
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor
import uuid

from app.common.base_classes import BaseOrchestrationService
from app.utils.performance_monitor import PerformanceMonitor

class BatchPriority(Enum):
    """Priority levels for batch processing"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class BatchItem:
    """Individual item in a batch"""
    id: str
    text: str
    model: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    priority: BatchPriority = BatchPriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    callback: Optional[Callable] = None

@dataclass
class BatchResult:
    """Result of batch processing"""
    item_id: str
    embeddings: Optional[List[List[float]]]
    error: Optional[str]
    processing_time: float
    cache_hit: bool = False

@dataclass
class BatchStats:
    """Batch processing statistics"""
    total_batches: int
    total_items: int
    avg_batch_size: float
    avg_processing_time: float
    throughput_per_second: float
    current_queue_size: int

class BatchProcessor(BaseOrchestrationService):
    """
    High-performance batch processor for embedding operations
    Provides optimal throughput through intelligent batching and parallel processing
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("batch_processor", config)
        
        # Batch configuration
        self.max_batch_size = config.get("max_batch_size", 20)
        self.min_batch_size = config.get("min_batch_size", 1)
        self.batch_timeout = config.get("batch_timeout", 2.0)  # seconds
        self.max_queue_size = config.get("max_queue_size", 1000)
        
        # Processing configuration
        self.max_workers = config.get("max_workers", 4)
        self.enable_adaptive_batching = config.get("enable_adaptive_batching", True)
        self.priority_processing = config.get("priority_processing", True)
        
        # Processing queues by priority
        self.queues = {
            BatchPriority.URGENT: asyncio.Queue(maxsize=200),
            BatchPriority.HIGH: asyncio.Queue(maxsize=300),
            BatchPriority.NORMAL: asyncio.Queue(maxsize=400),
            BatchPriority.LOW: asyncio.Queue(maxsize=100)
        }
        
        # Processing state
        self.processing_tasks: List[asyncio.Task] = []
        self.batch_futures: Dict[str, asyncio.Future] = {}
        self.is_running = False
        
        # Statistics
        self.stats = {
            "total_batches": 0,
            "total_items": 0,
            "total_processing_time": 0.0,
            "start_time": time.time()
        }
        
        self.performance_monitor = PerformanceMonitor()
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Adaptive batching parameters
        self.current_batch_size = self.min_batch_size
        self.recent_processing_times: List[float] = []
        self.adaptation_window = 10  # Number of batches to consider for adaptation
    
    async def initialize(self) -> bool:
        """Initialize the batch processor"""
        try:
            self.is_running = True
            
            # Start processing tasks for each priority level
            for priority in BatchPriority:
                task = asyncio.create_task(
                    self._process_queue(priority),
                    name=f"batch_processor_{priority.name.lower()}"
                )
                self.processing_tasks.append(task)
            
            # Start adaptive batching task if enabled
            if self.enable_adaptive_batching:
                adapt_task = asyncio.create_task(
                    self._adaptive_batch_optimizer(),
                    name="batch_optimizer"
                )
                self.processing_tasks.append(adapt_task)
            
            self._health_status = "healthy"
            self.logger.info("Batch processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize batch processor: {e}")
            self._health_status = "unhealthy"
            return False
    
    async def add_item(self,
                      text: str,
                      model: Optional[str] = None,
                      options: Optional[Dict[str, Any]] = None,
                      priority: BatchPriority = BatchPriority.NORMAL,
                      callback: Optional[Callable] = None) -> str:
        """
        Add an item to the batch processing queue
        
        Args:
            text: Text to process
            model: Model to use (optional)
            options: Processing options
            priority: Processing priority
            callback: Optional callback function
            
        Returns:
            Item ID for tracking
        """
        
        item_id = str(uuid.uuid4())
        
        item = BatchItem(
            id=item_id,
            text=text,
            model=model,
            options=options,
            priority=priority,
            callback=callback
        )
        
        try:
            # Add to appropriate queue based on priority
            queue = self.queues[priority]
            
            if queue.full():
                self.logger.warning(f"Queue for priority {priority.name} is full")
                # Try to add to lower priority queue if possible
                if priority != BatchPriority.LOW:
                    for lower_priority in list(BatchPriority)[priority.value:]:
                        if not self.queues[lower_priority].full():
                            await self.queues[lower_priority].put(item)
                            break
                    else:
                        raise Exception("All queues are full")
                else:
                    raise Exception("Low priority queue is full")
            else:
                await queue.put(item)
            
            # Create future for tracking result
            future = asyncio.Future()
            self.batch_futures[item_id] = future
            
            self.logger.debug(f"Added item {item_id} to {priority.name} queue")
            return item_id
            
        except Exception as e:
            self.logger.error(f"Failed to add item to queue: {e}")
            raise
    
    async def get_result(self, item_id: str, timeout: Optional[float] = None) -> BatchResult:
        """
        Get the result of a processed item
        
        Args:
            item_id: Item ID to get result for
            timeout: Optional timeout in seconds
            
        Returns:
            BatchResult with processing results
        """
        
        if item_id not in self.batch_futures:
            raise ValueError(f"Unknown item ID: {item_id}")
        
        try:
            future = self.batch_futures[item_id]
            result = await asyncio.wait_for(future, timeout=timeout)
            
            # Clean up
            del self.batch_futures[item_id]
            
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout waiting for result of item {item_id}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting result for item {item_id}: {e}")
            raise
    
    async def _process_queue(self, priority: BatchPriority):
        """Process items from a specific priority queue"""
        queue = self.queues[priority]
        
        while self.is_running:
            try:
                batch_items = []
                batch_start = time.time()
                
                # Collect items for batch
                while (len(batch_items) < self.current_batch_size and 
                       (time.time() - batch_start) < self.batch_timeout):
                    
                    try:
                        # Wait for item with timeout
                        remaining_time = max(0, self.batch_timeout - (time.time() - batch_start))
                        if remaining_time <= 0:
                            break
                        
                        item = await asyncio.wait_for(queue.get(), timeout=remaining_time)
                        batch_items.append(item)
                        
                    except asyncio.TimeoutError:
                        break
                
                # Process batch if we have items
                if batch_items:
                    await self._process_batch(batch_items, priority)
                else:
                    # No items, wait a bit before checking again
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Error in queue processor for {priority.name}: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    async def _process_batch(self, items: List[BatchItem], priority: BatchPriority):
        """Process a batch of items"""
        batch_start = time.time()
        batch_id = str(uuid.uuid4())[:8]
        
        self.logger.debug(f"Processing batch {batch_id} with {len(items)} items (priority: {priority.name})")
        
        try:
            # Group items by model for efficient processing
            model_groups = {}
            for item in items:
                model = item.model or "default"
                if model not in model_groups:
                    model_groups[model] = []
                model_groups[model].append(item)
            
            # Process each model group
            all_results = []
            
            for model, model_items in model_groups.items():
                try:
                    group_results = await self._process_model_group(model_items, model)
                    all_results.extend(group_results)
                except Exception as e:
                    self.logger.error(f"Error processing model group {model}: {e}")
                    # Create error results for failed items
                    for item in model_items:
                        error_result = BatchResult(
                            item_id=item.id,
                            embeddings=None,
                            error=str(e),
                            processing_time=time.time() - batch_start
                        )
                        all_results.append(error_result)
            
            # Update statistics
            processing_time = time.time() - batch_start
            self.stats["total_batches"] += 1
            self.stats["total_items"] += len(items)
            self.stats["total_processing_time"] += processing_time
            
            # Track processing time for adaptive batching
            if self.enable_adaptive_batching:
                self.recent_processing_times.append(processing_time)
                if len(self.recent_processing_times) > self.adaptation_window:
                    self.recent_processing_times.pop(0)
            
            # Set results for futures
            for result in all_results:
                if result.item_id in self.batch_futures:
                    future = self.batch_futures[result.item_id]
                    if not future.done():
                        future.set_result(result)
            
            # Execute callbacks
            for item, result in zip(items, all_results):
                if item.callback:
                    try:
                        await self._execute_callback(item.callback, result)
                    except Exception as e:
                        self.logger.error(f"Error executing callback for item {item.id}: {e}")
            
            self.logger.debug(f"Completed batch {batch_id} in {processing_time:.3f}s")
            
        except Exception as e:
            self.logger.error(f"Error processing batch {batch_id}: {e}")
            
            # Set error results for all items
            for item in items:
                if item.id in self.batch_futures:
                    future = self.batch_futures[item.id]
                    if not future.done():
                        error_result = BatchResult(
                            item_id=item.id,
                            embeddings=None,
                            error=str(e),
                            processing_time=time.time() - batch_start
                        )
                        future.set_result(error_result)
    
    async def _process_model_group(self, items: List[BatchItem], model: str) -> List[BatchResult]:
        """Process a group of items using the same model"""
        # This is where you'd integrate with your actual embedding generation
        # For now, this is a placeholder that simulates processing
        
        results = []
        
        for item in items:
            start_time = time.time()
            
            try:
                # Simulate embedding generation
                # In real implementation, this would call your Ollama client
                embeddings = await self._generate_embeddings_for_item(item, model)
                
                processing_time = time.time() - start_time
                
                result = BatchResult(
                    item_id=item.id,
                    embeddings=embeddings,
                    error=None,
                    processing_time=processing_time,
                    cache_hit=False  # Would be determined by cache manager
                )
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error generating embeddings for item {item.id}: {e}")
                
                result = BatchResult(
                    item_id=item.id,
                    embeddings=None,
                    error=str(e),
                    processing_time=time.time() - start_time
                )
                
                results.append(result)
        
        return results
    
    async def _generate_embeddings_for_item(self, item: BatchItem, model: str) -> List[List[float]]:
        """Generate embeddings for a single item (placeholder)"""
        # This would integrate with your actual embedding generation service
        # For now, simulate processing time and return dummy embeddings
        
        await asyncio.sleep(0.01)  # Simulate processing time
        
        # Return dummy embeddings (in real implementation, use actual service)
        return [[0.1, 0.2, 0.3] * 256]  # 768-dimensional dummy embedding
    
    async def _execute_callback(self, callback: Callable, result: BatchResult):
        """Execute item callback safely"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(result)
            else:
                callback(result)
        except Exception as e:
            self.logger.error(f"Callback execution failed: {e}")
    
    async def _adaptive_batch_optimizer(self):
        """Optimize batch size based on processing performance"""
        while self.is_running:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                if len(self.recent_processing_times) >= 3:
                    avg_time = sum(self.recent_processing_times) / len(self.recent_processing_times)
                    
                    # Adjust batch size based on performance
                    if avg_time < 1.0:  # Fast processing, can increase batch size
                        self.current_batch_size = min(
                            self.current_batch_size + 2,
                            self.max_batch_size
                        )
                    elif avg_time > 3.0:  # Slow processing, decrease batch size
                        self.current_batch_size = max(
                            self.current_batch_size - 1,
                            self.min_batch_size
                        )
                    
                    self.logger.debug(f"Adaptive batch size: {self.current_batch_size} (avg time: {avg_time:.3f}s)")
                
            except Exception as e:
                self.logger.error(f"Error in adaptive batch optimizer: {e}")
    
    async def get_stats(self) -> BatchStats:
        """Get comprehensive batch processing statistics"""
        try:
            uptime = time.time() - self.stats["start_time"]
            
            # Calculate queue sizes
            total_queue_size = sum(queue.qsize() for queue in self.queues.values())
            
            # Calculate averages
            avg_batch_size = (self.stats["total_items"] / max(self.stats["total_batches"], 1))
            avg_processing_time = (self.stats["total_processing_time"] / max(self.stats["total_batches"], 1))
            throughput = self.stats["total_items"] / max(uptime, 1)
            
            return BatchStats(
                total_batches=self.stats["total_batches"],
                total_items=self.stats["total_items"],
                avg_batch_size=avg_batch_size,
                avg_processing_time=avg_processing_time,
                throughput_per_second=throughput,
                current_queue_size=total_queue_size
            )
            
        except Exception as e:
            self.logger.error(f"Error getting batch stats: {e}")
            return BatchStats(0, 0, 0.0, 0.0, 0.0, 0)
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for batch processor"""
        try:
            stats = await self.get_stats()
            
            # Check queue health
            queue_health = {}
            for priority, queue in self.queues.items():
                queue_health[priority.name] = {
                    "size": queue.qsize(),
                    "max_size": queue.maxsize,
                    "utilization": queue.qsize() / queue.maxsize if queue.maxsize > 0 else 0
                }
            
            # Check processing tasks
            active_tasks = sum(1 for task in self.processing_tasks if not task.done())
            
            return {
                "status": "healthy" if self.is_running and active_tasks > 0 else "unhealthy",
                "is_running": self.is_running,
                "active_tasks": active_tasks,
                "total_tasks": len(self.processing_tasks),
                "current_batch_size": self.current_batch_size,
                "queue_health": queue_health,
                "statistics": stats.__dict__,
                "config": {
                    "max_batch_size": self.max_batch_size,
                    "min_batch_size": self.min_batch_size,
                    "batch_timeout": self.batch_timeout,
                    "max_workers": self.max_workers,
                    "adaptive_batching": self.enable_adaptive_batching
                }
            }
            
        except Exception as e:
            self.logger.error(f"Batch processor health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def shutdown(self) -> None:
        """Graceful shutdown of batch processor"""
        self.is_running = False
        
        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        # Complete any remaining futures with error
        for future in self.batch_futures.values():
            if not future.done():
                future.set_exception(Exception("Batch processor shutting down"))
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        await super().shutdown()
        self.logger.info("Batch processor shut down gracefully")
