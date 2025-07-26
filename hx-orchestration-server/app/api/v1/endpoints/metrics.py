"""
Metrics Endpoints

Prometheus metrics endpoints for monitoring and observability.
Provides application metrics, performance data, and health indicators.
"""

from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time

from app.core.services.monitoring_service import MonitoringService

router = APIRouter()


@router.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint
    
    Returns:
        Response: Prometheus-formatted metrics
    """
    try:
        # Update dynamic metrics
        monitoring = MonitoringService()
        await monitoring.update_metrics()
        
        # Generate Prometheus format
        metrics_data = generate_latest()
        
        return Response(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST
        )
        
    except Exception as e:
        # Return basic metrics even if monitoring service fails
        basic_metrics = f"""
# HELP hx_orchestration_up Service availability
# TYPE hx_orchestration_up gauge
hx_orchestration_up 1

# HELP hx_orchestration_errors_total Total number of errors
# TYPE hx_orchestration_errors_total counter
hx_orchestration_errors_total 1

# HELP hx_orchestration_response_time_seconds Response time
# TYPE hx_orchestration_response_time_seconds histogram
hx_orchestration_response_time_seconds_bucket{{le="0.1"}} 0
hx_orchestration_response_time_seconds_bucket{{le="0.5"}} 0
hx_orchestration_response_time_seconds_bucket{{le="1.0"}} 0
hx_orchestration_response_time_seconds_bucket{{le="+Inf"}} 1
hx_orchestration_response_time_seconds_count 1
hx_orchestration_response_time_seconds_sum {time.time()}
"""
        
        return Response(
            content=basic_metrics,
            media_type=CONTENT_TYPE_LATEST
        )
