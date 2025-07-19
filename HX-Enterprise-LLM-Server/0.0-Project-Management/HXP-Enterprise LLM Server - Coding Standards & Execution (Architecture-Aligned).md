# HXP-Enterprise LLM Server - Coding Standards & Execution (Architecture-Aligned)

**Document Version:** 3.0 (Architecture-Driven)  
**Date:** 2025-01-18  
**Project:** Citadel AI Operating System - HXP-Enterprise LLM Server  
**Server:** hx-llm-server-01 (192.168.10.29)  
**Architecture Reference:** HXP-Enterprise LLM Server Architecture Document v1.0  
**Modular Library:** HXP-Enterprise LLM Server Modular Architecture Library v3.0  
**High-Level Task Reference:** HXP-Enterprise LLM Server High-Level Summary Task List v1.0  

---

## 1. 🎯 **INTRODUCTION AND STRATEGIC ALIGNMENT**

This document outlines the mandatory coding standards, execution protocols, and Object-Oriented Programming (OOP) methodologies for the HXP-Enterprise LLM Server project. These standards are designed to ensure complete alignment with the project's architecture, modular library, and high-level tasks while maintaining strong OOP principles for scalability, maintainability, and operational excellence.

### **1.1. Core Objectives:**
- **Architecture Alignment:** Ensure all code directly maps to architectural components and specifications.
- **Modular Integration:** Promote the use of reusable components from the modular library.
- **Performance Excellence:** Meet or exceed performance targets for latency, throughput, and resource utilization.
- **Operational Readiness:** Implement comprehensive monitoring, testing, and deployment standards.
- **Quality Assurance:** Maintain high code quality through automated testing, code reviews, and static analysis.

### **1.2. Project Context:**
- **Primary Purpose:** HXP-Enterprise LLM Server hosting 4 AI models with advanced monitoring and API capabilities.
- **Server Location:** 192.168.10.29 (hx-llm-server-01)
- **Technical Stack:** Python 3.12.3, vLLM, FastAPI, Prometheus, Grafana, Docker
- **Performance Requirements:** Model-specific latency and throughput targets.

---

## 2. 🏗️ **FOUNDATIONAL OOP AND SOLID PRINCIPLES**

### **2.1. Mandatory OOP Principles:**
- **Encapsulation:** Object state must be protected with private/protected access modifiers. Functionality is exposed through public methods.
- **Abstraction:** Classes must expose only essential information, hiding complex implementation details through abstract classes and interfaces.
- **Inheritance:** Use inheritance strictly for "is-a" relationships. **Prefer composition over inheritance** for "has-a" relationships.
- **Polymorphism:** Design objects to exhibit behavior based on their specific type at runtime, leveraging method overriding and interfaces.

### **2.2. Strict SOLID Principles Compliance:**
- **Single Responsibility Principle (SRP):** Each class and module must have one, and only one, reason to change.
- **Open/Closed Principle (OCP):** Software entities must be open for extension but closed for modification.
- **Liskov Substitution Principle (LSP):** Subtypes must be substitutable for their base types without altering program correctness.
- **Interface Segregation Principle (ISP):** Clients must not be forced to depend on interfaces they do not use.
- **Dependency Inversion Principle (DIP):** High-level modules must not depend on low-level modules; both must depend on abstractions.

---

## 3. 📝 **GENERAL CODING STANDARDS AND PRACTICES**

### **3.1. Naming Conventions:**
- **Standard:** Adhere to Python's PEP 8 naming conventions (`snake_case` for functions/variables, `PascalCase` for classes).
- **Clarity:** Use clear, descriptive, and unambiguous names. Avoid generic names and excessive abbreviations.
- **Constants:** Use `ALL_CAPS_WITH_UNDERSCORES` for constants.

### **3.2. Code Readability and Formatting:**
- **Standard:** Follow Black code formatter with an 88-character line limit.
- **Automation:** Use Black and isort for automated formatting and import sorting.
- **Comments:** Use comments to explain *why* code does something, not *what* it does. Strive for self-documenting code.

### **3.3. Modularity and Cohesion:**
- **Rule:** Break down large problems into small, highly cohesive units (classes, methods).
- **Guideline:** Methods should perform one specific task. Classes should have a single, well-defined responsibility (SRP).

### **3.4. Low Coupling:**
- **Rule:** Minimize dependencies between distinct components.
- **Guideline:** Avoid "God objects." Pass necessary dependencies as parameters or inject them.

### **3.5. Error Handling and Exception Management:**
- **Rule:** Implement robust and predictable error handling with custom exception classes.
- **Guideline:** Use specific exceptions instead of generic ones. Handle exceptions at the appropriate layer and log critical errors.

### **3.6. Unit Testing:**
- **Rule:** All new features and bug fixes must be accompanied by comprehensive unit tests.
- **Guideline:** Aim for >90% code coverage. Use pytest with async support and mock external dependencies.

### **3.7. Version Control (Git):**
- **Rule:** Adhere to GitHub Flow branching strategy.
- **Guideline:** Commit small, atomic changes frequently with clear, descriptive commit messages.

### **3.8. Code Reviews:**
- **Rule:** All code changes must undergo a mandatory peer code review before merging.
- **Guideline:** Provide constructive and actionable feedback, focusing on adherence to standards and design quality.

### **3.9. Design Patterns:**
- **Guideline:** Leverage established OOP design patterns (e.g., Factory, Strategy, Observer) to solve recurring design problems.

### **3.10. Refactoring:**
- **Rule:** Continuously refactor code to improve its internal structure and readability without changing its external behavior.

### **3.11. Documentation:**
- **Rule:** Public APIs must be clearly documented with their purpose, parameters, return values, and exceptions.
- **Docstring Format:** Use Google-style docstrings for all public functions and classes.

---

## 4. 📦 **MODULAR LIBRARY INTEGRATION STANDARDS**

### **4.1. Module Usage and Integration:**
- **Rule:** All implementations must utilize components from the HXP-Enterprise LLM Server Modular Architecture Library.
- **Guideline:** Follow the defined module structure for AI model services, infrastructure services, and integration services.
- **Example:**
  ```python
  from hxp_enterprise_llm.services.ai_models.mixtral.service import MixtralService
  from hxp_enterprise_llm.services.infrastructure.monitoring.prometheus import PrometheusExporter
  from hxp_enterprise_llm.services.integration.database.postgresql import PostgreSQLConnector
  ```

### **4.2. Configuration Schema Integration:**
- **Rule:** Use service-specific configuration schemas from the modular library.
- **Guideline:** Validate all configurations against the defined schemas on startup.
- **Example:**
  ```python
  from hxp_enterprise_llm.schemas.configuration.service_schemas import MixtralServiceConfig
  
  config = MixtralServiceConfig(
      port=11400,
      memory_limit_gb=90,
      cpu_cores=8,
      # ... other parameters
  )
  ```

### **4.3. Testing Suite Integration:**
- **Rule:** Use the isolated testing suites from the modular library for all components.
- **Guideline:** Run unit, integration, performance, and security tests for each module.
- **Example:**
  ```bash
  # Run Mixtral service unit tests
  pytest testing/component/ai_models_tests/test_mixtral.py
  
  # Run integration tests for database connectivity
  pytest testing/component/integration_tests/test_postgresql_integration.py
  ```

### **4.4. Orchestration Logic Integration:**
- **Rule:** Utilize reusable orchestration components for deployment, health checks, and metrics.
- **Guideline:** Use standardized deployment scaffolds and operational scripts.
- **Example:**
  ```python
  from hxp_enterprise_llm.orchestration.deployment.service_manager import ServiceManager
  from hxp_enterprise_llm.orchestration.operational.health_checks.health_check_framework import HealthCheckFramework
  
  service_manager = ServiceManager()
  service_manager.deploy_service("mixtral")
  
  health_checker = HealthCheckFramework()
  status = health_checker.get_service_health("mixtral")
  ```

---

## 5. 🚀 **EXECUTION AND DEPLOYMENT STANDARDS**

### **5.1. vLLM Service Implementation:**
- **Rule:** Implement all AI model services using the vLLM inference engine.
- **Guideline:** Use systemd for service management with resource allocation and lifecycle management.
- **Example:**
  ```bash
  # /etc/systemd/system/citadel-llm@.service
  [Unit]
  Description=Citadel AI LLM Service - %i
  After=network.target
  
  [Service]
  User=agent0
  Group=agent0
  WorkingDirectory=/opt/citadel/hxp-enterprise-llm
  EnvironmentFile=/opt/citadel/config/services/%i.conf
  ExecStart=/opt/citadel/env/bin/python -m hxp_enterprise_llm.services.ai_models.%i.service
  Restart=always
  RestartSec=10
  
  [Install]
  WantedBy=multi-user.target
  ```

### **5.2. API Gateway Implementation:**
- **Rule:** Implement the unified API gateway using FastAPI.
- **Guideline:** Provide centralized access to all AI models with load balancing, health monitoring, and request routing.
- **Example:**
  ```python
  from fastapi import FastAPI
  from hxp_enterprise_llm.services.infrastructure.api_gateway.router import APIRouter
  
  app = FastAPI(title="HXP-Enterprise LLM Server API Gateway")
  router = APIRouter()
  app.include_router(router.get_router())
  ```

### **5.3. Monitoring and Observability:**
- **Rule:** Implement comprehensive monitoring with Prometheus and Grafana.
- **Guideline:** Use custom metrics for business intelligence, performance analytics, and cost tracking.
- **Example:**
  ```python
  from hxp_enterprise_llm.services.infrastructure.monitoring.prometheus import PrometheusExporter
  
  exporter = PrometheusExporter()
  exporter.start_server(port=9090)
  
  # Custom metrics
  exporter.track_model_accuracy("mixtral", 0.95)
  exporter.track_user_satisfaction("mixtral", 9)
  exporter.track_business_value("mixtral", 150)
  exporter.track_cost_per_request("mixtral", 0.0025)
  ```

### **5.4. Containerization and Deployment:**
- **Rule:** Use Docker for containerization with multi-stage builds.
- **Guideline:** Use Docker Compose for local development and testing. Implement CI/CD pipelines for automated deployment.
- **Example:**
  ```yaml
  # docker-compose.yml
  version: '3.8'
  services:
    llm-server:
      build: .
      ports:
        - "8000:8000"
        - "9090:9090"
      environment:
        - CITADEL_ENV=development
        - DATABASE_HOST=192.168.10.35
        - VECTOR_DB_HOST=192.168.10.30
        - METRICS_HOST=192.168.10.37
      networks:
        - citadel-network
  networks:
    citadel-network:
      driver: bridge
  ```

---

## 6. 🛡️ **COMPLIANCE AND ENFORCEMENT**

Adherence to these coding standards is mandatory for all development activities. Compliance will be ensured through:

- **Automated Static Analysis:** Black, flake8, mypy, and pytest integrated into the CI/CD pipeline.
- **Mandatory Code Reviews:** All pull requests subject to peer review with emphasis on enforcing standards.
- **CI Pipeline Enforcement:** CI pipelines will fail if style or static analysis checks do not pass.
- **Mentorship and Training:** Ongoing training and mentorship to help developers apply these principles effectively.
- **Project Lead Responsibility:** Project leads are responsible for guiding their teams in adopting and maintaining these standards.

---

## 7. 📚 **RESOURCES AND REFERENCES**

### **Project Documentation:**
- [HXP-Enterprise LLM Server Architecture Document](./HXP_Enterprise_LLM_Server_Architecture_Document.md)
- [HXP-Enterprise LLM Server Modular Architecture Library](./HXP_Enterprise_LLM_Server_Modular_Architecture_Library.md)
- [HXP-Enterprise LLM Server High-Level Summary Task List](./HXP_Enterprise_LLM_Server_High_Level_Task_List.md)
- [HXP-Enterprise LLM Server Detailed Task Template](./HXP_Enterprise_LLM_Server_Detailed_Task_Template_Aligned.md)

### **Technical References:**
- [Python PEP 8 Style Guide](https://pep8.org/)
- [vLLM Documentation](https://vllm.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)

### **Development Tools:**
- [Black Code Formatter](https://black.readthedocs.io/)
- [pytest Testing Framework](https://pytest.org/)
- [Docker Documentation](https://docs.docker.com/)

---

**🎯 This document provides the complete coding standards and execution protocols for the HXP-Enterprise LLM Server project, ensuring alignment with architecture, modularity, and operational excellence.**

