# HANA-X Shared Library

## Introduction

The HANA-X Shared Library serves as a centralized source of common utilities, models, and constants that are reused across multiple HANA-X projects. This approach prevents code duplication and ensures consistency in coding standards and practices across the organization.

## Repository Structure

The repository is designed as an installable Python package with the following structure:

```
hana-x-shared-library/
│
├── pyproject.toml    # Core file that defines the package
├── README.md
├── .gitignore
│
└── src/
    └── hana_x_shared/
        ├── __init__.py
        ├── models.py     # Example shared Pydantic data models
        └── utils.py      # Example shared utility functions
```

## Key File Contents

### pyproject.toml
This file defines the package configuration for Python's packaging tools like pip.

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "hana-x-shared"
version = "0.1.0"
authors = [
  { name="Jarvis Richardson", email="agentzero88@example.com" },
]
description = "Shared utilities, data models, and constants for the Hana-X AI Landscape."
requires-python = ">=3.12"
classifiers = [
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
]
dependencies = [
    "pydantic>=2.0",
]

[project.urls]
"Homepage" = "https://github.com/hanax-ai/hana-x-shared-library"
"Bug Tracker" = "https://github.com/hanax-ai/hana-x-shared-library/issues"
```

### Example Shared Model
An example of a Pydantic model usable by multiple services.

```python
from pydantic import BaseModel
from typing import List
from enum import Enum

class ServerStatus(str, Enum):
    """Enumeration for server health status."""
    OK = "OK"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"

class HealthCheckResponse(BaseModel):
    """A standard health check response model."""
    service_name: str
    status: ServerStatus
    dependencies: List[str] = []
```

## How to Use in Other Repositories

To use this shared code in other HANA-X projects, include it in the project's `requirements.txt` file.

### Update requirements.txt
Add the following line to the requirements.txt of each server that needs access to the shared code:

```
# requirements.txt

# other dependencies...
torch>=2.0
vllm

# Install our private shared library from GitHub
hana-x-shared @ git+https://<YOUR_GITHUB_TOKEN>@github.com/hanax-ai/hana-x-shared-library.git
```

_Note: Replace `<YOUR_GITHUB_TOKEN>` with a GitHub Personal Access Token that has the appropriate access rights._

After running `pip install -r requirements.txt`, you can import and use the shared code just like any other package.

### Example Usage

```python
# Example usage in the LLM server's code
from hana_x_shared.models import HealthCheckResponse, ServerStatus

def get_llm_server_health() -> HealthCheckResponse:
    # ... logic to check health ...
    return HealthCheckResponse(
        service_name="llm-inference-server",
        status=ServerStatus.OK,
        dependencies=["NVIDIA Driver", "CUDA"]
    )
```

## Maintenance Guidelines

1. **Version Control**: Follow semantic versioning for updates.
2. **Contribution**: Encourage clear guidelines on contributing to the shared library.
3. **Documentation**: Maintain up-to-date docstrings and README entries for clarity.

This setup provides a clean, version-controlled way to manage and distribute your common code, ensuring consistency across the HANA-X landscape.
