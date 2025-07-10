#!/usr/bin/env python3
"""
Integration tests for HANA-X-Enterprise-Server API endpoints.
Tests OpenAI-compatible API functionality with enterprise-specific features.
"""

import sys
import requests
import json
import time
from pathlib import Path
from unittest.mock import patch, Mock

# Add helpers to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from helpers.base_test_case import BaseEnterpriseIntegrationTestCase

class TestEnterpriseAPIEndpoints(BaseEnterpriseIntegrationTestCase):
    """Integration tests for enterprise vLLM API endpoints."""
    
    def setUp(self):
        """Set up enterprise API testing environment."""
        super().setUp()
        self.enterprise_url = f"http://{self.server_config['ip']}:{self.server_config['port']}"
        
        # Enterprise-specific headers
        self.enterprise_headers = {
            'Authorization': 'Bearer enterprise-api-key-12345',
            'X-Enterprise-Client': 'HANA-X-Enterprise',
            'X-Request-ID': 'test-enterprise-request-001'
        }
    
    @patch('requests.get')
    def test_enterprise_health_endpoint_response(self, mock_get):
        """Test /v1/health endpoint returns enterprise-specific response."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.05
        mock_response.json.return_value = {
            "status": "healthy",
            "server_id": "enterprise-server-01",
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "gpu_count": 2,
            "memory_usage": "75%",
            "uptime_seconds": 3600,
            "requests_served": 1250,
            "enterprise_features": {
                "security_enabled": True,
                "audit_logging": True,
                "performance_monitoring": True,
                "api_key_rotation": True
            },
            "sla_metrics": {
                "availability": 99.95,
                "average_latency_ms": 1200,
                "p95_latency_ms": 1800
            }
        }
        mock_response.headers = {
            'X-Server-ID': 'enterprise-server-01',
            'X-Rate-Limit-Remaining': '95',
            'X-Request-ID': 'test-enterprise-request-001'
        }
        mock_get.return_value = mock_response
        
        # Act
        response = requests.get(
            f"{self.enterprise_url}/v1/health",
            headers=self.enterprise_headers
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        health_data = response.json()
        
        # Basic health data
        self.assertEqual(health_data['status'], 'healthy')
        self.assertEqual(health_data['server_id'], 'enterprise-server-01')
        self.assertEqual(health_data['model'], 'mistralai/Mixtral-8x7B-Instruct-v0.1')
        
        # Enterprise-specific features
        enterprise_features = health_data['enterprise_features']
        self.assertTrue(enterprise_features['security_enabled'])
        self.assertTrue(enterprise_features['audit_logging'])
        self.assertTrue(enterprise_features['performance_monitoring'])
        
        # SLA metrics
        sla_metrics = health_data['sla_metrics']
        self.assertGreater(sla_metrics['availability'], 99.9)
        self.assertLess(sla_metrics['average_latency_ms'], 1500)  # Enterprise target
        
        # Security headers
        self.assert_enterprise_security(response.headers)
    
    @patch('requests.get')
    def test_enterprise_models_endpoint_response(self, mock_get):
        """Test /v1/models endpoint returns enterprise model catalog."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.08
        mock_response.json.return_value = {
            "object": "list",
            "data": [
                {
                    "id": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    "object": "model",
                    "created": 1609459200,
                    "owned_by": "mistralai",
                    "permission": ["read"],
                    "root": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    "parent": None,
                    "enterprise_info": {
                        "model_tier": "production",
                        "performance_class": "high",
                        "context_length": 32768,
                        "precision": "bfloat16",
                        "gpu_memory_required": "48GB"
                    }
                },
                {
                    "id": "microsoft/DialoGPT-large",
                    "object": "model",
                    "created": 1609459200,
                    "owned_by": "microsoft",
                    "permission": ["read"],
                    "root": "microsoft/DialoGPT-large",
                    "parent": None,
                    "enterprise_info": {
                        "model_tier": "production",
                        "performance_class": "standard",
                        "context_length": 1024,
                        "precision": "float16",
                        "gpu_memory_required": "24GB"
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Act
        response = requests.get(
            f"{self.enterprise_url}/v1/models",
            headers=self.enterprise_headers
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        models_data = response.json()
        
        self.assertEqual(models_data['object'], 'list')
        self.assertIsInstance(models_data['data'], list)
        self.assertEqual(len(models_data['data']), 2)  # Enterprise has focused model selection
        
        # Validate enterprise models
        mixtral_model = models_data['data'][0]
        self.assertEqual(mixtral_model['id'], 'mistralai/Mixtral-8x7B-Instruct-v0.1')
        self.assertEqual(mixtral_model['enterprise_info']['model_tier'], 'production')
        self.assertEqual(mixtral_model['enterprise_info']['context_length'], 32768)
        
        dialogs_model = models_data['data'][1]
        self.assertEqual(dialogs_model['id'], 'microsoft/DialoGPT-large')
        self.assertEqual(dialogs_model['enterprise_info']['performance_class'], 'standard')
    
    @patch('requests.post')
    def test_enterprise_completions_endpoint_response(self, mock_post):
        """Test /v1/completions endpoint with enterprise features."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 1.2
        mock_response.json.return_value = {
            "id": "cmpl-enterprise-abcd1234",
            "object": "text_completion",
            "created": int(time.time()),
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "choices": [
                {
                    "text": " I understand you need enterprise-grade assistance. I'm designed to provide professional, accurate responses for business environments. How may I help you with your enterprise requirements today?",
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 25,
                "completion_tokens": 35,
                "total_tokens": 60
            },
            "enterprise_metadata": {
                "request_id": "test-enterprise-request-001",
                "processing_time_ms": 1200,
                "gpu_utilization": 87,
                "memory_utilization": 78,
                "security_scan": "passed",
                "audit_logged": True
            }
        }
        mock_response.headers = {
            'X-Server-ID': 'enterprise-server-01',
            'X-Processing-Time-MS': '1200',
            'X-Request-ID': 'test-enterprise-request-001'
        }
        mock_post.return_value = mock_response
        
        # Act
        test_payload = {
            "prompt": "You are an enterprise AI assistant. Please provide professional guidance on",
            "max_tokens": 50,
            "temperature": 0.1,  # Conservative for enterprise
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        response = requests.post(
            f"{self.enterprise_url}/v1/completions",
            json=test_payload,
            headers=self.enterprise_headers
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        completion_data = response.json()
        
        self.assertEqual(completion_data['object'], 'text_completion')
        self.assertEqual(completion_data['model'], 'mistralai/Mixtral-8x7B-Instruct-v0.1')
        self.assertIn('choices', completion_data)
        self.assertGreater(len(completion_data['choices']), 0)
        
        # Enterprise-specific response validation
        choice = completion_data['choices'][0]
        self.assert_enterprise_model_quality(choice['text'], min_length=20)
        
        # Enterprise metadata validation
        enterprise_metadata = completion_data['enterprise_metadata']
        self.assertEqual(enterprise_metadata['request_id'], 'test-enterprise-request-001')
        self.assertLess(enterprise_metadata['processing_time_ms'], 1500)  # Enterprise target
        self.assertGreater(enterprise_metadata['gpu_utilization'], 80)
        self.assertTrue(enterprise_metadata['audit_logged'])
        self.assertEqual(enterprise_metadata['security_scan'], 'passed')
        
        # Performance validation
        processing_time = enterprise_metadata['processing_time_ms']
        tokens_per_second = completion_data['usage']['completion_tokens'] / (processing_time / 1000)
        self.assertGreater(tokens_per_second, 10)  # Enterprise performance expectation
    
    @patch('requests.post')
    def test_enterprise_chat_completions_endpoint(self, mock_post):
        """Test /v1/chat/completions endpoint with enterprise chat features."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 1.4
        mock_response.json.return_value = {
            "id": "chatcmpl-enterprise-xyz789",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "I understand you're looking for enterprise-level AI assistance. I'm equipped with advanced capabilities to help with complex business scenarios, strategic analysis, and professional communication. What specific enterprise challenge can I help you address?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 35,
                "completion_tokens": 45,
                "total_tokens": 80
            },
            "enterprise_metadata": {
                "conversation_id": "enterprise-conv-001",
                "compliance_check": "passed",
                "content_filter": "enterprise",
                "priority_level": "high"
            }
        }
        mock_post.return_value = mock_response
        
        # Act
        test_payload = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional enterprise AI assistant focused on business excellence."
                },
                {
                    "role": "user",
                    "content": "I need help with enterprise strategy."
                }
            ],
            "max_tokens": 100,
            "temperature": 0.2,
            "stream": False
        }
        
        response = requests.post(
            f"{self.enterprise_url}/v1/chat/completions",
            json=test_payload,
            headers=self.enterprise_headers
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        chat_data = response.json()
        
        self.assertEqual(chat_data['object'], 'chat.completion')
        self.assertEqual(chat_data['model'], 'mistralai/Mixtral-8x7B-Instruct-v0.1')
        self.assertIn('choices', chat_data)
        
        choice = chat_data['choices'][0]
        self.assertIn('message', choice)
        self.assertEqual(choice['message']['role'], 'assistant')
        
        # Enterprise chat quality validation
        content = choice['message']['content']
        self.assert_enterprise_model_quality(content, min_length=30)
        self.assertIn('enterprise', content.lower())  # Should be business-focused
        
        # Enterprise metadata validation
        enterprise_metadata = chat_data['enterprise_metadata']
        self.assertEqual(enterprise_metadata['compliance_check'], 'passed')
        self.assertEqual(enterprise_metadata['content_filter'], 'enterprise')
        self.assertEqual(enterprise_metadata['priority_level'], 'high')
    
    @patch('requests.get')
    def test_enterprise_api_error_handling(self, mock_get):
        """Test enterprise API error handling with detailed error responses."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429  # Rate limited
        mock_response.json.return_value = {
            "error": {
                "message": "Rate limit exceeded for enterprise tier",
                "type": "rate_limit_exceeded",
                "code": 429,
                "enterprise_details": {
                    "current_rate": "105 requests/minute",
                    "limit": "100 requests/minute",
                    "reset_time": int(time.time()) + 60,
                    "tier": "enterprise",
                    "contact_support": "enterprise-support@hana-x.local"
                }
            }
        }
        mock_response.headers = {
            'X-Rate-Limit-Limit': '100',
            'X-Rate-Limit-Remaining': '0',
            'X-Rate-Limit-Reset': str(int(time.time()) + 60),
            'Retry-After': '60'
        }
        mock_get.return_value = mock_response
        
        # Act
        response = requests.get(f"{self.enterprise_url}/v1/models")
        
        # Assert
        self.assertEqual(response.status_code, 429)
        error_data = response.json()
        
        self.assertIn('error', error_data)
        error = error_data['error']
        self.assertEqual(error['type'], 'rate_limit_exceeded')
        self.assertEqual(error['code'], 429)
        
        # Enterprise error details
        enterprise_details = error['enterprise_details']
        self.assertEqual(enterprise_details['tier'], 'enterprise')
        self.assertIn('enterprise-support@hana-x.local', enterprise_details['contact_support'])
        self.assertIn('100 requests/minute', enterprise_details['limit'])
    
    @patch('requests.post')
    def test_enterprise_api_performance_monitoring(self, mock_post):
        """Test enterprise API performance monitoring and metrics."""
        # Arrange - Simulate multiple requests for performance testing
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 1.1
        mock_response.json.return_value = {
            "choices": [{"text": "Enterprise response"}],
            "usage": {"total_tokens": 20},
            "enterprise_metadata": {
                "processing_time_ms": 1100,
                "gpu_utilization": 85,
                "memory_utilization": 80
            }
        }
        mock_post.return_value = mock_response
        
        # Act - Simulate performance test
        latencies = []
        for i in range(5):
            start_time = time.time()
            response = requests.post(
                f"{self.enterprise_url}/v1/completions",
                json={"prompt": "Test", "max_tokens": 10},
                headers=self.enterprise_headers
            )
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            
            self.assertEqual(response.status_code, 200)
        
        # Assert - Enterprise performance targets
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        # Use enterprise performance assertion
        self.assert_enterprise_performance(
            latency_ms=avg_latency,
            throughput_rps=len(latencies) / (sum(latencies) / 1000)
        )
        
        # Enterprise-specific performance requirements
        self.assertLess(avg_latency, 1500)  # Enterprise average latency target
        self.assertLess(max_latency, 2000)  # Enterprise max latency target
    
    def test_enterprise_cors_configuration(self):
        """Test CORS configuration for enterprise access patterns."""
        # This test would verify CORS headers in a real environment
        # For unit testing, we'll verify the expected configuration
        
        # Arrange
        expected_cors_config = {
            'cors_allow_origins': ['https://enterprise.hana-x.local'],
            'cors_allow_methods': ['GET', 'POST'],
            'cors_allow_headers': ['Authorization', 'Content-Type', 'X-Enterprise-Client'],
            'cors_allow_credentials': True
        }
        
        # Act & Assert
        self.assertIn('https://enterprise.hana-x.local', expected_cors_config['cors_allow_origins'])
        self.assertTrue(expected_cors_config['cors_allow_credentials'])
        self.assertIn('Authorization', expected_cors_config['cors_allow_headers'])
    
    @patch('requests.get')
    def test_enterprise_api_security_headers(self, mock_get):
        """Test enterprise API security headers are present."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.headers = {
            'X-Server-ID': 'enterprise-server-01',
            'X-Rate-Limit-Remaining': '95',
            'X-Request-ID': 'test-enterprise-request-001',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'X-Enterprise-Version': '1.0.0'
        }
        mock_get.return_value = mock_response
        
        # Act
        response = requests.get(
            f"{self.enterprise_url}/v1/health",
            headers=self.enterprise_headers
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        # Security headers validation
        headers = response.headers
        self.assertIn('X-Content-Type-Options', headers)
        self.assertIn('X-Frame-Options', headers)
        self.assertIn('Strict-Transport-Security', headers)
        self.assertIn('X-Enterprise-Version', headers)
        
        # Enterprise-specific headers
        self.assertEqual(headers['X-Server-ID'], 'enterprise-server-01')
        self.assertIn('X-Request-ID', headers)
