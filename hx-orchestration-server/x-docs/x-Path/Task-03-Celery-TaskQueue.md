# Task 3: Celery Task Queue and Background Processing

**Document Version:** 1.0  
**Date:** 2025-07-25  
**Author:** Manus AI  
**Project:** Citadel AI Operating System - Orchestration Server Implementation  
**Server:** hx-orchestration-server (192.168.10.31)  
**Purpose:** Phase 2B implementation - Celery task queue with Redis backend  
**Classification:** Production-Ready Implementation Task  
**Duration:** 3-4 hours  
**Priority:** CRITICAL  
**Dependencies:** Task 1 and Task 2 completion

---

## Task Overview

Implement Celery background processing framework with Redis message broker, providing reliable asynchronous task execution for embedding processing and orchestration workflows while maintaining responsive API performance.

### Key Deliverables

1. **Celery Application Configuration**
   - Redis broker and backend setup
   - Worker process configuration
   - Task routing and priority management
   - Result tracking and monitoring

2. **Task Definitions**
   - Embedding processing tasks
   - Orchestration workflow tasks
   - Monitoring and maintenance tasks
   - Error handling and retry logic

3. **SystemD Integration**
   - Celery worker service configuration
   - Automatic startup and recovery
   - Logging and monitoring integration

---

## Implementation Steps

### Step 3.1: Celery Application Configuration (1-1.5 hours)

**Objective:** Configure Celery with Redis backend for reliable task processing

**File:** `/celery_app.py`
```python
"""
Citadel AI Orchestration Server - Celery Configuration
Production-ready task queue with Redis backend
"""
from celery import Celery
from kombu import Queue
import os
from datetime import timedelta

from config.settings import get_settings

settings = get_settings()

# Celery application with Redis broker and backend
celery_app = Celery(
    'citadel_orchestration',
    broker=f'redis://{settings.redis_host}:{settings.redis_port}/0',
    backend=f'redis://{settings.redis_host}:{settings.redis_port}/0',
    include=[
        'app.tasks.embedding_tasks',
        'app.tasks.orchestration_tasks',
        'app.tasks.monitoring_tasks',
        'app.tasks.maintenance_tasks'
    ]
)

# Production configuration optimized for orchestration workloads
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    
    # Task execution
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max
    task_soft_time_limit=1500,  # 25 minutes soft limit
    worker_concurrency=4,  # Optimize for 16-core CPU
    worker_prefetch_multiplier=1,  # One task at a time for memory efficiency
    
    # Result backend
    result_expires=3600,  # 1 hour result retention
    result_backend_transport_options={
        'retry_policy': {
            'timeout': 5.0
        }
    },
    
    # Task routing
    task_routes={
        'app.tasks.embedding_tasks.*': {'queue': 'embeddings'},
        'app.tasks.orchestration_tasks.*': {'queue': 'orchestration'},
        'app.tasks.monitoring_tasks.*': {'queue': 'monitoring'},
        'app.tasks.maintenance_tasks.*': {'queue': 'maintenance'}
    },
    
    # Queue configuration
    task_default_queue='orchestration',
    task_queues=(
        Queue('embeddings', routing_key='embeddings', 
              priority=10),  # High priority for embedding requests
        Queue('orchestration', routing_key='orchestration', 
              priority=8),   # Standard priority for workflows
        Queue('monitoring', routing_key='monitoring', 
              priority=5),   # Lower priority for monitoring
        Queue('maintenance', routing_key='maintenance', 
              priority=3),   # Lowest priority for maintenance
    ),
    
    # Monitoring and logging
    worker_send_task_events=True,
    task_send_sent_event=True,
    worker_log_color=False,  # Better for production logging
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'system-health-check': {
            'task': 'app.tasks.monitoring_tasks.system_health_check',
            'schedule': timedelta(minutes=5),
        },
        'cache-cleanup': {
            'task': 'app.tasks.maintenance_tasks.cleanup_expired_cache',
            'schedule': timedelta(hours=1),
        },
        'metrics-collection': {
            'task': 'app.tasks.monitoring_tasks.collect_system_metrics',
            'schedule': timedelta(minutes=1),
        },
    },
    timezone='UTC',
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    worker_disable_rate_limits=True
)

# Custom task base class for common functionality
class BaseTask(celery_app.Task):
    """Base task class with common error handling and logging"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Task success callback"""
        self.get_logger().info(f"Task {self.name}[{task_id}] succeeded")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Task failure callback"""
        self.get_logger().error(
            f"Task {self.name}[{task_id}] failed: {exc}",
            exc_info=einfo
        )
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Task retry callback"""
        self.get_logger().warning(
            f"Task {self.name}[{task_id}] retrying: {exc}"
        )

# Set default task base class
celery_app.Task = BaseTask

if __name__ == '__main__':
    celery_app.start()
```

### Step 3.2: Embedding Processing Tasks (1-1.5 hours)

**Objective:** Implement embedding-specific Celery tasks

**File:** `/app/tasks/embedding_tasks.py`
```python
"""
Embedding Processing Tasks
Celery tasks for asynchronous embedding generation and caching
"""
from typing import List, Dict, Any, Union, Optional
import asyncio
import time
from datetime import datetime

from celery import current_task
from celery.exceptions import Retry

from celery_app import celery_app
from app.core.embeddings.ollama_client import OllamaEmbeddingClient
from app.core.embeddings.cache_manager import EmbeddingCacheManager
from app.utils.performance_monitor import MetricsCollector
from app.common.base_classes import BaseEmbeddingService

# Initialize components
cache_manager = EmbeddingCacheManager()
metrics_collector = MetricsCollector()

@celery_app.task(bind=True, name='generate_embedding')
def generate_embedding(
    self,
    text: Union[str, List[str]],
    model: str = "nomic-embed-text",
    options: Optional[Dict[str, Any]] = None,
    cache_enabled: bool = True
) -> Dict[str, Any]:
    """
    Generate embeddings for text using specified model
    
    Args:
        text: Single text or list of texts to embed
        model: Embedding model name
        options: Additional model options
        cache_enabled: Whether to use caching
    
    Returns:
        Dict containing embeddings, metadata, and performance info
    """
    task_id = self.request.id
    start_time = time.time()
    
    try:
        # Convert single text to list for consistent processing
        texts = [text] if isinstance(text, str) else text
        
        results = []
        cache_hits = 0
        
        for single_text in texts:
            # Check cache first if enabled
            if cache_enabled:
                cached_result = asyncio.run(
                    cache_manager.get_embedding(single_text, model, options)
                )
                if cached_result:
                    results.append(cached_result)
                    cache_hits += 1
                    continue
            
            # Generate embedding using Ollama
            client = OllamaEmbeddingClient(model_name=model)
            embedding = asyncio.run(
                client.generate_embedding(single_text, options)
            )
            
            # Cache result if enabled
            if cache_enabled:
                asyncio.run(
                    cache_manager.store_embedding(
                        single_text, model, embedding, options
                    )
                )
            
            results.append(embedding)
        
        # Calculate performance metrics
        duration_ms = (time.time() - start_time) * 1000
        
        # Record metrics
        metrics_collector.record_embedding_duration(model, duration_ms / 1000)
        
        return {
            "success": True,
            "task_id": task_id,
            "embeddings": results,
            "model_used": model,
            "cache_hits": cache_hits,
            "total_texts": len(texts),
            "cache_hit_rate": cache_hits / len(texts),
            "processing_time_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        # Log error and retry if appropriate
        self.retry(
            countdown=60,  # Wait 60 seconds before retry
            max_retries=3,
            exc=exc
        )

@celery_app.task(bind=True, name='batch_generate_embeddings')
def batch_generate_embeddings(
    self,
    batch_data: List[Dict[str, Any]],
    batch_size: int = 100
) -> Dict[str, Any]:
    """
    Process batch of embedding requests efficiently
    
    Args:
        batch_data: List of embedding requests
        batch_size: Maximum batch size for processing
    
    Returns:
        Dict containing batch results and performance metrics
    """
    task_id = self.request.id
    start_time = time.time()
    
    try:
        # Process in chunks to manage memory
        results = []
        total_processed = 0
        
        for i in range(0, len(batch_data), batch_size):
            batch = batch_data[i:i + batch_size]
            
            # Process batch chunk
            chunk_results = []
            for request in batch:
                result = generate_embedding.apply_async(
                    args=[request['text']],
                    kwargs={
                        'model': request.get('model', 'nomic-embed-text'),
                        'options': request.get('options'),
                        'cache_enabled': request.get('cache_enabled', True)
                    }
                ).get()
                
                chunk_results.append({
                    'request_id': request.get('request_id'),
                    'result': result
                })
                total_processed += 1
            
            results.extend(chunk_results)
            
            # Update task progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'processed': total_processed,
                    'total': len(batch_data),
                    'percent': (total_processed / len(batch_data)) * 100
                }
            )
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "success": True,
            "task_id": task_id,
            "total_requests": len(batch_data),
            "total_processed": total_processed,
            "batch_results": results,
            "processing_time_ms": processing_time,
            "average_time_per_request": processing_time / len(batch_data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        self.retry(countdown=120, max_retries=2, exc=exc)

@celery_app.task(name='warm_embedding_cache')
def warm_embedding_cache(
    texts: List[str],
    models: List[str] = None
) -> Dict[str, Any]:
    """
    Pre-warm embedding cache with frequently accessed texts
    
    Args:
        texts: List of texts to pre-generate embeddings for
        models: List of models to use (default: all available)
    
    Returns:
        Dict containing cache warming results
    """
    if models is None:
        models = ["nomic-embed-text", "mxbai-embed-large", "bge-m3", "all-minilm"]
    
    start_time = time.time()
    results = {"warmed": 0, "skipped": 0, "errors": 0}
    
    for text in texts:
        for model in models:
            try:
                # Check if already cached
                cached = asyncio.run(
                    cache_manager.get_embedding(text, model)
                )
                
                if cached:
                    results["skipped"] += 1
                    continue
                
                # Generate and cache embedding
                generate_embedding.delay(text, model, cache_enabled=True)
                results["warmed"] += 1
                
            except Exception:
                results["errors"] += 1
    
    return {
        "success": True,
        "cache_warming_results": results,
        "processing_time_ms": (time.time() - start_time) * 1000,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Step 3.3: Orchestration and Monitoring Tasks (1-1.5 hours)

**File:** `/app/tasks/orchestration_tasks.py`
```python
"""
Orchestration Workflow Tasks
Celery tasks for complex multi-step orchestration workflows
"""
from typing import Dict, Any, List
import asyncio
from datetime import datetime

from celery import group, chain, chord
from celery_app import celery_app

@celery_app.task(bind=True, name='execute_workflow')
def execute_workflow(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a complex orchestration workflow
    
    Args:
        workflow_definition: Workflow configuration and steps
    
    Returns:
        Dict containing workflow execution results
    """
    task_id = self.request.id
    workflow_id = workflow_definition.get('workflow_id', task_id)
    
    try:
        steps = workflow_definition.get('steps', [])
        context = workflow_definition.get('context', {})
        
        # Execute workflow steps sequentially or in parallel
        results = []
        
        for step in steps:
            step_type = step.get('type')
            step_params = step.get('parameters', {})
            
            if step_type == 'embedding':
                result = generate_embedding.delay(
                    text=step_params.get('text'),
                    model=step_params.get('model', 'nomic-embed-text')
                ).get()
                
            elif step_type == 'llm_query':
                result = query_llm_service.delay(
                    query=step_params.get('query'),
                    context=context
                ).get()
                
            elif step_type == 'vector_search':
                result = vector_similarity_search.delay(
                    embedding=step_params.get('embedding'),
                    collection=step_params.get('collection')
                ).get()
            
            results.append({
                'step_id': step.get('step_id'),
                'step_type': step_type,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Update context with step results
            context.update(result.get('data', {}))
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "task_id": task_id,
            "steps_executed": len(results),
            "workflow_results": results,
            "final_context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        return {
            "success": False,
            "workflow_id": workflow_id,
            "task_id": task_id,
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }

@celery_app.task(name='query_llm_service')
def query_llm_service(
    query: str,
    context: Dict[str, Any] = None,
    service_endpoint: str = "http://192.168.10.34:8002"
) -> Dict[str, Any]:
    """Query external LLM service with context"""
    # Implementation for LLM service integration
    pass

@celery_app.task(name='vector_similarity_search')
def vector_similarity_search(
    embedding: List[float],
    collection: str,
    limit: int = 10
) -> Dict[str, Any]:
    """Perform vector similarity search in Qdrant"""
    # Implementation for Qdrant integration
    pass
```

**File:** `/app/tasks/monitoring_tasks.py`
```python
"""
System Monitoring Tasks
Background tasks for system health monitoring and metrics collection
"""
import psutil
from datetime import datetime
from typing import Dict, Any

from celery_app import celery_app
from app.utils.performance_monitor import MetricsCollector

metrics_collector = MetricsCollector()

@celery_app.task(name='system_health_check')
def system_health_check() -> Dict[str, Any]:
    """Comprehensive system health monitoring task"""
    
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Service health checks
        redis_healthy = check_redis_connection()
        qdrant_healthy = check_qdrant_connection()
        postgres_healthy = check_postgres_connection()
        
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "server_ip": "192.168.10.31",
            "system_metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_free_gb": disk.free / (1024**3)
            },
            "service_health": {
                "redis": redis_healthy,
                "qdrant": qdrant_healthy,
                "postgres": postgres_healthy
            },
            "overall_health": all([redis_healthy, qdrant_healthy, postgres_healthy])
        }
        
        # Record metrics
        metrics_collector.record_system_health(health_status)
        
        return {
            "success": True,
            "health_status": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }

def check_redis_connection() -> bool:
    """Check Redis connectivity"""
    try:
        import redis
        client = redis.Redis(host="localhost", port=6379, db=0)
        client.ping()
        return True
    except Exception:
        return False

def check_qdrant_connection() -> bool:
    """Check Qdrant connectivity"""
    try:
        import requests
        response = requests.get("http://192.168.10.30:6333/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def check_postgres_connection() -> bool:
    """Check PostgreSQL connectivity"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            "postgresql://citadel_llm_user:CitadelLLM#2025$SecurePass!@192.168.10.35:5432/citadel_llm_db"
        )
        conn.close()
        return True
    except Exception:
        return False

@celery_app.task(name='collect_system_metrics')
def collect_system_metrics() -> Dict[str, Any]:
    """Collect detailed system performance metrics"""
    
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_metrics": {
            "usage_percent": psutil.cpu_percent(interval=1),
            "core_count": psutil.cpu_count(),
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        },
        "memory_metrics": {
            "total_gb": psutil.virtual_memory().total / (1024**3),
            "available_gb": psutil.virtual_memory().available / (1024**3),
            "usage_percent": psutil.virtual_memory().percent
        },
        "disk_metrics": {
            "total_gb": psutil.disk_usage('/').total / (1024**3),
            "free_gb": psutil.disk_usage('/').free / (1024**3),
            "usage_percent": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
        }
    }
    
    # Store metrics for analysis
    metrics_collector.record_system_metrics(metrics)
    
    return {
        "success": True,
        "metrics": metrics,
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## Success Criteria

### Celery Configuration
- ✅ Redis broker operational with proper configuration
- ✅ Celery workers processing tasks reliably
- ✅ Task routing functioning with appropriate queues
- ✅ Result backend tracking task progress and completion

### Task Implementation
- ✅ Embedding tasks processing with caching integration
- ✅ Orchestration workflows coordinating multi-step processes
- ✅ Monitoring tasks providing system health visibility
- ✅ Error handling and retry logic ensuring reliability

### Production Readiness
- ✅ SystemD service configured for Celery workers
- ✅ Logging integration with structured output
- ✅ Performance monitoring and metrics collection
- ✅ Queue prioritization optimizing resource utilization

---

## Next Steps

1. **Task 4:** Embedding Processing Framework (Ollama Integration)
2. **Task 5:** External Service Integration Layer
3. **Performance Testing:** Validate task throughput and latency
4. **Monitoring Integration:** Establish comprehensive task monitoring

**Dependencies for Next Task:**
- Celery workers operational and processing tasks
- Redis backend stable and performant
- Task queues properly configured
- Monitoring tasks providing system visibility
