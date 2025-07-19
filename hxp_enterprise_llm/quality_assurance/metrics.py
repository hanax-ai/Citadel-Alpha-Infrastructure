"""
Quality Metrics Collector for HXP-Enterprise LLM Server

This module provides comprehensive quality metrics collection and analysis
for code quality, performance quality, and security quality.

Author: Manus AI
Version: 3.0.0
Date: 2025-01-18
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import json
import statistics

logger = logging.getLogger(__name__)


@dataclass
class CodeQualityMetrics:
    """Code quality metrics data structure"""
    maintainability_index: float
    cyclomatic_complexity: float
    code_duplication: float
    technical_debt: float
    code_coverage: float
    test_coverage: float
    documentation_coverage: float
    timestamp: datetime


@dataclass
class PerformanceQualityMetrics:
    """Performance quality metrics data structure"""
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    throughput: float
    resource_utilization: Dict[str, float]
    error_rate: float
    availability: float
    timestamp: datetime


@dataclass
class SecurityQualityMetrics:
    """Security quality metrics data structure"""
    vulnerability_count: int
    critical_vulnerabilities: int
    security_compliance_score: float
    access_control_score: float
    data_protection_score: float
    security_incidents: int
    timestamp: datetime


@dataclass
class QualityTrend:
    """Quality trend analysis data structure"""
    metric_name: str
    current_value: float
    previous_value: float
    trend_direction: str  # "improving", "declining", "stable"
    change_percentage: float
    trend_period: str  # "daily", "weekly", "monthly"


class QualityMetricsCollector:
    """
    Quality Metrics Collector for comprehensive quality monitoring
    
    This collector gathers and analyzes quality metrics across:
    - Code quality metrics
    - Performance quality metrics
    - Security quality metrics
    - Trend analysis and reporting
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the Quality Metrics Collector
        
        Args:
            storage_path: Path to store metrics data
        """
        self.storage_path = Path(storage_path or "/opt/citadel/hxp-enterprise-llm/data/quality_metrics")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Metrics storage
        self.code_metrics: List[CodeQualityMetrics] = []
        self.performance_metrics: List[PerformanceQualityMetrics] = []
        self.security_metrics: List[SecurityQualityMetrics] = []
        
        # Collection intervals
        self.collection_interval = 300  # 5 minutes
        self.is_collecting = False
        
        logger.info("Quality Metrics Collector initialized")
    
    async def start_collection(self) -> None:
        """Start continuous metrics collection"""
        if self.is_collecting:
            logger.warning("Metrics collection already running")
            return
        
        self.is_collecting = True
        logger.info("Starting quality metrics collection")
        
        try:
            while self.is_collecting:
                await self._collect_all_metrics()
                await asyncio.sleep(self.collection_interval)
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            raise
        finally:
            self.is_collecting = False
    
    async def stop_collection(self) -> None:
        """Stop continuous metrics collection"""
        self.is_collecting = False
        logger.info("Stopped quality metrics collection")
    
    async def collect_snapshot(self) -> Dict[str, Any]:
        """Collect a single snapshot of all quality metrics"""
        logger.info("Collecting quality metrics snapshot")
        
        try:
            # Collect all metrics
            code_metrics = await self._collect_code_quality_metrics()
            performance_metrics = await self._collect_performance_quality_metrics()
            security_metrics = await self._collect_security_quality_metrics()
            
            # Store metrics
            self.code_metrics.append(code_metrics)
            self.performance_metrics.append(performance_metrics)
            self.security_metrics.append(security_metrics)
            
            # Generate comprehensive report
            report = {
                "timestamp": datetime.now().isoformat(),
                "code_quality": self._serialize_code_metrics(code_metrics),
                "performance_quality": self._serialize_performance_metrics(performance_metrics),
                "security_quality": self._serialize_security_metrics(security_metrics),
                "overall_quality_score": self._calculate_overall_quality_score(
                    code_metrics, performance_metrics, security_metrics
                )
            }
            
            # Save to storage
            await self._save_metrics_snapshot(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Metrics snapshot collection failed: {e}")
            raise
    
    async def _collect_all_metrics(self) -> None:
        """Collect all quality metrics"""
        await self.collect_snapshot()
    
    async def _collect_code_quality_metrics(self) -> CodeQualityMetrics:
        """Collect code quality metrics"""
        logger.debug("Collecting code quality metrics")
        
        try:
            # Analyze code maintainability
            maintainability_index = await self._analyze_maintainability()
            
            # Analyze cyclomatic complexity
            cyclomatic_complexity = await self._analyze_cyclomatic_complexity()
            
            # Analyze code duplication
            code_duplication = await self._analyze_code_duplication()
            
            # Calculate technical debt
            technical_debt = await self._calculate_technical_debt()
            
            # Get code coverage
            code_coverage = await self._get_code_coverage()
            
            # Get test coverage
            test_coverage = await self._get_test_coverage()
            
            # Get documentation coverage
            documentation_coverage = await self._get_documentation_coverage()
            
            return CodeQualityMetrics(
                maintainability_index=maintainability_index,
                cyclomatic_complexity=cyclomatic_complexity,
                code_duplication=code_duplication,
                technical_debt=technical_debt,
                code_coverage=code_coverage,
                test_coverage=test_coverage,
                documentation_coverage=documentation_coverage,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Code quality metrics collection failed: {e}")
            # Return default metrics on error
            return CodeQualityMetrics(
                maintainability_index=0.0,
                cyclomatic_complexity=0.0,
                code_duplication=0.0,
                technical_debt=0.0,
                code_coverage=0.0,
                test_coverage=0.0,
                documentation_coverage=0.0,
                timestamp=datetime.now()
            )
    
    async def _collect_performance_quality_metrics(self) -> PerformanceQualityMetrics:
        """Collect performance quality metrics"""
        logger.debug("Collecting performance quality metrics")
        
        try:
            # Measure response times
            response_times = await self._measure_response_times()
            
            # Calculate throughput
            throughput = await self._measure_throughput()
            
            # Monitor resource utilization
            resource_utilization = await self._monitor_resource_utilization()
            
            # Calculate error rate
            error_rate = await self._calculate_error_rate()
            
            # Calculate availability
            availability = await self._calculate_availability()
            
            return PerformanceQualityMetrics(
                response_time_avg=response_times.get("average", 0.0),
                response_time_p95=response_times.get("p95", 0.0),
                response_time_p99=response_times.get("p99", 0.0),
                throughput=throughput,
                resource_utilization=resource_utilization,
                error_rate=error_rate,
                availability=availability,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Performance quality metrics collection failed: {e}")
            # Return default metrics on error
            return PerformanceQualityMetrics(
                response_time_avg=0.0,
                response_time_p95=0.0,
                response_time_p99=0.0,
                throughput=0.0,
                resource_utilization={},
                error_rate=0.0,
                availability=0.0,
                timestamp=datetime.now()
            )
    
    async def _collect_security_quality_metrics(self) -> SecurityQualityMetrics:
        """Collect security quality metrics"""
        logger.debug("Collecting security quality metrics")
        
        try:
            # Scan for vulnerabilities
            vulnerabilities = await self._scan_vulnerabilities()
            
            # Check security compliance
            compliance_score = await self._check_security_compliance()
            
            # Test access control
            access_control_score = await self._test_access_control()
            
            # Test data protection
            data_protection_score = await self._test_data_protection()
            
            # Count security incidents
            security_incidents = await self._count_security_incidents()
            
            return SecurityQualityMetrics(
                vulnerability_count=vulnerabilities.get("total", 0),
                critical_vulnerabilities=vulnerabilities.get("critical", 0),
                security_compliance_score=compliance_score,
                access_control_score=access_control_score,
                data_protection_score=data_protection_score,
                security_incidents=security_incidents,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Security quality metrics collection failed: {e}")
            # Return default metrics on error
            return SecurityQualityMetrics(
                vulnerability_count=0,
                critical_vulnerabilities=0,
                security_compliance_score=0.0,
                access_control_score=0.0,
                data_protection_score=0.0,
                security_incidents=0,
                timestamp=datetime.now()
            )
    
    async def _analyze_maintainability(self) -> float:
        """Analyze code maintainability index"""
        # Placeholder for maintainability analysis
        # This would integrate with tools like SonarQube
        return 85.5  # Simulated maintainability index
    
    async def _analyze_cyclomatic_complexity(self) -> float:
        """Analyze cyclomatic complexity"""
        # Placeholder for complexity analysis
        return 8.2  # Simulated average complexity
    
    async def _analyze_code_duplication(self) -> float:
        """Analyze code duplication percentage"""
        # Placeholder for duplication analysis
        return 3.5  # Simulated duplication percentage
    
    async def _calculate_technical_debt(self) -> float:
        """Calculate technical debt"""
        # Placeholder for technical debt calculation
        return 2.1  # Simulated technical debt in days
    
    async def _get_code_coverage(self) -> float:
        """Get code coverage percentage"""
        # Placeholder for code coverage measurement
        return 95.5  # Simulated coverage percentage
    
    async def _get_test_coverage(self) -> float:
        """Get test coverage percentage"""
        # Placeholder for test coverage measurement
        return 92.3  # Simulated test coverage percentage
    
    async def _get_documentation_coverage(self) -> float:
        """Get documentation coverage percentage"""
        # Placeholder for documentation coverage measurement
        return 88.7  # Simulated documentation coverage percentage
    
    async def _measure_response_times(self) -> Dict[str, float]:
        """Measure response times for all services"""
        # Placeholder for response time measurement
        return {
            "average": 1250.0,
            "p95": 2100.0,
            "p99": 3500.0
        }
    
    async def _measure_throughput(self) -> float:
        """Measure system throughput"""
        # Placeholder for throughput measurement
        return 850.0  # requests per second
    
    async def _monitor_resource_utilization(self) -> Dict[str, float]:
        """Monitor resource utilization"""
        # Placeholder for resource monitoring
        return {
            "cpu": 65.2,
            "memory": 78.5,
            "disk": 45.1,
            "network": 32.8
        }
    
    async def _calculate_error_rate(self) -> float:
        """Calculate error rate"""
        # Placeholder for error rate calculation
        return 0.15  # 0.15% error rate
    
    async def _calculate_availability(self) -> float:
        """Calculate system availability"""
        # Placeholder for availability calculation
        return 99.95  # 99.95% availability
    
    async def _scan_vulnerabilities(self) -> Dict[str, int]:
        """Scan for security vulnerabilities"""
        # Placeholder for vulnerability scanning
        return {
            "total": 2,
            "critical": 0,
            "high": 1,
            "medium": 1,
            "low": 0
        }
    
    async def _check_security_compliance(self) -> float:
        """Check security compliance score"""
        # Placeholder for compliance checking
        return 98.5  # 98.5% compliance score
    
    async def _test_access_control(self) -> float:
        """Test access control effectiveness"""
        # Placeholder for access control testing
        return 99.2  # 99.2% access control score
    
    async def _test_data_protection(self) -> float:
        """Test data protection effectiveness"""
        # Placeholder for data protection testing
        return 97.8  # 97.8% data protection score
    
    async def _count_security_incidents(self) -> int:
        """Count security incidents"""
        # Placeholder for incident counting
        return 0  # No incidents in current period
    
    def _serialize_code_metrics(self, metrics: CodeQualityMetrics) -> Dict[str, Any]:
        """Serialize code quality metrics"""
        return {
            "maintainability_index": metrics.maintainability_index,
            "cyclomatic_complexity": metrics.cyclomatic_complexity,
            "code_duplication": metrics.code_duplication,
            "technical_debt": metrics.technical_debt,
            "code_coverage": metrics.code_coverage,
            "test_coverage": metrics.test_coverage,
            "documentation_coverage": metrics.documentation_coverage,
            "timestamp": metrics.timestamp.isoformat()
        }
    
    def _serialize_performance_metrics(self, metrics: PerformanceQualityMetrics) -> Dict[str, Any]:
        """Serialize performance quality metrics"""
        return {
            "response_time_avg": metrics.response_time_avg,
            "response_time_p95": metrics.response_time_p95,
            "response_time_p99": metrics.response_time_p99,
            "throughput": metrics.throughput,
            "resource_utilization": metrics.resource_utilization,
            "error_rate": metrics.error_rate,
            "availability": metrics.availability,
            "timestamp": metrics.timestamp.isoformat()
        }
    
    def _serialize_security_metrics(self, metrics: SecurityQualityMetrics) -> Dict[str, Any]:
        """Serialize security quality metrics"""
        return {
            "vulnerability_count": metrics.vulnerability_count,
            "critical_vulnerabilities": metrics.critical_vulnerabilities,
            "security_compliance_score": metrics.security_compliance_score,
            "access_control_score": metrics.access_control_score,
            "data_protection_score": metrics.data_protection_score,
            "security_incidents": metrics.security_incidents,
            "timestamp": metrics.timestamp.isoformat()
        }
    
    def _calculate_overall_quality_score(self, code: CodeQualityMetrics, 
                                       performance: PerformanceQualityMetrics,
                                       security: SecurityQualityMetrics) -> float:
        """Calculate overall quality score"""
        # Weighted average of all quality metrics
        code_score = (
            code.maintainability_index * 0.3 +
            (100 - code.cyclomatic_complexity * 2) * 0.2 +
            (100 - code.code_duplication * 2) * 0.1 +
            code.code_coverage * 0.2 +
            code.test_coverage * 0.2
        )
        
        performance_score = (
            (100 - performance.response_time_avg / 50) * 0.3 +
            (100 - performance.error_rate * 100) * 0.3 +
            performance.availability * 0.4
        )
        
        security_score = (
            (100 - security.vulnerability_count * 5) * 0.3 +
            security.security_compliance_score * 0.3 +
            security.access_control_score * 0.2 +
            security.data_protection_score * 0.2
        )
        
        # Overall weighted score
        overall_score = (
            code_score * 0.4 +
            performance_score * 0.35 +
            security_score * 0.25
        )
        
        return max(0.0, min(100.0, overall_score))
    
    async def _save_metrics_snapshot(self, report: Dict[str, Any]) -> None:
        """Save metrics snapshot to storage"""
        timestamp = datetime.now()
        filename = f"quality_metrics_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.storage_path / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            logger.debug(f"Metrics snapshot saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save metrics snapshot: {e}")
    
    def get_quality_trends(self, period: str = "weekly") -> List[QualityTrend]:
        """Analyze quality trends over time"""
        trends = []
        
        # Analyze code quality trends
        if len(self.code_metrics) >= 2:
            current = self.code_metrics[-1]
            previous = self.code_metrics[-2]
            
            trends.extend([
                self._calculate_trend("maintainability_index", 
                                    current.maintainability_index, 
                                    previous.maintainability_index, period),
                self._calculate_trend("code_coverage", 
                                    current.code_coverage, 
                                    previous.code_coverage, period),
                self._calculate_trend("test_coverage", 
                                    current.test_coverage, 
                                    previous.test_coverage, period)
            ])
        
        # Analyze performance trends
        if len(self.performance_metrics) >= 2:
            current = self.performance_metrics[-1]
            previous = self.performance_metrics[-2]
            
            trends.extend([
                self._calculate_trend("response_time_avg", 
                                    current.response_time_avg, 
                                    previous.response_time_avg, period),
                self._calculate_trend("throughput", 
                                    current.throughput, 
                                    previous.throughput, period),
                self._calculate_trend("availability", 
                                    current.availability, 
                                    previous.availability, period)
            ])
        
        # Analyze security trends
        if len(self.security_metrics) >= 2:
            current = self.security_metrics[-1]
            previous = self.security_metrics[-2]
            
            trends.extend([
                self._calculate_trend("vulnerability_count", 
                                    current.vulnerability_count, 
                                    previous.vulnerability_count, period),
                self._calculate_trend("security_compliance_score", 
                                    current.security_compliance_score, 
                                    previous.security_compliance_score, period)
            ])
        
        return trends
    
    def _calculate_trend(self, metric_name: str, current: float, previous: float, 
                        period: str) -> QualityTrend:
        """Calculate trend for a specific metric"""
        if previous == 0:
            change_percentage = 0.0
            trend_direction = "stable"
        else:
            change_percentage = ((current - previous) / previous) * 100
            if change_percentage > 1.0:
                trend_direction = "improving"
            elif change_percentage < -1.0:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        
        return QualityTrend(
            metric_name=metric_name,
            current_value=current,
            previous_value=previous,
            trend_direction=trend_direction,
            change_percentage=change_percentage,
            trend_period=period
        )
    
    def get_quality_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter metrics by date
        recent_code_metrics = [m for m in self.code_metrics if m.timestamp >= cutoff_date]
        recent_performance_metrics = [m for m in self.performance_metrics if m.timestamp >= cutoff_date]
        recent_security_metrics = [m for m in self.security_metrics if m.timestamp >= cutoff_date]
        
        return {
            "report_period": f"Last {days} days",
            "generated_at": datetime.now().isoformat(),
            "code_quality_summary": self._summarize_code_quality(recent_code_metrics),
            "performance_quality_summary": self._summarize_performance_quality(recent_performance_metrics),
            "security_quality_summary": self._summarize_security_quality(recent_security_metrics),
            "trends": self.get_quality_trends("weekly"),
            "recommendations": self._generate_recommendations(recent_code_metrics, 
                                                           recent_performance_metrics, 
                                                           recent_security_metrics)
        }
    
    def _summarize_code_quality(self, metrics: List[CodeQualityMetrics]) -> Dict[str, Any]:
        """Summarize code quality metrics"""
        if not metrics:
            return {"error": "No code quality metrics available"}
        
        return {
            "avg_maintainability": statistics.mean([m.maintainability_index for m in metrics]),
            "avg_code_coverage": statistics.mean([m.code_coverage for m in metrics]),
            "avg_test_coverage": statistics.mean([m.test_coverage for m in metrics]),
            "avg_technical_debt": statistics.mean([m.technical_debt for m in metrics]),
            "total_measurements": len(metrics)
        }
    
    def _summarize_performance_quality(self, metrics: List[PerformanceQualityMetrics]) -> Dict[str, Any]:
        """Summarize performance quality metrics"""
        if not metrics:
            return {"error": "No performance quality metrics available"}
        
        return {
            "avg_response_time": statistics.mean([m.response_time_avg for m in metrics]),
            "avg_throughput": statistics.mean([m.throughput for m in metrics]),
            "avg_availability": statistics.mean([m.availability for m in metrics]),
            "avg_error_rate": statistics.mean([m.error_rate for m in metrics]),
            "total_measurements": len(metrics)
        }
    
    def _summarize_security_quality(self, metrics: List[SecurityQualityMetrics]) -> Dict[str, Any]:
        """Summarize security quality metrics"""
        if not metrics:
            return {"error": "No security quality metrics available"}
        
        return {
            "avg_vulnerabilities": statistics.mean([m.vulnerability_count for m in metrics]),
            "avg_compliance_score": statistics.mean([m.security_compliance_score for m in metrics]),
            "avg_access_control_score": statistics.mean([m.access_control_score for m in metrics]),
            "total_incidents": sum([m.security_incidents for m in metrics]),
            "total_measurements": len(metrics)
        }
    
    def _generate_recommendations(self, code_metrics: List[CodeQualityMetrics],
                                performance_metrics: List[PerformanceQualityMetrics],
                                security_metrics: List[SecurityQualityMetrics]) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        # Code quality recommendations
        if code_metrics:
            avg_coverage = statistics.mean([m.code_coverage for m in code_metrics])
            if avg_coverage < 90:
                recommendations.append("Increase code coverage to at least 90%")
            
            avg_debt = statistics.mean([m.technical_debt for m in code_metrics])
            if avg_debt > 5:
                recommendations.append("Reduce technical debt to less than 5 days")
        
        # Performance recommendations
        if performance_metrics:
            avg_response = statistics.mean([m.response_time_avg for m in performance_metrics])
            if avg_response > 2000:
                recommendations.append("Optimize response times to under 2000ms")
            
            avg_error_rate = statistics.mean([m.error_rate for m in performance_metrics])
            if avg_error_rate > 0.5:
                recommendations.append("Reduce error rate to under 0.5%")
        
        # Security recommendations
        if security_metrics:
            avg_vulnerabilities = statistics.mean([m.vulnerability_count for m in security_metrics])
            if avg_vulnerabilities > 0:
                recommendations.append("Address all security vulnerabilities")
        
        return recommendations 