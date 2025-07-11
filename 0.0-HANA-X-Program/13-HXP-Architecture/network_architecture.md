# 🌐 Network Architecture Diagram: HANA-X Program

**Document ID:** ARCH-NET-001  
**Version:** 1.0  
**Date:** July 11, 2025  
**Purpose:** Comprehensive network architecture diagram illustrating all inter-server communications for the HANA-X Program infrastructure.

---

## 🏗️ Network Architecture Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "External Access Layer"
        EXT["🌐 External Users<br/>Enterprise Applications"]
    end
    
    subgraph "Load Balancer/Gateway"
        LB["⚖️ Load Balancer<br/>(Future Implementation)"]
    end
    
    subgraph "Core Infrastructure - 192.168.10.0/24"
        subgraph "Orchestration Layer"
            ORCH["🎯 hx-orchestration-server<br/>192.168.10.31<br/>FastAPI Task Router<br/>LangGraph Workflows<br/>Celery Workers"]
        end
        
        subgraph "AI Processing Layer"
            LLM1["🧠 hx-llm-server-01<br/>192.168.10.29<br/>vLLM Primary<br/>OpenAI API"]
            LLM2["🧠 hx-llm-server-02<br/>192.168.10.28<br/>vLLM Secondary<br/>Load Balancing"]
        end
        
        subgraph "Data Layer"
            SQL["🗄️ hx-sql-database-server<br/>192.168.10.35<br/>PostgreSQL<br/>Redis Cache"]
            VDB["🔍 hx-vector-database-server<br/>192.168.10.30<br/>Qdrant Vector DB"]
        end
        
        subgraph "Development & Testing"
            DEV["💻 hx-dev-server<br/>192.168.10.33<br/>Multimodal AI<br/>Dev Tools"]
            TEST["🧪 hx-test-server<br/>192.168.10.34<br/>CI/CD Jenkins<br/>Selenium QA"]
        end
        
        subgraph "Operations Layer"
            METRICS["📊 hx-metric-server<br/>192.168.10.37<br/>Prometheus/Grafana<br/>Loki/OpenUI"]
            DEVOPS["⚙️ hx-dev-ops-server<br/>192.168.10.36<br/>Automation<br/>PowerShell"]
        end
    end
    
    %% External Connections
    EXT --> LB
    LB --> ORCH
    
    %% Core Processing Flow
    ORCH --> LLM1
    ORCH --> LLM2
    ORCH --> SQL
    ORCH --> VDB
    
    %% AI Processing Connections
    LLM1 --> SQL
    LLM1 --> VDB
    LLM2 --> SQL
    LLM2 --> VDB
    
    %% Development Connections
    DEV --> ORCH
    DEV --> LLM1
    DEV --> LLM2
    TEST --> ORCH
    TEST --> SQL
    TEST --> VDB
    
    %% Operations Monitoring
    METRICS --> ORCH
    METRICS --> LLM1
    METRICS --> LLM2
    METRICS --> SQL
    METRICS --> VDB
    METRICS --> DEV
    METRICS --> TEST
    METRICS --> DEVOPS
    
    %% DevOps Management
    DEVOPS --> ORCH
    DEVOPS --> LLM1
    DEVOPS --> LLM2
    DEVOPS --> SQL
    DEVOPS --> VDB
    DEVOPS --> DEV
    DEVOPS --> TEST
    DEVOPS --> METRICS
```

---

## 🔗 Detailed Inter-Server Communications

### 1. Primary Data Flow Paths

#### **Request Processing Pipeline**
```
External User → Load Balancer → hx-orchestration-server → hx-llm-server-01/02 → hx-sql-database-server/hx-vector-database-server
```

#### **AI Inference Chain**
```
hx-orchestration-server ←→ hx-llm-server-01/02 ←→ hx-vector-database-server
                        ↓
                   hx-sql-database-server
```

### 2. Communication Protocols & Ports

| Source Server | Target Server | Protocol | Port | Purpose |
|---|---|---|---|---|
| **hx-orchestration-server** | hx-llm-server-01 | HTTP/HTTPS | 8000 | OpenAI API calls |
| **hx-orchestration-server** | hx-llm-server-02 | HTTP/HTTPS | 8000 | Load balancing |
| **hx-orchestration-server** | hx-sql-database-server | TCP | 5432 | PostgreSQL queries |
| **hx-orchestration-server** | hx-sql-database-server | TCP | 6379 | Redis cache |
| **hx-orchestration-server** | hx-vector-database-server | HTTP | 6333 | Qdrant vector ops |
| **hx-llm-server-01/02** | hx-vector-database-server | HTTP | 6333 | Embedding retrieval |
| **hx-llm-server-01/02** | hx-sql-database-server | TCP | 5432 | Context data |
| **hx-dev-server** | hx-orchestration-server | HTTP | 8001 | Dev API testing |
| **hx-test-server** | All Servers | HTTP/TCP | Various | QA testing |
| **hx-metric-server** | All Servers | HTTP | 9090 | Prometheus metrics |
| **hx-devops-server** | All Servers | SSH/WinRM | 22/5985 | Management |

### 3. Network Security Zones

#### **DMZ (Future Implementation)**
- External-facing load balancer
- Web application firewall
- SSL termination

#### **Internal Network (192.168.10.0/24)**
- All HANA-X servers
- Private subnet with controlled access
- Internal DNS resolution

#### **Management Network (Future Enhancement)**
- Dedicated management interfaces
- Out-of-band management
- Secure admin access

### 4. Service Discovery & Load Balancing

#### **Internal Service Discovery**
```
hx-orchestration-server maintains service registry:
├── LLM Services: [hx-llm-server-01:8000, hx-llm-server-02:8000]
├── Database Services: [hx-sql-database-server:5432]
├── Vector DB: [hx-vector-database-server:6333]
└── Cache: [hx-sql-database-server:6379]
```

#### **Load Balancing Strategy**
- **LLM Servers**: Round-robin with health checks
- **Database**: Primary/standby (PostgreSQL)
- **Cache**: Redis with potential clustering

### 5. Monitoring & Observability Flow

```mermaid
graph LR
    subgraph "Data Collection"
        A["All Servers<br/>Metrics Export"]
    end
    
    subgraph "Centralized Monitoring"
        B["hx-metric-server<br/>Prometheus"]
        C["hx-metric-server<br/>Grafana"]
        D["hx-metric-server<br/>Loki"]
    end
    
    A --> B
    B --> C
    A --> D
```

### 6. Development & Testing Workflow

```mermaid
sequenceDiagram
    participant DEV as hx-dev-server
    participant TEST as hx-test-server
    participant ORCH as hx-orchestration-server
    participant LLM as hx-llm-server-01
    
    DEV->>ORCH: Deploy new code
    TEST->>ORCH: Run integration tests
    TEST->>LLM: Validate model endpoints
    TEST->>DEV: Report test results
```

---

## 🔐 Security Considerations

### Network Segmentation
- **Internal network isolation**: All servers on private subnet
- **Firewall rules**: Only necessary ports exposed
- **VPN access**: Secure remote management

### Authentication & Authorization
- **Service-to-service**: mTLS certificates
- **Database access**: Role-based access control
- **API security**: JWT tokens and rate limiting

### Encryption
- **Data in transit**: TLS 1.3 for all HTTP communications
- **Database connections**: SSL/TLS enabled
- **Internal APIs**: HTTPS with internal CA

---

## 🚀 Future Enhancements

### Phase 2 Networking
- **External load balancer**: nginx/HAProxy
- **Service mesh**: Istio for advanced traffic management
- **CDN integration**: Static asset delivery

### High Availability
- **Multi-AZ deployment**: Geographic redundancy
- **Database clustering**: PostgreSQL HA setup
- **Cache replication**: Redis Cluster

### Enhanced Security
- **Zero-trust networking**: mTLS everywhere
- **Network monitoring**: Intrusion detection
- **Compliance**: SOC2/ISO27001 alignment

---

## 📋 Validation Checklist

- [ ] All servers can reach each other on specified ports
- [ ] DNS resolution works for all hostnames
- [ ] SSL certificates are valid and trusted
- [ ] Firewall rules allow necessary traffic
- [ ] Monitoring endpoints are accessible
- [ ] Load balancing distributes requests properly
- [ ] Health checks return expected responses
- [ ] Backup and recovery procedures tested

---

**Document Status:** Draft  
**Next Review:** Post-Project 10 Integration  
**Owner:** HANA-X Program Team
