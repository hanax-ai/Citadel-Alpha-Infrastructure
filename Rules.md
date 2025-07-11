# 🤖 AI Operating Rules: Hana-X Landscape

**Document ID:** GOV-AI-001  
**Version:** 1.5
**Purpose:** This document contains the mandatory operating rules for the AI Coding Assistant. These rules ensure all generated output aligns with the project's architecture, standards, and governance.

---

## Rule Group 1000: Task Initialization & Context

- **Rule 1001 - Review Project Context:**  
  Review /home/agent0/Citadel-Alpha-Infrastructure/0.0-HANA-X-Program/01-HXP-PRD.md.

- **Rule 1002 - Review Coding Standards:**  
  Review /home/agent0/Citadel-Alpha-Infrastructure/0.0-HANA-X-Program/12-HXP-Governance/hx-coding-standards.md.

- **Rule 1003 - Acknowledge Monorepo Structure:**  
  Confirm understanding of the project structure.

- **Rule 1004 - Holistically Review Task Requirements:**  
  Review all relevant project documents for the assigned task.

---

## Rule Group 2000: Code & Artifact Generation

- **Rule 2001 - Enforce Code Placement:**  
  Place code in the correct project directory (service-specific vs. shared-library).

- **Rule 2002 - Adhere to All Standards:**  
  Follow all conventions in /home/agent0/Citadel-Alpha-Infrastructure/0.0-HANA-X-Program/12-HXP-Governance/hx-coding-standards.md.

- **Rule 2003 - Generate Unit Tests:**  
  Generate corresponding unit tests for new logic.

- **Rule 2004 - Avoid Hardcoding:**  
  Never hardcode secrets, keys, paths, or other configuration values.

- **Rule 2005 - Follow VCS Best Practices:**  
  Use clear, descriptive commit messages and ensure commits are atomic and focused on single changes.

---

## Rule Group 3000: Interaction & Communication

- **Rule 3001 - State the Executed Rule:**  
  State the primary rule number being executed in the response.

- **Rule 3002 - Request Clarification:**  
  Ask for clarification if a request is ambiguous or contradicts a rule.

- **Rule 3003 - Provide Full Context for Artifacts:**  
  Specify the full, correct file path for any generated content.

- **Rule 3004 - Confirm Destructive Actions:**  
  Ask for user confirmation before generating commands that are potentially destructive (e.g., `rm -rf`).

---

## Rule Group 4000: Self-Correction & Recovery

- **Rule 4001 - Prevent Infinite Loops:**  
  After 3 failed attempts on a task, stop and ask the user for guidance.

- **Rule 4002 - Document Error Recovery:**  
  When technical errors occur, provide clear error description, attempted solutions, and next steps for resolution.

---

## Rule Group 5000: Quality & Best Practices

- **Rule 5001 - Prioritize Security:**  
  Default to secure practices, such as validating inputs.

- **Rule 5002 - Make Scripts Idempotent:**  
  Ensure operational scripts can be run multiple times without causing errors.

- **Rule 5003 - Implement Observability:**  
  Include appropriate logging (`INFO`, `WARNING`, `ERROR`) in new features.

- **Rule 5004 - Handle Privileged Commands Securely:**  
  - **Action:** execute sudo commands
    When a command requires elevated privileges, generate the complete command prefixed with `sudo`.  Then, read password from this directory/file "\\wsl.localhost\Ubuntu-24.04\home\agent0\vLLM Installation\secrets-file.md", proceed with task.

---

## Rule Group 6000: Documentation & Maintenance

- **Rule 6001 - Maintain Documentation:**  
  If a code change impacts documentation, identify and generate the necessary updates for:  
  - API documentation and endpoint specifications  
  - README files and setup instructions  
  - Code comments and inline documentation  
  - Architecture and design documents
