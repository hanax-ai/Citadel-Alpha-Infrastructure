"""
Base test case utilities for HANA-X infrastructure projects.

This module provides common test case patterns and utilities that can be
reused across Enterprise and LoB server test suites.
"""

import unittest
import tempfile
import shutil
import logging
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from unittest.mock import Mock, patch, MagicMock
from abc import ABC, abstractmethod


class BaseHanaXTestCase(unittest.TestCase, ABC):
    """
    Base test case for HANA-X infrastructure testing.
    
    Provides common setup, teardown, and utility methods following
    FASTT principles with configurable server-specific features.
    """
    
    def setUp(self) -> None:
        """Set up test environment with isolated temporary directories."""
        super().setUp()
        
        # Create isolated test environment
        self.test_dir = Path(tempfile.mkdtemp(prefix=f"{self.get_server_type()}_vllm_test_"))
        self.config_dir = self.test_dir / "configs"
        self.logs_dir = self.test_dir / "logs" / self.get_server_type()
        self.models_dir = self.test_dir / "models" / self.get_model_storage_type()
        self.backup_dir = self.test_dir / "backup" / self.get_server_type()
        
        # Create additional server-specific directories
        additional_dirs = self.get_additional_directories()
        for dir_path in additional_dirs:
            (self.test_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create required directories
        base_dirs = [self.config_dir, self.logs_dir, self.models_dir, self.backup_dir]
        for directory in base_dirs:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger(f"{self.get_server_type()}_test_{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)
        
        # Server configuration
        self.server_config = self.get_server_config()
        
        # Track created resources for cleanup
        self.created_resources: List[Path] = []
        self.mock_patches: List[Any] = []
        
        # Performance targets
        self.performance_targets = self.get_performance_targets()
    
    def tearDown(self) -> None:
        """Clean up test environment and resources."""
        # Stop all mock patches
        for patch_obj in self.mock_patches:
            if hasattr(patch_obj, 'stop'):
                try:
                    patch_obj.stop()
                except RuntimeError:
                    # Patch was already stopped
                    pass
        
        # Clean up temporary directories
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)
        
        super().tearDown()
    
    @abstractmethod
    def get_server_type(self) -> str:
        """Get the server type identifier (e.g., 'enterprise', 'lob')."""
        pass
    
    @abstractmethod
    def get_server_config(self) -> Dict[str, Any]:
        """Get server-specific configuration."""
        pass
    
    @abstractmethod
    def get_performance_targets(self) -> Dict[str, Any]:
        """Get server-specific performance targets."""
        pass
    
    @abstractmethod
    def get_model_storage_type(self) -> str:
        """Get model storage type (e.g., 'production', 'coding')."""
        pass
    
    def get_additional_directories(self) -> List[str]:
        """Get additional directories to create (override in subclasses)."""
        return []
    
    def create_config(self, config_type: str, **overrides) -> Dict[str, Any]:
        """
        Create server-specific configuration for testing.
        
        Args:
            config_type: Type of configuration to create
            **overrides: Configuration values to override
            
        Returns:
            Configuration dictionary
        """
        base_config = self.get_base_config(config_type)
        merged_config = base_config.copy()
        self._deep_update(merged_config, overrides)
        return merged_config
    
    @abstractmethod
    def get_base_config(self, config_type: str) -> Dict[str, Any]:
        """Get base configuration for the specified type."""
        pass
    
    def create_model_files(self, model_type: str, model_dir: Path) -> Path:
        """
        Create mock model files for testing.
        
        Args:
            model_type: Type of model to create
            model_dir: Directory to create model files in
            
        Returns:
            Path to created model directory
        """
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Get model-specific configuration
        model_config = self.get_model_config(model_type)
        
        # Create config.json
        (model_dir / "config.json").write_text(json.dumps(model_config, indent=2))
        
        # Create model files
        (model_dir / "pytorch_model.bin").write_text(f"mock_{model_type}_weights")
        (model_dir / "tokenizer.json").write_text(json.dumps({
            "version": "1.0",
            "model_max_length": model_config.get("max_position_embeddings", 2048),
            "tokenizer_class": "LlamaTokenizer"
        }))
        
        self.created_resources.append(model_dir)
        return model_dir
    
    @abstractmethod
    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """Get model configuration for the specified model type."""
        pass
    
    def mock_gpu_environment(self) -> Mock:
        """Create mock for GPU environment."""
        mock_nvidia_smi = self.mock_subprocess_run(
            return_code=0,
            stdout=f"GPU 0: NVIDIA RTX 4070 Ti SUPER (UUID: GPU-{self.get_server_type()}-01)\\n"
                   f"GPU 1: NVIDIA RTX 4070 Ti SUPER (UUID: GPU-{self.get_server_type()}-02)\\n"
                   "Driver Version: 570.57.01    CUDA Version: 12.4"
        )
        
        mock_torch_cuda = patch('torch.cuda.is_available', return_value=True)
        mock_torch_cuda.start()
        self.mock_patches.append(mock_torch_cuda)
        
        mock_device_count = patch('torch.cuda.device_count', return_value=2)
        mock_device_count.start()
        self.mock_patches.append(mock_device_count)
        
        return mock_nvidia_smi
    
    def mock_api_response(self, status_code: int = 200, response_data: Optional[Dict] = None) -> Mock:
        """Create mock for API responses."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.elapsed.total_seconds.return_value = self.get_expected_latency()
        
        default_response = {
            "server_id": self.server_config['server_id'],
            "model": self.get_primary_model(),
            "timestamp": int(time.time()),
        }
        
        # Add server-specific features
        default_response.update(self.get_server_specific_response_data())
        
        if response_data:
            default_response.update(response_data)
        
        mock_response.json.return_value = default_response
        
        patcher = patch('requests.get', return_value=mock_response)
        mock_obj = patcher.start()
        self.mock_patches.append(patcher)
        return mock_obj
    
    @abstractmethod
    def get_expected_latency(self) -> float:
        """Get expected latency for the server type."""
        pass
    
    @abstractmethod
    def get_primary_model(self) -> str:
        """Get primary model name for the server type."""
        pass
    
    @abstractmethod
    def get_server_specific_response_data(self) -> Dict[str, Any]:
        """Get server-specific response data."""
        pass
    
    def assert_performance_targets(self, latency_ms: float, throughput_rps: float) -> None:
        """Assert that performance meets targets."""
        targets = self.performance_targets
        
        self.assertLessEqual(
            latency_ms,
            targets['max_latency_ms'],
            f"Latency {latency_ms}ms exceeds target {targets['max_latency_ms']}ms"
        )
        
        self.assertGreaterEqual(
            throughput_rps,
            targets['min_throughput_rps'],
            f"Throughput {throughput_rps} RPS below target {targets['min_throughput_rps']} RPS"
        )
    
    def assert_model_response_quality(self, model_response: str, min_length: int = 10) -> None:
        """Assert that model response meets quality standards."""
        self.assertIsNotNone(model_response, "Model response cannot be None")
        self.assertGreater(
            len(model_response.strip()),
            min_length,
            f"Model response too short: {len(model_response)} chars"
        )
        
        # Server-specific quality checks
        self.perform_server_specific_quality_checks(model_response)
    
    def perform_server_specific_quality_checks(self, model_response: str) -> None:
        """Perform server-specific quality checks (override in subclasses)."""
        pass
    
    def create_test_file(self, file_path: Path, content: str = "") -> Path:
        """Create a test file with specified content."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        self.created_resources.append(file_path)
        return file_path
    
    def mock_subprocess_run(self, return_code: int = 0, stdout: str = "", stderr: str = "") -> Mock:
        """Create mock for subprocess.run with specified outputs."""
        mock_result = Mock()
        mock_result.returncode = return_code
        mock_result.stdout = stdout
        mock_result.stderr = stderr
        
        patcher = patch('subprocess.run', return_value=mock_result)
        mock_obj = patcher.start()
        self.mock_patches.append(patcher)
        return mock_obj
    
    @staticmethod
    def _deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """Recursively update nested dictionary."""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                BaseHanaXTestCase._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


class BaseHanaXIntegrationTestCase(BaseHanaXTestCase):
    """
    Base class for integration tests requiring more complex setup.
    """
    
    def setUp(self) -> None:
        """Set up integration test environment."""
        super().setUp()
        
        # API configuration
        self.api_base_url = f"http://{self.server_config['ip']}:{self.server_config['port']}"
        self.test_timeout = self.get_test_timeout()
        
        # Performance monitoring
        self.performance_metrics = {
            'request_count': 0,
            'total_latency': 0.0,
            'error_count': 0
        }
        
        # Mock dependencies by default
        self.setup_mocks()
    
    @abstractmethod
    def get_test_timeout(self) -> int:
        """Get test timeout for the server type."""
        pass
    
    def setup_mocks(self) -> None:
        """Set up mocks for dependencies."""
        # Mock GPU environment
        self.mock_gpu_environment()
        
        # Mock monitoring
        self.mock_monitoring_systems()
        
        # Server-specific mocks
        self.setup_server_specific_mocks()
    
    def mock_monitoring_systems(self) -> None:
        """Mock monitoring systems."""
        # Mock Prometheus metrics
        mock_counter = Mock()
        mock_histogram = Mock()
        mock_gauge = Mock()
        
        prometheus_patcher = patch('prometheus_client.Counter', return_value=mock_counter)
        histogram_patcher = patch('prometheus_client.Histogram', return_value=mock_histogram)
        gauge_patcher = patch('prometheus_client.Gauge', return_value=mock_gauge)
        
        prometheus_patcher.start()
        histogram_patcher.start()
        gauge_patcher.start()
        
        self.mock_patches.extend([prometheus_patcher, histogram_patcher, gauge_patcher])
    
    @abstractmethod
    def setup_server_specific_mocks(self) -> None:
        """Set up server-specific mocks."""
        pass


class BaseHanaXSystemTestCase(BaseHanaXIntegrationTestCase):
    """
    Base class for system tests requiring full environment setup.
    """
    
    def setUp(self) -> None:
        """Set up system test environment."""
        super().setUp()
        
        # System test configuration
        self.system_timeout = self.get_system_timeout()
        self.load_test_scenarios = self.get_load_test_scenarios()
        
        # Monitoring configuration
        self.monitoring_config = self.get_monitoring_config()
    
    @abstractmethod
    def get_system_timeout(self) -> int:
        """Get system test timeout."""
        pass
    
    @abstractmethod
    def get_load_test_scenarios(self) -> List[Dict[str, Any]]:
        """Get load test scenarios."""
        pass
    
    @abstractmethod
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        pass
    
    def simulate_load(self, concurrent_users: int = 10, duration_seconds: int = 60) -> Dict[str, Any]:
        """Simulate load testing scenario."""
        return {
            'concurrent_users': concurrent_users,
            'duration_seconds': duration_seconds,
            'total_requests': concurrent_users * (duration_seconds // self.get_request_interval()),
            'success_rate': self.get_expected_success_rate(),
            'average_latency_ms': self.get_expected_latency(),
            'p95_latency_ms': self.get_expected_latency() * 1.5
        }
    
    @abstractmethod
    def get_request_interval(self) -> int:
        """Get request interval for load testing."""
        pass
    
    @abstractmethod
    def get_expected_success_rate(self) -> float:
        """Get expected success rate for load testing."""
        pass


def create_mock_model_response(
    model_name: str,
    response_text: str,
    server_id: str,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a mock model response for testing.
    
    Args:
        model_name: Name of the model
        response_text: Response text to return
        server_id: Server identifier
        additional_metadata: Additional metadata to include
        
    Returns:
        Mock response dictionary
    """
    response = {
        "id": f"cmpl-{server_id}-{int(time.time())}",
        "object": "text_completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [
            {
                "text": response_text,
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(response_text.split()) // 4,  # Rough estimate
            "completion_tokens": len(response_text.split()),
            "total_tokens": len(response_text.split()) + (len(response_text.split()) // 4)
        }
    }
    
    if additional_metadata:
        response.update(additional_metadata)
    
    return response


def create_mock_health_response(
    server_id: str,
    model_name: str,
    additional_features: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a mock health response for testing.
    
    Args:
        server_id: Server identifier
        model_name: Model name
        additional_features: Additional features to include
        
    Returns:
        Mock health response dictionary
    """
    response = {
        "status": "healthy",
        "server_id": server_id,
        "model": model_name,
        "gpu_count": 2,
        "memory_usage": "80%",
        "uptime_seconds": 3600,
        "requests_served": 1000
    }
    
    if additional_features:
        response.update(additional_features)
    
    return response
