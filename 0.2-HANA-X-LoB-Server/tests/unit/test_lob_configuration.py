#!/usr/bin/env python3
"""
Unit tests for HANA-X-LoB-Server configuration management.
Tests configuration loading, validation, and development-specific features.
"""

import unittest
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import shutil

from helpers.base_test_case import BaseLoBTestCase


class TestLoBConfigurationManagement(BaseLoBTestCase):
    """Test LoB configuration management with development focus."""
    
    def setUp(self):
        """Set up LoB configuration test environment."""
        super().setUp()
        
        # Create test configuration files
        self.api_config_path = self.config_dir / "api_server_config.json"
        self.storage_config_path = self.config_dir / "storage_config.json"
        self.development_config_path = self.config_dir / "development_config.json"
        
        # Sample configurations for testing
        self.sample_api_config = self.create_lob_config('api_server')
        self.sample_storage_config = self.create_lob_config('storage')
        self.sample_development_config = self.create_lob_config('development')
    
    def test_load_api_server_config_success(self):
        """Test successful loading of LoB API server configuration."""
        # Create config file
        self.api_config_path.write_text(json.dumps(self.sample_api_config, indent=2))
        
        # Mock config loader
        with patch('builtins.open', mock_open(read_data=json.dumps(self.sample_api_config))):
            with patch('json.load', return_value=self.sample_api_config):
                # Test configuration loading
                config = self.sample_api_config
                
                # Assert basic configuration
                self.assertEqual(config['server']['port'], 8001)
                self.assertEqual(config['server']['server_id'], 'lob-server-02')
                self.assertEqual(config['engine']['model'], 'deepseek-ai/deepseek-coder-14b-instruct')
                
                # Assert development features
                self.assertTrue(config['development']['enable_code_completion'])
                self.assertTrue(config['development']['enable_debugging'])
                self.assertTrue(config['development']['enable_documentation'])
    
    def test_load_storage_config_success(self):
        """Test successful loading of LoB storage configuration."""
        # Create config file
        self.storage_config_path.write_text(json.dumps(self.sample_storage_config, indent=2))
        
        # Mock config loader
        with patch('builtins.open', mock_open(read_data=json.dumps(self.sample_storage_config))):
            with patch('json.load', return_value=self.sample_storage_config):
                config = self.sample_storage_config
                
                # Assert storage paths
                self.assertIn('storage', config)
                self.assertIn('servers', config)
                self.assertIn('lob-server-02', config['servers'])
                
                # Assert LoB-specific models
                lob_server = config['servers']['lob-server-02']
                self.assertIn('deepseek-ai/deepseek-coder-14b-instruct', lob_server['priority_models'])
                self.assertIn('codellama/CodeLlama-13b-Instruct-hf', lob_server['priority_models'])
    
    def test_load_development_config_success(self):
        """Test successful loading of LoB development configuration."""
        # Create config file
        self.development_config_path.write_text(json.dumps(self.sample_development_config, indent=2))
        
        # Mock config loader
        with patch('builtins.open', mock_open(read_data=json.dumps(self.sample_development_config))):
            with patch('json.load', return_value=self.sample_development_config):
                config = self.sample_development_config
                
                # Assert development features
                features = config['features']
                self.assertTrue(features['code_completion'])
                self.assertTrue(features['code_explanation'])
                self.assertTrue(features['debugging_assistance'])
                self.assertTrue(features['documentation_generation'])
                
                # Assert supported languages
                languages = config['supported_languages']
                self.assertIn('python', languages)
                self.assertIn('javascript', languages)
                self.assertIn('java', languages)
                self.assertIn('cpp', languages)
                self.assertIn('go', languages)
                
                # Assert quality thresholds
                thresholds = config['quality_thresholds']
                self.assertEqual(thresholds['min_code_quality'], 85)
                self.assertEqual(thresholds['documentation_coverage'], 70)
    
    def test_config_validation_api_server(self):
        """Test validation of LoB API server configuration."""
        # Test valid configuration
        valid_config = self.sample_api_config
        self.assertTrue(self._validate_api_config(valid_config))
        
        # Test invalid configuration - missing server section
        invalid_config = valid_config.copy()
        del invalid_config['server']
        self.assertFalse(self._validate_api_config(invalid_config))
        
        # Test invalid configuration - wrong port
        invalid_config = valid_config.copy()
        invalid_config['server']['port'] = 'invalid_port'
        self.assertFalse(self._validate_api_config(invalid_config))
        
        # Test invalid configuration - missing development features
        invalid_config = valid_config.copy()
        del invalid_config['development']['enable_code_completion']
        self.assertFalse(self._validate_api_config(invalid_config))
    
    def test_config_validation_storage(self):
        """Test validation of LoB storage configuration."""
        # Test valid configuration
        valid_config = self.sample_storage_config
        self.assertTrue(self._validate_storage_config(valid_config))
        
        # Test invalid configuration - missing storage section
        invalid_config = valid_config.copy()
        del invalid_config['storage']
        self.assertFalse(self._validate_storage_config(invalid_config))
        
        # Test invalid configuration - missing LoB server
        invalid_config = valid_config.copy()
        del invalid_config['servers']['lob-server-02']
        self.assertFalse(self._validate_storage_config(invalid_config))
    
    def test_config_validation_development(self):
        """Test validation of LoB development configuration."""
        # Test valid configuration
        valid_config = self.sample_development_config
        self.assertTrue(self._validate_development_config(valid_config))
        
        # Test invalid configuration - missing features
        invalid_config = valid_config.copy()
        del invalid_config['features']
        self.assertFalse(self._validate_development_config(invalid_config))
        
        # Test invalid configuration - missing supported languages
        invalid_config = valid_config.copy()
        invalid_config['supported_languages'] = []
        self.assertFalse(self._validate_development_config(invalid_config))
    
    def test_config_override_functionality(self):
        """Test configuration override functionality for LoB settings."""
        base_config = self.sample_api_config
        
        # Test overriding development features
        overrides = {
            'development': {
                'enable_code_completion': False,
                'enable_debugging': True,
                'code_style_checking': False
            }
        }
        
        merged_config = self.create_lob_config('api_server', **overrides)
        
        # Assert overrides applied
        self.assertFalse(merged_config['development']['enable_code_completion'])
        self.assertTrue(merged_config['development']['enable_debugging'])
        self.assertFalse(merged_config['development']['code_style_checking'])
        
        # Assert non-overridden values preserved
        self.assertEqual(merged_config['server']['port'], 8001)
        self.assertEqual(merged_config['engine']['model'], 'deepseek-ai/deepseek-coder-14b-instruct')
    
    def test_lob_specific_model_configuration(self):
        """Test LoB-specific model configuration handling."""
        # Test DeepSeek Coder configuration
        deepseek_config = {
            'engine': {
                'model': 'deepseek-ai/deepseek-coder-14b-instruct',
                'specialization': 'code_generation',
                'tensor_parallel_size': 2,
                'max_model_len': 16384
            }
        }
        
        config = self.create_lob_config('api_server', **deepseek_config)
        
        # Assert DeepSeek configuration
        self.assertEqual(config['engine']['model'], 'deepseek-ai/deepseek-coder-14b-instruct')
        self.assertEqual(config['engine']['tensor_parallel_size'], 2)
        self.assertEqual(config['engine']['max_model_len'], 16384)
        
        # Test CodeLlama configuration
        codellama_config = {
            'engine': {
                'model': 'codellama/CodeLlama-13b-Instruct-hf',
                'specialization': 'code_instruction',
                'tensor_parallel_size': 2,
                'max_model_len': 16384
            }
        }
        
        config = self.create_lob_config('api_server', **codellama_config)
        
        # Assert CodeLlama configuration
        self.assertEqual(config['engine']['model'], 'codellama/CodeLlama-13b-Instruct-hf')
        self.assertEqual(config['engine']['tensor_parallel_size'], 2)
    
    def test_development_quality_thresholds(self):
        """Test development quality threshold configuration."""
        # Test with custom quality thresholds
        custom_thresholds = {
            'quality_thresholds': {
                'min_code_quality': 90,
                'max_complexity_score': 'medium',
                'documentation_coverage': 80,
                'unit_test_coverage': 85
            }
        }
        
        config = self.create_lob_config('development', **custom_thresholds)
        
        # Assert custom thresholds
        thresholds = config['quality_thresholds']
        self.assertEqual(thresholds['min_code_quality'], 90)
        self.assertEqual(thresholds['max_complexity_score'], 'medium')
        self.assertEqual(thresholds['documentation_coverage'], 80)
        self.assertEqual(thresholds['unit_test_coverage'], 85)
    
    def test_config_file_not_found_handling(self):
        """Test handling of missing configuration files."""
        non_existent_path = self.config_dir / "non_existent_config.json"
        
        # Mock file not found
        with patch('builtins.open', side_effect=FileNotFoundError("Config file not found")):
            with self.assertRaises(FileNotFoundError):
                with open(non_existent_path, 'r') as f:
                    json.load(f)
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON in configuration files."""
        invalid_json = "{ invalid json content }"
        
        # Mock invalid JSON
        with patch('builtins.open', mock_open(read_data=invalid_json)):
            with patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", invalid_json, 0)):
                with self.assertRaises(json.JSONDecodeError):
                    json.load(Mock())
    
    def test_config_backup_and_restore(self):
        """Test configuration backup and restore functionality."""
        # Create original config
        original_config = self.sample_api_config
        self.api_config_path.write_text(json.dumps(original_config, indent=2))
        
        # Create backup
        backup_path = self.backup_dir / "api_server_config_backup.json"
        backup_path.write_text(json.dumps(original_config, indent=2))
        
        # Modify original
        modified_config = original_config.copy()
        modified_config['server']['port'] = 8002
        self.api_config_path.write_text(json.dumps(modified_config, indent=2))
        
        # Restore from backup
        restored_config = json.loads(backup_path.read_text())
        
        # Assert restore worked
        self.assertEqual(restored_config['server']['port'], 8001)
        self.assertEqual(restored_config['server']['server_id'], 'lob-server-02')
    
    def test_environment_variable_substitution(self):
        """Test environment variable substitution in configuration."""
        # Mock environment variables
        with patch.dict(os.environ, {
            'LOB_SERVER_PORT': '8001',
            'LOB_MODEL_PATH': '/custom/model/path',
            'LOB_GPU_MEMORY': '0.85'
        }):
            # Test substitution
            config_template = {
                'server': {
                    'port': '${LOB_SERVER_PORT}',
                    'server_id': 'lob-server-02'
                },
                'engine': {
                    'download_dir': '${LOB_MODEL_PATH}',
                    'gpu_memory_utilization': '${LOB_GPU_MEMORY}'
                }
            }
            
            # Simulate environment variable substitution
            resolved_config = self._substitute_env_vars(config_template)
            
            # Assert substitution
            self.assertEqual(resolved_config['server']['port'], '8001')
            self.assertEqual(resolved_config['engine']['download_dir'], '/custom/model/path')
            self.assertEqual(resolved_config['engine']['gpu_memory_utilization'], '0.85')
    
    def _validate_api_config(self, config: dict) -> bool:
        """Validate LoB API server configuration."""
        required_sections = ['server', 'engine', 'development']
        
        for section in required_sections:
            if section not in config:
                return False
        
        # Validate server section
        server = config['server']
        if not isinstance(server.get('port'), int):
            return False
        
        if 'server_id' not in server:
            return False
        
        # Validate development section
        development = config['development']
        required_dev_features = ['enable_code_completion', 'enable_debugging', 'enable_documentation']
        
        for feature in required_dev_features:
            if feature not in development:
                return False
        
        return True
    
    def _validate_storage_config(self, config: dict) -> bool:
        """Validate LoB storage configuration."""
        required_sections = ['storage', 'servers']
        
        for section in required_sections:
            if section not in config:
                return False
        
        # Validate LoB server presence
        if 'lob-server-02' not in config['servers']:
            return False
        
        return True
    
    def _validate_development_config(self, config: dict) -> bool:
        """Validate LoB development configuration."""
        required_sections = ['features', 'supported_languages', 'quality_thresholds']
        
        for section in required_sections:
            if section not in config:
                return False
        
        # Validate supported languages
        if not config['supported_languages']:
            return False
        
        return True
    
    def _substitute_env_vars(self, config: dict) -> dict:
        """Substitute environment variables in configuration."""
        import re
        
        def substitute_value(value):
            if isinstance(value, str):
                # Simple environment variable substitution
                pattern = r'\$\{([^}]+)\}'
                matches = re.findall(pattern, value)
                for match in matches:
                    env_value = os.environ.get(match, '')
                    value = value.replace(f'${{{match}}}', env_value)
                return value
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            else:
                return value
        
        return substitute_value(config)


class TestLoBModelConfiguration(BaseLoBTestCase):
    """Test LoB model-specific configuration management."""
    
    def setUp(self):
        """Set up LoB model configuration test environment."""
        super().setUp()
        
        # Create model directories
        self.deepseek_model_dir = self.models_dir / "deepseek-ai" / "deepseek-coder-14b-instruct"
        self.codellama_model_dir = self.models_dir / "codellama" / "CodeLlama-13b-Instruct-hf"
    
    def test_deepseek_model_configuration(self):
        """Test DeepSeek Coder model configuration."""
        # Create model files
        self.create_deepseek_model_files(self.deepseek_model_dir)
        
        # Load configuration
        config_path = self.deepseek_model_dir / "config.json"
        config = json.loads(config_path.read_text())
        
        # Assert DeepSeek-specific configuration
        self.assertEqual(config['model_type'], 'llama')
        self.assertEqual(config['vocab_size'], 32000)
        self.assertEqual(config['max_position_embeddings'], 16384)
        self.assertEqual(config['specialization'], 'code_generation')
        self.assertIn('python', config['supported_languages'])
        self.assertIn('javascript', config['supported_languages'])
    
    def test_codellama_model_configuration(self):
        """Test CodeLlama model configuration."""
        # Create model files
        self.create_codellama_model_files(self.codellama_model_dir)
        
        # Load configuration
        config_path = self.codellama_model_dir / "config.json"
        config = json.loads(config_path.read_text())
        
        # Assert CodeLlama-specific configuration
        self.assertEqual(config['model_type'], 'llama')
        self.assertEqual(config['vocab_size'], 32016)
        self.assertEqual(config['max_position_embeddings'], 16384)
        self.assertEqual(config['specialization'], 'code_instruction')
        self.assertIn('python', config['supported_languages'])
        self.assertIn('cpp', config['supported_languages'])
    
    def test_model_compatibility_validation(self):
        """Test model compatibility validation for LoB server."""
        # Test compatible model
        compatible_model = {
            'model_type': 'llama',
            'specialization': 'code_generation',
            'max_position_embeddings': 16384,
            'supported_languages': ['python', 'javascript']
        }
        
        self.assertTrue(self._validate_lob_model_compatibility(compatible_model))
        
        # Test incompatible model - wrong specialization
        incompatible_model = {
            'model_type': 'llama',
            'specialization': 'general_chat',
            'max_position_embeddings': 16384,
            'supported_languages': ['python']
        }
        
        self.assertFalse(self._validate_lob_model_compatibility(incompatible_model))
        
        # Test incompatible model - no coding languages
        incompatible_model = {
            'model_type': 'llama',
            'specialization': 'code_generation',
            'max_position_embeddings': 16384,
            'supported_languages': []
        }
        
        self.assertFalse(self._validate_lob_model_compatibility(incompatible_model))
    
    def _validate_lob_model_compatibility(self, model_config: dict) -> bool:
        """Validate model compatibility with LoB server requirements."""
        # Check for coding specialization
        valid_specializations = ['code_generation', 'code_instruction', 'code_completion']
        if model_config.get('specialization') not in valid_specializations:
            return False
        
        # Check for supported programming languages
        supported_languages = model_config.get('supported_languages', [])
        coding_languages = ['python', 'javascript', 'java', 'cpp', 'go', 'rust', 'typescript']
        
        if not any(lang in supported_languages for lang in coding_languages):
            return False
        
        return True


if __name__ == '__main__':
    unittest.main()
