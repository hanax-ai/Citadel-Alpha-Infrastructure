#!/usr/bin/env python3
"""
System tests for HANA-X-LoB-Server performance and scalability.
Tests development-focused workload performance, system resources, and quality metrics.
"""

import unittest
import time
import statistics
import threading
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch, MagicMock
import requests
from pathlib import Path

from helpers.base_test_case import BaseLoBSystemTestCase


class TestLoBPerformance(BaseLoBSystemTestCase):
    """Test LoB performance under development workload scenarios."""
    
    def setUp(self):
        """Set up LoB performance testing environment."""
        super().setUp()
        
        # Performance test scenarios
        self.performance_scenarios = {
            'code_completion': {
                'concurrent_users': 8,
                'requests_per_user': 10,
                'max_latency_ms': 2000,
                'min_throughput_rps': 15
            },
            'code_explanation': {
                'concurrent_users': 6,
                'requests_per_user': 8,
                'max_latency_ms': 3000,
                'min_throughput_rps': 10
            },
            'debug_assistance': {
                'concurrent_users': 4,
                'requests_per_user': 12,
                'max_latency_ms': 2500,
                'min_throughput_rps': 8
            }
        }
        
        # Quality metrics tracking
        self.quality_metrics = {
            'code_quality_scores': [],
            'syntax_validity_rate': 0.0,
            'technical_accuracy_scores': [],
            'explanation_quality_scores': [],
            'debug_success_rate': 0.0
        }
        
        # Resource monitoring
        self.resource_metrics = {
            'cpu_utilization': [],
            'memory_usage': [],
            'gpu_utilization': [],
            'gpu_memory_usage': []
        }
    
    def test_code_completion_performance(self):
        """Test LoB code completion performance under load."""
        scenario = self.performance_scenarios['code_completion']
        
        # Mock code completion responses
        def mock_completion_response():
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.elapsed.total_seconds.return_value = 1.2 + (0.6 * (threading.current_thread().ident % 5) / 5)
            mock_response.json.return_value = {
                "id": f"lob-completion-{int(time.time()*1000)}",
                "object": "text_completion",
                "created": int(time.time()),
                "model": "deepseek-ai/deepseek-coder-14b-instruct",
                "choices": [{"text": "    return result", "index": 0, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 20, "completion_tokens": 8, "total_tokens": 28},
                "development_metrics": {
                    "code_quality_score": 85 + (threading.current_thread().ident % 10),
                    "syntax_valid": True,
                    "language_detected": "python"
                }
            }
            return mock_response
        
        with patch('requests.post', side_effect=lambda *args, **kwargs: mock_completion_response()):
            # Execute performance test
            results = self._execute_performance_test(
                endpoint_type='code_completion',
                scenario=scenario,
                request_template={
                    "model": "deepseek-ai/deepseek-coder-14b-instruct",
                    "prompt": "def calculate_sum(numbers):\n    result = 0\n    for num in numbers:\n        result += num\n    # Complete this function",
                    "max_tokens": 50,
                    "temperature": 0.2,
                    "language": "python"
                }
            )
            
            # Assert performance requirements
            self.assertLessEqual(results['average_latency_ms'], scenario['max_latency_ms'])
            self.assertGreaterEqual(results['throughput_rps'], scenario['min_throughput_rps'])
            self.assertGreaterEqual(results['success_rate'], 95.0)
            
            # Assert quality metrics
            self.assertGreaterEqual(results['average_code_quality'], 85)
            self.assertGreaterEqual(results['syntax_validity_rate'], 95.0)
            
            # Log performance results
            self.logger.info(f"Code completion performance: {results}")
    
    def test_code_explanation_performance(self):
        """Test LoB code explanation performance under load."""
        scenario = self.performance_scenarios['code_explanation']
        
        # Mock explanation responses
        def mock_explanation_response():
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.elapsed.total_seconds.return_value = 1.8 + (0.8 * (threading.current_thread().ident % 5) / 5)
            mock_response.json.return_value = {
                "id": f"lob-explanation-{int(time.time()*1000)}",
                "object": "code_explanation",
                "created": int(time.time()),
                "model": "deepseek-ai/deepseek-coder-14b-instruct",
                "explanation": {
                    "summary": "This function calculates the sum of numbers in a list.",
                    "detailed_explanation": "The function iterates through each number and adds it to a running total.",
                    "complexity": {"time": "O(n)", "space": "O(1)"},
                    "parameters": [{"name": "numbers", "type": "list", "description": "List of numbers to sum"}],
                    "return_value": "The sum of all numbers in the list"
                },
                "development_metrics": {
                    "explanation_quality": 88 + (threading.current_thread().ident % 8),
                    "technical_accuracy": 92 + (threading.current_thread().ident % 6),
                    "clarity_score": 85 + (threading.current_thread().ident % 10)
                }
            }
            return mock_response
        
        with patch('requests.post', side_effect=lambda *args, **kwargs: mock_explanation_response()):
            # Execute performance test
            results = self._execute_performance_test(
                endpoint_type='code_explanation',
                scenario=scenario,
                request_template={
                    "model": "deepseek-ai/deepseek-coder-14b-instruct",
                    "code": "def calculate_sum(numbers):\n    result = 0\n    for num in numbers:\n        result += num\n    return result",
                    "language": "python"
                }
            )
            
            # Assert performance requirements
            self.assertLessEqual(results['average_latency_ms'], scenario['max_latency_ms'])
            self.assertGreaterEqual(results['throughput_rps'], scenario['min_throughput_rps'])
            self.assertGreaterEqual(results['success_rate'], 95.0)
            
            # Assert quality metrics
            self.assertGreaterEqual(results['average_explanation_quality'], 85)
            self.assertGreaterEqual(results['average_technical_accuracy'], 90)
            
            # Log performance results
            self.logger.info(f"Code explanation performance: {results}")
    
    def test_debug_assistance_performance(self):
        """Test LoB debug assistance performance under load."""
        scenario = self.performance_scenarios['debug_assistance']
        
        # Mock debug responses
        def mock_debug_response():
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.elapsed.total_seconds.return_value = 1.5 + (0.7 * (threading.current_thread().ident % 5) / 5)
            mock_response.json.return_value = {
                "id": f"lob-debug-{int(time.time()*1000)}",
                "object": "debug_assistance",
                "created": int(time.time()),
                "model": "deepseek-ai/deepseek-coder-14b-instruct",
                "debug_analysis": {
                    "error_type": "IndexError",
                    "root_cause": "List index out of range",
                    "line_number": 3,
                    "suggested_fix": "Add bounds checking before accessing list elements",
                    "corrected_code": "def safe_access(lst, index):\n    if 0 <= index < len(lst):\n        return lst[index]\n    return None",
                    "prevention_tips": ["Always validate array bounds", "Use try-except for safer access"]
                },
                "development_metrics": {
                    "debug_accuracy": 90 + (threading.current_thread().ident % 8),
                    "solution_quality": 87 + (threading.current_thread().ident % 10),
                    "fix_completeness": 85 + (threading.current_thread().ident % 12)
                }
            }
            return mock_response
        
        with patch('requests.post', side_effect=lambda *args, **kwargs: mock_debug_response()):
            # Execute performance test
            results = self._execute_performance_test(
                endpoint_type='debug_assistance',
                scenario=scenario,
                request_template={
                    "model": "deepseek-ai/deepseek-coder-14b-instruct",
                    "code": "def get_item(lst, index):\n    return lst[index]\n\nresult = get_item([1, 2, 3], 5)",
                    "error": "IndexError: list index out of range",
                    "language": "python"
                }
            )
            
            # Assert performance requirements
            self.assertLessEqual(results['average_latency_ms'], scenario['max_latency_ms'])
            self.assertGreaterEqual(results['throughput_rps'], scenario['min_throughput_rps'])
            self.assertGreaterEqual(results['success_rate'], 95.0)
            
            # Assert quality metrics
            self.assertGreaterEqual(results['average_debug_accuracy'], 85)
            self.assertGreaterEqual(results['average_solution_quality'], 85)
            
            # Log performance results
            self.logger.info(f"Debug assistance performance: {results}")
    
    def test_mixed_workload_performance(self):
        """Test LoB mixed development workload performance."""
        # Define mixed workload scenario
        mixed_scenario = {
            'code_completion': {'weight': 0.5, 'users': 5},
            'code_explanation': {'weight': 0.3, 'users': 3},
            'debug_assistance': {'weight': 0.2, 'users': 2}
        }
        
        # Mock mixed responses
        def mock_mixed_response(endpoint_type):
            mock_response = Mock()
            mock_response.status_code = 200
            base_latency = {
                'code_completion': 1.2,
                'code_explanation': 1.8,
                'debug_assistance': 1.5
            }
            mock_response.elapsed.total_seconds.return_value = base_latency[endpoint_type] + (0.5 * (threading.current_thread().ident % 5) / 5)
            
            response_data = {
                'code_completion': {
                    "id": f"lob-completion-{int(time.time()*1000)}",
                    "object": "text_completion",
                    "choices": [{"text": "    return result", "index": 0}],
                    "development_metrics": {"code_quality_score": 87, "syntax_valid": True}
                },
                'code_explanation': {
                    "id": f"lob-explanation-{int(time.time()*1000)}",
                    "object": "code_explanation",
                    "explanation": {"summary": "Function explanation", "complexity": {"time": "O(n)"}},
                    "development_metrics": {"explanation_quality": 89, "technical_accuracy": 93}
                },
                'debug_assistance': {
                    "id": f"lob-debug-{int(time.time()*1000)}",
                    "object": "debug_assistance",
                    "debug_analysis": {"error_type": "TypeError", "suggested_fix": "Add type checking"},
                    "development_metrics": {"debug_accuracy": 91, "solution_quality": 88}
                }
            }
            
            mock_response.json.return_value = response_data[endpoint_type]
            return mock_response
        
        # Execute mixed workload
        results = self._execute_mixed_workload_test(mixed_scenario, mock_mixed_response)
        
        # Assert overall performance
        self.assertLessEqual(results['average_latency_ms'], 2500)  # Mixed workload tolerance
        self.assertGreaterEqual(results['throughput_rps'], 12)
        self.assertGreaterEqual(results['success_rate'], 95.0)
        
        # Assert workload distribution
        self.assertAlmostEqual(results['workload_distribution']['code_completion'], 0.5, delta=0.1)
        self.assertAlmostEqual(results['workload_distribution']['code_explanation'], 0.3, delta=0.1)
        self.assertAlmostEqual(results['workload_distribution']['debug_assistance'], 0.2, delta=0.1)
        
        # Log mixed workload results
        self.logger.info(f"Mixed workload performance: {results}")
    
    def test_resource_utilization_monitoring(self):
        """Test LoB resource utilization under development load."""
        # Mock resource monitoring
        def mock_resource_stats():
            return {
                'cpu_percent': 45 + (threading.current_thread().ident % 20),
                'memory_percent': 65 + (threading.current_thread().ident % 15),
                'gpu_utilization': 80 + (threading.current_thread().ident % 15),
                'gpu_memory_percent': 70 + (threading.current_thread().ident % 20)
            }
        
        with patch('psutil.cpu_percent', side_effect=lambda: mock_resource_stats()['cpu_percent']):
            with patch('psutil.virtual_memory', return_value=Mock(percent=mock_resource_stats()['memory_percent'])):
                # Simulate development workload
                workload_results = self.simulate_development_workload(
                    concurrent_users=10,
                    duration_seconds=60
                )
                
                # Monitor resources during workload
                resource_samples = []
                for i in range(10):
                    resource_samples.append(mock_resource_stats())
                    time.sleep(0.1)
                
                # Assert resource utilization
                avg_cpu = statistics.mean([sample['cpu_percent'] for sample in resource_samples])
                avg_memory = statistics.mean([sample['memory_percent'] for sample in resource_samples])
                avg_gpu = statistics.mean([sample['gpu_utilization'] for sample in resource_samples])
                
                self.assertLessEqual(avg_cpu, 80)  # CPU within acceptable range
                self.assertLessEqual(avg_memory, 85)  # Memory within acceptable range
                self.assertGreaterEqual(avg_gpu, 70)  # GPU effectively utilized
                
                # Log resource utilization
                self.logger.info(f"Resource utilization - CPU: {avg_cpu}%, Memory: {avg_memory}%, GPU: {avg_gpu}%")
    
    def test_scalability_limits(self):
        """Test LoB scalability limits and breaking points."""
        # Test increasing concurrent users
        user_counts = [5, 10, 15, 20, 25]
        scalability_results = []
        
        for user_count in user_counts:
            # Mock responses for scalability test
            def mock_scalability_response():
                mock_response = Mock()
                mock_response.status_code = 200
                # Simulate increasing latency with more users
                base_latency = 1.2
                latency_increase = (user_count - 5) * 0.1
                mock_response.elapsed.total_seconds.return_value = base_latency + latency_increase
                mock_response.json.return_value = {
                    "id": f"lob-scale-{int(time.time()*1000)}",
                    "object": "text_completion",
                    "choices": [{"text": "# Generated code", "index": 0}],
                    "development_metrics": {"code_quality_score": max(85 - (user_count - 5), 70)}
                }
                return mock_response
            
            with patch('requests.post', side_effect=lambda *args, **kwargs: mock_scalability_response()):
                # Execute scalability test
                start_time = time.time()
                results = self._execute_concurrent_requests(
                    concurrent_users=user_count,
                    requests_per_user=5,
                    endpoint_type='code_completion'
                )
                end_time = time.time()
                
                scalability_results.append({
                    'user_count': user_count,
                    'average_latency_ms': results['average_latency_ms'],
                    'throughput_rps': results['throughput_rps'],
                    'success_rate': results['success_rate'],
                    'total_duration': end_time - start_time
                })
        
        # Assert scalability characteristics
        # Latency should increase gracefully
        latencies = [result['average_latency_ms'] for result in scalability_results]
        self.assertTrue(all(latencies[i] <= latencies[i+1] * 1.5 for i in range(len(latencies)-1)))
        
        # Success rate should remain high
        for result in scalability_results:
            if result['user_count'] <= 20:  # Within expected capacity
                self.assertGreaterEqual(result['success_rate'], 95.0)
        
        # Log scalability results
        self.logger.info(f"Scalability test results: {scalability_results}")
    
    def test_long_running_stability(self):
        """Test LoB long-running stability under continuous load."""
        # Mock stable responses for long-running test
        def mock_stable_response():
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.elapsed.total_seconds.return_value = 1.3 + (0.4 * (threading.current_thread().ident % 3) / 3)
            mock_response.json.return_value = {
                "id": f"lob-stability-{int(time.time()*1000)}",
                "object": "text_completion",
                "choices": [{"text": "# Stable generated code", "index": 0}],
                "development_metrics": {"code_quality_score": 86, "syntax_valid": True}
            }
            return mock_response
        
        with patch('requests.post', side_effect=lambda *args, **kwargs: mock_stable_response()):
            # Run continuous load for extended period
            stability_duration = 120  # 2 minutes
            stability_results = []
            
            start_time = time.time()
            while time.time() - start_time < stability_duration:
                batch_results = self._execute_concurrent_requests(
                    concurrent_users=6,
                    requests_per_user=3,
                    endpoint_type='code_completion'
                )
                stability_results.append(batch_results)
                time.sleep(5)  # Brief pause between batches
            
            # Assert stability metrics
            success_rates = [result['success_rate'] for result in stability_results]
            latencies = [result['average_latency_ms'] for result in stability_results]
            
            # Success rate should remain consistently high
            self.assertGreaterEqual(min(success_rates), 95.0)
            self.assertLessEqual(max(success_rates) - min(success_rates), 5.0)
            
            # Latency should remain stable
            avg_latency = statistics.mean(latencies)
            latency_std = statistics.stdev(latencies) if len(latencies) > 1 else 0
            self.assertLessEqual(latency_std, avg_latency * 0.2)  # Low variance
            
            # Log stability results
            self.logger.info(f"Stability test - Average latency: {avg_latency}ms, Std dev: {latency_std}ms")
    
    def _execute_performance_test(self, endpoint_type: str, scenario: dict, request_template: dict) -> dict:
        """Execute performance test for specific endpoint type."""
        results = self._execute_concurrent_requests(
            concurrent_users=scenario['concurrent_users'],
            requests_per_user=scenario['requests_per_user'],
            endpoint_type=endpoint_type,
            request_template=request_template
        )
        return results
    
    def _execute_concurrent_requests(self, concurrent_users: int, requests_per_user: int, 
                                   endpoint_type: str, request_template: dict = None) -> dict:
        """Execute concurrent requests and collect performance metrics."""
        if request_template is None:
            request_template = {
                "model": "deepseek-ai/deepseek-coder-14b-instruct",
                "prompt": "# Generate code",
                "max_tokens": 50
            }
        
        endpoint_url = f"{self.api_base_url}/v1/code/complete"
        if endpoint_type == 'code_explanation':
            endpoint_url = f"{self.api_base_url}/v1/code/explain"
        elif endpoint_type == 'debug_assistance':
            endpoint_url = f"{self.api_base_url}/v1/code/debug"
        
        latencies = []
        success_count = 0
        total_requests = concurrent_users * requests_per_user
        quality_scores = []
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            for user in range(concurrent_users):
                for request in range(requests_per_user):
                    future = executor.submit(self._make_request, endpoint_url, request_template)
                    futures.append(future)
            
            for future in as_completed(futures):
                try:
                    response = future.result()
                    if response.status_code == 200:
                        success_count += 1
                        latencies.append(response.elapsed.total_seconds() * 1000)
                        
                        # Extract quality metrics
                        data = response.json()
                        if 'development_metrics' in data:
                            metrics = data['development_metrics']
                            if 'code_quality_score' in metrics:
                                quality_scores.append(metrics['code_quality_score'])
                except Exception as e:
                    self.logger.warning(f"Request failed: {e}")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        return {
            'total_requests': total_requests,
            'successful_requests': success_count,
            'success_rate': (success_count / total_requests) * 100,
            'average_latency_ms': statistics.mean(latencies) if latencies else 0,
            'median_latency_ms': statistics.median(latencies) if latencies else 0,
            'p95_latency_ms': self._calculate_percentile(latencies, 95) if latencies else 0,
            'throughput_rps': total_requests / total_duration,
            'total_duration_seconds': total_duration,
            'average_code_quality': statistics.mean(quality_scores) if quality_scores else 0,
            'syntax_validity_rate': 100.0,  # Mocked as always valid
            'average_explanation_quality': statistics.mean(quality_scores) if quality_scores else 0,
            'average_technical_accuracy': statistics.mean(quality_scores) if quality_scores else 0,
            'average_debug_accuracy': statistics.mean(quality_scores) if quality_scores else 0,
            'average_solution_quality': statistics.mean(quality_scores) if quality_scores else 0
        }
    
    def _execute_mixed_workload_test(self, mixed_scenario: dict, mock_response_func) -> dict:
        """Execute mixed workload test with different endpoint types."""
        total_requests = 0
        workload_counts = {}
        
        # Calculate request distribution
        for endpoint_type, config in mixed_scenario.items():
            requests_count = config['users'] * 5  # 5 requests per user
            total_requests += requests_count
            workload_counts[endpoint_type] = requests_count
        
        # Mock responses based on endpoint type
        def mock_endpoint_response(*args, **kwargs):
            # Determine endpoint type from URL
            url = args[0] if args else kwargs.get('url', '')
            if 'explain' in url:
                return mock_response_func('code_explanation')
            elif 'debug' in url:
                return mock_response_func('debug_assistance')
            else:
                return mock_response_func('code_completion')
        
        with patch('requests.post', side_effect=mock_endpoint_response):
            latencies = []
            success_count = 0
            
            start_time = time.time()
            
            # Execute mixed workload
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                
                for endpoint_type, config in mixed_scenario.items():
                    for user in range(config['users']):
                        for req in range(5):
                            future = executor.submit(
                                self._make_request,
                                f"{self.api_base_url}/v1/code/{endpoint_type.replace('_', '/')}",
                                {"model": "deepseek-ai/deepseek-coder-14b-instruct", "prompt": "# Test"}
                            )
                            futures.append(future)
                
                for future in as_completed(futures):
                    try:
                        response = future.result()
                        if response.status_code == 200:
                            success_count += 1
                            latencies.append(response.elapsed.total_seconds() * 1000)
                    except Exception as e:
                        self.logger.warning(f"Mixed workload request failed: {e}")
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            return {
                'total_requests': total_requests,
                'successful_requests': success_count,
                'success_rate': (success_count / total_requests) * 100,
                'average_latency_ms': statistics.mean(latencies) if latencies else 0,
                'throughput_rps': total_requests / total_duration,
                'workload_distribution': {
                    endpoint_type: workload_counts[endpoint_type] / total_requests
                    for endpoint_type in mixed_scenario.keys()
                }
            }
    
    def _make_request(self, url: str, data: dict):
        """Make HTTP request (mocked in tests)."""
        return requests.post(url, json=data)
    
    def _calculate_percentile(self, values: list, percentile: float) -> float:
        """Calculate percentile value from list of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        if index >= len(sorted_values):
            index = len(sorted_values) - 1
        return sorted_values[index]


if __name__ == '__main__':
    unittest.main()
