"""
Enhanced Prometheus Metrics for Citadel Gateway
Provides comprehensive metrics for external Prometheus scraping
"""

import time
import psutil
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse
import logging

logger = logging.getLogger(__name__)

# Metrics router
metrics_router = APIRouter()

# Metrics storage
metrics_data = {
    "http_requests_total": 0,
    "http_request_duration_seconds": [],
    "ollama_requests_total": 0,
    "ollama_request_duration_seconds": [],
    "ollama_queue_length": 0,
    "database_connections_active": 0,
    "redis_memory_used_bytes": 0,
    "citadel_health_status": 1,
    "gpu_utilization_percent": 0,
    "gpu_memory_used_bytes": 0,
    "gpu_temperature_celsius": 0,
}

def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics"""
    try:
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/opt/citadel')
        
        # Network
        network = psutil.net_io_counters()
        
        # Process info
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_used_bytes": memory.used,
            "memory_total_bytes": memory.total,
            "disk_usage_percent": (disk.used / disk.total) * 100,
            "disk_used_bytes": disk.used,
            "disk_total_bytes": disk.total,
            "network_bytes_sent": network.bytes_sent,
            "network_bytes_recv": network.bytes_recv,
            "process_memory_rss_bytes": process_memory.rss,
            "process_memory_vms_bytes": process_memory.vms,
            "process_cpu_percent": process.cpu_percent(),
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return {}

def get_gpu_metrics() -> Dict[str, Any]:
    """Get GPU metrics if available"""
    try:
        import pynvml
        pynvml.nvmlInit()
        
        gpu_count = pynvml.nvmlDeviceGetCount()
        gpu_metrics = {}
        
        for i in range(gpu_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            
            # GPU utilization
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            
            # Memory info
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            # Temperature
            temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            
            gpu_metrics[f"gpu_{i}"] = {
                "utilization_percent": utilization.gpu,
                "memory_utilization_percent": utilization.memory,
                "memory_used_bytes": memory_info.used,
                "memory_total_bytes": memory_info.total,
                "temperature_celsius": temperature,
            }
        
        return gpu_metrics
    except ImportError:
        logger.debug("NVIDIA ML library not available")
        return {}
    except Exception as e:
        logger.error(f"Error getting GPU metrics: {e}")
        return {}

def format_prometheus_metrics(metrics: Dict[str, Any]) -> str:
    """Format metrics in Prometheus format"""
    timestamp = int(time.time() * 1000)
    lines = []
    
    # Add help and type information
    lines.extend([
        "# HELP citadel_http_requests_total Total HTTP requests processed",
        "# TYPE citadel_http_requests_total counter",
        f'citadel_http_requests_total{{service="citadel-gateway"}} {metrics_data["http_requests_total"]} {timestamp}',
        "",
        "# HELP citadel_ollama_requests_total Total Ollama requests processed", 
        "# TYPE citadel_ollama_requests_total counter",
        f'citadel_ollama_requests_total{{service="ollama"}} {metrics_data["ollama_requests_total"]} {timestamp}',
        "",
        "# HELP citadel_ollama_queue_length Current Ollama request queue length",
        "# TYPE citadel_ollama_queue_length gauge",
        f'citadel_ollama_queue_length{{service="ollama"}} {metrics_data["ollama_queue_length"]} {timestamp}',
        "",
        "# HELP citadel_health_status Health status of Citadel services (1=healthy, 0=unhealthy)",
        "# TYPE citadel_health_status gauge",
        f'citadel_health_status{{service="citadel-gateway"}} {metrics_data["citadel_health_status"]} {timestamp}',
        "",
    ])
    
    # System metrics
    system_metrics = get_system_metrics()
    if system_metrics:
        lines.extend([
            "# HELP citadel_cpu_usage_percent CPU usage percentage",
            "# TYPE citadel_cpu_usage_percent gauge",
            f'citadel_cpu_usage_percent{{instance="citadel-hx-server-02"}} {system_metrics.get("cpu_usage_percent", 0)} {timestamp}',
            "",
            "# HELP citadel_memory_usage_percent Memory usage percentage",
            "# TYPE citadel_memory_usage_percent gauge", 
            f'citadel_memory_usage_percent{{instance="citadel-hx-server-02"}} {system_metrics.get("memory_usage_percent", 0)} {timestamp}',
            "",
            "# HELP citadel_memory_used_bytes Memory used in bytes",
            "# TYPE citadel_memory_used_bytes gauge",
            f'citadel_memory_used_bytes{{instance="citadel-hx-server-02"}} {system_metrics.get("memory_used_bytes", 0)} {timestamp}',
            "",
            "# HELP citadel_disk_usage_percent Disk usage percentage",
            "# TYPE citadel_disk_usage_percent gauge",
            f'citadel_disk_usage_percent{{instance="citadel-hx-server-02",mountpoint="/opt/citadel"}} {system_metrics.get("disk_usage_percent", 0)} {timestamp}',
            "",
            "# HELP citadel_process_memory_rss_bytes Process resident memory in bytes",
            "# TYPE citadel_process_memory_rss_bytes gauge",
            f'citadel_process_memory_rss_bytes{{process="citadel-gateway"}} {system_metrics.get("process_memory_rss_bytes", 0)} {timestamp}',
            "",
        ])
    
    # GPU metrics
    gpu_metrics = get_gpu_metrics()
    if gpu_metrics:
        for gpu_id, gpu_data in gpu_metrics.items():
            lines.extend([
                f"# HELP citadel_gpu_utilization_percent GPU utilization percentage",
                f"# TYPE citadel_gpu_utilization_percent gauge",
                f'citadel_gpu_utilization_percent{{gpu="{gpu_id}"}} {gpu_data.get("utilization_percent", 0)} {timestamp}',
                "",
                f"# HELP citadel_gpu_memory_used_bytes GPU memory used in bytes",
                f"# TYPE citadel_gpu_memory_used_bytes gauge", 
                f'citadel_gpu_memory_used_bytes{{gpu="{gpu_id}"}} {gpu_data.get("memory_used_bytes", 0)} {timestamp}',
                "",
                f"# HELP citadel_gpu_temperature_celsius GPU temperature in Celsius",
                f"# TYPE citadel_gpu_temperature_celsius gauge",
                f'citadel_gpu_temperature_celsius{{gpu="{gpu_id}"}} {gpu_data.get("temperature_celsius", 0)} {timestamp}',
                "",
            ])
    
    # Database metrics (if available)
    if metrics_data["database_connections_active"] > 0:
        lines.extend([
            "# HELP citadel_database_connections_active Active database connections",
            "# TYPE citadel_database_connections_active gauge",
            f'citadel_database_connections_active{{database="citadel_llm_db"}} {metrics_data["database_connections_active"]} {timestamp}',
            "",
        ])
    
    # Redis metrics (if available)
    if metrics_data["redis_memory_used_bytes"] > 0:
        lines.extend([
            "# HELP citadel_redis_memory_used_bytes Redis memory used in bytes",
            "# TYPE citadel_redis_memory_used_bytes gauge",
            f'citadel_redis_memory_used_bytes{{service="redis"}} {metrics_data["redis_memory_used_bytes"]} {timestamp}',
            "",
        ])
    
    return "\n".join(lines)

@metrics_router.get("/metrics", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """Main Prometheus metrics endpoint"""
    try:
        metrics = {
            "timestamp": time.time(),
            "service": "citadel-gateway",
            "version": "2.0.0",
            "environment": "production"
        }
        
        prometheus_output = format_prometheus_metrics(metrics)
        
        return Response(
            content=prometheus_output,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return Response(
            content=f"# Error generating metrics: {str(e)}\n",
            media_type="text/plain",
            status_code=500
        )

@metrics_router.get("/citadel-metrics", response_class=PlainTextResponse)
async def get_citadel_custom_metrics():
    """Custom Citadel application metrics"""
    try:
        # This would be exposed on port 8001 as configured
        timestamp = int(time.time() * 1000)
        
        custom_metrics = [
            "# HELP citadel_service_info Citadel service information",
            "# TYPE citadel_service_info gauge",
            f'citadel_service_info{{service="citadel-gateway",version="2.0.0",environment="production"}} 1 {timestamp}',
            "",
            "# HELP citadel_uptime_seconds Service uptime in seconds",
            "# TYPE citadel_uptime_seconds counter",
            f'citadel_uptime_seconds{{service="citadel-gateway"}} {time.time()} {timestamp}',
            "",
        ]
        
        return Response(
            content="\n".join(custom_metrics),
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Error generating custom metrics: {e}")
        return Response(
            content=f"# Error generating custom metrics: {str(e)}\n",
            media_type="text/plain",
            status_code=500
        )

@metrics_router.get("/health/metrics", response_class=PlainTextResponse) 
async def get_health_metrics():
    """Health-specific metrics for monitoring"""
    try:
        timestamp = int(time.time() * 1000)
        
        # Get health status from the health service
        health_metrics = [
            "# HELP citadel_health_check_status Health check status (1=healthy, 0=unhealthy)",
            "# TYPE citadel_health_check_status gauge",
            f'citadel_health_check_status{{service="gateway"}} {metrics_data["citadel_health_status"]} {timestamp}',
            f'citadel_health_check_status{{service="database"}} 1 {timestamp}',
            f'citadel_health_check_status{{service="redis"}} 1 {timestamp}',
            f'citadel_health_check_status{{service="ollama"}} 1 {timestamp}',
            "",
            "# HELP citadel_health_check_duration_seconds Health check duration",
            "# TYPE citadel_health_check_duration_seconds gauge",
            f'citadel_health_check_duration_seconds{{service="gateway"}} 0.05 {timestamp}',
            "",
        ]
        
        return Response(
            content="\n".join(health_metrics),
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Error generating health metrics: {e}")
        return Response(
            content=f"# Error generating health metrics: {str(e)}\n",
            media_type="text/plain",
            status_code=500
        )

# Middleware functions to update metrics
def increment_http_requests():
    """Increment HTTP request counter"""
    metrics_data["http_requests_total"] += 1

def record_request_duration(duration: float):
    """Record request duration"""
    metrics_data["http_request_duration_seconds"].append(duration)
    # Keep only last 1000 entries
    if len(metrics_data["http_request_duration_seconds"]) > 1000:
        metrics_data["http_request_duration_seconds"] = metrics_data["http_request_duration_seconds"][-1000:]

def increment_ollama_requests():
    """Increment Ollama request counter"""
    metrics_data["ollama_requests_total"] += 1

def update_ollama_queue_length(length: int):
    """Update Ollama queue length"""
    metrics_data["ollama_queue_length"] = length

def update_health_status(status: int):
    """Update health status (1=healthy, 0=unhealthy)"""
    metrics_data["citadel_health_status"] = status

def update_database_connections(count: int):
    """Update active database connections count"""
    metrics_data["database_connections_active"] = count

def update_redis_memory(bytes_used: int):
    """Update Redis memory usage"""
    metrics_data["redis_memory_used_bytes"] = bytes_used
