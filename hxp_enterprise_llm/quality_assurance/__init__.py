"""
HXP-Enterprise LLM Server - Quality Assurance and Validation Framework

This package provides comprehensive quality assurance and validation capabilities
for the HXP-Enterprise LLM Server modular library, including end-to-end testing,
performance validation, security assessment, and quality monitoring.

Author: Manus AI
Version: 3.0.0
Date: 2025-01-18
"""

from .framework import QualityAssuranceFramework
from .metrics import QualityMetricsCollector
from .monitoring import QualityMonitor
from .automation import QualityAutomation

__version__ = "3.0.0"
__author__ = "Manus AI"
__all__ = [
    "QualityAssuranceFramework",
    "QualityMetricsCollector", 
    "QualityMonitor",
    "QualityAutomation"
] 