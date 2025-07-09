# ✅ Task Creation Guidelines: SMART+ST

To ensure clarity, focus, and ease of execution, every task should follow the **SMART+ST** principles:

| Letter | Principle     | Guidance |
|--------|----------------|----------|
| **S**  | **Specific**   | The task must **clearly define what is to be done**. Avoid vague language. Include necessary context so anyone reading it understands the scope without back-and-forth. |
| **M**  | **Measurable** | Define **how success will be measured**. Use concrete metrics, completion conditions, or testable outcomes. |
| **A**  | **Achievable** | The task should be **realistic** given time, skill, and resource constraints. Don’t assign impossible objectives. |
| **R**  | **Relevant**   | Ensure the task is **aligned with the project’s or system’s goals**. It should contribute meaningfully to the larger initiative. |
| **S**  | **Small**      | Keep the task **narrow in scope**. If it’s too large, break it down into sub-tasks. Each task should include the **actual sequence of commands or steps to execute** when possible, making it operationally ready. |
| **T**  | **Testable**   | The task must be **verifiably complete**. Define success criteria or expected outputs so the result can be tested or validated without interpretation. |

---

## 📏 Basic Principles for Configuration and Maintainability

To ensure maintainable and secure implementations:

- ✅ **Always externalize configuration**:
  - Use `.env` for environment variables, secrets, tokens, and service credentials
  - Use `.json` for structured data, metadata, and internal settings
  - Use `.yaml` for multi-step configurations, deployment flows, and LLM pipeline definitions

- ❌ **Never hardcode values** in scripts, notebooks, or source files:
  - Paths (e.g. model directories, cache locations)
  - Port numbers, endpoint URLs, or IP addresses
  - API tokens, HuggingFace keys, or service credentials

> ⚠️ Hardcoded values introduce hidden dependencies, break portability, and increase the risk of misconfiguration across environments. All values should be overridable and environment-aware.

---

## ✅ Example: Task and Sub-Task Structure

Use hierarchical task numbering for clarity and traceability. Define the main task with subtasks broken down by execution step.

**Task 1.0: Install NVIDIA 570.x drivers on Ubuntu 24.04**

**Sub-Tasks:**
- **Task 1.1:** Use `apt` to install required kernel headers
- **Task 1.2:** Download the official NVIDIA `.run` installer from [link or variable from config]
- **Task 1.3:** Run the `.run` installer in command-line mode
- **Task 1.4:** Reboot the system to apply changes
- **Task 1.5:** Verify installation with `nvidia-smi`

Each sub-task should:
- Be **self-contained** and **atomic**
- Include any required command or configuration reference
- Avoid internal dependencies on hardcoded values

**This task is:**
- ✔ **Small** (broken into discrete, executable steps)
- ✔ **Testable** (can be validated via CLI output and system checks)
- ✔ **Aligned**, **achievable**, and **measurable**

---

## 📌 Use This Framework For:
- OS and package installation
- LLM and vLLM deployment tasks
- Configuration updates and service wiring
- Any repeatable technical implementation task

Stick to SMART+ST for consistency, clarity, and rapid execution across the team.

---

## 🏁 Task Completion Policy

A task is **not considered complete** until:
- ✅ **All sub-tasks are 100% completed**
- ✅ Results have been validated against success criteria

This prevents partial delivery or assumptions of completeness before verification.

---

## 🔗 Task Dependencies and Sequencing

For complex infrastructure deployments, tasks often have dependencies and must be executed in specific sequences. Follow these guidelines to manage task relationships:

### 📋 Dependency Types

| Type | Description | Example |
|------|-------------|--------|
| **Hard Dependency** | Task B cannot start until Task A is 100% complete | NVIDIA drivers must be installed before CUDA toolkit |
| **Soft Dependency** | Task B should ideally wait for Task A, but can proceed with warnings | Model download can start before vLLM installation completion |
| **Parallel Tasks** | Tasks can run simultaneously without conflicts | Installing Python packages on different servers |
| **Conditional Tasks** | Task execution depends on the outcome of previous tasks | GPU memory test only runs if GPU drivers are successfully installed |

### 🎯 Dependency Documentation Format

For each task, clearly document dependencies using this format:

```
**Task X.X: [Task Title]**

**Prerequisites:**
- Task A.A: [Description] (Hard/Soft/Conditional)
- Task B.B: [Description] (Hard/Soft/Conditional)

**Enables:**
- Task C.C: [Description]
- Task D.D: [Description]

**Parallel Candidates:**
- Task E.E: [Description]
```

### 📊 Sequencing Best Practices

1. **Critical Path First**: Identify and execute the longest dependency chain first
2. **Fail Fast**: Place validation tasks early to catch issues before dependent tasks
3. **Rollback Readiness**: Document rollback procedures for tasks with dependencies
4. **Checkpoint Validation**: Validate critical dependencies before proceeding to dependent tasks

### 🔄 Example: Multi-Server Task Sequencing

**Phase 1: Foundation (Sequential)**
- Task 1.0: Install OS updates on hx-llm-server-01
- Task 1.1: Install NVIDIA drivers on hx-llm-server-01
- Task 1.2: Validate GPU functionality on hx-llm-server-01

**Phase 2: Software Stack (Conditional)**
- Task 2.0: Install Python 3.12 (depends on Task 1.0)
- Task 2.1: Install CUDA toolkit (depends on Task 1.1, 1.2)
- Task 2.2: Install vLLM (depends on Task 2.0, 2.1)

**Phase 3: Replication (Parallel)**
- Task 3.0: Replicate Phase 1 on hx-llm-server-02 (parallel with Phase 2)
- Task 3.1: Replicate Phase 2 on hx-llm-server-02 (depends on Task 3.0)

### ⚠️ Dependency Failure Handling

When a task with dependencies fails:
1. **Stop dependent tasks** immediately
2. **Document the failure** and its impact on dependent tasks
3. **Identify rollback requirements** for already-completed dependent tasks
4. **Update task status** to reflect blocked dependencies

---

## 📄 Task Result Summary

After completing a task:
1. Create a summary document titled:
   - `[Task Title]_Results.md`
   - Example: `Install_NVIDIA_570x_on_Ubuntu_24_04_Results.md`

2. The result document should include:
   - The final outcome of each sub-task
   - Any deviations from the plan or unexpected findings
   - Validated output or screenshots (if applicable)

3. Save this file in the designated results directory:
   - `/project/tasks/results/`

---

## ✅ Task List Update

Once the task is complete:
- Go to the project task list located at:
  - `/project/tasks/task-list.md`
- Locate the relevant task number (e.g. `Task 1.0`)
- Check the status box in front of the task:
  - Change from `- [ ]` to `- [x]`

This maintains traceability and project-wide visibility into execution status.
