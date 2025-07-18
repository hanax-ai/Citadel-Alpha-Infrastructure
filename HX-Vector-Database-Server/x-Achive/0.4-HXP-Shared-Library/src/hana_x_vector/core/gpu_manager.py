"""
GPU Memory Management

GPU memory allocation and management for dual GPU setup.
Implements Task 2.2: GPU Memory Allocation Strategy.

Author: Citadel AI Team
License: MIT
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import logging
from dataclasses import dataclass
import threading
import time
from contextlib import contextmanager

from hana_x_vector.utils.logging import get_logger
from hana_x_vector.utils.metrics import MetricsCollector, monitor_performance

logger = get_logger(__name__)


class GPUDevice(Enum):
    """GPU device enumeration."""
    GPU_0 = 0
    GPU_1 = 1


@dataclass
class GPUMemoryInfo:
    """GPU memory information."""
    device_id: int
    total_memory_mb: float
    allocated_memory_mb: float
    free_memory_mb: float
    utilization_percent: float
    temperature_celsius: Optional[float] = None
    power_usage_watts: Optional[float] = None


@dataclass
class ModelAllocation:
    """Model allocation information."""
    model_name: str
    device_id: int
    memory_mb: float
    priority: int
    load_time: float
    last_used: float


class GPUMemoryManager:
    """
    GPU Memory Manager
    
    Manages memory allocation across dual NVIDIA GT 1030 GPUs (6GB each).
    Implements intelligent allocation strategy with load balancing and monitoring.
    """
    
    # GPU specifications from PRD
    GPU_SPECS = {
        0: {"name": "NVIDIA GT 1030", "memory_gb": 6, "cuda_cores": 384},
        1: {"name": "NVIDIA GT 1030", "memory_gb": 6, "cuda_cores": 384}
    }
    
    # Model memory requirements (estimated)
    MODEL_MEMORY_REQUIREMENTS = {
        "all-MiniLM-L6-v2": 400,  # MB
        "phi-3-mini": 2800,       # MB
        "e5-small": 500,          # MB
        "bge-base": 1200          # MB
    }
    
    def __init__(self):
        """Initialize GPU memory manager."""
        self.logger = get_logger(__name__)
        self.metrics = MetricsCollector()
        self.allocations: Dict[str, ModelAllocation] = {}
        self.gpu_info: Dict[int, GPUMemoryInfo] = {}
        self.allocation_lock = threading.Lock()
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Initialize GPU information
        self._initialize_gpu_info()
    
    def _initialize_gpu_info(self) -> None:
        """Initialize GPU information."""
        try:
            # Try to import PyTorch for GPU management
            try:
                import torch
                self.torch_available = torch.cuda.is_available()
                self.device_count = torch.cuda.device_count() if self.torch_available else 0
            except ImportError:
                self.torch_available = False
                self.device_count = 0
                self.logger.warning("PyTorch not available, using mock GPU info")
            
            # Initialize GPU info for available devices
            for device_id in range(max(2, self.device_count)):  # Ensure we have info for both GPUs
                self.gpu_info[device_id] = GPUMemoryInfo(
                    device_id=device_id,
                    total_memory_mb=self.GPU_SPECS.get(device_id, {}).get("memory_gb", 6) * 1024,
                    allocated_memory_mb=0.0,
                    free_memory_mb=self.GPU_SPECS.get(device_id, {}).get("memory_gb", 6) * 1024,
                    utilization_percent=0.0
                )
            
            self.logger.info(f"Initialized GPU manager for {len(self.gpu_info)} devices")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GPU info: {e}")
            # Fallback to mock GPU info
            for device_id in range(2):
                self.gpu_info[device_id] = GPUMemoryInfo(
                    device_id=device_id,
                    total_memory_mb=6144,  # 6GB in MB
                    allocated_memory_mb=0.0,
                    free_memory_mb=6144,
                    utilization_percent=0.0
                )
    
    def _update_gpu_info(self) -> None:
        """Update GPU memory information."""
        try:
            if self.torch_available:
                import torch
                
                for device_id in range(self.device_count):
                    if device_id in self.gpu_info:
                        # Get memory info from PyTorch
                        torch.cuda.set_device(device_id)
                        memory_allocated = torch.cuda.memory_allocated(device_id) / (1024 * 1024)  # MB
                        memory_reserved = torch.cuda.memory_reserved(device_id) / (1024 * 1024)  # MB
                        
                        # Update GPU info
                        self.gpu_info[device_id].allocated_memory_mb = memory_allocated
                        self.gpu_info[device_id].free_memory_mb = (
                            self.gpu_info[device_id].total_memory_mb - memory_reserved
                        )
                        self.gpu_info[device_id].utilization_percent = (
                            (memory_allocated / self.gpu_info[device_id].total_memory_mb) * 100
                        )
                        
                        # Try to get additional info
                        try:
                            import pynvml
                            pynvml.nvmlInit()
                            handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
                            
                            # Temperature
                            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                            self.gpu_info[device_id].temperature_celsius = temp
                            
                            # Power usage
                            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000  # Convert to watts
                            self.gpu_info[device_id].power_usage_watts = power
                            
                        except ImportError:
                            # pynvml not available, skip additional metrics
                            pass
                        except Exception as e:
                            self.logger.debug(f"Failed to get additional GPU metrics: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to update GPU info: {e}")
    
    def get_gpu_info(self) -> Dict[int, GPUMemoryInfo]:
        """Get current GPU information."""
        self._update_gpu_info()
        return self.gpu_info.copy()
    
    def get_optimal_device(self, model_name: str, required_memory_mb: float) -> Optional[int]:
        """Get optimal GPU device for model allocation."""
        try:
            self._update_gpu_info()
            
            # Check if model is already allocated
            if model_name in self.allocations:
                return self.allocations[model_name].device_id
            
            # Find device with most free memory that can fit the model
            best_device = None
            best_free_memory = 0
            
            for device_id, gpu_info in self.gpu_info.items():
                if gpu_info.free_memory_mb >= required_memory_mb:
                    if gpu_info.free_memory_mb > best_free_memory:
                        best_free_memory = gpu_info.free_memory_mb
                        best_device = device_id
            
            if best_device is not None:
                self.logger.info(f"Selected GPU {best_device} for {model_name} ({required_memory_mb:.1f} MB)")
                return best_device
            else:
                self.logger.warning(f"No GPU has enough memory for {model_name} ({required_memory_mb:.1f} MB)")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get optimal device: {e}")
            return None
    
    @monitor_performance
    def allocate_model(self, model_name: str, device_id: Optional[int] = None, 
                      priority: int = 1) -> bool:
        """Allocate model to GPU device."""
        try:
            with self.allocation_lock:
                # Check if model is already allocated
                if model_name in self.allocations:
                    self.logger.info(f"Model {model_name} already allocated to GPU {self.allocations[model_name].device_id}")
                    return True
                
                # Get memory requirement
                required_memory = self.MODEL_MEMORY_REQUIREMENTS.get(model_name, 1000)
                
                # Get optimal device if not specified
                if device_id is None:
                    device_id = self.get_optimal_device(model_name, required_memory)
                    if device_id is None:
                        return False
                
                # Check if device has enough memory
                if device_id not in self.gpu_info:
                    self.logger.error(f"Invalid device ID: {device_id}")
                    return False
                
                gpu_info = self.gpu_info[device_id]
                if gpu_info.free_memory_mb < required_memory:
                    self.logger.error(f"Insufficient memory on GPU {device_id}: {gpu_info.free_memory_mb:.1f} MB available, {required_memory:.1f} MB required")
                    return False
                
                # Allocate model
                allocation = ModelAllocation(
                    model_name=model_name,
                    device_id=device_id,
                    memory_mb=required_memory,
                    priority=priority,
                    load_time=time.time(),
                    last_used=time.time()
                )
                
                self.allocations[model_name] = allocation
                
                # Update GPU info
                self.gpu_info[device_id].allocated_memory_mb += required_memory
                self.gpu_info[device_id].free_memory_mb -= required_memory
                
                self.logger.info(f"Allocated {model_name} to GPU {device_id} ({required_memory:.1f} MB)")
                
                # Update metrics
                self.metrics.increment_counter("gpu_allocations_total")
                self.metrics.set_gauge("gpu_allocated_memory_mb", self.gpu_info[device_id].allocated_memory_mb, {"device": str(device_id)})
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to allocate model {model_name}: {e}")
            return False
    
    @monitor_performance
    def deallocate_model(self, model_name: str) -> bool:
        """Deallocate model from GPU."""
        try:
            with self.allocation_lock:
                if model_name not in self.allocations:
                    self.logger.warning(f"Model {model_name} not allocated")
                    return False
                
                allocation = self.allocations[model_name]
                device_id = allocation.device_id
                memory_mb = allocation.memory_mb
                
                # Update GPU info
                self.gpu_info[device_id].allocated_memory_mb -= memory_mb
                self.gpu_info[device_id].free_memory_mb += memory_mb
                
                # Remove allocation
                del self.allocations[model_name]
                
                self.logger.info(f"Deallocated {model_name} from GPU {device_id} ({memory_mb:.1f} MB)")
                
                # Update metrics
                self.metrics.increment_counter("gpu_deallocations_total")
                self.metrics.set_gauge("gpu_allocated_memory_mb", self.gpu_info[device_id].allocated_memory_mb, {"device": str(device_id)})
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to deallocate model {model_name}: {e}")
            return False
    
    def get_allocations(self) -> Dict[str, ModelAllocation]:
        """Get current model allocations."""
        return self.allocations.copy()
    
    def get_allocation_summary(self) -> Dict[str, Any]:
        """Get allocation summary."""
        try:
            self._update_gpu_info()
            
            summary = {
                "total_models": len(self.allocations),
                "gpu_utilization": {},
                "allocations": []
            }
            
            # GPU utilization
            for device_id, gpu_info in self.gpu_info.items():
                summary["gpu_utilization"][f"gpu_{device_id}"] = {
                    "total_memory_mb": gpu_info.total_memory_mb,
                    "allocated_memory_mb": gpu_info.allocated_memory_mb,
                    "free_memory_mb": gpu_info.free_memory_mb,
                    "utilization_percent": gpu_info.utilization_percent,
                    "temperature_celsius": gpu_info.temperature_celsius,
                    "power_usage_watts": gpu_info.power_usage_watts
                }
            
            # Allocations
            for model_name, allocation in self.allocations.items():
                summary["allocations"].append({
                    "model_name": model_name,
                    "device_id": allocation.device_id,
                    "memory_mb": allocation.memory_mb,
                    "priority": allocation.priority,
                    "load_time": allocation.load_time,
                    "last_used": allocation.last_used
                })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get allocation summary: {e}")
            return {"error": str(e)}
    
    @contextmanager
    def gpu_context(self, device_id: int):
        """Context manager for GPU device selection."""
        try:
            if self.torch_available:
                import torch
                current_device = torch.cuda.current_device()
                torch.cuda.set_device(device_id)
                yield device_id
                torch.cuda.set_device(current_device)
            else:
                yield device_id
        except Exception as e:
            self.logger.error(f"GPU context error: {e}")
            yield device_id
    
    def optimize_allocations(self) -> Dict[str, Any]:
        """Optimize model allocations across GPUs."""
        try:
            self.logger.info("Starting allocation optimization")
            
            # Get current allocations
            current_allocations = list(self.allocations.items())
            
            # Clear all allocations
            for model_name in list(self.allocations.keys()):
                self.deallocate_model(model_name)
            
            # Sort models by memory requirement (largest first)
            sorted_models = sorted(
                current_allocations,
                key=lambda x: x[1].memory_mb,
                reverse=True
            )
            
            # Reallocate models optimally
            optimization_results = {
                "reallocated_models": [],
                "failed_allocations": [],
                "memory_saved_mb": 0
            }
            
            for model_name, old_allocation in sorted_models:
                optimal_device = self.get_optimal_device(model_name, old_allocation.memory_mb)
                
                if optimal_device is not None:
                    success = self.allocate_model(
                        model_name, 
                        optimal_device, 
                        old_allocation.priority
                    )
                    
                    if success:
                        optimization_results["reallocated_models"].append({
                            "model": model_name,
                            "old_device": old_allocation.device_id,
                            "new_device": optimal_device
                        })
                    else:
                        optimization_results["failed_allocations"].append(model_name)
                else:
                    optimization_results["failed_allocations"].append(model_name)
            
            self.logger.info(f"Optimization complete: {len(optimization_results['reallocated_models'])} models reallocated")
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Failed to optimize allocations: {e}")
            return {"error": str(e)}
    
    async def start_monitoring(self, interval_seconds: int = 30) -> None:
        """Start GPU monitoring."""
        try:
            if self.monitoring_active:
                self.logger.warning("Monitoring already active")
                return
            
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop(interval_seconds))
            
            self.logger.info(f"Started GPU monitoring with {interval_seconds}s interval")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
    
    async def stop_monitoring(self) -> None:
        """Stop GPU monitoring."""
        try:
            if not self.monitoring_active:
                return
            
            self.monitoring_active = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("Stopped GPU monitoring")
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
    
    async def _monitoring_loop(self, interval_seconds: int) -> None:
        """GPU monitoring loop."""
        try:
            while self.monitoring_active:
                # Update GPU info
                self._update_gpu_info()
                
                # Update metrics
                for device_id, gpu_info in self.gpu_info.items():
                    device_label = {"device": str(device_id)}
                    
                    self.metrics.set_gauge("gpu_memory_total_mb", gpu_info.total_memory_mb, device_label)
                    self.metrics.set_gauge("gpu_memory_allocated_mb", gpu_info.allocated_memory_mb, device_label)
                    self.metrics.set_gauge("gpu_memory_free_mb", gpu_info.free_memory_mb, device_label)
                    self.metrics.set_gauge("gpu_utilization_percent", gpu_info.utilization_percent, device_label)
                    
                    if gpu_info.temperature_celsius is not None:
                        self.metrics.set_gauge("gpu_temperature_celsius", gpu_info.temperature_celsius, device_label)
                    
                    if gpu_info.power_usage_watts is not None:
                        self.metrics.set_gauge("gpu_power_usage_watts", gpu_info.power_usage_watts, device_label)
                
                # Check for memory pressure
                for device_id, gpu_info in self.gpu_info.items():
                    if gpu_info.utilization_percent > 90:
                        self.logger.warning(f"High memory usage on GPU {device_id}: {gpu_info.utilization_percent:.1f}%")
                
                # Wait for next iteration
                await asyncio.sleep(interval_seconds)
                
        except asyncio.CancelledError:
            self.logger.info("Monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Monitoring loop error: {e}")
    
    def clear_all_allocations(self) -> None:
        """Clear all model allocations."""
        try:
            with self.allocation_lock:
                model_names = list(self.allocations.keys())
                for model_name in model_names:
                    self.deallocate_model(model_name)
                
                self.logger.info("Cleared all allocations")
                
        except Exception as e:
            self.logger.error(f"Failed to clear allocations: {e}")
    
    def get_model_device(self, model_name: str) -> Optional[int]:
        """Get device ID for allocated model."""
        allocation = self.allocations.get(model_name)
        return allocation.device_id if allocation else None
    
    def update_model_usage(self, model_name: str) -> None:
        """Update model last used timestamp."""
        if model_name in self.allocations:
            self.allocations[model_name].last_used = time.time()


# Global GPU manager instance
_gpu_manager = None


def get_gpu_manager() -> GPUMemoryManager:
    """Get global GPU manager instance."""
    global _gpu_manager
    if _gpu_manager is None:
        _gpu_manager = GPUMemoryManager()
    return _gpu_manager
