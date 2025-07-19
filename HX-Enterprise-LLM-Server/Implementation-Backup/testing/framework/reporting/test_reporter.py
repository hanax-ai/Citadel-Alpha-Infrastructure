"""
Test Reporter Implementation

Provides reporting and analysis utilities for test results.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class TestReport:
    """Test report data class."""
    report_id: str
    timestamp: str
    test_suite: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    coverage_percentage: Optional[float] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    security_metrics: Optional[Dict[str, Any]] = None


class TestReporter:
    """Test reporter for generating and managing test reports."""
    
    def __init__(self, output_directory: str = "/opt/citadel/reports/testing"):
        """Initialize test reporter."""
        self.output_directory = output_directory
        self.ensure_output_directory()
    
    def ensure_output_directory(self) -> None:
        """Ensure output directory exists."""
        os.makedirs(self.output_directory, exist_ok=True)
    
    def generate_report(self, test_results: Dict[str, Any], test_suite: str = "all") -> TestReport:
        """Generate a test report from results."""
        report_id = f"test_report_{int(time.time())}"
        timestamp = datetime.now().isoformat()
        
        report = TestReport(
            report_id=report_id,
            timestamp=timestamp,
            test_suite=test_suite,
            total_tests=test_results.get('total_tests', 0),
            passed=test_results.get('passed', 0),
            failed=test_results.get('failed', 0),
            skipped=test_results.get('skipped', 0),
            duration=test_results.get('duration', 0.0)
        )
        
        return report
    
    def save_report(self, report: TestReport, format: str = "json") -> str:
        """Save test report to file."""
        if format == "json":
            return self._save_json_report(report)
        elif format == "html":
            return self._save_html_report(report)
        else:
            raise ValueError(f"Unsupported report format: {format}")
    
    def _save_json_report(self, report: TestReport) -> str:
        """Save report as JSON."""
        filename = f"{report.report_id}.json"
        filepath = os.path.join(self.output_directory, filename)
        
        with open(filepath, 'w') as f:
            json.dump(asdict(report), f, indent=2)
        
        return filepath
    
    def _save_html_report(self, report: TestReport) -> str:
        """Save report as HTML."""
        filename = f"{report.report_id}.html"
        filepath = os.path.join(self.output_directory, filename)
        
        html_content = self._generate_html_content(report)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return filepath
    
    def _generate_html_content(self, report: TestReport) -> str:
        """Generate HTML content for report."""
        success_rate = (report.passed / report.total_tests * 100) if report.total_tests > 0 else 0
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {report.test_suite}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; border-radius: 5px; }}
        .passed {{ background-color: #d4edda; color: #155724; }}
        .failed {{ background-color: #f8d7da; color: #721c24; }}
        .skipped {{ background-color: #fff3cd; color: #856404; }}
        .total {{ background-color: #d1ecf1; color: #0c5460; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>HXP-Enterprise LLM Server Test Report</h1>
        <p><strong>Report ID:</strong> {report.report_id}</p>
        <p><strong>Timestamp:</strong> {report.timestamp}</p>
        <p><strong>Test Suite:</strong> {report.test_suite}</p>
    </div>
    
    <div class="summary">
        <h2>Test Summary</h2>
        <div class="metric total">
            <strong>Total Tests:</strong> {report.total_tests}
        </div>
        <div class="metric passed">
            <strong>Passed:</strong> {report.passed}
        </div>
        <div class="metric failed">
            <strong>Failed:</strong> {report.failed}
        </div>
        <div class="metric skipped">
            <strong>Skipped:</strong> {report.skipped}
        </div>
        <div class="metric total">
            <strong>Success Rate:</strong> {success_rate:.1f}%
        </div>
        <div class="metric total">
            <strong>Duration:</strong> {report.duration:.2f} seconds
        </div>
    </div>
    
    <div class="summary">
        <h2>Coverage Information</h2>
        <p>Coverage percentage: {report.coverage_percentage or 'N/A'}%</p>
    </div>
    
    <div class="summary">
        <h2>Performance Metrics</h2>
        <p>{json.dumps(report.performance_metrics, indent=2) if report.performance_metrics else 'N/A'}</p>
    </div>
    
    <div class="summary">
        <h2>Security Metrics</h2>
        <p>{json.dumps(report.security_metrics, indent=2) if report.security_metrics else 'N/A'}</p>
    </div>
</body>
</html>
        """
        
        return html
    
    def get_latest_report(self) -> Optional[TestReport]:
        """Get the latest test report."""
        try:
            json_files = [f for f in os.listdir(self.output_directory) if f.endswith('.json')]
            if not json_files:
                return None
            
            # Sort by modification time
            json_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.output_directory, x)), reverse=True)
            latest_file = json_files[0]
            
            with open(os.path.join(self.output_directory, latest_file), 'r') as f:
                data = json.load(f)
                return TestReport(**data)
        
        except Exception:
            return None
    
    def get_report_summary(self) -> Dict[str, Any]:
        """Get summary of all reports."""
        try:
            json_files = [f for f in os.listdir(self.output_directory) if f.endswith('.json')]
            
            total_reports = len(json_files)
            total_tests = 0
            total_passed = 0
            total_failed = 0
            total_skipped = 0
            
            for json_file in json_files:
                with open(os.path.join(self.output_directory, json_file), 'r') as f:
                    data = json.load(f)
                    total_tests += data.get('total_tests', 0)
                    total_passed += data.get('passed', 0)
                    total_failed += data.get('failed', 0)
                    total_skipped += data.get('skipped', 0)
            
            return {
                'total_reports': total_reports,
                'total_tests': total_tests,
                'total_passed': total_passed,
                'total_failed': total_failed,
                'total_skipped': total_skipped,
                'overall_success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
            }
        
        except Exception:
            return {
                'total_reports': 0,
                'total_tests': 0,
                'total_passed': 0,
                'total_failed': 0,
                'total_skipped': 0,
                'overall_success_rate': 0
            } 