#!/usr/bin/env python3
"""
Integration tests for HANA-X-LoB-Server API endpoints.
Tests API functionality, development features, and coding assistance capabilities.
"""

import unittest
import json
import time
import requests
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from helpers.base_test_case import BaseLoBIntegrationTestCase


class TestLoBAPIIntegration(BaseLoBIntegrationTestCase):
    """Test LoB API integration with development focus."""
    
    def setUp(self):
        """Set up LoB API integration test environment."""
        super().setUp()
        
        # LoB API endpoints
        self.endpoints = {
            'health': f"{self.api_base_url}/health",
            'models': f"{self.api_base_url}/v1/models",
            'completions': f"{self.api_base_url}/v1/completions",
            'chat': f"{self.api_base_url}/v1/chat/completions",
            'code_completion': f"{self.api_base_url}/v1/code/complete",
            'code_explanation': f"{self.api_base_url}/v1/code/explain",
            'debug_assistance': f"{self.api_base_url}/v1/code/debug",
            'documentation': f"{self.api_base_url}/v1/code/document"
        }
        
        # Development request templates
        self.code_completion_request = {
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            "prompt": "def fibonacci(n):\n    if n <= 1:\n        return n\n    # Complete this function",
            "max_tokens": 150,
            "temperature": 0.2,
            "language": "python"
        }
        
        self.code_explanation_request = {
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            "code": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
            "language": "python"
        }
        
        self.debug_request = {
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            "code": "def divide_numbers(a, b):\n    return a / b\n\nresult = divide_numbers(10, 0)",
            "error": "ZeroDivisionError: division by zero",
            "language": "python"
        }
    
    def test_health_endpoint_success(self):
        """Test LoB server health endpoint."""
        # Mock successful health response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "server_id": "lob-server-02",
            "timestamp": int(time.time()),
            "models_loaded": ["deepseek-ai/deepseek-coder-14b-instruct"],
            "development_features": {
                "code_completion": True,
                "code_explanation": True,
                "debugging_assistance": True,
                "documentation_generation": True
            }
        }
        
        with patch('requests.get', return_value=mock_response):
            response = requests.get(self.endpoints['health'])
            
            # Assert health check
            self.assertEqual(response.status_code, 200)
            health_data = response.json()
            self.assertEqual(health_data['status'], 'healthy')
            self.assertEqual(health_data['server_id'], 'lob-server-02')
            self.assertIn('deepseek-ai/deepseek-coder-14b-instruct', health_data['models_loaded'])
            
            # Assert development features
            self.assert_development_features(health_data)
    
    def test_models_endpoint_success(self):
        """Test LoB models endpoint."""
        # Mock models response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "object": "list",
            "data": [
                {
                    "id": "deepseek-ai/deepseek-coder-14b-instruct",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "lob-server-02",
                    "specialization": "code_generation",
                    "supported_languages": ["python", "javascript", "java", "cpp", "go"]
                },
                {
                    "id": "codellama/CodeLlama-13b-Instruct-hf",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "lob-server-02",
                    "specialization": "code_instruction",
                    "supported_languages": ["python", "javascript", "java", "cpp"]
                }
            ]
        }
        
        with patch('requests.get', return_value=mock_response):
            response = requests.get(self.endpoints['models'])
            
            # Assert models response
            self.assertEqual(response.status_code, 200)
            models_data = response.json()
            self.assertEqual(models_data['object'], 'list')
            self.assertEqual(len(models_data['data']), 2)
            
            # Assert DeepSeek model
            deepseek_model = models_data['data'][0]
            self.assertEqual(deepseek_model['id'], 'deepseek-ai/deepseek-coder-14b-instruct')
            self.assertEqual(deepseek_model['specialization'], 'code_generation')
            self.assertIn('python', deepseek_model['supported_languages'])
    
    def test_code_completion_endpoint_success(self):
        """Test LoB code completion endpoint."""
        # Mock code completion response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 1.5
        mock_response.json.return_value = {
            "id": "lob-code-completion-123",
            "object": "text_completion",
            "created": int(time.time()),
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            "choices": [
                {
                    "text": "    else:\n        return fibonacci(n-1) + fibonacci(n-2)",
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 25,
                "completion_tokens": 15,
                "total_tokens": 40
            },
            "development_metrics": {
                "code_quality_score": 88,
                "syntax_valid": True,
                "language_detected": "python"
            }
        }
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post(
                self.endpoints['code_completion'],
                json=self.code_completion_request
            )
            
            # Assert completion response
            self.assertEqual(response.status_code, 200)
            completion_data = response.json()
            self.assertEqual(completion_data['model'], 'deepseek-ai/deepseek-coder-14b-instruct')
            self.assertEqual(len(completion_data['choices']), 1)
            
            # Assert code quality metrics
            metrics = completion_data['development_metrics']
            self.assertGreaterEqual(metrics['code_quality_score'], 85)
            self.assertTrue(metrics['syntax_valid'])
            self.assertEqual(metrics['language_detected'], 'python')
            
            # Assert performance
            self.assert_lob_performance(
                latency_ms=response.elapsed.total_seconds() * 1000,
                throughput_rps=1 / response.elapsed.total_seconds()
            )
    
    def test_code_explanation_endpoint_success(self):
        """Test LoB code explanation endpoint."""
        # Mock code explanation response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 2.0
        mock_response.json.return_value = {
            "id": "lob-code-explanation-456",
            "object": "code_explanation",
            "created": int(time.time()),
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            "explanation": {
                "summary": "This function implements the binary search algorithm.",
                "detailed_explanation": "The binary search algorithm works by repeatedly dividing the search interval in half. It compares the target value with the middle element and eliminates half of the search space in each iteration.",
                "complexity": {
                    "time": "O(log n)",
                    "space": "O(1)"
                },
                "parameters": [
                    {"name": "arr", "type": "list", "description": "Sorted array to search in"},
                    {"name": "target", "type": "any", "description": "Value to search for"}
                ],
                "return_value": "Index of target element or -1 if not found"
            },
            "development_metrics": {
                "explanation_quality": 92,
                "technical_accuracy": 95,
                "clarity_score": 89
            }
        }
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post(
                self.endpoints['code_explanation'],
                json=self.code_explanation_request
            )
            
            # Assert explanation response
            self.assertEqual(response.status_code, 200)
            explanation_data = response.json()
            self.assertEqual(explanation_data['model'], 'deepseek-ai/deepseek-coder-14b-instruct')
            
            # Assert explanation quality
            explanation = explanation_data['explanation']
            self.assertIn('binary search', explanation['summary'].lower())
            self.assertIn('time', explanation['complexity'])
            self.assertIn('space', explanation['complexity'])
            
            # Assert metrics
            metrics = explanation_data['development_metrics']
            self.assertGreaterEqual(metrics['explanation_quality'], 85)
            self.assertGreaterEqual(metrics['technical_accuracy'], 90)
    
    def test_debug_assistance_endpoint_success(self):
        """Test LoB debug assistance endpoint."""
        # Mock debug assistance response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 1.8
        mock_response.json.return_value = {
            "id": "lob-debug-assistance-789",
            "object": "debug_assistance",
            "created": int(time.time()),
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            "debug_analysis": {
                "error_type": "ZeroDivisionError",
                "root_cause": "Division by zero in the divide_numbers function",
                "line_number": 2,
                "suggested_fix": "Add input validation to check if the divisor is zero before performing division",
                "corrected_code": "def divide_numbers(a, b):\n    if b == 0:\n        raise ValueError('Cannot divide by zero')\n    return a / b\n\nresult = divide_numbers(10, 0)",
                "prevention_tips": [
                    "Always validate inputs before mathematical operations",
                    "Use try-except blocks for error handling",
                    "Consider returning None or a default value for invalid inputs"
                ]
            },
            "development_metrics": {
                "debug_accuracy": 94,
                "solution_quality": 91,
                "fix_completeness": 88
            }
        }
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post(
                self.endpoints['debug_assistance'],
                json=self.debug_request
            )
            
            # Assert debug response
            self.assertEqual(response.status_code, 200)
            debug_data = response.json()
            self.assertEqual(debug_data['model'], 'deepseek-ai/deepseek-coder-14b-instruct')
            
            # Assert debug analysis
            analysis = debug_data['debug_analysis']
            self.assertEqual(analysis['error_type'], 'ZeroDivisionError')
            self.assertIn('zero', analysis['root_cause'].lower())
            self.assertIn('if b == 0', analysis['corrected_code'])
            
            # Assert metrics
            metrics = debug_data['development_metrics']
            self.assertGreaterEqual(metrics['debug_accuracy'], 85)
            self.assertGreaterEqual(metrics['solution_quality'], 85)
    
    def test_documentation_generation_endpoint_success(self):
        """Test LoB documentation generation endpoint."""
        # Mock documentation generation response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 2.2
        mock_response.json.return_value = {
            "id": "lob-documentation-101",
            "object": "documentation",
            "created": int(time.time()),
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            "documentation": {
                "docstring": '"""\\nPerform binary search on a sorted array.\\n\\nArgs:\\n    arr (list): A sorted list of elements to search through.\\n    target: The element to search for.\\n\\nReturns:\\n    int: The index of the target element if found, -1 otherwise.\\n\\nExample:\\n    >>> binary_search([1, 3, 5, 7, 9], 5)\\n    2\\n    >>> binary_search([1, 3, 5, 7, 9], 4)\\n    -1\\n"""',
                "comments": [
                    "# Initialize left and right pointers",
                    "# Calculate middle index",
                    "# Compare middle element with target",
                    "# Adjust search boundaries"
                ],
                "documentation_type": "function_docstring",
                "format": "google_style"
            },
            "development_metrics": {
                "documentation_quality": 90,
                "completeness": 85,
                "clarity": 88
            }
        }
        
        doc_request = {
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            "code": self.code_explanation_request["code"],
            "language": "python",
            "doc_style": "google"
        }
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post(
                self.endpoints['documentation'],
                json=doc_request
            )
            
            # Assert documentation response
            self.assertEqual(response.status_code, 200)
            doc_data = response.json()
            self.assertEqual(doc_data['model'], 'deepseek-ai/deepseek-coder-14b-instruct')
            
            # Assert documentation quality
            documentation = doc_data['documentation']
            self.assertIn('binary search', documentation['docstring'].lower())
            self.assertIn('Args:', documentation['docstring'])
            self.assertIn('Returns:', documentation['docstring'])
            self.assertEqual(documentation['format'], 'google_style')
            
            # Assert metrics
            metrics = doc_data['development_metrics']
            self.assertGreaterEqual(metrics['documentation_quality'], 80)
            self.assertGreaterEqual(metrics['completeness'], 80)
    
    def test_concurrent_requests_handling(self):
        """Test LoB server handling of concurrent development requests."""
        # Mock concurrent responses
        def mock_post_response(*args, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.elapsed.total_seconds.return_value = 1.5
            mock_response.json.return_value = {
                "id": f"lob-concurrent-{int(time.time()*1000)}",
                "object": "text_completion",
                "created": int(time.time()),
                "model": "deepseek-ai/deepseek-coder-14b-instruct",
                "choices": [{"text": "# Generated code", "index": 0, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
                "development_metrics": {"code_quality_score": 87, "syntax_valid": True}
            }
            return mock_response
        
        with patch('requests.post', side_effect=mock_post_response):
            # Simulate concurrent requests
            requests_data = [
                {
                    "model": "deepseek-ai/deepseek-coder-14b-instruct",
                    "prompt": f"# Generate Python function {i}",
                    "max_tokens": 100,
                    "temperature": 0.2
                }
                for i in range(5)
            ]
            
            # Execute concurrent requests
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(
                        requests.post,
                        self.endpoints['code_completion'],
                        json=req_data
                    )
                    for req_data in requests_data
                ]
                
                responses = [future.result() for future in futures]
            
            # Assert all requests succeeded
            for response in responses:
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data['model'], 'deepseek-ai/deepseek-coder-14b-instruct')
                self.assertIn('development_metrics', data)
    
    def test_error_handling_invalid_request(self):
        """Test LoB server error handling for invalid requests."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid request format",
                "type": "invalid_request_error",
                "param": "prompt",
                "code": "missing_required_parameter"
            }
        }
        
        invalid_request = {
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            # Missing required 'prompt' field
            "max_tokens": 100
        }
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post(
                self.endpoints['code_completion'],
                json=invalid_request
            )
            
            # Assert error response
            self.assertEqual(response.status_code, 400)
            error_data = response.json()
            self.assertIn('error', error_data)
            self.assertEqual(error_data['error']['type'], 'invalid_request_error')
            self.assertEqual(error_data['error']['param'], 'prompt')
    
    def test_rate_limiting_handling(self):
        """Test LoB server rate limiting for development requests."""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "error": {
                "message": "Rate limit exceeded",
                "type": "rate_limit_error",
                "code": "rate_limit_exceeded"
            }
        }
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post(
                self.endpoints['code_completion'],
                json=self.code_completion_request
            )
            
            # Assert rate limit response
            self.assertEqual(response.status_code, 429)
            error_data = response.json()
            self.assertIn('error', error_data)
            self.assertEqual(error_data['error']['type'], 'rate_limit_error')
    
    def test_model_switching_functionality(self):
        """Test LoB server model switching between DeepSeek and CodeLlama."""
        # Test DeepSeek request
        deepseek_request = self.code_completion_request.copy()
        deepseek_request['model'] = 'deepseek-ai/deepseek-coder-14b-instruct'
        
        deepseek_response = Mock()
        deepseek_response.status_code = 200
        deepseek_response.json.return_value = {
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            "choices": [{"text": "# DeepSeek generated code", "index": 0}],
            "development_metrics": {"specialization": "code_generation"}
        }
        
        # Test CodeLlama request
        codellama_request = self.code_completion_request.copy()
        codellama_request['model'] = 'codellama/CodeLlama-13b-Instruct-hf'
        
        codellama_response = Mock()
        codellama_response.status_code = 200
        codellama_response.json.return_value = {
            "model": "codellama/CodeLlama-13b-Instruct-hf",
            "choices": [{"text": "# CodeLlama generated code", "index": 0}],
            "development_metrics": {"specialization": "code_instruction"}
        }
        
        # Mock responses based on model
        def mock_post_by_model(*args, **kwargs):
            request_data = kwargs.get('json', {})
            if request_data.get('model') == 'deepseek-ai/deepseek-coder-14b-instruct':
                return deepseek_response
            elif request_data.get('model') == 'codellama/CodeLlama-13b-Instruct-hf':
                return codellama_response
            else:
                mock_error = Mock()
                mock_error.status_code = 404
                return mock_error
        
        with patch('requests.post', side_effect=mock_post_by_model):
            # Test DeepSeek
            response1 = requests.post(
                self.endpoints['code_completion'],
                json=deepseek_request
            )
            self.assertEqual(response1.status_code, 200)
            data1 = response1.json()
            self.assertEqual(data1['model'], 'deepseek-ai/deepseek-coder-14b-instruct')
            self.assertEqual(data1['development_metrics']['specialization'], 'code_generation')
            
            # Test CodeLlama
            response2 = requests.post(
                self.endpoints['code_completion'],
                json=codellama_request
            )
            self.assertEqual(response2.status_code, 200)
            data2 = response2.json()
            self.assertEqual(data2['model'], 'codellama/CodeLlama-13b-Instruct-hf')
            self.assertEqual(data2['development_metrics']['specialization'], 'code_instruction')


class TestLoBAdvancedFeatures(BaseLoBIntegrationTestCase):
    """Test LoB advanced development features and integrations."""
    
    def test_code_review_integration(self):
        """Test LoB code review integration capability."""
        # Mock code review response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "lob-code-review-001",
            "object": "code_review",
            "created": int(time.time()),
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            "review": {
                "overall_score": 85,
                "issues": [
                    {
                        "severity": "medium",
                        "type": "performance",
                        "line": 3,
                        "message": "Consider using list comprehension for better performance",
                        "suggestion": "result = [x*2 for x in numbers]"
                    },
                    {
                        "severity": "low",
                        "type": "style",
                        "line": 1,
                        "message": "Function name should be more descriptive",
                        "suggestion": "def double_numbers(numbers):"
                    }
                ],
                "strengths": [
                    "Clear variable naming",
                    "Proper error handling",
                    "Good documentation"
                ],
                "recommendations": [
                    "Add input validation",
                    "Consider edge cases",
                    "Add unit tests"
                ]
            },
            "development_metrics": {
                "review_quality": 88,
                "issue_detection_accuracy": 92,
                "suggestion_relevance": 85
            }
        }
        
        code_review_request = {
            "model": "deepseek-ai/deepseek-coder-14b-instruct",
            "code": "def process_numbers(numbers):\n    result = []\n    for num in numbers:\n        result.append(num * 2)\n    return result",
            "language": "python",
            "review_level": "comprehensive"
        }
        
        with patch('requests.post', return_value=mock_response):
            response = requests.post(
                f"{self.api_base_url}/v1/code/review",
                json=code_review_request
            )
            
            # Assert code review response
            self.assertEqual(response.status_code, 200)
            review_data = response.json()
            self.assertEqual(review_data['model'], 'deepseek-ai/deepseek-coder-14b-instruct')
            
            # Assert review quality
            review = review_data['review']
            self.assertGreaterEqual(review['overall_score'], 80)
            self.assertGreater(len(review['issues']), 0)
            self.assertGreater(len(review['strengths']), 0)
            self.assertGreater(len(review['recommendations']), 0)
    
    def test_multi_language_support(self):
        """Test LoB multi-language development support."""
        languages = ['python', 'javascript', 'java', 'cpp', 'go']
        
        for language in languages:
            # Mock language-specific response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": f"lob-{language}-completion-001",
                "object": "text_completion",
                "model": "deepseek-ai/deepseek-coder-14b-instruct",
                "choices": [{"text": f"// {language.capitalize()} generated code", "index": 0}],
                "development_metrics": {
                    "language_detected": language,
                    "syntax_valid": True,
                    "language_specific_score": 90
                }
            }
            
            language_request = {
                "model": "deepseek-ai/deepseek-coder-14b-instruct",
                "prompt": f"# Write a hello world function in {language}",
                "language": language,
                "max_tokens": 100
            }
            
            with patch('requests.post', return_value=mock_response):
                response = requests.post(
                    self.endpoints['code_completion'],
                    json=language_request
                )
                
                # Assert language-specific response
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data['development_metrics']['language_detected'], language)
                self.assertTrue(data['development_metrics']['syntax_valid'])
                self.assertGreaterEqual(data['development_metrics']['language_specific_score'], 85)


if __name__ == '__main__':
    unittest.main()
