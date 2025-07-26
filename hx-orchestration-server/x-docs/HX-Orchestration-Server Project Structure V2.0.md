# HX-Orchestration-Server Project Structure V2.0

**Document Version:** 2.0  
**Date:** 2025-01-25  
**Author:** Manus AI  
**Server:** hx-orchestration-server (192.168.10.31)  
**Purpose:** Comprehensive project structure aligned with Task List V2.0 and project rules  
**Architecture:** 3-Layer FastAPI + Celery (Production Pattern)  

---

## Project Structure Overview

This structure supports all 5 phases of the implementation task list while adhering to project rules (R5.1-R5.4: OOP principles, utility classes, common library, 500-line limit).

```
/opt/citadel-orca/hx-orchestration-server/
├── README.md                           # Project overview and quick start
├── requirements.txt                    # Core dependencies
├── main.py                            # FastAPI application entry point
├── celery_app.py                      # Celery configuration
│
├── app/                               # Core application modules
│   ├── __init__.py
│   ├── api/                          # API layer (Phase 2: FastAPI Framework)
│   │   ├── __init__.py
│   │   ├── v1/                       # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/            # API endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── embeddings.py     # /v1/embeddings (OpenAI compatible)
│   │   │   │   ├── orchestration.py  # /v1/workflows, /v1/orchestrate
│   │   │   │   ├── health.py         # /health/, /health/detailed
│   │   │   │   ├── metrics.py        # /metrics (Prometheus)
│   │   │   │   └── auth.py           # Authentication endpoints
│   │   │   └── dependencies.py       # FastAPI dependencies
│   │   └── middleware.py             # CORS, auth, logging middleware
│   │
│   ├── core/                         # Core business logic (Phase 2-3)
│   │   ├── __init__.py
│   │   ├── orchestration/            # Orchestration engine
│   │   │   ├── __init__.py
│   │   │   ├── workflow_manager.py   # Workflow coordination
│   │   │   ├── task_router.py        # Task routing logic
│   │   │   └── state_manager.py      # State management
│   │   ├── embeddings/               # Embedding processing (Phase 3)
│   │   │   ├── __init__.py
│   │   │   ├── ollama_client.py      # Ollama integration
│   │   │   ├── model_selector.py     # Model selection logic
│   │   │   ├── cache_manager.py      # Multi-layer caching
│   │   │   └── batch_processor.py    # Batch embedding processing
│   │   └── services/                 # External service integration
│   │       ├── __init__.py
│   │       ├── llm_service.py        # LLM-01/LLM-02 integration
│   │       ├── vector_service.py     # Qdrant integration
│   │       ├── database_service.py   # PostgreSQL integration
│   │       └── monitoring_service.py # Prometheus integration
│   │
│   ├── common/                       # Common utilities (R5.3: Common Class Library)
│   │   ├── __init__.py
│   │   ├── base_classes.py           # Base classes for OOP (R5.1)
│   │   ├── exceptions.py             # Custom exceptions
│   │   ├── validators.py             # Input validation utilities
│   │   ├── decorators.py             # Common decorators
│   │   └── constants.py              # Application constants
│   │
│   ├── utils/                        # Utility classes (R5.2: Utility Classes)
│   │   ├── __init__.py
│   │   ├── http_client.py            # HTTP client utilities
│   │   ├── connection_pool.py        # Connection pooling
│   │   ├── circuit_breaker.py        # Circuit breaker pattern
│   │   ├── retry_logic.py            # Retry with backoff
│   │   ├── performance_monitor.py    # Performance monitoring
│   │   └── security_utils.py         # Security utilities
│   │
│   ├── models/                       # Data models and schemas
│   │   ├── __init__.py
│   │   ├── api_models.py             # Pydantic API models
│   │   ├── database_models.py        # SQLAlchemy models
│   │   ├── embedding_models.py       # Embedding data structures
│   │   └── workflow_models.py        # Workflow definitions
│   │
│   ├── tasks/                        # Celery tasks (Phase 2: Celery Implementation)
│   │   ├── __init__.py
│   │   ├── embedding_tasks.py        # Embedding processing tasks
│   │   ├── orchestration_tasks.py    # Orchestration tasks
│   │   ├── monitoring_tasks.py       # Background monitoring
│   │   └── maintenance_tasks.py      # System maintenance tasks
│   │
│   └── integrations/                 # Modern framework integrations (Phase 4)
│       ├── __init__.py
│       ├── clerk_auth.py             # Clerk authentication
│       ├── ag_ui_bridge.py           # AG UI integration
│       ├── copilot_kit.py            # Copilot Kit bridge
│       └── livekit_comm.py           # LiveKit communication
│
├── config/                           # Configuration management
│   ├── __init__.py
│   ├── settings.py                   # Application settings (environment-based)
│   ├── database.py                   # Database configuration
│   ├── redis.py                      # Redis configuration
│   ├── ollama.py                     # Ollama configuration
│   ├── monitoring.py                 # Monitoring configuration
│   └── environments/                 # Environment-specific configs
│       ├── development.yaml
│       ├── testing.yaml
│       └── production.yaml
│
├── tests/                            # Test suite (Phase 5: Testing)
│   ├── __init__.py
│   ├── unit/                         # Unit tests
│   │   ├── __init__.py
│   │   ├── test_embeddings.py
│   │   ├── test_orchestration.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/                  # Integration tests
│   │   ├── __init__.py
│   │   ├── test_api_endpoints.py
│   │   ├── test_external_services.py
│   │   ├── test_workflows.py
│   │   └── test_auth_integration.py
│   ├── load/                         # Load testing (Phase 5)
│   │   ├── __init__.py
│   │   ├── embedding_load_test.py
│   │   ├── orchestration_load_test.py
│   │   └── concurrent_test.py
│   ├── fixtures/                     # Test data and fixtures
│   │   ├── __init__.py
│   │   ├── sample_embeddings.py
│   │   ├── test_workflows.py
│   │   └── mock_responses.py
│   ├── conftest.py                   # Pytest configuration
│   └── test_config.py                # Test environment configuration
│
├── docs/                             # Documentation (Phase 5: Documentation)
│   ├── api/                          # API documentation
│   │   ├── openapi.json              # OpenAPI specification
│   │   ├── endpoints.md              # Endpoint documentation
│   │   └── authentication.md        # Auth documentation
│   ├── operations/                   # Operational procedures
│   │   ├── deployment.md             # Deployment procedures
│   │   ├── monitoring.md             # Monitoring guide
│   │   ├── troubleshooting.md        # Troubleshooting guide
│   │   └── backup_recovery.md        # Backup and recovery
│   ├── development/                  # Development guides
│   │   ├── setup.md                  # Development setup
│   │   ├── testing.md                # Testing guide
│   │   └── contributing.md           # Contribution guidelines
│   └── architecture/                 # Architecture documentation
│       ├── overview.md               # System overview
│       ├── component_design.md       # Component design
│       └── integration_patterns.md   # Integration patterns
│
├── scripts/                          # Operational scripts
│   ├── deployment/                   # Deployment scripts
│   │   ├── deploy.sh                 # Main deployment script
│   │   ├── rollback.sh               # Rollback script
│   │   └── health_check.sh           # Health verification
│   ├── maintenance/                  # Maintenance scripts
│   │   ├── backup.sh                 # Backup script
│   │   ├── restore.sh                # Restore script
│   │   ├── cleanup.sh                # Cleanup script
│   │   └── monitor.sh                # Monitoring script
│   ├── development/                  # Development utilities
│   │   ├── setup_dev.sh              # Development setup
│   │   ├── run_tests.sh              # Test runner
│   │   └── lint_code.sh              # Code linting
│   └── tools/                        # Utility tools
│       ├── migrate_db.py             # Database migration
│       ├── seed_data.py              # Data seeding
│       └── performance_check.py      # Performance validation
│
├── systemd/                          # SystemD service files
│   ├── citadel-orchestration.service # Main service
│   ├── citadel-celery.service        # Celery worker service
│   └── citadel-redis.service         # Redis service
│
├── logs/                             # Log files
│   ├── application.log               # Application logs
│   ├── celery.log                    # Celery logs
│   ├── error.log                     # Error logs
│   ├── audit.log                     # Audit logs
│   └── performance.log               # Performance logs
│
├── quality_assurance/                # QA and testing
│   ├── performance/                  # Performance testing
│   │   ├── benchmarks.py             # Performance benchmarks
│   │   ├── stress_tests.py           # Stress testing
│   │   └── load_profiles.py          # Load testing profiles
│   ├── security/                     # Security testing
│   │   ├── auth_tests.py             # Authentication tests
│   │   ├── vulnerability_scan.py     # Security scanning
│   │   └── penetration_tests.py      # Penetration testing
│   └── compliance/                   # Compliance validation
│       ├── code_standards.py         # Code standard validation
│       ├── api_compliance.py         # API compliance tests
│       └── documentation_check.py    # Documentation validation
│
├── monitoring/                       # Monitoring configuration
│   ├── prometheus/                   # Prometheus configuration
│   │   ├── metrics.py                # Custom metrics
│   │   ├── alerts.yaml               # Alert rules
│   │   └── dashboard.json            # Grafana dashboard
│   ├── grafana/                      # Grafana dashboards
│   │   ├── orchestration_dashboard.json
│   │   ├── performance_dashboard.json
│   │   └── system_dashboard.json
│   └── alerting/                     # Alerting configuration
│       ├── alert_rules.yaml
│       ├── notification_config.yaml
│       └── escalation_policies.yaml
│
└── .env.example                      # Environment variables template
```

---

## Phase Alignment Matrix

### Phase 1: Infrastructure Foundation (6-10 hours)
**Focus:** Basic setup, network configuration, Python environment
- **Primary Directories:** `config/`, `scripts/deployment/`, `systemd/`
- **Key Files:** `requirements.txt`, environment configs, SystemD services
- **Rules Compliance:** Uses existing `citadel_venv` (R1.0)

### Phase 2: Core Orchestration Framework (8-12 hours)
**Focus:** FastAPI application, Celery workers, service integration
- **Primary Directories:** `app/api/`, `app/core/`, `app/tasks/`
- **Key Files:** `main.py`, `celery_app.py`, API endpoints, task definitions
- **Rules Compliance:** OOP principles (R5.1), utility classes (R5.2)

### Phase 3: Embedding Processing Framework (6-10 hours)
**Focus:** Ollama integration, model deployment, caching
- **Primary Directories:** `app/core/embeddings/`, `config/`
- **Key Files:** Ollama client, model selector, cache manager
- **Rules Compliance:** <500 lines per file (R5.4), modular design

### Phase 4: Modern Framework Integration (10-14 hours)
**Focus:** Clerk, AG UI, Copilot Kit, LiveKit integration
- **Primary Directories:** `app/integrations/`, `app/api/v1/endpoints/`
- **Key Files:** Authentication bridges, UI connectors, real-time communication
- **Rules Compliance:** Common class library (R5.3)

### Phase 5: Testing and Production Readiness (8-12 hours)
**Focus:** Comprehensive testing, monitoring, documentation
- **Primary Directories:** `tests/`, `docs/`, `monitoring/`, `quality_assurance/`
- **Key Files:** Test suites, operational procedures, monitoring configs
- **Rules Compliance:** Systematic validation, operational excellence

---

## Key Design Principles

### OOP Compliance (R5.1)
- **Base Classes:** `app/common/base_classes.py` provides foundation
- **Encapsulation:** Service classes encapsulate external integrations
- **Inheritance:** Common patterns inherited from base classes
- **Polymorphism:** Interface-based design for pluggable components

### Utility Organization (R5.2)
- **HTTP Utils:** Connection pooling, circuit breakers, retry logic
- **Performance Utils:** Monitoring, caching, optimization
- **Security Utils:** Authentication, validation, encryption

### Common Library (R5.3)
- **Shared Components:** `app/common/` provides reusable functionality
- **Documentation:** Each utility class fully documented
- **Accessibility:** Clean imports and consistent interfaces

### File Size Management (R5.4)
- **Modular Design:** No file exceeds 500 lines
- **Functional Decomposition:** Related functions grouped in focused modules
- **Clear Separation:** Distinct modules for distinct responsibilities

---

## Network Configuration Alignment

**Server Configuration (from .rulesfile R3.0):**
- **Hostname:** hx-orchestration-server
- **IP Address:** 192.168.10.31

**External Service Connections:**
- **LLM-01:** 192.168.10.34:8002 (production endpoint)
- **LLM-02:** 192.168.10.28:8000 (planned business models)
- **PostgreSQL:** 192.168.10.35:5432 (metadata storage)
- **Qdrant:** 192.168.10.30:6333 (vector database)
- **Prometheus:** 192.168.10.37:9090 (monitoring)
- **Grafana:** 192.168.10.37:3000 (visualization)

---

## Implementation Strategy

1. **Phase-by-Phase Creation:** Structure supports systematic implementation
2. **Root Directory Implementation:** Direct implementation in `/opt/citadel-orca/`
3. **Rules Compliance:** Every aspect aligned with project rules
4. **Production Readiness:** SystemD services, monitoring, operational procedures
5. **Modern Integration:** Support for all required frameworks and technologies

This structure provides a solid foundation for implementing all 5 phases of the task list while maintaining code quality, operational excellence, and adherence to project standards.
