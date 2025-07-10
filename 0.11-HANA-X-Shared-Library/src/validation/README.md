# Validation Tools

This directory contains validation utilities for system and configuration checks.

## Overview
- Hardware validation (GPU, memory, CPU)
- Configuration validation
- System requirement checks

## Example

```python
from validation.hardware import GPUValidator

validator = GPUValidator(min_gpus=2, min_vram_gb=30)
if validator.validate():
    print("Hardware requirements met")
```
