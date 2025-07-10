# 📄 Product Requirements Document (PRD)

## Title: This is a draft / Example – For Installing vLLM and Hugging Face Models on LLM Server

---

### 🧭 Overview
This draft/example PRD outlines the requirements and scope for installing and testing the vLLM inference engine and selected Hugging Face models on a pre-configured LLM server. The OS (Ubuntu 24.04 LTS) has been fully installed and hardened, and this project focuses on enabling the system to support local inferencing with vLLM.

This document also serves as the basis for the following deliverables:

1. ✅ **Task List** (`TL-001`): A list of top-level tasks derived from this PRD. Each task includes a title, a clear objective, and traceability to implementation or validation.

2. ✅ **Task Implementation Plan** (`TIP-001`): A structured, hierarchical plan outlining execution-level tasks (Level 1 and 2) with commands, dependencies, and SMART+ST alignment.

3. ✅ **Test Suite Specification** (`TS-001`): A formal definition of a `pytest` test suite covering OS verification, dependency installation, model loading, API health, and GPU usage checks.

4. ✅ **Project Repository Layout** (`PRL-001`): A recommended file and directory structure for organizing scripts, configuration files, models, logs, results, and test cases in a clear, maintainable format.

> Each deliverable is a standalone artifact with its own purpose, audience, and update lifecycle.

---

### ✅ Objective
Enable an LLM server to:
- Run the vLLM engine from source or package
- Load and serve multiple Hugging Face models
- Validate compatibility with CUDA, Python 3.12, and NVIDIA 570.x drivers
- Prepare the environment with required folders, scripts, and configuration files

---

### 🧱 Assumptions
- Ubuntu 24.04 LTS is fully installed and patched
- NVIDIA 570.x drivers are installed and verified
- Python 3.12 is available and `venv` is configured

> ⚠️ All assumptions should be verified and confirmed before work begins. If any gaps are discovered, create new tasks to account for that scope.

---

### 📦 Scope

#### 0. Metrics & Observability
- Integrate **Prometheus exporters** on the LLM server to collect hardware, memory, and GPU metrics
- Use **Grafana dashboards** (hosted on the Dev-Ops server) for real-time and historical visibility
- Metrics to track include:
  - GPU utilization per model
  - Inference latency and throughput
  - System memory and disk usage
  - Python process uptime and resource consumption
- Note: The **Grafana Web UI will not be hosted locally on the LLM server**. All dashboard access and visualization will be managed centrally on the Dev-Ops infrastructure

#### 1. OS Verification & Prep
- Verify NVIDIA drivers via `nvidia-smi`
- Check Python 3.12 installation
- Validate disk layout, available GPU memory, and system paths

#### 2. Environment & Dependency Setup
- Create isolated virtual environment (e.g. `/opt/llm/env`)
- Install `torch`, `vllm`, `transformers`, and other required packages
- Handle CUDA runtime support and `ninja`, `wheel`, `triton`
- Define all environment variables in `.env`

#### 3. Directory Layout
Create the following folders (if not already present):
- `/opt/llm/env` — Python virtual environment
- `/mnt/citadel-models` — model storage
- `/opt/llm/scripts` — custom scripts and launchers
- `/opt/llm/config` — `.env`, `yaml`, or `json` configuration files

#### 4. vLLM Installation
- Clone or install vLLM from PyPI/GitHub
- Validate installation with `python3 -m vllm.entrypoints.openai.api_server`
- Configure OpenAI-compatible endpoint (e.g. port 8000)

#### 5. Model Installation
- Download models from Hugging Face using `transformers` or `hf_transfer`
- Configure access using `.env` (e.g. `HF_TOKEN`)
- Verify model structure (`config.json`, `tokenizer.json`, etc.)

#### 6. Validation & Testing
- Launch vLLM server with at least one model
- Validate health via HTTP `/health` endpoint
- Run dummy inference and verify latency/response
- Check logs, GPU memory utilization

---

### 🚫 Out of Scope
- OS-level changes or secure boot modifications
- Orchestration or containerization (e.g., Docker, Kubernetes)
- Front-end UI for inferencing

---

### ✅ Deliverables

#### D1: Operational Deployment
- vLLM engine installed and operational on bare-metal
- Hugging Face models loaded and accessible via OpenAI-compatible API

#### D2: Configuration Artifacts
- Complete set of `.env`, `yaml`, or `json` config files located in `/opt/llm/config`
- All paths, ports, and tokens are externalized with no hardcoding

#### D3: Documentation
- `README.md` with:
  - Installation and launch instructions
  - Environment setup notes
  - Testing and validation steps

#### D4: Monitoring Integration
- Prometheus exporters configured and scraping metrics
- Grafana dashboards created on the Dev-Ops server
- Metrics verified for GPU, latency, and system performance

#### D5: Supporting Artifacts (Cross-linked Deliverables)
- `TL-001`: Task List
- `TIP-001`: Task Implementation Plan
- `TS-001`: Pytest Test Suite
- `PRL-001`: Project Repository Layout

> These deliverables collectively ensure full traceability, repeatability, and operational readiness for the vLLM installation scope. with commands for launching, updating, and checking system state

---

### 🧪 Success Criteria

#### For Scope 0: Metrics & Observability
- Prometheus node exporter and NVIDIA DCGM metrics are accessible via Dev-Ops Grafana instance
- No errors in Prometheus scrape logs from LLM node
- Key metrics are available: GPU usage, model latency, memory consumption

#### For Scope 1: OS Verification & Prep
- `nvidia-smi` confirms active drivers with no errors
- `python3 --version` returns 3.12.x
- Sufficient disk space and memory are verified and documented

#### For Scope 2: Environment & Dependency Setup
- Python virtual environment is created at `/opt/llm/env`
- All dependencies (`torch`, `vllm`, `transformers`, etc.) are installed with no pip errors
- `.env` contains all required variables and is correctly referenced in scripts

#### For Scope 3: Directory Layout
- Required folders are created with correct permissions
- Folder structure is persistent across reboots

#### For Scope 4: vLLM Installation
- `vllm` can be imported and executed via CLI and Python entrypoints
- `vllm.entrypoints.openai.api_server` launches with no errors

#### For Scope 5: Model Installation
- Selected models are downloaded with correct structure (e.g., config, tokenizer, safetensors)
- No hardcoded model paths; all defined in config or `.env`

#### For Scope 6: Validation & Testing
- Inference server responds on configured port
- `/health` endpoint returns 200 OK
- Dummy prompt returns valid response from model
- GPU usage reflects model activity during inference
 with no startup errors
- Server responds to `/health` and basic inference requests
- No hardcoded values — all configuration externalized
- Directory structure is created and persists across reboots

---

### 📁 Result Tracking & Handoff

#### Companion Status Document
- A central status tracking file named: `vllm_installation_status.md`
- Located at: `/project/status/`
- Includes:
  - Progress of each scoped item (0–6)
  - Associated task references (e.g., TL-001, TIP-001)
  - Verification notes and completion sign-off

#### Repository Mirror: README.md
- The root-level `README.md` in the project repository must mirror:
  - The final directory structure
  - Installation flow and configuration references
  - Basic testing commands and validation expectations
- Purpose: to support day-to-day operations, onboarding, and CI/CD extensions

- Task results documented in: `Install_vLLM_and_Hugging_Models_on_LLM_Server_Results.md`
- Save in: `/project/tasks/results/`
- Update status in: `/project/tasks/task-list.md`
