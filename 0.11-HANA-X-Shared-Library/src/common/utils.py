"""
Common utility functions for HANA-X infrastructure projects.
"""

import os
import socket
import subprocess
import platform
from pathlib import Path
from typing import Dict, Optional, Union, Tuple


def ensure_directory(path: Union[str, Path], mode: int = 0o755) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to create
        mode: Permission mode for directory
        
    Returns:
        Path object of the created/existing directory
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True, mode=mode)
    return path_obj


def get_system_info() -> Dict[str, str]:
    """
    Get basic system information.
    
    Returns:
        Dictionary containing system information
    """
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "system": platform.system(),
        "release": platform.release(),
    }


def validate_port(port: int, host: str = "localhost") -> bool:
    """
    Check if a port is available on the specified host.
    
    Args:
        port: Port number to check
        host: Host to check (default: localhost)
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            return result != 0  # Port is available if connection fails
    except socket.error:
        return False


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human-readable string.
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.2 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def run_command_with_timeout(
    command: str, 
    timeout: int = 30,
    shell: bool = True
) -> Tuple[bool, str, str]:
    """
    Run a shell command with timeout.
    
    Args:
        command: Command to execute
        timeout: Timeout in seconds
        shell: Whether to run in shell mode
        
    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return (
            result.returncode == 0,
            result.stdout.strip(),
            result.stderr.strip()
        )
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)


def check_gpu_availability() -> Dict[str, Union[bool, int, str]]:
    """
    Check GPU availability using nvidia-smi.
    
    Returns:
        Dictionary with GPU information
    """
    gpu_info = {
        "available": False,
        "count": 0,
        "driver_version": "Unknown",
        "cuda_version": "Unknown"
    }
    
    success, stdout, stderr = run_command_with_timeout("nvidia-smi --query-gpu=count --format=csv,noheader,nounits")
    
    if success and stdout:
        try:
            gpu_info["count"] = len(stdout.strip().split('\n'))
            gpu_info["available"] = gpu_info["count"] > 0
        except (ValueError, AttributeError):
            pass
    
    # Get driver version
    success, stdout, stderr = run_command_with_timeout("nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits")
    if success and stdout:
        gpu_info["driver_version"] = stdout.strip().split('\n')[0]
    
    return gpu_info
