# 🐞 vLLM Project – Defect Tracker

This document tracks all known defects encountered during the vLLM and Hugging Face model installation and testing process.
Each defect must be traceable to the task or test where it was discovered, and if remediated, linked to a follow-up resolution task.

---

## 📘 Reference Documents
- `PRD_vllm_model_install.md`
- `TL-001` – Task List
- `TIP-001` – Task Implementation Plan
- `TS-001` – Test Suite Specification
- `vllm_installation_status.md`

---

## 🏷️ Defect Categories

Classify defects by type to improve tracking and resolution patterns:

| Category | Description | Examples |
|----------|-------------|----------|
| **ENV** | Environment and system setup issues | OS compatibility, driver conflicts, permission issues |
| **INSTALL** | Installation and dependency issues | Package conflicts, version mismatches, download failures |
| **CONFIG** | Configuration and setup issues | Invalid paths, missing env variables, incorrect settings |
| **GPU** | GPU and CUDA related issues | Memory allocation, driver compatibility, CUDA toolkit problems |
| **MODEL** | Model download and loading issues | Corrupt downloads, incompatible models, storage issues |
| **API** | API server and endpoint issues | Port conflicts, service startup failures, connectivity problems |
| **PERF** | Performance and resource issues | High memory usage, slow inference, resource contention |
| **TEST** | Testing and validation issues | Test failures, assertion errors, validation problems |
| **DOC** | Documentation and process issues | Missing instructions, unclear procedures, outdated information |

---

## 🧾 Defect Log

| Defect ID | Category | Related Task/Test ID | Description | Severity | Status | Resolution Task (if any) | Date Reported | Owner |
|-----------|----------|----------------------|-------------|----------|--------|---------------------------|----------------|--------|
|           |          |                      |             |          |        |                           |                |        |

Legend:
- **Category**: ENV | INSTALL | CONFIG | GPU | MODEL | API | PERF | TEST | DOC
- **Severity**: Low | Medium | High | Critical
- **Status**: Open | Investigating | Deferred | Closed

---

## 🔗 Guidelines
- Defect titles should be clearly prefixed with `DEFECT:` if promoted into the Task List.
- All status updates should be recorded in both this tracker and linked tasks/tests.
- Related entries in `TIP-001`, `TS-001`, and `vllm_installation_status.md` must be cross-referenced.

---

_Last updated: [Insert Date]_
