# Citadel LLM-02 Production Deployment Guide

## System Overview

**Citadel LLM-02** is a production-ready Large Language Model system with intelligent business API gateway, external service integrations, and comprehensive knowledge base.

### Core Components

1. **LLM Model Stack (5 Models)**
   - DeepSeek-R1:32b - Strategic Research & Intelligence
   - JARVIS:latest - Advanced Business Intelligence
   - Qwen:1.8b - High-Volume Operations
   - DeepCoder:14b - Code Generation
   - Yi:34b-chat - Advanced Reasoning

2. **Enhanced API Gateway v2.0**
   - Business intelligence endpoints
   - Technical operations endpoints
   - External service integrations
   - Knowledge base integration

3. **External Service Integrations**
   - PostgreSQL Database (192.168.10.35)
   - Vector Database with 15,847 vectors (192.168.10.30)
   - Monitoring System (192.168.10.37)
   - Web Server Integration (192.168.10.38)

## Production Deployment

### Prerequisites

- Ubuntu 24.04 LTS
- Python 3.12.x
- Ollama 0.9.6+
- 62GB+ RAM
- Network access to Citadel infrastructure

### Service Management

```bash
# Start all services
sudo systemctl start ollama-02.service
sudo systemctl start citadel-api-gateway.service

# Check status
sudo systemctl status ollama-02.service
sudo systemctl status citadel-api-gateway.service

# Enable auto-start
sudo systemctl enable ollama-02.service
sudo systemctl enable citadel-api-gateway.service
```

### Health Monitoring

```bash
# Run comprehensive health check
/opt/citadel-02/bin/production-health-check.sh

# Run performance test suite
/opt/citadel-02/bin/performance-test-suite.sh
```

### API Endpoints

**Base URL:** `http://192.168.10.28:8000`

**Core Endpoints:**

- `GET /` - Service information
- `GET /health` - Health check
- `GET /models` - Available models
- `GET /integration-health` - Comprehensive health check

**Business Intelligence:**

- `POST /api/v1/business/analyze` - Business analysis
- `POST /api/v2/business/analyze-enhanced` - Enhanced analysis with knowledge base
- `GET /api/v2/business/integration-status` - Integration status

**Technical Operations:**

- `POST /api/v1/technical/generate-code` - Code generation
- `POST /api/v1/technical/quick-process` - High-volume processing

### Performance Targets

- Qwen (Quick Processing): <5 seconds
- DeepCoder (Code Generation): <60 seconds
- JARVIS (Business Intelligence): <90 seconds
- Yi (Advanced Reasoning): <120 seconds
- DeepSeek-R1 (Strategic Research): <180 seconds

### Monitoring and Maintenance

1. **Daily Health Checks**
   - Run production health check script
   - Verify all models operational
   - Check external service connectivity

2. **Performance Monitoring**
   - Monitor response times
   - Check system resource usage
   - Verify knowledge base performance

3. **Log Management**
   - Monitor system logs: `journalctl -u citadel-api-gateway.service`
   - Check Ollama logs: `journalctl -u ollama-02.service`

### Troubleshooting

**Common Issues:**

1. **High Memory Usage**
   - Check model concurrency settings
   - Monitor system resources
   - Restart services if needed

2. **Slow Response Times**
   - Check network connectivity
   - Verify model performance
   - Review system load

3. **Integration Failures**
   - Test external service connectivity
   - Check configuration files
   - Verify credentials and permissions

### Support Contacts

- **System Administrator:** agent0@citadel
- **Infrastructure Team:** Citadel Operations
- **Documentation:** `/opt/citadel-02/X-Doc/`

## Production Readiness Checklist

- [x] All 5 models operational
- [x] API Gateway responding on port 8000
- [x] External service connectivity verified
- [x] Knowledge base search functional (15,847 vectors)
- [x] Performance targets met
- [x] Health monitoring operational
- [x] Documentation complete
- [x] Service auto-start configured
- [ ] Monitoring alerts configured
- [ ] Backup procedures in place

---

**Citadel LLM-02 - Production Ready**  
**Version:** 2.0.0  
**Last Updated:** 2025-07-26
