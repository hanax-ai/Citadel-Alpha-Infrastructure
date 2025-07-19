#!/usr/bin/env python3
"""
Component Testing Runner

Comprehensive component testing for HXP-Enterprise LLM Server.
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any

# Add the component testing path
sys.path.insert(0, '/opt/citadel/hxp-enterprise-llm/testing/component')

from config import ComponentTestConfig
from ai_models_tests import AIModelComponentTester
from infrastructure_tests import InfrastructureComponentTester


def run_ai_model_tests(config: ComponentTestConfig) -> Dict[str, Any]:
    """Run AI model component tests."""
    print("🤖 Running AI Model Component Tests...")
    
    tester = AIModelComponentTester(config)
    results = tester.test_all_models()
    summary = tester.get_test_summary(results)
    
    # Convert TestResult objects to dictionaries for JSON serialization
    serializable_results = {}
    for model_name, model_results in results.items():
        serializable_results[model_name] = [result.to_dict() for result in model_results]
    
    print(f"   ✅ AI Models Tested: {len(results)}")
    print(f"   ✅ Total Tests: {summary['total_tests']}")
    print(f"   ✅ Passed: {summary['passed_tests']}, Failed: {summary['failed_tests']}")
    print(f"   ✅ Success Rate: {summary['success_rate']:.1f}%")
    
    return {
        'type': 'ai_models',
        'results': serializable_results,
        'summary': summary,
        'timestamp': datetime.now().isoformat()
    }


def run_infrastructure_tests(config: ComponentTestConfig) -> Dict[str, Any]:
    """Run infrastructure component tests."""
    print("🏗️ Running Infrastructure Component Tests...")
    
    tester = InfrastructureComponentTester(config)
    results = tester.test_all_infrastructure()
    summary = tester.get_test_summary(results)
    
    # Convert TestResult objects to dictionaries for JSON serialization
    serializable_results = {}
    for component_name, component_results in results.items():
        serializable_results[component_name] = [result.to_dict() for result in component_results]
    
    print(f"   ✅ Infrastructure Components Tested: {len(results)}")
    print(f"   ✅ Total Tests: {summary['total_tests']}")
    print(f"   ✅ Passed: {summary['passed_tests']}, Failed: {summary['failed_tests']}")
    print(f"   ✅ Success Rate: {summary['success_rate']:.1f}%")
    
    return {
        'type': 'infrastructure',
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
        'report_id': f"component_test_report_{int(time.time())}",
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
    """Main component testing function."""
    print("🎯 HXP-Enterprise LLM Server Component Testing")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Load configuration
        print("📋 Loading Component Test Configuration...")
        config = ComponentTestConfig()
        
        if not config.validate():
            print("❌ Configuration validation failed!")
            return 1
        
        print("   ✅ Configuration loaded successfully")
        
        # Run tests
        all_results = []
        
        # Run AI model tests
        ai_model_results = run_ai_model_tests(config)
        all_results.append(ai_model_results)
        
        # Run infrastructure tests
        infrastructure_results = run_infrastructure_tests(config)
        all_results.append(infrastructure_results)
        
        # Generate comprehensive report
        print("\n📊 Generating Comprehensive Report...")
        comprehensive_report = generate_comprehensive_report(all_results)
        
        # Save report
        report_file = save_report(comprehensive_report, "json")
        
        duration = time.time() - start_time
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📋 COMPONENT TESTING SUMMARY")
        print("=" * 60)
        
        overall = comprehensive_report['overall_summary']
        print(f"Overall Status: {'✅ PASSED' if overall['success_rate'] >= 95 else '❌ FAILED'}")
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
        
        if overall['success_rate'] >= 95:
            print("\n🎉 Component testing completed successfully!")
            return 0
        else:
            print("\n⚠️ Component testing completed with some failures.")
            return 1
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ Component testing failed with error: {str(e)}")
        print(f"Duration: {duration:.2f}s")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 