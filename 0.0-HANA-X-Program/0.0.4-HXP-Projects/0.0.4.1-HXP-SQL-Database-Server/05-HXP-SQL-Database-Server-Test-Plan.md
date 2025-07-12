# 🧪 HXP SQL Database Server Test Plan

**Target:** hx-sql-database-server (192.168.10.35)  
**Services:** PostgreSQL 17.5, Redis 8.0.3  
**Timeline:** 11 days (July 14-25, 2025)  
**Focus:** Core database functionality, performance, and integration

---

## 🎯 Core Test Objectives

**What we're testing:**
- ✅ PostgreSQL 17.5 and Redis 8.0.3 work correctly
- ✅ Performance meets targets (P95 <50ms PostgreSQL, <5ms Redis)
- ✅ 1000+ concurrent connections supported
- ✅ Integration with Citadel AI services works
- ✅ Basic security and backup/recovery functional

**What we're NOT over-testing:**
- Complex compliance frameworks
- Extensive documentation workflows
- Bureaucratic approval processes

---

## 🚀 Simple Test Strategy

### **Essential Test Categories**

| Category | What We Test | Success = | Tools |
|----------|--------------|-----------|-------|
| **Installation** | PostgreSQL 17.5 + Redis 8.0.3 install correctly | Services running, basic connectivity | `systemctl`, `psql`, `redis-cli` |
| **Performance** | Latency and throughput under load | P95 <50ms (PostgreSQL), <5ms (Redis), 1000+ connections | `pgbench`, `redis-benchmark` |
| **Integration** | Citadel AI services can connect and use databases | All services connect successfully | `curl`, connectivity scripts |
| **Security** | Basic security works (encryption, auth, backups) | SSL connections, RBAC, backups complete | `openssl`, backup tests |

---

## 🔧 Test Execution

### **Phase 1: Installation & Basic Function (Days 1-3)**
```bash
# Test PostgreSQL Installation
sudo systemctl status postgresql
psql -h 192.168.10.35 -c "SELECT version();"

# Test Redis Installation  
sudo systemctl status redis
redis-cli -h 192.168.10.35 ping

# Test Basic Schemas
psql -h 192.168.10.35 -d citadel_ai -c "\dt"
```

### **Phase 2: Performance Validation (Days 4-6)**
```bash
# PostgreSQL Performance Test
pgbench -h 192.168.10.35 -p 5432 -U citadel_admin -d citadel_ai -c 100 -j 10 -T 300

# Redis Performance Test
redis-benchmark -h 192.168.10.35 -p 6379 -c 100 -n 100000 -t get,set

# Connection Load Test
./test-concurrent-connections.sh --target=1000 --duration=60
```

### **Phase 3: Foundation Readiness (Days 7-9)**
```bash
# Prepare for future integrations - Database Foundation
psql -h 192.168.10.35 -d citadel_ai -c "CREATE SCHEMA IF NOT EXISTS integration_test;"

# Test database readiness for future AI services
psql -h 192.168.10.35 -d citadel_ai -c "SELECT COUNT(*) FROM ai_models;"
psql -h 192.168.10.35 -d citadel_ai -c "SELECT COUNT(*) FROM training_data;"

# Validate network infrastructure for future server connections
ping -c 3 192.168.10.31  # Future Orchestration Server
ping -c 3 192.168.10.29  # Future LLM Server 1
ping -c 3 192.168.10.28  # Future LLM Server 2
ping -c 3 192.168.10.33  # Future Development Server

# Test database is ready to accept connections from future servers
psql -h 192.168.10.35 -U citadel_app -c "SELECT 'Ready for AI services' as status;"
```

### **Phase 4: Security & Backup (Days 10-11)**
```bash
# Test SSL Connections
psql "sslmode=require host=192.168.10.35 dbname=citadel_ai"

# Test RBAC
psql -h 192.168.10.35 -U readonly_user -c "CREATE TABLE test_table(id INT);" # Should fail

# Test Backup/Recovery
sudo -u postgres pgbackrest backup --stanza=citadel_ai
sudo -u postgres pgbackrest restore --stanza=citadel_ai --delta
```

---

## 🎯 Success Criteria (The Real Deal)

### **Must Pass:**
- [ ] PostgreSQL 17.5 running and accessible
- [ ] Redis 8.0.3 running with 8GB memory configured
- [ ] pgbench achieves >8000 TPS with <50ms P95 latency
- [ ] redis-benchmark achieves >80000 ops/sec with <5ms P95 latency
- [ ] 1000+ concurrent connections work without errors
- [ ] Database foundation ready for future Citadel AI service integration
- [ ] SSL connections work
- [ ] Backup and restore completes successfully

### **Performance Targets:**
| Metric | Target | Test Command |
|--------|--------|--------------|
| PostgreSQL Latency P95 | <50ms | `pgbench -c 100 -j 10 -T 300` |
| Redis Latency P95 | <5ms | `redis-benchmark -c 100 -n 100000` |
| Concurrent Connections | 1000+ | Custom connection test script |
| PostgreSQL Throughput | 8000+ TPS | `pgbench` load test |
| Redis Throughput | 80000+ ops/sec | `redis-benchmark` |
| Backup Time | <15 minutes | `pgbackrest backup` timing |
| Recovery Time | <15 minutes | `pgbackrest restore` timing |

---

## 🔍 Test Scripts (Keep It Simple)

### **Quick Health Check**
```bash
#!/bin/bash
# quick-health-check.sh
echo "Testing PostgreSQL..."
psql -h 192.168.10.35 -c "SELECT 1;" && echo "✅ PostgreSQL OK" || echo "❌ PostgreSQL FAIL"

echo "Testing Redis..."
redis-cli -h 192.168.10.35 ping && echo "✅ Redis OK" || echo "❌ Redis FAIL"

echo "Testing Performance..."
pgbench -h 192.168.10.35 -c 10 -j 2 -T 60 | grep "tps =" && echo "✅ Performance test completed"
```

### **Foundation Readiness Test**
```bash
#!/bin/bash
# foundation-readiness-test.sh
FUTURE_SERVICES=("192.168.10.31" "192.168.10.29" "192.168.10.28" "192.168.10.33")

echo "Testing database foundation for future AI services..."

# Test database readiness
psql -h 192.168.10.35 -U citadel_app -c "SELECT 'Database Ready' as status;" && echo "✅ Database foundation ready"

# Test network readiness for future servers
for service in "${FUTURE_SERVICES[@]}"; do
    echo "Testing network path to future service $service..."
    ping -c 1 $service > /dev/null 2>&1 && echo "✅ Network path to $service ready" || echo "⚠️ $service not yet deployed (expected)"
done

# Test connection capacity for future services
psql -h 192.168.10.35 -c "SHOW max_connections;" && echo "✅ Connection capacity configured"
```

---

## 📊 Simple Reporting

### **Daily Status (Keep it short)**
```
Day X Status:
- PostgreSQL: ✅/❌
- Redis: ✅/❌  
- Performance: ✅/❌
- Integration: ✅/❌
- Issues: [Brief description if any]
```

### **Final Report (One page max)**
```
HXP SQL Database Server Test Results:
====================================
✅ PostgreSQL 17.5 installed and performing (X TPS, Y ms latency)
✅ Redis 8.0.3 installed and performing (X ops/sec, Y ms latency)  
✅ Integration with all Citadel AI services verified
✅ Basic security and backup/recovery functional
❌ [Any failures with brief resolution plan]

Production Ready: YES/NO
```

---

**Bottom Line:** Database works, performs well, integrates correctly. Let's ship it! 🚀

*"The ability to destroy a planet is insignificant next to the power of a working database." - Darth Vader (probably)*
