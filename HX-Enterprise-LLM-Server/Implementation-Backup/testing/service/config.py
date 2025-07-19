"""
Service Testing Configuration

Manages configuration for service-level testing including unit tests, load tests, security tests, and reliability tests.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class CoverageConfig:
    """Unit test coverage configuration."""
    minimum_line_coverage: int
    minimum_branch_coverage: int
    minimum_function_coverage: int
    coverage_report_format: str


@dataclass
class ExecutionConfig:
    """Test execution configuration."""
    timeout_seconds: int
    parallel_workers: int
    retry_failed: bool
    fail_fast: bool


@dataclass
class ReportingConfig:
    """Test reporting configuration."""
    output_format: str
    output_directory: str
    include_coverage: bool
    include_performance: bool


@dataclass
class UnitTestConfig:
    """Unit test configuration."""
    coverage: CoverageConfig
    execution: ExecutionConfig
    reporting: ReportingConfig


@dataclass
class LoadTestScenario:
    """Load test scenario configuration."""
    duration_seconds: int
    ramp_up_time_seconds: int
    concurrent_users: int
    target_rps: int
    error_threshold_percent: int


@dataclass
class LoadTestConfig:
    """Load test configuration."""
    scenarios: Dict[str, LoadTestScenario]
    monitoring: Dict[str, Any]
    reporting: ReportingConfig


@dataclass
class SecurityTestConfig:
    """Security test configuration."""
    vulnerability_scanning: Dict[str, Any]
    penetration_testing: Dict[str, Any]
    compliance_testing: Dict[str, Any]
    reporting: ReportingConfig


@dataclass
class ReliabilityTestConfig:
    """Reliability test configuration."""
    availability_testing: Dict[str, Any]
    recovery_testing: Dict[str, Any]
    chaos_testing: Dict[str, Any]
    reporting: ReportingConfig


class ServiceTestConfig:
    """Service testing configuration."""
    
    def __init__(self):
        """Initialize service test configuration."""
        self._load_config()
        self._load_environment_variables()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        config_path = "/opt/citadel/config/testing/service_tests.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                if config_data and 'service_tests' in config_data:
                    self._config = config_data['service_tests']
                else:
                    self._config = {}
        else:
            self._config = {}
    
    def _load_environment_variables(self) -> None:
        """Load environment variables."""
        # Load from .env file first
        env_file = "/opt/citadel/config/testing/.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        
        self.test_environment = os.environ.get('SERVICE_TEST_ENVIRONMENT', 'development')
        self.test_timeout = int(os.environ.get('SERVICE_TEST_TIMEOUT', '300'))
        self.test_retries = int(os.environ.get('SERVICE_TEST_RETRIES', '3'))
        self.concurrent_requests = int(os.environ.get('SERVICE_TEST_CONCURRENT_REQUESTS', '50'))
    
    def get_unit_test_config(self) -> Optional[UnitTestConfig]:
        """Get unit test configuration."""
        if 'unit_tests' in self._config:
            unit_config = self._config['unit_tests']
            
            coverage = CoverageConfig(
                minimum_line_coverage=unit_config.get('coverage', {}).get('minimum_line_coverage', 95),
                minimum_branch_coverage=unit_config.get('coverage', {}).get('minimum_branch_coverage', 90),
                minimum_function_coverage=unit_config.get('coverage', {}).get('minimum_function_coverage', 95),
                coverage_report_format=unit_config.get('coverage', {}).get('coverage_report_format', 'html')
            )
            
            execution = ExecutionConfig(
                timeout_seconds=unit_config.get('execution', {}).get('timeout_seconds', 60),
                parallel_workers=unit_config.get('execution', {}).get('parallel_workers', 4),
                retry_failed=unit_config.get('execution', {}).get('retry_failed', True),
                fail_fast=unit_config.get('execution', {}).get('fail_fast', False)
            )
            
            reporting = ReportingConfig(
                output_format=unit_config.get('reporting', {}).get('output_format', 'html'),
                output_directory=unit_config.get('reporting', {}).get('output_directory', '/opt/citadel/reports/testing/unit_tests'),
                include_coverage=unit_config.get('reporting', {}).get('include_coverage', True),
                include_performance=unit_config.get('reporting', {}).get('include_performance', True)
            )
            
            return UnitTestConfig(coverage=coverage, execution=execution, reporting=reporting)
        return None
    
    def get_load_test_config(self) -> Optional[LoadTestConfig]:
        """Get load test configuration."""
        if 'load_tests' in self._config:
            load_config = self._config['load_tests']
            
            scenarios = {}
            for scenario_name, scenario_data in load_config.get('scenarios', {}).items():
                scenarios[scenario_name] = LoadTestScenario(
                    duration_seconds=scenario_data.get('duration_seconds', 300),
                    ramp_up_time_seconds=scenario_data.get('ramp_up_time_seconds', 60),
                    concurrent_users=scenario_data.get('concurrent_users', 50),
                    target_rps=scenario_data.get('target_rps', 25),
                    error_threshold_percent=scenario_data.get('error_threshold_percent', 1)
                )
            
            reporting = ReportingConfig(
                output_format=load_config.get('reporting', {}).get('output_format', 'html'),
                output_directory=load_config.get('reporting', {}).get('output_directory', '/opt/citadel/reports/testing/load_tests'),
                include_coverage=False,
                include_performance=load_config.get('reporting', {}).get('include_performance_graphs', True)
            )
            
            return LoadTestConfig(
                scenarios=scenarios,
                monitoring=load_config.get('monitoring', {}),
                reporting=reporting
            )
        return None
    
    def get_security_test_config(self) -> Optional[SecurityTestConfig]:
        """Get security test configuration."""
        if 'security_tests' in self._config:
            security_config = self._config['security_tests']
            
            reporting = ReportingConfig(
                output_format=security_config.get('reporting', {}).get('output_format', 'html'),
                output_directory=security_config.get('reporting', {}).get('output_directory', '/opt/citadel/reports/testing/security_tests'),
                include_coverage=False,
                include_performance=False
            )
            
            return SecurityTestConfig(
                vulnerability_scanning=security_config.get('vulnerability_scanning', {}),
                penetration_testing=security_config.get('penetration_testing', {}),
                compliance_testing=security_config.get('compliance_testing', {}),
                reporting=reporting
            )
        return None
    
    def get_reliability_test_config(self) -> Optional[ReliabilityTestConfig]:
        """Get reliability test configuration."""
        if 'reliability_tests' in self._config:
            reliability_config = self._config['reliability_tests']
            
            reporting = ReportingConfig(
                output_format=reliability_config.get('reporting', {}).get('output_format', 'html'),
                output_directory=reliability_config.get('reporting', {}).get('output_directory', '/opt/citadel/reports/testing/reliability_tests'),
                include_coverage=False,
                include_performance=False
            )
            
            return ReliabilityTestConfig(
                availability_testing=reliability_config.get('availability_testing', {}),
                recovery_testing=reliability_config.get('recovery_testing', {}),
                chaos_testing=reliability_config.get('chaos_testing', {}),
                reporting=reporting
            )
        return None
    
    def get_performance_targets(self) -> Dict[str, Any]:
        """Get service performance targets."""
        return {
            'latency_ms': int(os.environ.get('SERVICE_TARGET_LATENCY_MS', '2000')),
            'throughput_rps': int(os.environ.get('SERVICE_TARGET_THROUGHPUT_RPS', '50')),
            'memory_gb': int(os.environ.get('SERVICE_TARGET_MEMORY_GB', '90')),
            'cpu_cores': int(os.environ.get('SERVICE_TARGET_CPU_CORES', '8'))
        }
    
    def validate(self) -> bool:
        """Validate configuration."""
        try:
            # Check required environment variables
            required_env_vars = ['SERVICE_TEST_ENVIRONMENT']
            for var in required_env_vars:
                if not os.environ.get(var):
                    return False
            
            # Check configuration structure
            if not self._config:
                return False
            
            # Check unit test configuration
            unit_config = self.get_unit_test_config()
            if not unit_config:
                return False
            
            # Check load test configuration
            load_config = self.get_load_test_config()
            if not load_config:
                return False
            
            # Check security test configuration
            security_config = self.get_security_test_config()
            if not security_config:
                return False
            
            # Check reliability test configuration
            reliability_config = self.get_reliability_test_config()
            if not reliability_config:
                return False
            
            return True
        except Exception:
            return False 