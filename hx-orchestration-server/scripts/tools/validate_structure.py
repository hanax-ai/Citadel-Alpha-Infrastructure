#!/usr/bin/env python3
"""
Simple Structure Validation Script

Validates the HX-Orchestration-Server structure without external dependencies.
Run this to verify the implementation is set up correctly.
"""

import sys
import os
from pathlib import Path
import importlib.util


def validate_directory_structure():
    """Validate that the expected directory structure exists"""
    print("🔍 Validating directory structure...")
    
    expected_dirs = [
        "app/api/v1/endpoints",
        "app/core/orchestration",
        "app/core/embeddings", 
        "app/core/services",
        "app/common",
        "app/utils",
        "app/models",
        "app/tasks",
        "app/integrations",
        "config",
        "tests/unit",
        "tests/integration",
        "docs/api",
        "scripts/deployment",
        "systemd",
        "logs",
        "monitoring"
    ]
    
    project_root = Path(__file__).parent.parent.parent
    missing_dirs = []
    
    for dir_path in expected_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print(f"✅ All {len(expected_dirs)} expected directories found")
    return True


def validate_configuration_files():
    """Validate that configuration files exist and are valid"""
    print("🔍 Validating configuration files...")
    
    project_root = Path(__file__).parent.parent.parent
    
    required_files = [
        ("requirements.txt", 100),
        ("main.py", 500),
        ("celery_app.py", 100),
        (".env.example", 100),
        ("config/settings.py", 500),
        ("systemd/citadel-orchestration.service", 100),
        ("systemd/citadel-celery.service", 100),
        ("scripts/deployment/deploy.sh", 1000),
        ("README.md", 500),
        ("x-docs/IMPLEMENTATION_STATUS.md", 1000)
    ]
    
    missing_files = []
    empty_files = []
    
    for file_path, min_size in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        elif full_path.stat().st_size < min_size:
            empty_files.append(f"{file_path} (size: {full_path.stat().st_size})")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    if empty_files:
        print(f"⚠️  Files smaller than expected: {empty_files}")
    
    print(f"✅ All {len(required_files)} required files found")
    return True


def validate_python_files():
    """Validate that Python files have correct syntax"""
    print("🔍 Validating Python file syntax...")
    
    project_root = Path(__file__).parent.parent.parent
    
    python_files = [
        "main.py",
        "celery_app.py",
        "config/settings.py",
        "app/common/base_classes.py",
        "app/core/services/monitoring_service.py",
        "app/utils/performance_monitor.py",
        "app/api/v1/endpoints/health.py",
        "app/api/v1/endpoints/embeddings.py"
    ]
    
    syntax_errors = []
    
    for file_path in python_files:
        full_path = project_root / file_path
        if full_path.exists():
            try:
                with open(full_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
            except SyntaxError as e:
                syntax_errors.append(f"{file_path}: {e}")
        else:
            syntax_errors.append(f"{file_path}: File not found")
    
    if syntax_errors:
        print(f"❌ Syntax errors: {syntax_errors}")
        return False
    
    print(f"✅ All {len(python_files)} Python files have valid syntax")
    return True


def validate_imports():
    """Validate that core modules can be imported"""
    print("🔍 Validating module imports...")
    
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    import_tests = []
    
    try:
        # Test config imports
        from config.settings import get_settings
        settings = get_settings()
        assert settings.SERVER_NAME == "hx-orchestration-server"
        import_tests.append("✅ config.settings")
        
    except Exception as e:
        import_tests.append(f"❌ config.settings: {e}")
    
    try:
        # Test base classes
        from app.common.base_classes import BaseService
        import_tests.append("✅ app.common.base_classes")
        
    except Exception as e:
        import_tests.append(f"❌ app.common.base_classes: {e}")
    
    try:
        # Test monitoring service
        from app.core.services.monitoring_service import MonitoringService
        import_tests.append("✅ app.core.services.monitoring_service")
        
    except Exception as e:
        import_tests.append(f"❌ app.core.services.monitoring_service: {e}")
    
    # Print results
    for result in import_tests:
        print(f"  {result}")
    
    success_count = len([r for r in import_tests if r.startswith("✅")])
    total_count = len(import_tests)
    
    return success_count == total_count


def main():
    """Run all validation tests"""
    print("🚀 HX-Orchestration-Server Structure Validation")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent.parent
    print(f"📁 Project root: {project_root}")
    print()
    
    tests = [
        ("Directory Structure", validate_directory_structure),
        ("Configuration Files", validate_configuration_files),
        ("Python Syntax", validate_python_files),
        ("Module Imports", validate_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")
        if result:
            passed += 1
    
    print()
    print(f"Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED!")
        print("🚀 HX-Orchestration-Server structure is ready for implementation!")
        return 0
    else:
        print("⚠️  Some tests failed - please review and fix issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
