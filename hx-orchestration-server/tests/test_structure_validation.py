"""
Basic health test for HX-Orchestration-Server

Simple test to validate the basic structure and imports are working.
Run this to verify the implementation is set up correctly.
"""

import sys
import os
import asyncio
import pytest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.mark.asyncio
async def test_imports():
    """Test that core modules can be imported"""
    try:
        # Test config imports
        from config.settings import get_settings
        settings = get_settings()
        assert settings.SERVER_NAME == "hx-orchestration-server"
        
        # Test base classes
        from app.common.base_classes import BaseService, BaseClient
        assert BaseService is not None
        assert BaseClient is not None
        
        # Test monitoring service
        from app.core.services.monitoring_service import MonitoringService
        monitoring = MonitoringService()
        await monitoring.initialize()
        await monitoring.cleanup()
        
        # Test performance monitor
        from app.utils.performance_monitor import PerformanceMonitor
        perf_monitor = PerformanceMonitor()
        await perf_monitor.initialize()
        
        print("✓ All core imports successful")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise


def test_directory_structure():
    """Test that the expected directory structure exists"""
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
    
    project_root = Path(__file__).parent.parent
    
    for dir_path in expected_dirs:
        full_path = project_root / dir_path
        assert full_path.exists(), f"Directory {dir_path} does not exist"
    
    print("✓ Directory structure validation passed")


def test_configuration_files():
    """Test that configuration files exist and are valid"""
    project_root = Path(__file__).parent.parent
    
    # Check required files
    required_files = [
        "requirements.txt",
        "main.py",
        "celery_app.py",
        ".env.example",
        "config/settings.py",
        "systemd/citadel-orchestration.service",
        "systemd/citadel-celery.service",
        "scripts/deployment/deploy.sh"
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"File {file_path} does not exist"
        assert full_path.stat().st_size > 0, f"File {file_path} is empty"
    
    print("✓ Configuration files validation passed")


@pytest.mark.asyncio 
async def test_performance_monitor():
    """Test performance monitoring functionality"""
    from app.utils.performance_monitor import PerformanceMonitor
    
    monitor = PerformanceMonitor()
    await monitor.initialize()
    
    # Test recording metrics
    await monitor.record_request("/test", "GET", 0.1, 200)
    await monitor.record_embedding_request(5, "test-model", 0.5, 2)
    await monitor.record_workflow_execution("test-workflow", 1.0, "completed", 3)
    
    # Test getting metrics
    metrics = await monitor.get_current_metrics()
    assert "timestamp" in metrics
    assert "uptime" in metrics
    assert "totals" in metrics
    
    # Test health score
    health_score = await monitor.get_health_score()
    assert 0.0 <= health_score <= 1.0
    
    await monitor.cleanup()
    print("✓ Performance monitor test passed")


if __name__ == "__main__":
    print("Running HX-Orchestration-Server structure validation...")
    print(f"Project root: {Path(__file__).parent.parent}")
    
    # Run synchronous tests
    test_directory_structure()
    test_configuration_files()
    
    # Run async tests
    async def run_async_tests():
        await test_imports()
        await test_performance_monitor()
    
    asyncio.run(run_async_tests())
    
    print("\n✅ All validation tests passed!")
    print("🚀 HX-Orchestration-Server structure is ready for implementation!")
