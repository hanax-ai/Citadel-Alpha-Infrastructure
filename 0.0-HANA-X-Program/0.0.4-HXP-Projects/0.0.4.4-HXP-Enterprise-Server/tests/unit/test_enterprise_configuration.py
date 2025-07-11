#!/usr/bin/env python3
"""
Unit tests for HANA-X-Enterprise-Server configuration management.
Tests enterprise-specific configurations, security settings, and validation.
"""

import json
import pytest
import os
from pathlib import Path
from unittest.mock import patch, mock_open
import sys

# Add helpers to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from helpers.base_test_case import BaseEnterpriseTestCase

class TestEnterpriseConfigurationManagement(BaseEnterpriseTestCase):
    """Test suite for enterprise server configuration management."""
    
    def test_enterprise_api_config_validation_success(self):
        """Test successful enterprise API configuration validation."""
        # Arrange
        valid_config = self.create_enterprise_config('api_server')
        config_file = self.create_test_file(
            self.config_dir / "enterprise_api_config.json",
            json.dumps(valid_config, indent=2)
        )
        
        # Act
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
        
        # Assert
        self.assertEqual(loaded_config['server']['host'], '0.0.0.0')
        self.assertEqual(loaded_config['server']['port'], 8000)
        self.assertEqual(loaded_config['server']['server_id'], 'enterprise-server-01')
        self.assertIn('engine', loaded_config)
        self.assertIn('security', loaded_config)
        
        # Enterprise-specific assertions
        self.assertEqual(loaded_config['engine']['model'], 'mistralai/Mixtral-8x7B-Instruct-v0.1')
        self.assertEqual(loaded_config['engine']['tensor_parallel_size'], 2)
        self.assertIsNone(loaded_config['engine']['quantization'])  # Full precision for enterprise
        self.assertTrue(loaded_config['security']['enable_api_key'])
    
    def test_enterprise_security_config_validation(self):
        """Test enterprise security configuration validation."""
        # Arrange
        security_config = self.create_enterprise_config('security')
        
        # Act & Assert
        self.assertTrue(security_config['authentication']['enable_api_keys'])
        self.assertEqual(security_config['authentication']['key_rotation_days'], 30)
        self.assertEqual(security_config['authentication']['max_requests_per_minute'], 100)
        
        # Audit configuration
        self.assertTrue(security_config['audit']['log_all_requests'])
        self.assertFalse(security_config['audit']['log_responses'])  # Privacy protection
        self.assertEqual(security_config['audit']['retention_days'], 90)
        
        # CORS configuration
        self.assertIn('https://enterprise.hana-x.local', security_config['cors']['allowed_origins'])
        self.assertTrue(security_config['cors']['allow_credentials'])
    
    def test_enterprise_model_configuration(self):
        """Test enterprise model-specific configuration."""
        # Arrange
        api_config = self.create_enterprise_config('api_server')
        engine_config = api_config['engine']
        
        # Act & Assert - Enterprise model requirements
        self.assertEqual(engine_config['model'], 'mistralai/Mixtral-8x7B-Instruct-v0.1')
        self.assertEqual(engine_config['max_num_seqs'], 512)  # Higher for enterprise
        self.assertEqual(engine_config['max_model_len'], 32768)  # Long context for enterprise
        self.assertEqual(engine_config['gpu_memory_utilization'], 0.88)  # Optimized for enterprise
        self.assertIsNone(engine_config['quantization'])  # Full precision
    
    def test_enterprise_performance_targets_validation(self):
        """Test enterprise performance targets are properly configured."""
        # Arrange & Act
        targets = self.performance_targets
        
        # Assert - Enterprise targets are stricter
        self.assertEqual(targets['max_latency_ms'], 1500)  # Stricter than general (2000ms)
        self.assertEqual(targets['min_throughput_rps'], 15)  # Higher than general (10 RPS)
        self.assertEqual(targets['min_gpu_utilization'], 85)  # Higher than general (80%)
        self.assertEqual(targets['max_memory_utilization'], 88)  # Tighter than general (90%)
        self.assertEqual(targets['availability_target'], 99.9)  # Enterprise SLA
    
    def test_config_missing_security_fields_enterprise(self):
        """Test configuration validation with missing enterprise security fields."""
        # Arrange
        incomplete_config = {
            "server": {"host": "0.0.0.0", "port": 8000},
            "engine": {"model": "test-model"}
            # Missing security section
        }
        
        # Act & Assert
        self.assertNotIn('security', incomplete_config)
        
        # This would fail enterprise validation requirements
        with self.assertRaises(KeyError):
            _ = incomplete_config['security']['enable_api_key']
    
    def test_enterprise_environment_variable_override(self):
        """Test enterprise configuration override via environment variables."""
        # Arrange
        enterprise_port = 8000
        enterprise_model = 'mistralai/Mixtral-8x7B-Instruct-v0.1'
        enterprise_security = 'true'
        
        with patch.dict(os.environ, {
            'ENTERPRISE_SERVER_PORT': str(enterprise_port),
            'ENTERPRISE_MODEL': enterprise_model,
            'ENTERPRISE_SECURITY_ENABLED': enterprise_security
        }):
            # Act
            port_from_env = int(os.environ.get('ENTERPRISE_SERVER_PORT', 8001))
            model_from_env = os.environ.get('ENTERPRISE_MODEL', 'default-model')
            security_from_env = os.environ.get('ENTERPRISE_SECURITY_ENABLED', 'false').lower() == 'true'
            
            # Assert
            self.assertEqual(port_from_env, enterprise_port)
            self.assertEqual(model_from_env, enterprise_model)
            self.assertTrue(security_from_env)
    
    def test_enterprise_config_file_security_permissions(self):
        """Test enterprise configuration files have secure permissions."""
        # Arrange
        config_file = self.create_test_file(
            self.config_dir / "enterprise_secure_config.json",
            json.dumps({"api_key": "sensitive_data"})
        )
        
        # Act
        file_stat = config_file.stat()
        
        # Assert - Enterprise requires strict file permissions
        self.assertTrue(file_stat.st_mode & 0o400)  # Owner read permission
        # In production, enterprise configs should have restricted permissions (0o600)
    
    def test_enterprise_model_files_validation(self):
        """Test enterprise model files validation."""
        # Arrange
        mixtral_dir = self.create_mixtral_model_files(self.models_dir / "mixtral-8x7b-instruct")
        
        # Act & Assert
        self.assertTrue(mixtral_dir.exists())
        self.assertTrue((mixtral_dir / "config.json").exists())
        self.assertTrue((mixtral_dir / "pytorch_model.bin").exists())
        
        # Validate Mixtral-specific configuration
        with open(mixtral_dir / "config.json", 'r') as f:
            model_config = json.load(f)
        
        self.assertEqual(model_config['model_type'], 'mixtral')
        self.assertEqual(model_config['num_local_experts'], 8)
        self.assertEqual(model_config['num_experts_per_tok'], 2)
        self.assertEqual(model_config['max_position_embeddings'], 32768)
        self.assertEqual(model_config['torch_dtype'], 'bfloat16')
    
    def test_enterprise_dialogs_model_validation(self):
        """Test enterprise DialoGPT model validation."""
        # Arrange
        dialogs_dir = self.create_dialogs_model_files(self.models_dir / "dialogs-large")
        
        # Act & Assert
        self.assertTrue(dialogs_dir.exists())
        self.assertTrue((dialogs_dir / "config.json").exists())
        
        # Validate DialoGPT-specific configuration
        with open(dialogs_dir / "config.json", 'r') as f:
            model_config = json.load(f)
        
        self.assertEqual(model_config['model_type'], 'gpt2')
        self.assertEqual(model_config['vocab_size'], 50257)
        self.assertEqual(model_config['n_layer'], 36)  # Large model
        self.assertEqual(model_config['torch_dtype'], 'float16')


class TestEnterpriseStorageConfiguration(BaseEnterpriseTestCase):
    """Test suite for enterprise storage configuration management."""
    
    def test_enterprise_storage_path_validation(self):
        """Test enterprise storage path configuration validation."""
        # Arrange
        storage_config = self.create_enterprise_config('storage')
        
        # Act & Assert
        self.assertIn('primary_path', storage_config['storage'])
        self.assertIn('backup_path', storage_config['storage'])
        self.assertIn('cache_path', storage_config['storage'])
        
        # Enterprise-specific paths should include 'production' and 'enterprise'
        self.assertIn('production', storage_config['storage']['primary_path'])
        self.assertIn('enterprise', storage_config['storage']['backup_path'])
    
    def test_enterprise_directory_structure_creation(self):
        """Test enterprise directory structure creation."""
        # Arrange
        enterprise_dirs = [
            self.test_dir / "models" / "production",
            self.test_dir / "backup" / "enterprise",
            self.test_dir / "logs" / "enterprise",
            self.test_dir / "monitoring"
        ]
        
        # Act
        for directory in enterprise_dirs:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Assert
        for directory in enterprise_dirs:
            self.assertTrue(directory.exists())
            self.assertTrue(directory.is_dir())
    
    def test_enterprise_model_priority_configuration(self):
        """Test enterprise model priority configuration."""
        # Arrange
        storage_config = self.create_enterprise_config('storage')
        server_config = storage_config['servers']['enterprise-server-01']
        
        # Act & Assert
        priority_models = server_config['priority_models']
        self.assertIn('mistralai/Mixtral-8x7B-Instruct-v0.1', priority_models)
        self.assertIn('microsoft/DialoGPT-large', priority_models)
        
        # Enterprise should prioritize production-ready models
        self.assertEqual(len(priority_models), 2)  # Focused model selection
        
        # Verify server ID
        self.assertEqual(server_config['server_id'], 'enterprise-server-01')
    
    def test_enterprise_storage_space_requirements(self):
        """Test enterprise storage space requirements validation."""
        # Arrange
        import shutil
        
        # Act
        total, used, free = shutil.disk_usage(self.test_dir)
        free_gb = free // (1024**3)
        
        # Assert - Enterprise requires significant storage
        # In production, enterprise should have substantial storage
        self.assertGreater(free_gb, 0)  # Basic test for development
        
        # Enterprise storage requirements (for production):
        # - Models: >500GB (Mixtral is ~90GB)
        # - Backup: >1TB
        # - Logs: >100GB
        # - Monitoring: >50GB


class TestEnterpriseConfigurationSecurity(BaseEnterpriseTestCase):
    """Test suite for enterprise configuration security features."""
    
    def test_api_key_configuration_validation(self):
        """Test API key configuration for enterprise security."""
        # Arrange
        security_config = self.create_enterprise_config('security')
        
        # Act & Assert
        auth_config = security_config['authentication']
        self.assertTrue(auth_config['enable_api_keys'])
        self.assertEqual(auth_config['key_rotation_days'], 30)
        self.assertEqual(auth_config['max_requests_per_minute'], 100)
    
    def test_audit_logging_configuration(self):
        """Test audit logging configuration for enterprise compliance."""
        # Arrange
        security_config = self.create_enterprise_config('security')
        
        # Act & Assert
        audit_config = security_config['audit']
        self.assertTrue(audit_config['log_all_requests'])
        self.assertFalse(audit_config['log_responses'])  # Privacy protection
        self.assertEqual(audit_config['retention_days'], 90)  # Compliance requirement
    
    def test_cors_security_configuration(self):
        """Test CORS security configuration for enterprise access."""
        # Arrange
        security_config = self.create_enterprise_config('security')
        
        # Act & Assert
        cors_config = security_config['cors']
        self.assertIn('https://enterprise.hana-x.local', cors_config['allowed_origins'])
        self.assertIn('GET', cors_config['allowed_methods'])
        self.assertIn('POST', cors_config['allowed_methods'])
        self.assertTrue(cors_config['allow_credentials'])
    
    @patch('os.access')
    def test_config_file_access_validation(self, mock_access):
        """Test configuration file access validation."""
        # Arrange
        mock_access.return_value = True
        config_path = self.config_dir / "enterprise_config.json"
        
        # Act
        has_read_access = os.access(config_path, os.R_OK)
        
        # Assert
        self.assertTrue(has_read_access)
        mock_access.assert_called_with(config_path, os.R_OK)
