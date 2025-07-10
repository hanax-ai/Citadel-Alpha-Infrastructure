"""
Test cases for common utilities in HANA-X shared library.
"""

import sys
import os
from pathlib import Path
import pytest

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from common.utils import (
    ensure_directory,
    get_system_info,
    validate_port,
    format_bytes,
    run_command_with_timeout,
    check_gpu_availability
)


def test_ensure_directory(tmp_path):
    """Test directory creation utility."""
    test_dir = tmp_path / "test_subdir"
    result = ensure_directory(test_dir)
    
    assert result.exists()
    assert result.is_dir()
    assert result == test_dir


def test_get_system_info():
    """Test system information retrieval."""
    info = get_system_info()
    
    required_keys = ["hostname", "platform", "architecture", "processor", 
                    "python_version", "system", "release"]
    
    for key in required_keys:
        assert key in info
        assert isinstance(info[key], str)
        assert len(info[key]) > 0


def test_validate_port():
    """Test port validation utility."""
    # Test invalid port
    assert not validate_port(80, "localhost")  # Usually occupied
    
    # Test valid high port (likely available)
    assert validate_port(58392, "localhost")


def test_format_bytes():
    """Test byte formatting utility."""
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1048576) == "1.0 MB"
    assert format_bytes(1073741824) == "1.0 GB"
    assert format_bytes(500) == "500.0 B"


def test_run_command_with_timeout():
    """Test command execution with timeout."""
    # Test simple command
    success, stdout, stderr = run_command_with_timeout("echo 'test'", timeout=5)
    
    assert success is True
    assert stdout == "test"
    assert stderr == ""
    
    # Test command that should fail
    success, stdout, stderr = run_command_with_timeout("false", timeout=5)
    assert success is False


def test_check_gpu_availability():
    """Test GPU availability check."""
    gpu_info = check_gpu_availability()
    
    required_keys = ["available", "count", "driver_version", "cuda_version"]
    
    for key in required_keys:
        assert key in gpu_info
    
    assert isinstance(gpu_info["available"], bool)
    assert isinstance(gpu_info["count"], int)
    assert gpu_info["count"] >= 0


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__])
