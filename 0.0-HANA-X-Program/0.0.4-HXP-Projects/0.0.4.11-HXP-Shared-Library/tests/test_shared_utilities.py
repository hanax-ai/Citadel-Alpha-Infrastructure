#!/usr/bin/env python3
"""
Comprehensive test suite for HANA-X shared utilities.

This test suite demonstrates and validates all the new shared utilities
that were refactored from the Enterprise and LoB server projects.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.base_config import (
    BaseConfigManager, 
    create_server_config, 
    create_model_config, 
    create_performance_targets
)
from monitoring.performance_monitor import PerformanceMonitor, PerformanceMetrics
from logging.hana_logger import create_hana_logger
from testing.base_test_case import (
    BaseHanaXTestCase, 
    create_mock_model_response, 
    create_mock_health_response
)
from common.utils import (
    ensure_directory,
    get_system_info,
    validate_port,
    check_gpu_availability
)


class TestSharedUtilities(unittest.TestCase):
    """Test suite for shared utilities."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.server_id = "test-server-01"
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_server_config_creation(self):
        """Test server configuration creation."""
        config = create_server_config(
            name="hx-llm-server-01",
            ip="192.168.10.29",
            port=8000,
            server_id="enterprise-server-01",
            description="Enterprise LLM Server"
        )
        
        self.assertEqual(config.name, "hx-llm-server-01")
        self.assertEqual(config.ip, "192.168.10.29")
        self.assertEqual(config.port, 8000)
        self.assertEqual(config.server_id, "enterprise-server-01")
        self.assertEqual(config.description, "Enterprise LLM Server")
    
    def test_model_config_creation(self):
        """Test model configuration creation."""
        config = create_model_config(
            model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
            model_type="mixtral",
            tensor_parallel_size=2,
            max_model_len=32768,
            specialization="enterprise"
        )
        
        self.assertEqual(config.model_name, "mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.assertEqual(config.model_type, "mixtral")
        self.assertEqual(config.tensor_parallel_size, 2)
        self.assertEqual(config.max_model_len, 32768)
        self.assertEqual(config.specialization, "enterprise")
    
    def test_performance_targets_creation(self):
        """Test performance targets creation."""
        targets = create_performance_targets(
            max_latency_ms=1500,
            min_throughput_rps=15,
            min_gpu_utilization=85,
            max_memory_utilization=88,
            availability_target=99.9
        )
        
        self.assertEqual(targets.max_latency_ms, 1500)
        self.assertEqual(targets.min_throughput_rps, 15)
        self.assertEqual(targets.min_gpu_utilization, 85)
        self.assertEqual(targets.max_memory_utilization, 88)
        self.assertEqual(targets.availability_target, 99.9)
    
    def test_performance_monitor(self):
        """Test performance monitoring functionality."""
        monitor = PerformanceMonitor(
            server_id=self.server_id,
            history_size=100
        )
        
        # Record some requests
        monitor.record_request(latency_ms=1200.5, success=True, endpoint="/v1/completions")
        monitor.record_request(latency_ms=1350.2, success=True, endpoint="/v1/completions")
        monitor.record_request(latency_ms=2100.8, success=False, endpoint="/v1/completions")
        
        # Get metrics
        metrics = monitor.get_metrics()
        
        self.assertEqual(metrics['requests_count'], 3)
        self.assertEqual(metrics['success_count'], 2)
        self.assertEqual(metrics['error_count'], 1)
        self.assertAlmostEqual(metrics['average_latency_ms'], 1550.5, places=1)
        self.assertAlmostEqual(metrics['success_rate'], 66.7, places=1)
        self.assertAlmostEqual(metrics['error_rate'], 33.3, places=1)
    
    def test_performance_monitor_thresholds(self):
        """Test performance monitor threshold alerting."""
        monitor = PerformanceMonitor(server_id=self.server_id)
        
        # Set threshold
        monitor.set_threshold("average_latency_ms", 1500.0)
        
        # Record requests that should trigger alert
        monitor.record_request(latency_ms=2000.0, success=True)
        monitor.record_request(latency_ms=2500.0, success=True)
        
        # Check for alerts
        alerts = monitor.get_alerts()
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0]['metric_name'], 'average_latency_ms')
        self.assertGreater(alerts[0]['current_value'], 1500.0)
    
    def test_hana_logger_creation(self):
        """Test HANA logger creation."""
        logger = create_hana_logger(
            server_id=self.server_id,
            server_type="test",
            log_dir=self.temp_dir,
            log_level="INFO",
            json_format=False
        )
        
        self.assertEqual(logger.server_id, self.server_id)
        self.assertEqual(logger.log_level, 20)  # INFO level
        self.assertFalse(logger.json_format)
        
        # Test logger functionality
        component_logger = logger.get_logger("test_component")
        self.assertIsNotNone(component_logger)
    
    def test_mock_model_response(self):
        """Test mock model response creation."""
        response = create_mock_model_response(
            model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
            response_text="This is a test response.",
            server_id=self.server_id
        )
        
        self.assertEqual(response['model'], "mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.assertEqual(response['choices'][0]['text'], "This is a test response.")
        self.assertIn(self.server_id, response['id'])
        self.assertIn('usage', response)
    
    def test_mock_health_response(self):
        """Test mock health response creation."""
        response = create_mock_health_response(
            server_id=self.server_id,
            model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
            additional_features={"test_feature": True}
        )
        
        self.assertEqual(response['server_id'], self.server_id)
        self.assertEqual(response['model'], "mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.assertEqual(response['status'], "healthy")
        self.assertTrue(response['test_feature'])
    
    def test_common_utilities(self):
        """Test common utility functions."""
        # Test directory creation
        test_dir = self.temp_dir / "test_subdir"
        result = ensure_directory(test_dir)
        self.assertTrue(result.exists())
        self.assertTrue(result.is_dir())
        
        # Test system info
        system_info = get_system_info()
        required_keys = ["hostname", "platform", "architecture", "system"]
        for key in required_keys:
            self.assertIn(key, system_info)
            self.assertIsInstance(system_info[key], str)
        
        # Test port validation
        # Test a high port that should be available
        self.assertTrue(validate_port(58392, "localhost"))
    
    @patch('subprocess.run')
    def test_gpu_availability_check(self, mock_run):
        """Test GPU availability check."""
        # Mock successful nvidia-smi output
        mock_run.return_value = Mock(
            returncode=0,
            stdout="2\n2\n",
            stderr=""
        )
        
        gpu_info = check_gpu_availability()
        
        self.assertTrue(gpu_info['available'])
        self.assertEqual(gpu_info['count'], 2)
        
        # Mock failed nvidia-smi (no GPUs)
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="nvidia-smi: command not found"
        )
        
        gpu_info = check_gpu_availability()
        self.assertFalse(gpu_info['available'])
        self.assertEqual(gpu_info['count'], 0)


class TestBaseHanaXTestCase(BaseHanaXTestCase):
    """Test case demonstrating BaseHanaXTestCase usage."""
    
    def get_server_type(self):
        """Get server type for testing."""
        return "test"
    
    def get_server_config(self):
        """Get server configuration for testing."""
        return {
            'name': 'hx-test-server',
            'ip': '127.0.0.1',
            'port': 8000,
            'server_id': 'test-server-01'
        }
    
    def get_performance_targets(self):
        """Get performance targets for testing."""
        return {
            'max_latency_ms': 2000,
            'min_throughput_rps': 10,
            'min_gpu_utilization': 80,
            'max_memory_utilization': 90,
            'availability_target': 99.5
        }
    
    def get_model_storage_type(self):
        """Get model storage type for testing."""
        return "test"
    
    def get_base_config(self, config_type):
        """Get base configuration for testing."""
        return {
            'server': {
                'host': '0.0.0.0',
                'port': 8000,
                'server_id': 'test-server-01'
            },
            'engine': {
                'model': 'test-model',
                'tensor_parallel_size': 1
            }
        }
    
    def get_model_config(self, model_type):
        """Get model configuration for testing."""
        return {
            'model_type': model_type,
            'vocab_size': 32000,
            'hidden_size': 4096,
            'max_position_embeddings': 2048
        }
    
    def get_expected_latency(self):
        """Get expected latency for testing."""
        return 1.5
    
    def get_primary_model(self):
        """Get primary model for testing."""
        return "test-model"
    
    def get_server_specific_response_data(self):
        """Get server-specific response data for testing."""
        return {
            'test_features': {
                'feature1': True,
                'feature2': False
            }
        }
    
    def test_base_functionality(self):
        """Test basic functionality of the base test case."""
        # Test configuration creation
        config = self.create_config('server')
        self.assertIn('server', config)
        self.assertIn('engine', config)
        
        # Test model file creation
        model_dir = self.models_dir / "test-model"
        created_dir = self.create_model_files("test", model_dir)
        self.assertTrue(created_dir.exists())
        self.assertTrue((created_dir / "config.json").exists())
        
        # Test performance assertion
        self.assert_performance_targets(1800.0, 12.0)  # Should pass
        
        # Test model response quality
        self.assert_model_response_quality("This is a good quality response.")
    
    def test_mock_functionality(self):
        """Test mock functionality."""
        # Test GPU mocking
        mock_gpu = self.mock_gpu_environment()
        self.assertIsNotNone(mock_gpu)
        
        # Test API response mocking
        mock_api = self.mock_api_response()
        self.assertIsNotNone(mock_api)


class TestConfigurationManager(unittest.TestCase):
    """Test configuration manager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = TestConfigManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_loading(self):
        """Test configuration loading."""
        config = self.config_manager.load_config('test_config')
        self.assertIsNotNone(config)
        self.assertIn('server', config)
    
    def test_config_saving(self):
        """Test configuration saving."""
        config = {'test': 'value'}
        self.config_manager.save_config('test_config', config)
        
        # Verify file was created
        config_file = self.temp_dir / 'test_config_config.json'
        self.assertTrue(config_file.exists())
        
        # Verify content
        with open(config_file, 'r') as f:
            saved_config = json.load(f)
        self.assertEqual(saved_config, config)
    
    def test_config_validation(self):
        """Test configuration validation."""
        valid_config = {
            'server': {'host': '0.0.0.0', 'port': 8000},
            'engine': {'model': 'test-model'}
        }
        self.assertTrue(self.config_manager.validate_config('api_server', valid_config))
        
        invalid_config = {'invalid': 'config'}
        self.assertFalse(self.config_manager.validate_config('api_server', invalid_config))
    
    def test_config_merge(self):
        """Test configuration merging."""
        base_config = {
            'server': {'host': '0.0.0.0', 'port': 8000},
            'engine': {'model': 'base-model'}
        }
        
        overrides = {
            'server': {'port': 8001},
            'engine': {'model': 'override-model'}
        }
        
        merged = self.config_manager.merge_configs(base_config, overrides)
        
        self.assertEqual(merged['server']['host'], '0.0.0.0')
        self.assertEqual(merged['server']['port'], 8001)
        self.assertEqual(merged['engine']['model'], 'override-model')


class TestConfigManager(BaseConfigManager):
    """Test implementation of BaseConfigManager."""
    
    def get_default_config(self, config_type):
        """Get default configuration for testing."""
        defaults = {
            'api_server': {
                'server': {
                    'host': '0.0.0.0',
                    'port': 8000,
                    'server_id': 'test-server'
                },
                'engine': {
                    'model': 'test-model',
                    'tensor_parallel_size': 1
                }
            },
            'test_config': {
                'server': {
                    'host': '127.0.0.1',
                    'port': 8000
                }
            }
        }
        return defaults.get(config_type, {})
    
    def _validate_config_specific(self, config_type, config):
        """Validate specific configuration types."""
        if config_type == 'api_server':
            return 'server' in config and 'engine' in config
        return True


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
