# 🧪 Testing Guidelines for vLLM + Model Installation (Pytest)

This guide outlines how to structure, write, and maintain clean, reusable, and modular tests using `pytest`, with a focus on vLLM installation and model deployment on an LLM server.

---

## ✅ Goals of This Testing Guide
- Ensure reliability and correctness of vLLM and model setup
- Provide clear structure and modular test design
- Enable fast, focused, and automated testing using `pytest`
- Promote reuse through helper utilities and OOP structure

---

## 🧱 Directory Structure

Organize your test suite by domain, keeping files and classes small and focused:

```
tests/
├── test_vllm_install.py           # Tests for vLLM installation and environment setup
├── test_model_install_llama.py    # Tests specific to LLaMA model download and config
├── test_gpu_allocation.py         # Tests for GPU memory and visibility
├── test_inference_api.py          # Health checks and inference-level testing
└── helpers/
    ├── conftest.py                # Shared pytest fixtures
    ├── model_utils.py             # Reusable model management helpers
    ├── vllm_check.py              # Utilities for vLLM presence and environment
    └── common_paths.py            # Paths and config constants
```

---

## 📐 Test Design Principles: **FASTT**

| Principle | Description |
|-----------|-------------|
| **F**ocused      | One behavior per test. Avoid multi-purpose assertions. |
| **A**utomated    | Must run via `pytest` or CI — no manual steps. |
| **S**elf-contained | Can run in isolation; mocks/stubs preferred. |
| **T**raceable    | Failures must be obvious and diagnostic. |
| **T**imely       | Executes quickly (unit tests < 1s ideally). |

---

## 🧠 Structural Best Practices

### 🔸 Keep Test Files and Classes Small
- Split tests by concern: one test class = one component/behavior.
- Large files (e.g. `test_full_stack.py`) should be broken down.

### 🔸 Use OOP for Clarity and Grouping

Example:
```python
class TestVLLMInstall:
    def test_cli_present(self): ...

class TestLlamaDownload:
    def test_model_files_exist(self): ...
```

### 🔸 Extract Reusable Logic
- Put common setup, checks, or filesystem logic in helper modules.
- E.g., `ModelInstaller`, `VLLMEnvironment`, `PathResolver`

---

## 🔧 What to Test

For vLLM + model setup:

### 🧪 vLLM Installation
- NVIDIA driver available (e.g. `nvidia-smi`)
- Correct Python version (e.g. 3.12)
- vLLM CLI executable available

### 🧪 Model Installation
- Model directory and files exist after download
- Configs (e.g. `config.json`, `tokenizer.json`) are present
- Files have valid format or hash (if needed)

### 🧪 GPU/Environment
- `torch.cuda.is_available()` returns True
- Model fits in available GPU memory (mock or real test)

### 🧪 Inference API (if applicable)
- `/health` returns 200
- Dummy inference returns a non-empty result

---

## 🧩 Fixtures and Utilities

Use `conftest.py` to define shared setup code:
```python
@pytest.fixture
def vllm_env():
    return {"bin": "/opt/llm/env/bin", "python": "/usr/bin/python3.12"}
```

Use utility classes for logic like model setup:
```python
class ModelInstaller:
    def __init__(self, model_name, download_path): ...
    def download(self): ...
    def is_downloaded(self): ...
```

---

## 🧪 Running Tests

```bash
pytest                     # Run all tests
pytest -v tests/test_vllm_install.py  # Run specific module
pytest -k test_download_llama3        # Run by test name pattern
```

Enable durations and logs:
```bash
pytest -v -s --durations=5
```

---

## ✅ Summary

Good tests are:
- **Focused**, fast, and reliable
- **Modular** and reusable
- **Clear** in what they validate
- **Easy to extend** as the vLLM stack evolves

Stick to these principles to ensure your test suite grows with confidence — not complexity.
