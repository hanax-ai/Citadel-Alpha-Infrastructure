"""
Framework Validation Tests

Self-testing framework for validating the test framework functionality.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the framework to the path
sys.path.insert(0, '/opt/citadel/hxp-enterprise-llm/testing/framework')

from config.test_framework_config import TestFrameworkConfig
from environment.test_environment import TestEnvironment
from runner.test_runner import TestRunner
from reporting.test_reporter import TestReporter


class TestFrameworkConfigValidation(unittest.TestCase):
    """Test framework configuration validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = TestFrameworkConfig()
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        self.assertIsNotNone(self.config)
        self.assertEqual(self.config.name, "HXP-Enterprise-LLM-Test-Framework")
        self.assertEqual(self.config.version, "1.0.0")
    
    def test_config_validation(self):
        """Test configuration validation."""
        self.assertTrue(self.config.validate())
    
    def test_coverage_config(self):
        """Test coverage configuration."""
        coverage_config = self.config.get_coverage_config()
        self.assertIn('minimum_line_coverage', coverage_config)
        self.assertIn('minimum_branch_coverage', coverage_config)
        self.assertIn('minimum_function_coverage', coverage_config)
    
    def test_performance_config(self):
        """Test performance configuration."""
        perf_config = self.config.get_performance_config()
        self.assertIn('latency_threshold_ms', perf_config)
        self.assertIn('throughput_threshold_rps', perf_config)
        self.assertIn('memory_limit_gb', perf_config)
    
    def test_security_config(self):
        """Test security configuration."""
        security_config = self.config.get_security_config()
        self.assertIn('vulnerability_threshold', security_config)
        self.assertIn('security_test_coverage', security_config)
        self.assertIn('compliance_score', security_config)


class TestEnvironmentValidation(unittest.TestCase):
    """Test environment validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.env = TestEnvironment()
    
    def test_environment_initialization(self):
        """Test environment initialization."""
        self.assertIsNotNone(self.env)
    
    def test_environment_variables(self):
        """Test environment variable loading."""
        # Test that we can get environment variables
        test_env = self.env.get_environment_variable('TEST_ENVIRONMENT', 'development')
        self.assertEqual(test_env, 'development')
    
    def test_server_info(self):
        """Test server information retrieval."""
        server_info = self.env.get_server_info()
        self.assertIn('hostname', server_info)
        self.assertIn('ip', server_info)
        self.assertIn('environment', server_info)
    
    def test_external_services_config(self):
        """Test external services configuration."""
        services = self.env.get_external_services()
        self.assertIn('database', services)
        self.assertIn('vector_db', services)
        self.assertIn('metrics', services)


class TestRunnerValidation(unittest.TestCase):
    """Test runner validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.runner = TestRunner()
    
    def test_runner_initialization(self):
        """Test runner initialization."""
        self.assertIsNotNone(self.runner)
    
    def test_runner_validation(self):
        """Test runner validation."""
        self.assertTrue(self.runner.validate())
    
    def test_simple_test_execution(self):
        """Test simple test execution."""
        test_path = "/opt/citadel/hxp-enterprise-llm/testing"
        results = self.runner.run_tests(test_path, "all")
        
        self.assertIn('status', results)
        self.assertIn('total_tests', results)
        self.assertIn('passed', results)
        self.assertIn('failed', results)
        self.assertIn('skipped', results)
        self.assertIn('duration', results)


class TestReporterValidation(unittest.TestCase):
    """Test reporter validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.reporter = TestReporter()
    
    def test_reporter_initialization(self):
        """Test reporter initialization."""
        self.assertIsNotNone(self.reporter)
    
    def test_report_generation(self):
        """Test report generation."""
        test_results = {
            'total_tests': 10,
            'passed': 8,
            'failed': 1,
            'skipped': 1,
            'duration': 5.5
        }
        
        report = self.reporter.generate_report(test_results, "test_suite")
        
        self.assertEqual(report.total_tests, 10)
        self.assertEqual(report.passed, 8)
        self.assertEqual(report.failed, 1)
        self.assertEqual(report.skipped, 1)
        self.assertEqual(report.duration, 5.5)
    
    def test_report_saving(self):
        """Test report saving."""
        test_results = {
            'total_tests': 5,
            'passed': 5,
            'failed': 0,
            'skipped': 0,
            'duration': 2.0
        }
        
        report = self.reporter.generate_report(test_results, "test_suite")
        filepath = self.reporter.save_report(report, "json")
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.json'))


class TestFrameworkIntegration(unittest.TestCase):
    """Test framework integration."""
    
    def test_framework_imports(self):
        """Test that all framework modules can be imported."""
        try:
            from config.test_framework_config import TestFrameworkConfig
            from environment.test_environment import TestEnvironment
            from runner.test_runner import TestRunner
            from reporting.test_reporter import TestReporter
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import framework modules: {e}")
    
    def test_directory_structure(self):
        """Test that required directory structure exists."""
        required_dirs = [
            "/opt/citadel/hxp-enterprise-llm/testing/component",
            "/opt/citadel/hxp-enterprise-llm/testing/integration_tests",
            "/opt/citadel/hxp-enterprise-llm/testing/service",
            "/opt/citadel/hxp-enterprise-llm/testing/utilities",
            "/opt/citadel/config/testing",
            "/opt/citadel/reports/testing"
        ]
        
        for dir_path in required_dirs:
            self.assertTrue(os.path.exists(dir_path), f"Directory not found: {dir_path}")
    
    def test_configuration_files(self):
        """Test that configuration files exist."""
        config_files = [
            "/opt/citadel/config/testing/test_framework.yaml",
            "/opt/citadel/config/testing/.env"
        ]
        
        for config_file in config_files:
            self.assertTrue(os.path.exists(config_file), f"Config file not found: {config_file}")


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestFrameworkConfigValidation))
    test_suite.addTest(unittest.makeSuite(TestEnvironmentValidation))
    test_suite.addTest(unittest.makeSuite(TestRunnerValidation))
    test_suite.addTest(unittest.makeSuite(TestReporterValidation))
    test_suite.addTest(unittest.makeSuite(TestFrameworkIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful()) 