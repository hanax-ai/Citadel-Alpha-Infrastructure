"""
Quality Monitoring for HXP-Enterprise LLM Server

This module provides real-time quality monitoring, alerting, and dashboard
capabilities for comprehensive quality assurance.

Author: Manus AI
Version: 3.0.0
Date: 2025-01-18
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import json
import time

logger = logging.getLogger(__name__)


@dataclass
class QualityAlert:
    """Quality alert data structure"""
    id: str
    severity: str  # "critical", "warning", "info"
    category: str  # "code_quality", "performance", "security"
    message: str
    metric_name: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class QualityThreshold:
    """Quality threshold configuration"""
    metric_name: str
    threshold_value: float
    operator: str  # ">", "<", ">=", "<=", "==", "!="
    severity: str
    enabled: bool = True
    description: str = ""


class QualityMonitor:
    """
    Real-time Quality Monitor for HXP-Enterprise LLM Server
    
    This monitor provides:
    - Real-time quality metrics monitoring
    - Configurable alerting and notifications
    - Quality dashboard and reporting
    - Trend analysis and prediction
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Quality Monitor
        
        Args:
            config_path: Path to monitoring configuration file
        """
        self.config_path = config_path or "/opt/citadel/hxp-enterprise-llm/config/quality_monitoring.yaml"
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_interval = 60  # 1 minute
        self.last_check = None
        
        # Thresholds and alerts
        self.thresholds: List[QualityThreshold] = self._initialize_thresholds()
        self.alerts: List[QualityAlert] = []
        self.alert_handlers: List[Callable] = []
        
        # Metrics storage
        self.metrics_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Dashboard data
        self.dashboard_data: Dict[str, Any] = {}
        
        logger.info("Quality Monitor initialized")
    
    def _initialize_thresholds(self) -> List[QualityThreshold]:
        """Initialize quality monitoring thresholds"""
        return [
            # Code Quality Thresholds
            QualityThreshold(
                metric_name="code_coverage",
                threshold_value=95.0,
                operator="<",
                severity="warning",
                description="Code coverage below 95%"
            ),
            QualityThreshold(
                metric_name="maintainability_index",
                threshold_value=80.0,
                operator="<",
                severity="warning",
                description="Maintainability index below 80"
            ),
            QualityThreshold(
                metric_name="technical_debt",
                threshold_value=5.0,
                operator=">",
                severity="warning",
                description="Technical debt exceeds 5 days"
            ),
            
            # Performance Thresholds
            QualityThreshold(
                metric_name="response_time_avg",
                threshold_value=2000.0,
                operator=">",
                severity="critical",
                description="Average response time exceeds 2000ms"
            ),
            QualityThreshold(
                metric_name="error_rate",
                threshold_value=0.5,
                operator=">",
                severity="critical",
                description="Error rate exceeds 0.5%"
            ),
            QualityThreshold(
                metric_name="availability",
                threshold_value=99.9,
                operator="<",
                severity="critical",
                description="Availability below 99.9%"
            ),
            
            # Security Thresholds
            QualityThreshold(
                metric_name="vulnerability_count",
                threshold_value=0,
                operator=">",
                severity="critical",
                description="Security vulnerabilities detected"
            ),
            QualityThreshold(
                metric_name="security_compliance_score",
                threshold_value=95.0,
                operator="<",
                severity="warning",
                description="Security compliance below 95%"
            )
        ]
    
    async def start_monitoring(self) -> None:
        """Start continuous quality monitoring"""
        if self.is_monitoring:
            logger.warning("Quality monitoring already running")
            return
        
        self.is_monitoring = True
        logger.info("Starting quality monitoring")
        
        try:
            while self.is_monitoring:
                await self._monitoring_cycle()
                await asyncio.sleep(self.monitoring_interval)
        except Exception as e:
            logger.error(f"Quality monitoring failed: {e}")
            raise
        finally:
            self.is_monitoring = False
    
    async def stop_monitoring(self) -> None:
        """Stop continuous quality monitoring"""
        self.is_monitoring = False
        logger.info("Stopped quality monitoring")
    
    async def _monitoring_cycle(self) -> None:
        """Execute one monitoring cycle"""
        try:
            # Collect current metrics
            current_metrics = await self._collect_current_metrics()
            
            # Store metrics
            self.metrics_history.append(current_metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)
            
            # Check thresholds and generate alerts
            new_alerts = await self._check_thresholds(current_metrics)
            
            # Process alerts
            if new_alerts:
                await self._process_alerts(new_alerts)
            
            # Update dashboard
            await self._update_dashboard(current_metrics)
            
            self.last_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Monitoring cycle failed: {e}")
    
    async def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current quality metrics"""
        # This would integrate with the QualityMetricsCollector
        # For now, return simulated metrics
        return {
            "timestamp": datetime.now().isoformat(),
            "code_coverage": 94.5,
            "maintainability_index": 82.3,
            "technical_debt": 3.2,
            "response_time_avg": 1850.0,
            "error_rate": 0.2,
            "availability": 99.95,
            "vulnerability_count": 0,
            "security_compliance_score": 97.8
        }
    
    async def _check_thresholds(self, metrics: Dict[str, Any]) -> List[QualityAlert]:
        """Check metrics against thresholds and generate alerts"""
        new_alerts = []
        
        for threshold in self.thresholds:
            if not threshold.enabled:
                continue
            
            if threshold.metric_name not in metrics:
                continue
            
            current_value = metrics[threshold.metric_name]
            threshold_value = threshold.threshold_value
            
            # Check if threshold is violated
            violated = self._evaluate_threshold(current_value, threshold_value, threshold.operator)
            
            if violated:
                # Check if this is a new alert (not already active)
                existing_alert = self._find_existing_alert(threshold.metric_name)
                
                if not existing_alert:
                    alert = QualityAlert(
                        id=f"alert_{int(time.time())}_{threshold.metric_name}",
                        severity=threshold.severity,
                        category=self._get_alert_category(threshold.metric_name),
                        message=threshold.description,
                        metric_name=threshold.metric_name,
                        current_value=current_value,
                        threshold_value=threshold_value,
                        timestamp=datetime.now()
                    )
                    new_alerts.append(alert)
                    self.alerts.append(alert)
                else:
                    # Update existing alert
                    existing_alert.current_value = current_value
                    existing_alert.timestamp = datetime.now()
            else:
                # Threshold is no longer violated, resolve existing alert
                existing_alert = self._find_existing_alert(threshold.metric_name)
                if existing_alert:
                    existing_alert.resolved = True
        
        return new_alerts
    
    def _evaluate_threshold(self, current_value: float, threshold_value: float, operator: str) -> bool:
        """Evaluate if a threshold is violated"""
        if operator == ">":
            return current_value > threshold_value
        elif operator == "<":
            return current_value < threshold_value
        elif operator == ">=":
            return current_value >= threshold_value
        elif operator == "<=":
            return current_value <= threshold_value
        elif operator == "==":
            return current_value == threshold_value
        elif operator == "!=":
            return current_value != threshold_value
        else:
            return False
    
    def _find_existing_alert(self, metric_name: str) -> Optional[QualityAlert]:
        """Find existing active alert for a metric"""
        for alert in self.alerts:
            if alert.metric_name == metric_name and not alert.resolved:
                return alert
        return None
    
    def _get_alert_category(self, metric_name: str) -> str:
        """Get alert category based on metric name"""
        code_metrics = ["code_coverage", "maintainability_index", "technical_debt", "cyclomatic_complexity"]
        performance_metrics = ["response_time_avg", "error_rate", "availability", "throughput"]
        security_metrics = ["vulnerability_count", "security_compliance_score", "access_control_score"]
        
        if metric_name in code_metrics:
            return "code_quality"
        elif metric_name in performance_metrics:
            return "performance"
        elif metric_name in security_metrics:
            return "security"
        else:
            return "general"
    
    async def _process_alerts(self, alerts: List[QualityAlert]) -> None:
        """Process new alerts"""
        for alert in alerts:
            logger.warning(f"Quality alert: {alert.severity.upper()} - {alert.message}")
            
            # Call alert handlers
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler failed: {e}")
    
    async def _update_dashboard(self, current_metrics: Dict[str, Any]) -> None:
        """Update dashboard with current metrics"""
        self.dashboard_data = {
            "last_updated": datetime.now().isoformat(),
            "current_metrics": current_metrics,
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "critical_alerts": len([a for a in self.alerts if a.severity == "critical" and not a.resolved]),
            "warning_alerts": len([a for a in self.alerts if a.severity == "warning" and not a.resolved]),
            "overall_quality_score": self._calculate_overall_quality_score(current_metrics),
            "trends": self._calculate_trends(),
            "recommendations": self._generate_recommendations(current_metrics)
        }
    
    def _calculate_overall_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score from current metrics"""
        # Weighted average of key metrics
        code_score = (
            metrics.get("code_coverage", 0) * 0.4 +
            metrics.get("maintainability_index", 0) * 0.3 +
            (100 - metrics.get("technical_debt", 0) * 10) * 0.3
        )
        
        performance_score = (
            (100 - metrics.get("response_time_avg", 0) / 50) * 0.4 +
            (100 - metrics.get("error_rate", 0) * 100) * 0.3 +
            metrics.get("availability", 0) * 0.3
        )
        
        security_score = (
            (100 - metrics.get("vulnerability_count", 0) * 10) * 0.5 +
            metrics.get("security_compliance_score", 0) * 0.5
        )
        
        overall_score = (
            code_score * 0.4 +
            performance_score * 0.35 +
            security_score * 0.25
        )
        
        return max(0.0, min(100.0, overall_score))
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate trends from metrics history"""
        if len(self.metrics_history) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        trends = {}
        current = self.metrics_history[-1]
        previous = self.metrics_history[-2]
        
        # Calculate trends for key metrics
        key_metrics = ["code_coverage", "response_time_avg", "error_rate", "availability"]
        
        for metric in key_metrics:
            if metric in current and metric in previous:
                current_val = current[metric]
                previous_val = previous[metric]
                
                if previous_val != 0:
                    change_percent = ((current_val - previous_val) / previous_val) * 100
                    if change_percent > 1:
                        trend = "improving"
                    elif change_percent < -1:
                        trend = "declining"
                    else:
                        trend = "stable"
                else:
                    trend = "stable"
                    change_percent = 0
                
                trends[metric] = {
                    "trend": trend,
                    "change_percent": change_percent,
                    "current_value": current_val,
                    "previous_value": previous_val
                }
        
        return trends
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on current metrics"""
        recommendations = []
        
        # Code quality recommendations
        if metrics.get("code_coverage", 100) < 95:
            recommendations.append("Increase code coverage to at least 95%")
        
        if metrics.get("maintainability_index", 100) < 80:
            recommendations.append("Improve code maintainability to at least 80")
        
        if metrics.get("technical_debt", 0) > 5:
            recommendations.append("Reduce technical debt to less than 5 days")
        
        # Performance recommendations
        if metrics.get("response_time_avg", 0) > 2000:
            recommendations.append("Optimize response times to under 2000ms")
        
        if metrics.get("error_rate", 0) > 0.5:
            recommendations.append("Reduce error rate to under 0.5%")
        
        if metrics.get("availability", 100) < 99.9:
            recommendations.append("Improve availability to at least 99.9%")
        
        # Security recommendations
        if metrics.get("vulnerability_count", 0) > 0:
            recommendations.append("Address all security vulnerabilities")
        
        if metrics.get("security_compliance_score", 100) < 95:
            recommendations.append("Improve security compliance to at least 95%")
        
        return recommendations
    
    def add_alert_handler(self, handler: Callable) -> None:
        """Add an alert handler function"""
        self.alert_handlers.append(handler)
        logger.info("Alert handler added")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        return self.dashboard_data.copy()
    
    def get_active_alerts(self) -> List[QualityAlert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def get_alerts_by_severity(self, severity: str) -> List[QualityAlert]:
        """Get alerts by severity level"""
        return [alert for alert in self.alerts if alert.severity == severity]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert {alert_id} acknowledged")
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                logger.info(f"Alert {alert_id} resolved")
                return True
        return False
    
    def configure_thresholds(self, thresholds: List[QualityThreshold]) -> None:
        """Configure monitoring thresholds"""
        self.thresholds = thresholds
        logger.info(f"Monitoring thresholds reconfigured with {len(thresholds)} thresholds")
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get quality monitoring summary"""
        active_alerts = self.get_active_alerts()
        
        return {
            "monitoring_status": "active" if self.is_monitoring else "inactive",
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "total_alerts": len(self.alerts),
            "active_alerts": len(active_alerts),
            "critical_alerts": len([a for a in active_alerts if a.severity == "critical"]),
            "warning_alerts": len([a for a in active_alerts if a.severity == "warning"]),
            "acknowledged_alerts": len([a for a in self.alerts if a.acknowledged]),
            "resolved_alerts": len([a for a in self.alerts if a.resolved]),
            "overall_quality_score": self.dashboard_data.get("overall_quality_score", 0.0)
        } 