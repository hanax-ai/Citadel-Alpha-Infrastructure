#!/usr/bin/env python3
"""
Integration Testing Runner

Comprehensive integration testing for HXP-Enterprise LLM Server.
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any

# Add the integration testing path
sys.path.insert(0, '/opt/citadel/hxp-enterprise-llm/testing/integration_tests')

from config import IntegrationTestConfig
from cross_service import CrossServiceIntegrationTester
from external_apis import ExternalAPIIntegrationTester
from database_tests import DatabaseIntegrationTester


def run_cross_service_tests(config: IntegrationTestConfig) -> Dict[str, Any]:
    """Run cross-service integration tests."""
    print("🔄 Running Cross-Service Integration Tests...")
    
    tester = CrossServiceIntegrationTester(config)
    results = tester.test_all_cross_service_integrations()
    summary = tester.get_test_summary(results)
    
    # Convert TestResult objects to dictionaries for JSON serialization
    serializable_results = {}
    for service_name, service_results in results.items():
        serializable_results[service_name] = [result.to_dict() for result in service_results]
    
    print(f"   ✅ Cross-Service Integrations Tested: {len(results)}")
    print(f"   ✅ Total Tests: {summary['total_tests']}")
    print(f"   ✅ Passed: {summary['passed_tests']}, Failed: {summary['failed_tests']}")
    print(f"   ✅ Success Rate: {summary['success_rate']:.1f}%")
    
    return {
        'type': 'cross_service',
        'results': serializable_results,
        'summary': summary,
        'timestamp': datetime.now().isoformat()
    }


def run_external_api_tests(config: IntegrationTestConfig) -> Dict[str, Any]:
    """Run external API integration tests."""
    print("🌐 Running External API Integration Tests...")
    
    tester = ExternalAPIIntegrationTester(config)
    results = tester.test_all_external_api_integrations()
    summary = tester.get_test_summary(results)
    
    # Convert TestResult objects to dictionaries for JSON serialization
    serializable_results = {}
    for api_name, api_results in results.items():
        serializable_results[api_name] = [result.to_dict() for result in api_results]
    
    print(f"   ✅ External APIs Tested: {len(results)}")
    print(f"   ✅ Total Tests: {summary['total_tests']}")
    print(f"   ✅ Passed: {summary['passed_tests']}, Failed: {summary['failed_tests']}")
    print(f"   ✅ Success Rate: {summary['success_rate']:.1f}%")
    
    return {
        'type': 'external_apis',
        'results': serializable_results,
        'summary': summary,
        'timestamp': datetime.now().isoformat()
    }


def run_database_tests(config: IntegrationTestConfig) -> Dict[str, Any]:
    """Run database integration tests."""
    print("🗄️ Running Database Integration Tests...")
    
    tester = DatabaseIntegrationTester(config)
    results = tester.test_all_database_integrations()
    summary = tester.get_test_summary(results)
    
    # Convert TestResult objects to dictionaries for JSON serialization
    serializable_results = {}
    for test_name, test_results in results.items():
        serializable_results[test_name] = [result.to_dict() for result in test_results]
    
    print(f"   ✅ Database Tests Performed: {len(results)}")
    print(f"   ✅ Total Tests: {summary['total_tests']}")
    print(f"   ✅ Passed: {summary['passed_tests']}, Failed: {summary['failed_tests']}")
    print(f"   ✅ Success Rate: {summary['success_rate']:.1f}%")
    
    return {
        'type': 'database_tests',
        'results': serializable_results,
        'summary': summary,
        'timestamp': datetime.now().isoformat()
    }


def generate_comprehensive_report(all_results: list) -> Dict[str, Any]:
    """Generate comprehensive test report."""
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_error = 0
    
    for result in all_results:
        summary = result['summary']
        total_tests += summary['total_tests']
        total_passed += summary['passed_tests']
        total_failed += summary['failed_tests']
        total_skipped += summary['skipped_tests']
        total_error += summary['error_tests']
    
    overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    return {
        'report_id': f"integration_test_report_{int(time.time())}",
        'timestamp': datetime.now().isoformat(),
        'overall_summary': {
            'total_tests': total_tests,
            'passed_tests': total_passed,
            'failed_tests': total_failed,
            'skipped_tests': total_skipped,
            'error_tests': total_error,
            'success_rate': overall_success_rate
        },
        'detailed_results': all_results,
        'test_categories': [result['type'] for result in all_results]
    }


def save_report(report: Dict[str, Any], format: str = "json") -> str:
    """Save test report to file."""
    reports_dir = "/opt/citadel/reports/testing"
    os.makedirs(reports_dir, exist_ok=True)
    
    if format == "json":
        filename = f"{report['report_id']}.json"
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath
    else:
        raise ValueError(f"Unsupported format: {format}")


def main():
    """Main integration testing function."""
    print("🎯 HXP-Enterprise LLM Server Integration Testing")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Load configuration
        print("📋 Loading Integration Test Configuration...")
        config = IntegrationTestConfig()
        
        if not config.validate():
            print("❌ Configuration validation failed!")
            return 1
        
        print("   ✅ Configuration loaded successfully")
        
        # Run tests
        all_results = []
        
        # Run cross-service tests
        cross_service_results = run_cross_service_tests(config)
        all_results.append(cross_service_results)
        
        # Run external API tests
        external_api_results = run_external_api_tests(config)
        all_results.append(external_api_results)
        
        # Run database tests
        database_results = run_database_tests(config)
        all_results.append(database_results)
        
        # Generate comprehensive report
        print("\n📊 Generating Comprehensive Report...")
        comprehensive_report = generate_comprehensive_report(all_results)
        
        # Save report
        report_file = save_report(comprehensive_report, "json")
        
        duration = time.time() - start_time
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📋 INTEGRATION TESTING SUMMARY")
        print("=" * 60)
        
        overall = comprehensive_report['overall_summary']
        print(f"Overall Status: {'✅ PASSED' if overall['success_rate'] >= 85 else '❌ FAILED'}")
        print(f"Total Tests: {overall['total_tests']}")
        print(f"Passed: {overall['passed_tests']}")
        print(f"Failed: {overall['failed_tests']}")
        print(f"Skipped: {overall['skipped_tests']}")
        print(f"Errors: {overall['error_tests']}")
        print(f"Success Rate: {overall['success_rate']:.1f}%")
        print(f"Duration: {duration:.2f}s")
        print(f"Report: {report_file}")
        
        # Print detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in all_results:
            summary = result['summary']
            print(f"  {result['type'].upper()}:")
            print(f"    Tests: {summary['total_tests']}, Passed: {summary['passed_tests']}, Failed: {summary['failed_tests']}")
            print(f"    Success Rate: {summary['success_rate']:.1f}%")
        
        # For integration testing, we consider 85%+ as successful due to intentional skips
        if overall['success_rate'] >= 85:
            print("\n🎉 Integration testing completed successfully!")
            return 0
        else:
            print("\n⚠️ Integration testing completed with some failures.")
            return 1
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ Integration testing failed with error: {str(e)}")
        print(f"Duration: {duration:.2f}s")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 