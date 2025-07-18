#!/bin/bash

# HANA-X Vector Database Shared Library - Master Test Runner
# Comprehensive test execution script for all test categories

set -e  # Exit on any error

echo "=== HANA-X VECTOR DATABASE SHARED LIBRARY - COMPREHENSIVE TEST SUITE ==="
echo "Starting comprehensive test execution..."
echo "Date: $(date)"
echo ""

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COVERAGE_THRESHOLD=95
PERFORMANCE_THRESHOLD_MS=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test execution functions
run_unit_tests() {
    log_info "Running unit tests..."
    if [ -d "$SCRIPT_DIR/unit" ]; then
        pytest "$SCRIPT_DIR/unit" \
            --cov=hana_x_vector \
            --cov-report=html:htmlcov \
            --cov-report=xml:coverage.xml \
            --cov-report=term-missing \
            --cov-fail-under=$COVERAGE_THRESHOLD \
            -v \
            --tb=short \
            -m "unit" || return 1
        log_success "Unit tests completed successfully"
    else
        log_warning "Unit tests directory not found, skipping..."
    fi
}

run_integration_tests() {
    log_info "Running integration tests..."
    if [ -d "$SCRIPT_DIR/integration" ]; then
        pytest "$SCRIPT_DIR/integration" \
            -v \
            --tb=short \
            -m "integration" || return 1
        log_success "Integration tests completed successfully"
    else
        log_warning "Integration tests directory not found, skipping..."
    fi
}

run_performance_tests() {
    log_info "Running performance tests..."
    if [ -d "$SCRIPT_DIR/performance" ]; then
        pytest "$SCRIPT_DIR/performance" \
            --benchmark-only \
            --benchmark-json=benchmark.json \
            --benchmark-histogram=benchmark_histogram \
            -v \
            -m "performance" || return 1
        log_success "Performance tests completed successfully"
    else
        log_warning "Performance tests directory not found, skipping..."
    fi
}

run_security_tests() {
    log_info "Running security tests..."
    if [ -d "$SCRIPT_DIR/security" ]; then
        pytest "$SCRIPT_DIR/security" \
            -v \
            --tb=short \
            -m "security" || return 1
        log_success "Security tests completed successfully"
    else
        log_warning "Security tests directory not found, skipping..."
    fi
}

run_cross_server_tests() {
    log_info "Running cross-server communication tests..."
    if [ -f "$SCRIPT_DIR/scripts/cross-server-communication-test.sh" ]; then
        bash "$SCRIPT_DIR/scripts/cross-server-communication-test.sh" || return 1
        log_success "Cross-server communication tests completed successfully"
    else
        log_warning "Cross-server communication test script not found, skipping..."
    fi
}

run_code_quality_checks() {
    log_info "Running code quality checks..."
    
    # Check if tools are available
    if command -v flake8 >/dev/null 2>&1; then
        log_info "Running flake8 linting..."
        flake8 "$PROJECT_ROOT/hana_x_vector" --max-line-length=88 --extend-ignore=E203,W503 || return 1
    else
        log_warning "flake8 not found, skipping linting..."
    fi
    
    if command -v black >/dev/null 2>&1; then
        log_info "Running black code formatting check..."
        black --check "$PROJECT_ROOT/hana_x_vector" || return 1
    else
        log_warning "black not found, skipping formatting check..."
    fi
    
    if command -v isort >/dev/null 2>&1; then
        log_info "Running isort import sorting check..."
        isort --check-only "$PROJECT_ROOT/hana_x_vector" || return 1
    else
        log_warning "isort not found, skipping import sorting check..."
    fi
    
    if command -v mypy >/dev/null 2>&1; then
        log_info "Running mypy type checking..."
        mypy "$PROJECT_ROOT/hana_x_vector" --ignore-missing-imports || return 1
    else
        log_warning "mypy not found, skipping type checking..."
    fi
    
    log_success "Code quality checks completed successfully"
}

run_security_scans() {
    log_info "Running security scans..."
    
    if command -v bandit >/dev/null 2>&1; then
        log_info "Running bandit security scan..."
        bandit -r "$PROJECT_ROOT/hana_x_vector" -f json -o bandit_report.json || return 1
    else
        log_warning "bandit not found, skipping security scan..."
    fi
    
    if command -v safety >/dev/null 2>&1; then
        log_info "Running safety dependency scan..."
        safety check --json --output safety_report.json || return 1
    else
        log_warning "safety not found, skipping dependency scan..."
    fi
    
    log_success "Security scans completed successfully"
}

# Environment setup
setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Set test environment variables
    export HANA_X_TEST_MODE=true
    export TESTING=true
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    # Create test directories if they don't exist
    mkdir -p "$SCRIPT_DIR/unit"
    mkdir -p "$SCRIPT_DIR/integration"
    mkdir -p "$SCRIPT_DIR/performance"
    mkdir -p "$SCRIPT_DIR/security"
    mkdir -p "$SCRIPT_DIR/fixtures"
    mkdir -p "$SCRIPT_DIR/scripts"
    
    # Check if test dependencies are installed
    if ! python -c "import pytest" 2>/dev/null; then
        log_warning "pytest not found, installing test dependencies..."
        pip install -r "$SCRIPT_DIR/requirements-test.txt" || {
            log_error "Failed to install test dependencies"
            return 1
        }
    fi
    
    log_success "Test environment setup completed"
}

# Cleanup function
cleanup_test_environment() {
    log_info "Cleaning up test environment..."
    
    # Remove temporary test files
    find "$SCRIPT_DIR" -name "*.pyc" -delete 2>/dev/null || true
    find "$SCRIPT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Clean up test databases if they exist
    if [ -f "$SCRIPT_DIR/test.db" ]; then
        rm "$SCRIPT_DIR/test.db"
    fi
    
    log_success "Test environment cleanup completed"
}

# Report generation
generate_test_report() {
    log_info "Generating test report..."
    
    cat > test_report.md << EOF
# HANA-X Vector Database Shared Library - Test Report

**Date:** $(date)
**Test Suite Version:** 1.0

## Test Results Summary

### Unit Tests
- **Status:** $UNIT_TEST_STATUS
- **Coverage:** Available in htmlcov/index.html

### Integration Tests
- **Status:** $INTEGRATION_TEST_STATUS

### Performance Tests
- **Status:** $PERFORMANCE_TEST_STATUS
- **Benchmark Results:** Available in benchmark.json

### Security Tests
- **Status:** $SECURITY_TEST_STATUS

### Cross-Server Communication Tests
- **Status:** $CROSS_SERVER_TEST_STATUS

### Code Quality
- **Status:** $CODE_QUALITY_STATUS

### Security Scans
- **Status:** $SECURITY_SCAN_STATUS

## Files Generated
- Coverage Report: htmlcov/index.html
- Coverage XML: coverage.xml
- Benchmark Results: benchmark.json
- Security Report: bandit_report.json
- Dependency Scan: safety_report.json

## Next Steps
$(if [ "$OVERALL_STATUS" = "PASSED" ]; then
    echo "✅ All tests passed! Ready for deployment."
else
    echo "❌ Some tests failed. Review the output above and fix issues before deployment."
fi)
EOF
    
    log_success "Test report generated: test_report.md"
}

# Main execution
main() {
    local start_time=$(date +%s)
    
    # Initialize status variables
    UNIT_TEST_STATUS="SKIPPED"
    INTEGRATION_TEST_STATUS="SKIPPED"
    PERFORMANCE_TEST_STATUS="SKIPPED"
    SECURITY_TEST_STATUS="SKIPPED"
    CROSS_SERVER_TEST_STATUS="SKIPPED"
    CODE_QUALITY_STATUS="SKIPPED"
    SECURITY_SCAN_STATUS="SKIPPED"
    OVERALL_STATUS="FAILED"
    
    # Setup environment
    setup_test_environment || {
        log_error "Failed to setup test environment"
        exit 1
    }
    
    # Parse command line arguments
    RUN_UNIT=true
    RUN_INTEGRATION=true
    RUN_PERFORMANCE=true
    RUN_SECURITY=true
    RUN_CROSS_SERVER=true
    RUN_CODE_QUALITY=true
    RUN_SECURITY_SCANS=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --unit-only)
                RUN_INTEGRATION=false
                RUN_PERFORMANCE=false
                RUN_SECURITY=false
                RUN_CROSS_SERVER=false
                RUN_CODE_QUALITY=false
                RUN_SECURITY_SCANS=false
                shift
                ;;
            --integration-only)
                RUN_UNIT=false
                RUN_PERFORMANCE=false
                RUN_SECURITY=false
                RUN_CROSS_SERVER=false
                RUN_CODE_QUALITY=false
                RUN_SECURITY_SCANS=false
                shift
                ;;
            --performance-only)
                RUN_UNIT=false
                RUN_INTEGRATION=false
                RUN_SECURITY=false
                RUN_CROSS_SERVER=false
                RUN_CODE_QUALITY=false
                RUN_SECURITY_SCANS=false
                shift
                ;;
            --no-quality)
                RUN_CODE_QUALITY=false
                RUN_SECURITY_SCANS=false
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --unit-only         Run only unit tests"
                echo "  --integration-only  Run only integration tests"
                echo "  --performance-only  Run only performance tests"
                echo "  --no-quality        Skip code quality and security scans"
                echo "  --help              Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Run test suites
    local failed_tests=0
    
    if [ "$RUN_UNIT" = true ]; then
        if run_unit_tests; then
            UNIT_TEST_STATUS="PASSED"
        else
            UNIT_TEST_STATUS="FAILED"
            ((failed_tests++))
        fi
    fi
    
    if [ "$RUN_INTEGRATION" = true ]; then
        if run_integration_tests; then
            INTEGRATION_TEST_STATUS="PASSED"
        else
            INTEGRATION_TEST_STATUS="FAILED"
            ((failed_tests++))
        fi
    fi
    
    if [ "$RUN_PERFORMANCE" = true ]; then
        if run_performance_tests; then
            PERFORMANCE_TEST_STATUS="PASSED"
        else
            PERFORMANCE_TEST_STATUS="FAILED"
            ((failed_tests++))
        fi
    fi
    
    if [ "$RUN_SECURITY" = true ]; then
        if run_security_tests; then
            SECURITY_TEST_STATUS="PASSED"
        else
            SECURITY_TEST_STATUS="FAILED"
            ((failed_tests++))
        fi
    fi
    
    if [ "$RUN_CROSS_SERVER" = true ]; then
        if run_cross_server_tests; then
            CROSS_SERVER_TEST_STATUS="PASSED"
        else
            CROSS_SERVER_TEST_STATUS="FAILED"
            ((failed_tests++))
        fi
    fi
    
    if [ "$RUN_CODE_QUALITY" = true ]; then
        if run_code_quality_checks; then
            CODE_QUALITY_STATUS="PASSED"
        else
            CODE_QUALITY_STATUS="FAILED"
            ((failed_tests++))
        fi
    fi
    
    if [ "$RUN_SECURITY_SCANS" = true ]; then
        if run_security_scans; then
            SECURITY_SCAN_STATUS="PASSED"
        else
            SECURITY_SCAN_STATUS="FAILED"
            ((failed_tests++))
        fi
    fi
    
    # Determine overall status
    if [ $failed_tests -eq 0 ]; then
        OVERALL_STATUS="PASSED"
    fi
    
    # Generate report
    generate_test_report
    
    # Cleanup
    cleanup_test_environment
    
    # Final summary
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    echo "=== TEST EXECUTION SUMMARY ==="
    echo "Duration: ${duration}s"
    echo "Unit Tests: $UNIT_TEST_STATUS"
    echo "Integration Tests: $INTEGRATION_TEST_STATUS"
    echo "Performance Tests: $PERFORMANCE_TEST_STATUS"
    echo "Security Tests: $SECURITY_TEST_STATUS"
    echo "Cross-Server Tests: $CROSS_SERVER_TEST_STATUS"
    echo "Code Quality: $CODE_QUALITY_STATUS"
    echo "Security Scans: $SECURITY_SCAN_STATUS"
    echo ""
    
    if [ "$OVERALL_STATUS" = "PASSED" ]; then
        log_success "🎉 ALL TESTS PASSED! Test suite execution completed successfully."
        exit 0
    else
        log_error "❌ $failed_tests test suite(s) failed. Please review the output above."
        exit 1
    fi
}

# Execute main function with all arguments
main "$@"
