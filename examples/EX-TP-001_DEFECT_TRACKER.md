# EX-TP-001_DEFECT_TRACKER.md

## Project: Installing vLLM and Hugging Face Models on LLM Server

### Overview
This document tracks all known defects encountered during the vLLM installation and testing process. Each defect is traceable to the task or test where it was discovered, and linked to a follow-up resolution task if remediated.

---

## 📑 Reference Documents
- **PRD**: EX-TP-001_PRD.md
- **Task List**: EX-TP-001_TASK_LIST.md
- **Traceability Matrix**: EX-TP-001_TRACEABILITY_MATRIX.md

---

## 🏷️ Defect Categories
Classify defects by type:
- **Environment**: OS compatibility, driver conflicts
- **Installation**: Package conflicts, version mismatches
- **Configuration**: Invalid paths, missing variables
- **GPU**: Memory allocation, CUDA problems
- **Model**: Corrupt downloads, incompatible structures
- **API**: Port conflicts, service failures
- **Performance**: High memory usage, slow inference
- **Testing**: Test failures, validation problems
- **Documentation**: Missing instructions, outdated information

---

## 🧾 Defect Log

| Defect ID | Category | Related Task/Test ID | Description | Severity | Status | Resolution Task | Date Reported | Owner |
|-----------|----------|----------------------|-------------|----------|--------|-----------------|----------------|-------|
| DEF-001   | Install  | TL-001.2             | Dependency conflict with package installation | High     | Open   | TL-002.1        | 2025-07-10     | DevOps |
| DEF-002   | Config   | TL-001.4             | Incorrect API endpoint configuration        | Medium   | Closed | TL-002.2        | 2025-07-11     | ML Eng |

---

## 🔗 Guidelines
- Defect titles should be clearly prefixed with `DEFECT:`
- All status updates recorded in this tracker and linked tasks/tests
- Related entries in `TIP-001`, `TS-001`, and `vllm_installation_status.md` must be cross-referenced

---

_Last updated: 2025-07-09_
