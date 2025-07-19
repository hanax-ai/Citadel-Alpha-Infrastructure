#!/usr/bin/env python3
"""
HXP-Enterprise LLM Server Test Framework Validation Script

Comprehensive validation of the test framework implementation.
"""

import os
import sys
import time
import json
from datetime import datetime

# Add the framework to the path
sys.path.insert(0, '/opt/citadel/hxp-enterprise-llm/testing/framework')

from config.test_framework_config import TestFrameworkConfig
from environment.test_environment import TestEnvironment
from runner.test_runner import TestRunner
from reporting.test_reporter import TestReporter


def validate_configuration():
    """Validate test framework configuration."""
    print("🔧 Validating Configuration...")
    
    try:
        config = TestFrameworkConfig()
        
        # Test configuration validation
        if not config.validate():
            return False, "Configuration validation failed"
        
        # Test configuration properties
        required_props = ['name', 'version', 'environment', 'coverage_threshold']
        for prop in required_props:
            if not hasattr(config, prop):
                return False, f"Missing configuration property: {prop}"
        
        print(f"   ✅ Configuration: {config.name} v{config.version}")
        print(f"   ✅ Environment: {config.environment}")
        print(f"   ✅ Coverage Threshold: {config.coverage_threshold}%")
        
        return True, "Configuration validation successful"
        
    except Exception as e:
        return False, f"Configuration validation error: {str(e)}"


def validate_environment():
    """Validate test environment."""
    print("🌍 Validating Environment...")
    
    try:
        env = TestEnvironment()
        
        # Test environment variables
        test_env = env.get_environment_variable('TEST_ENVIRONMENT', 'development')
        if test_env != 'development':
            return False, f"Unexpected environment: {test_env}"
        
        # Test server info
        server_info = env.get_server_info()
        if not all(key in server_info for key in ['hostname', 'ip', 'environment']):
            return False, "Missing server information"
        
        # Test external services config
        services = env.get_external_services()
        required_services = ['database', 'vector_db', 'metrics']
        for service in required_services:
            if service not in services:
                return False, f"Missing service configuration: {service}"
        
        print(f"   ✅ Server: {server_info['hostname']} ({server_info['ip']})")
        print(f"   ✅ Environment: {server_info['environment']}")
        print(f"   ✅ External Services: {len(services)} configured")
        
        return True, "Environment validation successful"
        
    except Exception as e:
        return False, f"Environment validation error: {str(e)}"


def validate_runner():
    """Validate test runner."""
    print("🏃 Validating Test Runner...")
    
    try:
        runner = TestRunner()
        
        # Test runner validation
        if not runner.validate():
            return False, "Test runner validation failed"
        
        # Test simple test execution
        test_path = "/opt/citadel/hxp-enterprise-llm/testing"
        results = runner.run_tests(test_path, "all")
        
        required_keys = ['status', 'total_tests', 'passed', 'failed', 'skipped', 'duration']
        for key in required_keys:
            if key not in results:
                return False, f"Missing result key: {key}"
        
        print(f"   ✅ Test Execution: {results['status']}")
        print(f"   ✅ Total Tests: {results['total_tests']}")
        print(f"   ✅ Passed: {results['passed']}, Failed: {results['failed']}, Skipped: {results['skipped']}")
        print(f"   ✅ Duration: {results['duration']:.2f}s")
        
        return True, "Test runner validation successful"
        
    except Exception as e:
        return False, f"Test runner validation error: {str(e)}"


def validate_reporter():
    """Validate test reporter."""
    print("📊 Validating Test Reporter...")
    
    try:
        reporter = TestReporter()
        
        # Test report generation
        test_results = {
            'total_tests': 10,
            'passed': 8,
            'failed': 1,
            'skipped': 1,
            'duration': 5.5
        }
        
        report = reporter.generate_report(test_results, "validation_suite")
        
        # Test report properties
        required_props = ['report_id', 'timestamp', 'test_suite', 'total_tests', 'passed', 'failed', 'skipped', 'duration']
        for prop in required_props:
            if not hasattr(report, prop):
                return False, f"Missing report property: {prop}"
        
        # Test report saving
        json_filepath = reporter.save_report(report, "json")
        if not os.path.exists(json_filepath):
            return False, "Failed to save JSON report"
        
        html_filepath = reporter.save_report(report, "html")
        if not os.path.exists(html_filepath):
            return False, "Failed to save HTML report"
        
        print(f"   ✅ Report Generation: {report.report_id}")
        print(f"   ✅ JSON Report: {os.path.basename(json_filepath)}")
        print(f"   ✅ HTML Report: {os.path.basename(html_filepath)}")
        
        return True, "Test reporter validation successful"
        
    except Exception as e:
        return False, f"Test reporter validation error: {str(e)}"


def validate_directory_structure():
    """Validate directory structure."""
    print("📁 Validating Directory Structure...")
    
    required_dirs = [
        "/opt/citadel/hxp-enterprise-llm/testing/component",
        "/opt/citadel/hxp-enterprise-llm/testing/integration_tests",
        "/opt/citadel/hxp-enterprise-llm/testing/service",
        "/opt/citadel/hxp-enterprise-llm/testing/utilities",
        "/opt/citadel/hxp-enterprise-llm/testing/framework",
        "/opt/citadel/config/testing",
        "/opt/citadel/reports/testing"
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            return False, f"Missing directory: {dir_path}"
    
    print(f"   ✅ All {len(required_dirs)} required directories exist")
    return True, "Directory structure validation successful"


def validate_configuration_files():
    """Validate configuration files."""
    print("📄 Validating Configuration Files...")
    
    config_files = [
        "/opt/citadel/config/testing/test_framework.yaml",
        "/opt/citadel/config/testing/.env"
    ]
    
    for config_file in config_files:
        if not os.path.exists(config_file):
            return False, f"Missing configuration file: {config_file}"
        
        # Check file size
        if os.path.getsize(config_file) == 0:
            return False, f"Empty configuration file: {config_file}"
    
    print(f"   ✅ All {len(config_files)} configuration files exist and are non-empty")
    return True, "Configuration files validation successful"


def main():
    """Main validation function."""
    print("🎯 HXP-Enterprise LLM Server Test Framework Validation")
    print("=" * 60)
    
    start_time = time.time()
    
    # Validation functions
    validations = [
        validate_directory_structure,
        validate_configuration_files,
        validate_configuration,
        validate_environment,
        validate_runner,
        validate_reporter
    ]
    
    results = []
    all_passed = True
    
    for validation_func in validations:
        try:
            success, message = validation_func()
            results.append({
                'function': validation_func.__name__,
                'success': success,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
            
            if not success:
                all_passed = False
                print(f"   ❌ {message}")
            else:
                print(f"   ✅ {message}")
                
        except Exception as e:
            all_passed = False
            error_msg = f"Validation error: {str(e)}"
            results.append({
                'function': validation_func.__name__,
                'success': False,
                'message': error_msg,
                'timestamp': datetime.now().isoformat()
            })
            print(f"   ❌ {error_msg}")
    
    duration = time.time() - start_time
    
    # Generate validation report
    validation_report = {
        'validation_id': f"validation_{int(time.time())}",
        'timestamp': datetime.now().isoformat(),
        'overall_success': all_passed,
        'total_validations': len(validations),
        'passed_validations': len([r for r in results if r['success']]),
        'failed_validations': len([r for r in results if not r['success']]),
        'duration': duration,
        'results': results
    }
    
    # Save validation report
    report_file = f"/opt/citadel/reports/testing/{validation_report['validation_id']}.json"
    with open(report_file, 'w') as f:
        json.dump(validation_report, f, indent=2)
    
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Overall Status: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    print(f"Total Validations: {len(validations)}")
    print(f"Passed: {validation_report['passed_validations']}")
    print(f"Failed: {validation_report['failed_validations']}")
    print(f"Duration: {duration:.2f}s")
    print(f"Report: {report_file}")
    
    if all_passed:
        print("\n🎉 All validations passed! Test framework is ready for use.")
        return 0
    else:
        print("\n⚠️  Some validations failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 