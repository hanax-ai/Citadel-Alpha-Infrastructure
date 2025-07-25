"""
Webhook endpoints for receiving alerts from external Alertmanager
Integrates with Citadel's monitoring and response system
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Webhook router
webhooks_router = APIRouter()

# Alert storage and tracking
active_alerts = {}
alert_history = []
MAX_ALERT_HISTORY = 1000

@webhooks_router.post("/webhooks/alerts")
async def receive_alertmanager_webhook(request: Request):
    """
    Receive webhook notifications from Alertmanager
    Process alerts and trigger appropriate responses
    """
    try:
        # Parse the incoming webhook payload
        payload = await request.json()
        
        # Alertmanager sends alerts in this format
        alerts = payload.get("alerts", [])
        group_key = payload.get("groupKey", "")
        status = payload.get("status", "")
        
        logger.info(f"Received {len(alerts)} alerts with status: {status}")
        
        processed_alerts = []
        
        for alert in alerts:
            processed_alert = process_alert(alert, status)
            processed_alerts.append(processed_alert)
            
            # Store in active alerts if firing
            if alert.get("status") == "firing":
                alert_key = f"{alert.get('labels', {}).get('alertname', 'unknown')}_{alert.get('labels', {}).get('instance', 'unknown')}"
                active_alerts[alert_key] = processed_alert
                
                # Trigger automated response if configured
                await trigger_alert_response(processed_alert)
            else:
                # Remove from active alerts if resolved
                alert_key = f"{alert.get('labels', {}).get('alertname', 'unknown')}_{alert.get('labels', {}).get('instance', 'unknown')}"
                if alert_key in active_alerts:
                    del active_alerts[alert_key]
        
        # Add to history
        alert_history.extend(processed_alerts)
        
        # Keep history manageable
        if len(alert_history) > MAX_ALERT_HISTORY:
            alert_history[:] = alert_history[-MAX_ALERT_HISTORY:]
        
        return JSONResponse(
            content={
                "status": "success",
                "message": f"Processed {len(processed_alerts)} alerts",
                "alerts_processed": len(processed_alerts),
                "active_alerts": len(active_alerts)
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

def process_alert(alert: Dict[str, Any], status: str) -> Dict[str, Any]:
    """Process and normalize alert data"""
    labels = alert.get("labels", {})
    annotations = alert.get("annotations", {})
    
    processed = {
        "alert_id": f"{labels.get('alertname', 'unknown')}_{labels.get('instance', 'unknown')}_{alert.get('startsAt', '')}",
        "alert_name": labels.get("alertname", "Unknown Alert"),
        "status": alert.get("status", status),
        "severity": labels.get("severity", "unknown"),
        "service": labels.get("service", "unknown"),
        "cluster": labels.get("cluster", "unknown"),
        "instance": labels.get("instance", "unknown"),
        "summary": annotations.get("summary", "No summary available"),
        "description": annotations.get("description", "No description available"),
        "runbook_url": annotations.get("runbook_url", ""),
        "starts_at": alert.get("startsAt", ""),
        "ends_at": alert.get("endsAt", ""),
        "generator_url": alert.get("generatorURL", ""),
        "labels": labels,
        "annotations": annotations,
        "received_at": datetime.utcnow().isoformat(),
        "fingerprint": alert.get("fingerprint", "")
    }
    
    logger.info(f"Processed alert: {processed['alert_name']} - {processed['status']} - {processed['severity']}")
    
    return processed

async def trigger_alert_response(alert: Dict[str, Any]):
    """Trigger automated responses based on alert content"""
    try:
        alert_name = alert.get("alert_name", "")
        severity = alert.get("severity", "")
        service = alert.get("service", "")
        
        logger.info(f"Triggering response for alert: {alert_name} (severity: {severity})")
        
        # Critical alerts - immediate response
        if severity == "critical":
            if "ServiceDown" in alert_name:
                await handle_service_down_alert(alert)
            elif "DiskSpaceLow" in alert_name:
                await handle_disk_space_alert(alert)
            elif "DatabaseConnectionsFull" in alert_name:
                await handle_database_connections_alert(alert)
            elif "GPUTemperatureHigh" in alert_name:
                await handle_gpu_temperature_alert(alert)
        
        # Warning alerts - monitoring and preparation
        elif severity == "warning":
            if "HighCPUUsage" in alert_name or "HighMemoryUsage" in alert_name:
                await handle_resource_usage_alert(alert)
            elif "HighResponseTime" in alert_name:
                await handle_performance_alert(alert)
        
        # Log all alerts for audit
        log_alert_action(alert, "response_triggered")
        
    except Exception as e:
        logger.error(f"Error triggering alert response: {e}")

async def handle_service_down_alert(alert: Dict[str, Any]):
    """Handle service down alerts with automated recovery"""
    service = alert.get("service", "")
    logger.warning(f"Service down detected: {service}")
    
    # Attempt automated service restart if configured
    if service in ["citadel-gateway", "redis", "ollama"]:
        try:
            # This would integrate with the service manager
            logger.info(f"Attempting automated restart of {service}")
            # Example: subprocess.run(["/opt/citadel/bin/citadel-service-manager", "restart", service])
        except Exception as e:
            logger.error(f"Failed to restart {service}: {e}")

async def handle_disk_space_alert(alert: Dict[str, Any]):
    """Handle disk space alerts with cleanup actions"""
    logger.warning("Disk space critically low - triggering cleanup")
    
    try:
        # Trigger log rotation and cleanup
        # subprocess.run(["/opt/citadel/bin/citadel-log-manager", "clean"])
        logger.info("Triggered disk cleanup procedures")
    except Exception as e:
        logger.error(f"Failed to trigger cleanup: {e}")

async def handle_database_connections_alert(alert: Dict[str, Any]):
    """Handle database connection alerts"""
    logger.warning("Database connections near maximum")
    
    # This could trigger connection pool resizing or cleanup

async def handle_gpu_temperature_alert(alert: Dict[str, Any]):
    """Handle GPU temperature alerts"""
    logger.critical("GPU temperature critical - may need thermal throttling")
    
    # This could trigger GPU workload reduction

async def handle_resource_usage_alert(alert: Dict[str, Any]):
    """Handle resource usage alerts"""
    alert_name = alert.get("alert_name", "")
    logger.warning(f"Resource usage alert: {alert_name}")
    
    # This could trigger performance monitoring or scaling decisions

async def handle_performance_alert(alert: Dict[str, Any]):
    """Handle performance-related alerts"""
    logger.warning("Performance degradation detected")
    
    # This could trigger performance optimization procedures

def log_alert_action(alert: Dict[str, Any], action: str):
    """Log alert actions for audit trail"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "alert_name": alert.get("alert_name", ""),
        "action": action,
        "severity": alert.get("severity", ""),
        "service": alert.get("service", ""),
        "instance": alert.get("instance", "")
    }
    
    logger.info(f"Alert action logged: {json.dumps(log_entry)}")

@webhooks_router.get("/webhooks/alerts/active")
async def get_active_alerts():
    """Get currently active alerts"""
    return JSONResponse(
        content={
            "active_alerts": list(active_alerts.values()),
            "count": len(active_alerts),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@webhooks_router.get("/webhooks/alerts/history")
async def get_alert_history(limit: int = 50):
    """Get alert history"""
    recent_alerts = alert_history[-limit:] if len(alert_history) > limit else alert_history
    
    return JSONResponse(
        content={
            "alert_history": recent_alerts,
            "count": len(recent_alerts),
            "total_history": len(alert_history),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@webhooks_router.delete("/webhooks/alerts/history")
async def clear_alert_history():
    """Clear alert history (admin operation)"""
    global alert_history
    cleared_count = len(alert_history)
    alert_history.clear()
    
    logger.info(f"Alert history cleared: {cleared_count} alerts removed")
    
    return JSONResponse(
        content={
            "status": "success",
            "message": f"Cleared {cleared_count} alerts from history",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@webhooks_router.get("/webhooks/alerts/stats")
async def get_alert_stats():
    """Get alert statistics"""
    stats = {
        "active_alerts": len(active_alerts),
        "total_history": len(alert_history),
        "alerts_by_severity": {},
        "alerts_by_service": {},
        "alerts_by_status": {}
    }
    
    # Analyze alert history
    for alert in alert_history:
        severity = alert.get("severity", "unknown")
        service = alert.get("service", "unknown") 
        status = alert.get("status", "unknown")
        
        stats["alerts_by_severity"][severity] = stats["alerts_by_severity"].get(severity, 0) + 1
        stats["alerts_by_service"][service] = stats["alerts_by_service"].get(service, 0) + 1
        stats["alerts_by_status"][status] = stats["alerts_by_status"].get(status, 0) + 1
    
    return JSONResponse(content=stats)
