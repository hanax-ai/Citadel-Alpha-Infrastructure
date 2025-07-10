# 📊 Task 1.3: Logging and Monitoring System Setup

**Objective**: Implement comprehensive logging and monitoring infrastructure  
**Duration**: 40 minutes  
**Dependencies**: Task 1.2 Complete (Virtual Environment)  
**Success Criteria**: Logging system operational, monitoring endpoints active, health checks functional

## Prerequisites
- [ ] Task 1.2 completed successfully (Virtual environments operational)
- [ ] Configuration management system functional
- [ ] SSH access to both servers with sudo privileges
- [ ] Virtual environments with monitoring dependencies installed

## Step 1: Create Logging Configuration - hx-llm-server-01 (192.168.10.29)
```bash
echo "🔍 Creating logging configuration on hx-llm-server-01..."

# Create logging configuration module
ssh agent0@192.168.10.29 'cat > /opt/citadel/configs/logging_config.py << EOF
"""
Citadel Logging Configuration Module
"""
import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from datetime import datetime

from pydantic import BaseSettings, Field
from base_settings import BaseConfig


class LoggingConfig(BaseSettings):
    """Logging configuration settings"""
    
    # Log levels
    log_level: str = Field(default="INFO", description="Main logging level")
    file_log_level: str = Field(default="DEBUG", description="File logging level")
    console_log_level: str = Field(default="INFO", description="Console logging level")
    
    # Log file settings
    log_file_max_bytes: int = Field(default=50*1024*1024, description="Max log file size in bytes (50MB)")
    log_file_backup_count: int = Field(default=5, description="Number of backup log files")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        description="Log message format"
    )
    
    # Component-specific logging
    vllm_log_level: str = Field(default="INFO", description="vLLM component log level")
    api_log_level: str = Field(default="INFO", description="API component log level")
    monitor_log_level: str = Field(default="INFO", description="Monitoring component log level")
    
    # Performance logging
    log_requests: bool = Field(default=True, description="Log HTTP requests")
    log_performance_metrics: bool = Field(default=True, description="Log performance metrics")
    performance_log_interval: int = Field(default=60, description="Performance logging interval in seconds")
    
    class Config:
        env_prefix = "LOG_"


def setup_citadel_logging(config: Optional[LoggingConfig] = None) -> logging.Logger:
    """Setup comprehensive logging for Citadel"""
    
    if config is None:
        config = LoggingConfig()
    
    # Create logs directory
    log_dir = Path("/opt/citadel/logs")
    log_dir.mkdir(exist_ok=True)
    
    # Main application logger
    logger = logging.getLogger("citadel")
    logger.setLevel(getattr(logging, config.log_level))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter(config.log_format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.console_log_level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Main log file handler (rotating)
    main_log_file = log_dir / "citadel.log"
    file_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=config.log_file_max_bytes,
        backupCount=config.log_file_backup_count
    )
    file_handler.setLevel(getattr(logging, config.file_log_level))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Component-specific loggers
    setup_component_loggers(config, log_dir, formatter)
    
    # Initial log message
    logger.info(f"Citadel logging initialized - Log Level: {config.log_level}")
    logger.info(f"Log directory: {log_dir}")
    
    return logger


def setup_component_loggers(config: LoggingConfig, log_dir: Path, formatter: logging.Formatter):
    """Setup component-specific loggers"""
    
    components = {
        "citadel.vllm": config.vllm_log_level,
        "citadel.api": config.api_log_level,
        "citadel.monitor": config.monitor_log_level,
        "citadel.performance": "DEBUG" if config.log_performance_metrics else "WARNING"
    }
    
    for component_name, level in components.items():
        component_logger = logging.getLogger(component_name)
        component_logger.setLevel(getattr(logging, level))
        
        # Component-specific log file
        log_file = log_dir / f"{component_name.split(\".\")[-1]}.log"
        component_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.log_file_max_bytes // 2,  # Smaller files for components
            backupCount=3
        )
        component_handler.setLevel(getattr(logging, level))
        component_handler.setFormatter(formatter)
        component_logger.addHandler(component_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific component"""
    return logging.getLogger(f"citadel.{name}")


class RequestLogger:
    """HTTP request logging utility"""
    
    def __init__(self):
        self.logger = get_logger("api")
        
    def log_request(self, method: str, path: str, status_code: int, 
                   response_time: float, client_ip: str = "unknown"):
        """Log HTTP request details"""
        self.logger.info(
            f"Request: {method} {path} - Status: {status_code} - "
            f"Time: {response_time:.3f}s - Client: {client_ip}"
        )


class PerformanceLogger:
    """Performance metrics logging utility"""
    
    def __init__(self):
        self.logger = get_logger("performance")
        
    def log_gpu_stats(self, gpu_id: int, utilization: float, memory_used: int, memory_total: int):
        """Log GPU performance statistics"""
        memory_percent = (memory_used / memory_total) * 100 if memory_total > 0 else 0
        self.logger.info(
            f"GPU-{gpu_id}: Util={utilization:.1f}% Memory={memory_used}MB/{memory_total}MB ({memory_percent:.1f}%)"
        )
        
    def log_model_stats(self, model_name: str, tokens_per_second: float, 
                       requests_processed: int, queue_size: int):
        """Log model performance statistics"""
        self.logger.info(
            f"Model {model_name}: TPS={tokens_per_second:.2f} Requests={requests_processed} Queue={queue_size}"
        )
        
    def log_system_stats(self, cpu_percent: float, memory_percent: float, 
                        disk_usage_percent: float):
        """Log system performance statistics"""
        self.logger.info(
            f"System: CPU={cpu_percent:.1f}% Memory={memory_percent:.1f}% Disk={disk_usage_percent:.1f}%"
        )


if __name__ == "__main__":
    # Test logging configuration
    config = LoggingConfig()
    logger = setup_citadel_logging(config)
    
    # Test different log levels
    logger.debug("Debug message test")
    logger.info("Info message test")
    logger.warning("Warning message test")
    logger.error("Error message test")
    
    # Test component loggers
    vllm_logger = get_logger("vllm")
    vllm_logger.info("vLLM component test message")
    
    api_logger = get_logger("api")
    api_logger.info("API component test message")
    
    # Test performance logger
    perf_logger = PerformanceLogger()
    perf_logger.log_gpu_stats(0, 85.5, 8192, 12288)
    perf_logger.log_system_stats(45.2, 62.8, 35.1)
    
    print("Logging configuration test completed")
EOF'

# Test logging configuration
ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 logging_config.py' && echo "✅ Logging Config 01: FUNCTIONAL" || echo "❌ Logging Config 01: FAILED"

# Verify log files created
ssh agent0@192.168.10.29 'ls -la /opt/citadel/logs/' && echo "✅ Log Files 01: CREATED" || echo "❌ Log Files 01: FAILED"
```

## Step 2: Create Monitoring System - hx-llm-server-01
```bash
echo "🔍 Creating monitoring system on hx-llm-server-01..."

# Create comprehensive monitoring module
ssh agent0@192.168.10.29 'cat > /opt/citadel/configs/monitoring.py << EOF
"""
Citadel Monitoring and Health Check System
"""
import asyncio
import time
import psutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    import GPUtil
    HAS_GPUTIL = True
except ImportError:
    HAS_GPUTIL = False

try:
    import pynvml
    pynvml.nvmlInit()
    HAS_PYNVML = True
except ImportError:
    HAS_PYNVML = False

from logging_config import get_logger, PerformanceLogger


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    load_average: List[float]
    uptime_hours: float


@dataclass
class GPUMetrics:
    """GPU performance metrics"""
    gpu_id: int
    name: str
    utilization_percent: float
    memory_used_mb: int
    memory_total_mb: int
    memory_percent: float
    temperature_c: int
    power_draw_w: float


@dataclass
class ProcessMetrics:
    """Process-specific metrics"""
    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    status: str
    create_time: datetime


@dataclass
class HealthStatus:
    """Overall system health status"""
    timestamp: datetime
    status: str  # "healthy", "warning", "critical"
    components: Dict[str, str]
    alerts: List[str]
    metrics_summary: Dict[str, Any]


class SystemMonitor:
    """System performance monitoring"""
    
    def __init__(self):
        self.logger = get_logger("monitor")
        self.perf_logger = PerformanceLogger()
        
    def get_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            load_avg = psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0.0, 0.0, 0.0]
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=memory.percent,
                memory_available_gb=memory.available / (1024**3),
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / (1024**3),
                load_average=list(load_avg),
                uptime_hours=time.time() - psutil.boot_time()) / 3600
            )
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            raise
            
    def get_gpu_metrics(self) -> List[GPUMetrics]:
        """Collect GPU performance metrics"""
        gpu_metrics = []
        
        if not HAS_GPUTIL and not HAS_PYNVML:
            self.logger.warning("No GPU monitoring libraries available")
            return gpu_metrics
            
        try:
            if HAS_GPUTIL:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_metrics.append(GPUMetrics(
                        gpu_id=gpu.id,
                        name=gpu.name,
                        utilization_percent=gpu.load * 100,
                        memory_used_mb=gpu.memoryUsed,
                        memory_total_mb=gpu.memoryTotal,
                        memory_percent=(gpu.memoryUsed / gpu.memoryTotal) * 100,
                        temperature_c=gpu.temperature,
                        power_draw_w=0.0  # GPUtil doesn return power info
                    ))
            elif HAS_PYNVML:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    
                    try:
                        power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                    except:
                        power = 0.0
                    
                    gpu_metrics.append(GPUMetrics(
                        gpu_id=i,
                        name=pynvml.nvmlDeviceGetName(handle).decode("utf-8"),
                        utilization_percent=util.gpu,
                        memory_used_mb=info.used // (1024*1024),
                        memory_total_mb=info.total // (1024*1024),
                        memory_percent=(info.used / info.total) * 100,
                        temperature_c=temp,
                        power_draw_w=power
                    ))
        except Exception as e:
            self.logger.error(f"Error collecting GPU metrics: {e}")
            
        return gpu_metrics
        
    def get_process_metrics(self, process_names: List[str]) -> List[ProcessMetrics]:
        """Collect metrics for specific processes"""
        process_metrics = []
        
        try:
            for proc in psutil.process_iter([\"pid\", \"name\", \"cpu_percent\", \"memory_info\", \"status\", \"create_time\"]):
                try:
                    if any(name.lower() in proc.info[\"name\"].lower() for name in process_names):
                        memory_mb = proc.info[\"memory_info\"].rss / (1024*1024)
                        memory_percent = proc.memory_percent()
                        
                        process_metrics.append(ProcessMetrics(
                            pid=proc.info[\"pid\"],
                            name=proc.info[\"name\"],
                            cpu_percent=proc.info[\"cpu_percent\"],
                            memory_mb=memory_mb,
                            memory_percent=memory_percent,
                            status=proc.info[\"status\"],
                            create_time=datetime.fromtimestamp(proc.info[\"create_time\"])
                        ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.error(f"Error collecting process metrics: {e}")
            
        return process_metrics


class HealthChecker:
    """System health monitoring and alerting"""
    
    def __init__(self, monitor: SystemMonitor):
        self.monitor = monitor
        self.logger = get_logger("monitor")
        
        # Health thresholds
        self.cpu_warning_threshold = 80.0
        self.cpu_critical_threshold = 95.0
        self.memory_warning_threshold = 85.0
        self.memory_critical_threshold = 95.0
        self.disk_warning_threshold = 85.0
        self.disk_critical_threshold = 95.0
        self.gpu_memory_warning_threshold = 90.0
        self.gpu_temp_warning_threshold = 80
        self.gpu_temp_critical_threshold = 90
        
    def check_health(self) -> HealthStatus:
        """Perform comprehensive health check"""
        timestamp = datetime.now()
        alerts = []
        components = {}
        
        try:
            # System metrics check
            sys_metrics = self.monitor.get_system_metrics()
            components["system"] = self._check_system_health(sys_metrics, alerts)
            
            # GPU metrics check
            gpu_metrics = self.monitor.get_gpu_metrics()
            components["gpu"] = self._check_gpu_health(gpu_metrics, alerts)
            
            # Process check
            vllm_processes = self.monitor.get_process_metrics(["python", "vllm", "uvicorn"])
            components["processes"] = self._check_process_health(vllm_processes, alerts)
            
            # Determine overall status
            if any(status == "critical" for status in components.values()):
                overall_status = "critical"
            elif any(status == "warning" for status in components.values()):
                overall_status = "warning"
            else:
                overall_status = "healthy"
                
            # Create metrics summary
            metrics_summary = {
                "cpu_percent": sys_metrics.cpu_percent,
                "memory_percent": sys_metrics.memory_percent,
                "disk_percent": sys_metrics.disk_usage_percent,
                "gpu_count": len(gpu_metrics),
                "process_count": len(vllm_processes)
            }
            
            return HealthStatus(
                timestamp=timestamp,
                status=overall_status,
                components=components,
                alerts=alerts,
                metrics_summary=metrics_summary
            )
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return HealthStatus(
                timestamp=timestamp,
                status="critical",
                components={"system": "critical"},
                alerts=[f"Health check failed: {str(e)}"],
                metrics_summary={}
            )
            
    def _check_system_health(self, metrics: SystemMetrics, alerts: List[str]) -> str:
        """Check system component health"""
        status = "healthy"
        
        # CPU check
        if metrics.cpu_percent >= self.cpu_critical_threshold:
            status = "critical"
            alerts.append(f"Critical CPU usage: {metrics.cpu_percent:.1f}%")
        elif metrics.cpu_percent >= self.cpu_warning_threshold:
            status = "warning"
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
            
        # Memory check
        if metrics.memory_percent >= self.memory_critical_threshold:
            status = "critical"
            alerts.append(f"Critical memory usage: {metrics.memory_percent:.1f}%")
        elif metrics.memory_percent >= self.memory_warning_threshold:
            if status != "critical":
                status = "warning"
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")
            
        # Disk check
        if metrics.disk_usage_percent >= self.disk_critical_threshold:
            status = "critical"
            alerts.append(f"Critical disk usage: {metrics.disk_usage_percent:.1f}%")
        elif metrics.disk_usage_percent >= self.disk_warning_threshold:
            if status != "critical":
                status = "warning"
            alerts.append(f"High disk usage: {metrics.disk_usage_percent:.1f}%")
            
        return status
        
    def _check_gpu_health(self, gpu_metrics: List[GPUMetrics], alerts: List[str]) -> str:
        """Check GPU component health"""
        if not gpu_metrics:
            return "unknown"
            
        status = "healthy"
        
        for gpu in gpu_metrics:
            # GPU memory check
            if gpu.memory_percent >= self.gpu_memory_warning_threshold:
                if status != "critical":
                    status = "warning"
                alerts.append(f"GPU-{gpu.gpu_id} high memory usage: {gpu.memory_percent:.1f}%")
                
            # GPU temperature check
            if gpu.temperature_c >= self.gpu_temp_critical_threshold:
                status = "critical"
                alerts.append(f"GPU-{gpu.gpu_id} critical temperature: {gpu.temperature_c}°C")
            elif gpu.temperature_c >= self.gpu_temp_warning_threshold:
                if status != "critical":
                    status = "warning"
                alerts.append(f"GPU-{gpu.gpu_id} high temperature: {gpu.temperature_c}°C")
                
        return status
        
    def _check_process_health(self, processes: List[ProcessMetrics], alerts: List[str]) -> str:
        """Check process health"""
        if not processes:
            alerts.append("No vLLM/Python processes found")
            return "warning"
            
        return "healthy"


class MonitoringServer:
    """Monitoring HTTP server for health checks and metrics"""
    
    def __init__(self, monitor: SystemMonitor, health_checker: HealthChecker):
        self.monitor = monitor
        self.health_checker = health_checker
        self.logger = get_logger("monitor")
        
    async def health_endpoint(self) -> Dict[str, Any]:
        """Health check endpoint"""
        health_status = self.health_checker.check_health()
        return asdict(health_status)
        
    async def metrics_endpoint(self) -> Dict[str, Any]:
        """Metrics endpoint"""
        try:
            system_metrics = self.monitor.get_system_metrics()
            gpu_metrics = self.monitor.get_gpu_metrics()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system": asdict(system_metrics),
                "gpus": [asdict(gpu) for gpu in gpu_metrics]
            }
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            raise


def save_metrics_to_file(metrics: Dict[str, Any], filename: str = None):
    """Save metrics to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/opt/citadel/logs/metrics_{timestamp}.json"
        
    try:
        with open(filename, "w") as f:
            json.dump(metrics, f, indent=2, default=str)
    except Exception as e:
        logger = get_logger("monitor")
        logger.error(f"Error saving metrics to file: {e}")


if __name__ == "__main__":
    # Test monitoring system
    monitor = SystemMonitor()
    health_checker = HealthChecker(monitor)
    
    print("Testing system monitoring...")
    
    # Test system metrics
    sys_metrics = monitor.get_system_metrics()
    print(f"System Metrics: CPU={sys_metrics.cpu_percent:.1f}%, Memory={sys_metrics.memory_percent:.1f}%")
    
    # Test GPU metrics
    gpu_metrics = monitor.get_gpu_metrics()
    if gpu_metrics:
        for gpu in gpu_metrics:
            print(f"GPU-{gpu.gpu_id}: {gpu.name}, Util={gpu.utilization_percent:.1f}%")
    else:
        print("No GPUs detected")
    
    # Test health check
    health = health_checker.check_health()
    print(f"Health Status: {health.status}")
    if health.alerts:
        print("Alerts:", health.alerts)
        
    # Save test metrics
    all_metrics = {
        "system": asdict(sys_metrics),
        "gpus": [asdict(gpu) for gpu in gpu_metrics],
        "health": asdict(health)
    }
    save_metrics_to_file(all_metrics)
    print("Monitoring system test completed")
EOF'

# Test monitoring system
ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 monitoring.py' && echo "✅ Monitoring System 01: FUNCTIONAL" || echo "❌ Monitoring System 01: FAILED"
```

## Step 3: Create Health Check API - hx-llm-server-01
```bash
echo "🔍 Creating health check API on hx-llm-server-01..."

# Create FastAPI health check server
ssh agent0@192.168.10.29 'cat > /opt/citadel/scripts/health_server.py << EOF
"""
Citadel Health Check and Monitoring API Server
"""
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
import os

# Add configs to path
sys.path.insert(0, "/opt/citadel/configs")

from monitoring import SystemMonitor, HealthChecker, MonitoringServer
from logging_config import setup_citadel_logging, get_logger


# Global monitoring components
monitor = None
health_checker = None
monitoring_server = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global monitor, health_checker, monitoring_server
    
    # Setup logging
    setup_citadel_logging()
    logger = get_logger("api")
    logger.info("Starting Citadel Health Check API")
    
    # Initialize monitoring
    monitor = SystemMonitor()
    health_checker = HealthChecker(monitor)
    monitoring_server = MonitoringServer(monitor, health_checker)
    
    logger.info("Health check API initialized")
    yield
    
    logger.info("Shutting down Health check API")


# Create FastAPI app
app = FastAPI(
    title="Citadel Health Check API",
    description="Health monitoring and metrics for Citadel vLLM deployment",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Citadel Health Check API", "status": "operational"}


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        health_status = await monitoring_server.health_endpoint()
        
        # Return appropriate HTTP status code
        if health_status["status"] == "critical":
            return JSONResponse(
                status_code=503,  # Service Unavailable
                content=health_status
            )
        elif health_status["status"] == "warning":
            return JSONResponse(
                status_code=200,  # OK but with warnings
                content=health_status
            )
        else:
            return JSONResponse(
                status_code=200,  # OK
                content=health_status
            )
            
    except Exception as e:
        logger = get_logger("api")
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/health/simple")
async def simple_health():
    """Simple health check for load balancers"""
    try:
        health_status = await monitoring_server.health_endpoint()
        
        if health_status["status"] == "critical":
            raise HTTPException(status_code=503, detail="Service unavailable")
        else:
            return {"status": "ok"}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/metrics")
async def get_metrics():
    """Get detailed system metrics"""
    try:
        metrics = await monitoring_server.metrics_endpoint()
        return metrics
    except Exception as e:
        logger = get_logger("api")
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics collection failed: {str(e)}")


@app.get("/metrics/system")
async def get_system_metrics():
    """Get system-only metrics"""
    try:
        system_metrics = monitor.get_system_metrics()
        return {"system": system_metrics.__dict__}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System metrics failed: {str(e)}")


@app.get("/metrics/gpu")
async def get_gpu_metrics():
    """Get GPU-only metrics"""
    try:
        gpu_metrics = monitor.get_gpu_metrics()
        return {"gpus": [gpu.__dict__ for gpu in gpu_metrics]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPU metrics failed: {str(e)}")


@app.get("/status")
async def get_status():
    """Get service status information"""
    try:
        health_status = await monitoring_server.health_endpoint()
        return {
            "service": "citadel-health",
            "version": "1.0.0",
            "status": health_status["status"],
            "timestamp": health_status["timestamp"],
            "components": health_status["components"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


if __name__ == "__main__":
    # Configuration
    host = os.getenv("HEALTH_HOST", "0.0.0.0")
    port = int(os.getenv("HEALTH_PORT", 9090))
    
    print(f"Starting Citadel Health Check API on {host}:{port}")
    
    uvicorn.run(
        "health_server:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
EOF'

# Make health server executable
ssh agent0@192.168.10.29 'chmod +x /opt/citadel/scripts/health_server.py' && echo "✅ Health API 01: CREATED" || echo "❌ Health API 01: FAILED"

# Test health server import (quick test)
ssh agent0@192.168.10.29 'cd /opt/citadel/scripts && source /opt/citadel/venvs/citadel-admin/bin/activate && python3 -c "import health_server; print(\"Health server import successful\")"' && echo "✅ Health Server Import 01: SUCCESS" || echo "❌ Health Server Import 01: FAILED"
```

## Step 4: Create Monitoring Scripts and Automation - hx-llm-server-01
```bash
echo "🔍 Creating monitoring scripts and automation on hx-llm-server-01..."

# Create monitoring runner script
ssh agent0@192.168.10.29 'cat > /opt/citadel/scripts/monitor.sh << EOF
#!/bin/bash
# Citadel Monitoring Runner Script

CITADEL_ROOT="/opt/citadel"
VENV_PATH="/opt/citadel/venvs/citadel-admin"
HEALTH_SERVER_SCRIPT="/opt/citadel/scripts/health_server.py"
MONITOR_PID_FILE="/opt/citadel/tmp/monitor.pid"

show_help() {
    echo "Citadel Monitoring Script"
    echo "Usage: \$0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start health monitoring server"
    echo "  stop      - Stop health monitoring server"
    echo "  restart   - Restart health monitoring server"
    echo "  status    - Show monitoring status"
    echo "  check     - Run one-time health check"
    echo "  metrics   - Show current metrics"
    echo "  logs      - Show monitoring logs"
    echo "  help      - Show this help"
}

start_monitor() {
    if [ -f "\$MONITOR_PID_FILE" ]; then
        PID=\$(cat \$MONITOR_PID_FILE)
        if ps -p \$PID > /dev/null 2>&1; then
            echo "❌ Monitor already running (PID: \$PID)"
            return 1
        else
            rm -f \$MONITOR_PID_FILE
        fi
    fi
    
    echo "🚀 Starting Citadel health monitoring server..."
    
    # Activate virtual environment and start server
    source \$VENV_PATH/bin/activate
    cd \$CITADEL_ROOT/scripts
    
    nohup python3 health_server.py > /opt/citadel/logs/health-server.log 2>&1 &
    echo \$! > \$MONITOR_PID_FILE
    
    sleep 2
    
    if ps -p \$(cat \$MONITOR_PID_FILE) > /dev/null 2>&1; then
        echo "✅ Health monitoring server started (PID: \$(cat \$MONITOR_PID_FILE))"
        echo "   API available at: http://localhost:9090"
        echo "   Health check: http://localhost:9090/health"
        echo "   Metrics: http://localhost:9090/metrics"
    else
        echo "❌ Failed to start health monitoring server"
        rm -f \$MONITOR_PID_FILE
        return 1
    fi
}

stop_monitor() {
    if [ ! -f "\$MONITOR_PID_FILE" ]; then
        echo "❌ Monitor PID file not found"
        return 1
    fi
    
    PID=\$(cat \$MONITOR_PID_FILE)
    
    if ps -p \$PID > /dev/null 2>&1; then
        echo "🛑 Stopping health monitoring server (PID: \$PID)..."
        kill \$PID
        
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! ps -p \$PID > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if ps -p \$PID > /dev/null 2>&1; then
            echo "⚠️  Forcing shutdown..."
            kill -9 \$PID
        fi
        
        rm -f \$MONITOR_PID_FILE
        echo "✅ Health monitoring server stopped"
    else
        echo "❌ Monitor not running"
        rm -f \$MONITOR_PID_FILE
    fi
}

show_status() {
    echo "📊 Citadel Monitoring Status"
    echo "============================"
    
    if [ -f "\$MONITOR_PID_FILE" ]; then
        PID=\$(cat \$MONITOR_PID_FILE)
        if ps -p \$PID > /dev/null 2>&1; then
            echo "✅ Health server: RUNNING (PID: \$PID)"
            
            # Test API endpoint
            if curl -s http://localhost:9090/ > /dev/null 2>&1; then
                echo "✅ API endpoint: ACCESSIBLE"
            else
                echo "❌ API endpoint: NOT ACCESSIBLE"
            fi
        else
            echo "❌ Health server: NOT RUNNING (stale PID file)"
            rm -f \$MONITOR_PID_FILE
        fi
    else
        echo "❌ Health server: NOT RUNNING"
    fi
    
    echo ""
    echo "Log files:"
    ls -la /opt/citadel/logs/*.log 2>/dev/null | tail -5
}

run_health_check() {
    echo "🔍 Running health check..."
    
    source \$VENV_PATH/bin/activate
    cd \$CITADEL_ROOT/configs
    
    python3 -c "
from monitoring import SystemMonitor, HealthChecker
import json

monitor = SystemMonitor()
health_checker = HealthChecker(monitor)
health = health_checker.check_health()

print(f\"Health Status: {health.status}\")
print(f\"Timestamp: {health.timestamp}\")
print(\"Components:\")
for component, status in health.components.items():
    print(f\"  {component}: {status}\")
    
if health.alerts:
    print(\"Alerts:\")
    for alert in health.alerts:
        print(f\"  - {alert}\")
else:
    print(\"No alerts\")
"
}

show_metrics() {
    echo "📈 Current System Metrics"
    echo "========================"
    
    source \$VENV_PATH/bin/activate
    cd \$CITADEL_ROOT/configs
    
    python3 -c "
from monitoring import SystemMonitor
import json

monitor = SystemMonitor()
sys_metrics = monitor.get_system_metrics()
gpu_metrics = monitor.get_gpu_metrics()

print(f\"System Metrics (as of {sys_metrics.timestamp}):\")
print(f\"  CPU Usage: {sys_metrics.cpu_percent:.1f}%\")
print(f\"  Memory Usage: {sys_metrics.memory_percent:.1f}% ({sys_metrics.memory_available_gb:.1f}GB available)\")
print(f\"  Disk Usage: {sys_metrics.disk_usage_percent:.1f}% ({sys_metrics.disk_free_gb:.1f}GB free)\")
print(f\"  Load Average: {sys_metrics.load_average}\")
print(f\"  Uptime: {sys_metrics.uptime_hours:.1f} hours\")

if gpu_metrics:
    print(\"\\nGPU Metrics:\")
    for gpu in gpu_metrics:
        print(f\"  GPU-{gpu.gpu_id} ({gpu.name}):\")
        print(f\"    Utilization: {gpu.utilization_percent:.1f}%\")
        print(f\"    Memory: {gpu.memory_used_mb}MB/{gpu.memory_total_mb}MB ({gpu.memory_percent:.1f}%)\")
        print(f\"    Temperature: {gpu.temperature_c}°C\")
        print(f\"    Power: {gpu.power_draw_w:.1f}W\")
else:
    print(\"\\nNo GPU metrics available\")
"
}

show_logs() {
    echo "📋 Recent Monitoring Logs"
    echo "========================="
    
    echo "Health Server Logs:"
    tail -20 /opt/citadel/logs/health-server.log 2>/dev/null || echo "No health server logs found"
    
    echo ""
    echo "Monitor Logs:"
    tail -20 /opt/citadel/logs/monitor.log 2>/dev/null || echo "No monitor logs found"
}

# Main command processing
case "\$1" in
    "start")
        start_monitor
        ;;
    "stop")
        stop_monitor
        ;;
    "restart")
        stop_monitor
        sleep 2
        start_monitor
        ;;
    "status")
        show_status
        ;;
    "check")
        run_health_check
        ;;
    "metrics")
        show_metrics
        ;;
    "logs")
        show_logs
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "❌ Unknown command: \$1"
        show_help
        exit 1
        ;;
esac
EOF'

# Make monitoring script executable
ssh agent0@192.168.10.29 'chmod +x /opt/citadel/scripts/monitor.sh' && echo "✅ Monitor Script 01: CREATED" || echo "❌ Monitor Script 01: FAILED"

# Test monitoring script
ssh agent0@192.168.10.29 '/opt/citadel/scripts/monitor.sh check' && echo "✅ Monitor Script Test 01: SUCCESS" || echo "❌ Monitor Script Test 01: FAILED"
```

## Step 5: Replicate Monitoring Setup on hx-llm-server-02 (192.168.10.28)
```bash
echo "🔍 Replicating monitoring setup on hx-llm-server-02..."

# Copy monitoring configuration files
ssh agent0@192.168.10.29 'cd /opt/citadel/configs && tar czf - logging_config.py monitoring.py' | ssh agent0@192.168.10.28 'cd /opt/citadel/configs && tar xzf -' && echo "✅ Config Files Copy 02: SUCCESS" || echo "❌ Config Files Copy 02: FAILED"

# Copy monitoring scripts
ssh agent0@192.168.10.29 'cd /opt/citadel/scripts && tar czf - health_server.py monitor.sh' | ssh agent0@192.168.10.28 'cd /opt/citadel/scripts && tar xzf -' && echo "✅ Script Files Copy 02: SUCCESS" || echo "❌ Script Files Copy 02: FAILED"

# Make scripts executable
ssh agent0@192.168.10.28 'chmod +x /opt/citadel/scripts/health_server.py /opt/citadel/scripts/monitor.sh' && echo "✅ Scripts Executable 02: SET" || echo "❌ Scripts Executable 02: FAILED"

# Customize health server port for server-02 (to avoid conflicts)
ssh agent0@192.168.10.28 'sed -i "s/port = int(os.getenv(\"HEALTH_PORT\", 9090))/port = int(os.getenv(\"HEALTH_PORT\", 9092))/" /opt/citadel/scripts/health_server.py' && echo "✅ Port Customization 02: APPLIED" || echo "❌ Port Customization 02: FAILED"

# Test monitoring configuration
ssh agent0@192.168.10.28 'cd /opt/citadel/configs && python3 logging_config.py' && echo "✅ Logging Config 02: FUNCTIONAL" || echo "❌ Logging Config 02: FAILED"
ssh agent0@192.168.10.28 'cd /opt/citadel/configs && python3 monitoring.py' && echo "✅ Monitoring System 02: FUNCTIONAL" || echo "❌ Monitoring System 02: FAILED"

# Test monitoring script
ssh agent0@192.168.10.28 '/opt/citadel/scripts/monitor.sh check' && echo "✅ Monitor Script Test 02: SUCCESS" || echo "❌ Monitor Script Test 02: FAILED"
```

## Step 6: Create Systemd Services for Monitoring - Both Servers
```bash
echo "🔍 Creating systemd services for monitoring on both servers..."

# Create systemd service for server-01
ssh agent0@192.168.10.29 'sudo cat > /etc/systemd/system/citadel-health.service << EOF
[Unit]
Description=Citadel Health Monitoring Service
After=network.target

[Service]
Type=simple
User=agent0
Group=agent0
WorkingDirectory=/opt/citadel/scripts
Environment=HEALTH_HOST=0.0.0.0
Environment=HEALTH_PORT=9090
Environment=PYTHONPATH=/opt/citadel/configs
ExecStart=/opt/citadel/venvs/citadel-admin/bin/python /opt/citadel/scripts/health_server.py
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
Restart=always
RestartSec=10
StandardOutput=append:/opt/citadel/logs/health-service.log
StandardError=append:/opt/citadel/logs/health-service.log

[Install]
WantedBy=multi-user.target
EOF' && echo "✅ Systemd Service 01: CREATED" || echo "❌ Systemd Service 01: FAILED"

# Create systemd service for server-02 (different port)
ssh agent0@192.168.10.28 'sudo cat > /etc/systemd/system/citadel-health.service << EOF
[Unit]
Description=Citadel Health Monitoring Service
After=network.target

[Service]
Type=simple
User=agent0
Group=agent0
WorkingDirectory=/opt/citadel/scripts
Environment=HEALTH_HOST=0.0.0.0
Environment=HEALTH_PORT=9092
Environment=PYTHONPATH=/opt/citadel/configs
ExecStart=/opt/citadel/venvs/citadel-admin/bin/python /opt/citadel/scripts/health_server.py
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
Restart=always
RestartSec=10
StandardOutput=append:/opt/citadel/logs/health-service.log
StandardError=append:/opt/citadel/logs/health-service.log

[Install]
WantedBy=multi-user.target
EOF' && echo "✅ Systemd Service 02: CREATED" || echo "❌ Systemd Service 02: FAILED"

# Reload systemd and enable services
ssh agent0@192.168.10.29 'sudo systemctl daemon-reload && sudo systemctl enable citadel-health' && echo "✅ Service Enable 01: SUCCESS" || echo "❌ Service Enable 01: FAILED"
ssh agent0@192.168.10.28 'sudo systemctl daemon-reload && sudo systemctl enable citadel-health' && echo "✅ Service Enable 02: SUCCESS" || echo "❌ Service Enable 02: FAILED"

# Test systemd service status (without starting)
ssh agent0@192.168.10.29 'sudo systemctl status citadel-health --no-pager' && echo "✅ Service Status Check 01: SUCCESS" || echo "❌ Service Status Check 01: FAILED"
ssh agent0@192.168.10.28 'sudo systemctl status citadel-health --no-pager' && echo "✅ Service Status Check 02: SUCCESS" || echo "❌ Service Status Check 02: FAILED"
```

## Step 7: Monitoring System Validation and Report
```bash
echo "📊 Generating logging and monitoring deployment report..."

cat > /tmp/logging-monitoring-report.md << EOF
# Logging and Monitoring System Report - $(date)

## hx-llm-server-01 (192.168.10.29)
- **Logging Config**: $(ssh agent0@192.168.10.29 'test -f /opt/citadel/configs/logging_config.py && echo "✅ CREATED" || echo "❌ MISSING"')
- **Monitoring System**: $(ssh agent0@192.168.10.29 'test -f /opt/citadel/configs/monitoring.py && echo "✅ CREATED" || echo "❌ MISSING"')
- **Health API**: $(ssh agent0@192.168.10.29 'test -x /opt/citadel/scripts/health_server.py && echo "✅ CREATED" || echo "❌ MISSING"')
- **Monitor Script**: $(ssh agent0@192.168.10.29 'test -x /opt/citadel/scripts/monitor.sh && echo "✅ CREATED" || echo "❌ MISSING"')
- **Systemd Service**: $(ssh agent0@192.168.10.29 'sudo systemctl is-enabled citadel-health 2>/dev/null && echo "✅ ENABLED" || echo "❌ DISABLED"')
- **Log Directory**: $(ssh agent0@192.168.10.29 'test -d /opt/citadel/logs && echo "✅ CREATED" || echo "❌ MISSING"')

## hx-llm-server-02 (192.168.10.28)
- **Logging Config**: $(ssh agent0@192.168.10.28 'test -f /opt/citadel/configs/logging_config.py && echo "✅ CREATED" || echo "❌ MISSING"')
- **Monitoring System**: $(ssh agent0@192.168.10.28 'test -f /opt/citadel/configs/monitoring.py && echo "✅ CREATED" || echo "❌ MISSING"')
- **Health API**: $(ssh agent0@192.168.10.28 'test -x /opt/citadel/scripts/health_server.py && echo "✅ CREATED" || echo "❌ MISSING"')
- **Monitor Script**: $(ssh agent0@192.168.10.28 'test -x /opt/citadel/scripts/monitor.sh && echo "✅ CREATED" || echo "❌ MISSING"')
- **Systemd Service**: $(ssh agent0@192.168.10.28 'sudo systemctl is-enabled citadel-health 2>/dev/null && echo "✅ ENABLED" || echo "❌ DISABLED"')
- **Log Directory**: $(ssh agent0@192.168.10.28 'test -d /opt/citadel/logs && echo "✅ CREATED" || echo "❌ MISSING"')

## Features Implemented
- **Structured Logging**: ✅ Pydantic-based configuration with rotating log files
- **Component Loggers**: ✅ Separate loggers for vLLM, API, monitoring, performance
- **System Monitoring**: ✅ CPU, memory, disk, load average tracking
- **GPU Monitoring**: ✅ GPU utilization, memory, temperature tracking
- **Health Checks**: ✅ Comprehensive health status with thresholds
- **HTTP API**: ✅ RESTful health and metrics endpoints
- **Process Monitoring**: ✅ vLLM process tracking
- **Alerting**: ✅ Warning and critical alerts
- **Automation**: ✅ Management scripts and systemd services

## Configuration Tests
- Server-01 Logging Test: $(ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 -c "from logging_config import setup_citadel_logging; setup_citadel_logging(); print(\"SUCCESS\")" 2>/dev/null || echo "FAILED"')
- Server-02 Logging Test: $(ssh agent0@192.168.10.28 'cd /opt/citadel/configs && python3 -c "from logging_config import setup_citadel_logging; setup_citadel_logging(); print(\"SUCCESS\")" 2>/dev/null || echo "FAILED"')
- Server-01 Monitoring Test: $(ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 -c "from monitoring import SystemMonitor; SystemMonitor().get_system_metrics(); print(\"SUCCESS\")" 2>/dev/null || echo "FAILED"')
- Server-02 Monitoring Test: $(ssh agent0@192.168.10.28 'cd /opt/citadel/configs && python3 -c "from monitoring import SystemMonitor; SystemMonitor().get_system_metrics(); print(\"SUCCESS\")" 2>/dev/null || echo "FAILED"')

## Health Check Endpoints
- **Server-01**: http://192.168.10.29:9090/health
- **Server-02**: http://192.168.10.28:9092/health

## Log Files Created
### Server-01
$(ssh agent0@192.168.10.29 'ls -la /opt/citadel/logs/ 2>/dev/null | head -10')

### Server-02  
$(ssh agent0@192.168.10.28 'ls -la /opt/citadel/logs/ 2>/dev/null | head -10')

## Management Commands
- Start monitoring: \`/opt/citadel/scripts/monitor.sh start\`
- Check health: \`/opt/citadel/scripts/monitor.sh check\`
- View metrics: \`/opt/citadel/scripts/monitor.sh metrics\`
- Service management: \`sudo systemctl start/stop/status citadel-health\`
EOF

echo "📄 Logging and monitoring report saved to: /tmp/logging-monitoring-report.md"
cat /tmp/logging-monitoring-report.md
```

## Validation
Calculate logging and monitoring readiness:
- Verify logging configuration functional on both servers
- Confirm monitoring system operational
- Test health check API imports successfully
- Validate management scripts functional
- Check systemd services configured
- If all components functional → Task SUCCESS

## Troubleshooting

**Logging Configuration Issues:**
```bash
# Check Python path and imports
ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 -c "import sys; print(sys.path)"'

# Test individual components
ssh agent0@192.168.10.29 'cd /opt/citadel/configs && python3 -c "from base_settings import BaseConfig; print(\"BaseConfig OK\")"'

# Check log directory permissions
ssh agent0@192.168.10.29 'ls -la /opt/citadel/logs/ && touch /opt/citadel/logs/test.log && rm /opt/citadel/logs/test.log'
```

**Monitoring System Issues:**
```bash
# Install missing dependencies
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-admin/bin/activate && pip install psutil GPUtil nvidia-ml-py3'

# Test GPU detection
ssh agent0@192.168.10.29 'python3 -c "import GPUtil; print(GPUtil.getGPUs())"'

# Check NVIDIA drivers
ssh agent0@192.168.10.29 'nvidia-smi'
```

**Health API Issues:**
```bash
# Test FastAPI import
ssh agent0@192.168.10.29 'source /opt/citadel/venvs/citadel-admin/bin/activate && python3 -c "import fastapi, uvicorn; print(\"FastAPI OK\")"'

# Check port availability
ssh agent0@192.168.10.29 'netstat -tuln | grep 9090'

# Test health server manually
ssh agent0@192.168.10.29 'cd /opt/citadel/scripts && source /opt/citadel/venvs/citadel-admin/bin/activate && python3 health_server.py'
```

**Systemd Service Issues:**
```bash
# Check service file syntax
ssh agent0@192.168.10.29 'sudo systemctl cat citadel-health'

# Check service logs
ssh agent0@192.168.10.29 'sudo journalctl -u citadel-health -n 20'

# Fix permissions
ssh agent0@192.168.10.29 'sudo chown -R agent0:agent0 /opt/citadel'
```

## Post-Task Checklist
- [ ] Logging configuration created and functional on both servers
- [ ] Monitoring system operational with system and GPU metrics
- [ ] Health check API created and importable
- [ ] Management scripts created and functional
- [ ] Systemd services configured and enabled
- [ ] Log directories created with proper permissions
- [ ] Cross-server consistency validated

## Result Documentation
Document results in format:
```
Task 1.3 Results:
- hx-llm-server-01: Logging [FUNCTIONAL/FAILED], Monitoring [OPERATIONAL/FAILED], Health API [CREATED/FAILED], Scripts [FUNCTIONAL/FAILED], Service [ENABLED/FAILED]
- hx-llm-server-02: Logging [FUNCTIONAL/FAILED], Monitoring [OPERATIONAL/FAILED], Health API [CREATED/FAILED], Scripts [FUNCTIONAL/FAILED], Service [ENABLED/FAILED]
- Logging and Monitoring System: [OPERATIONAL/NEEDS_ATTENTION]
- Overall: [X/10] components functional ([X]%)
- Status: [SUCCESS/FAILED]
```

**Next Step**: If successful, proceed to Phase 1 completion verification and Phase 2 initialization
