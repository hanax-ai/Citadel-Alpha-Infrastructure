# 📝 Test Case: Security Configuration Validation

## Test Case Information

**Test Case ID:** TC-P03-3.1  
**Test Case Name:** Validate Security Configuration & Access Control  
**Test Suite:** HXP SQL Database Server  
**Created Date:** 2025-07-12  
**Created By:** QA Team  
**Version:** 1.0  

---

## Test Case Classification

**Test Type:** Security  
**Test Category:** Access Control  
**Test Priority:** Critical  
**Test Complexity:** High  
**Automation Status:** Semi-Automated  
**Execution Environment:** hx-sql-database-server (192.168.10.35)  

---

## Test Objective

**Purpose:** Verify security configurations meet enterprise requirements for AI workload protection

**Test Description:** Validates SSL/TLS encryption, role-based access control (RBAC), authentication mechanisms, network security, and data protection for both PostgreSQL and Redis components.

**Business Value:** Ensures data security and compliance for AI operations in production environment

---

## Requirements Traceability

**Related Tasks:**
- **Task 3.1:** SSL/TLS Configuration & Certificate Management
- **Task 3.2:** Role-Based Access Control (RBAC) Implementation
- **Task 3.3:** Network Security & Firewall Configuration

**Related Documents:**
- [01-HXP-SQL-Database-Server-PRD.md](../01-HXP-SQL-Database-Server-PRD.md)
- [Task_3.1_SSL_TLS_Configuration_Certificate_Management.md](../HXP-SQL-Database-Server-Task/Task_3.1_SSL_TLS_Configuration_Certificate_Management.md)

---

## Test Prerequisites

**System Prerequisites:**
- PostgreSQL 17.5 with SSL configured
- Redis 8.0.3 with authentication enabled
- SSL certificates installed and valid
- Firewall rules configured

**Environment Prerequisites:**
- SSH access to hx-sql-database-server
- Administrative privileges for security testing
- Network access for external connection testing
- SSL certificate testing tools

---

## Test Steps

| Step # | Action | Expected Result | Notes |
|--------|--------|-----------------|-------|
| 1 | SSL/TLS connection test | Encrypted connections work | PostgreSQL SSL |
| 2 | Authentication validation | RBAC properly enforced | User role testing |
| 3 | Redis security test | AUTH required and working | Redis authentication |
| 4 | Network security test | Firewall rules effective | Port access control |
| 5 | Certificate validation | Valid certs and rotation | Certificate management |

### Step 1: SSL/TLS Connection Testing
**Action:** Verify SSL encryption for PostgreSQL  
**Commands:**
```bash
# Test SSL connection
psql "sslmode=require host=192.168.10.35 user=postgres dbname=citadel_ai"

# Verify SSL is enforced
psql "sslmode=disable host=192.168.10.35 user=postgres dbname=citadel_ai" 2>&1 | grep -i "ssl"

# Check SSL configuration
sudo -u postgres psql -c "SHOW ssl;"
sudo -u postgres psql -c "SELECT * FROM pg_stat_ssl;"
```
**Expected Result:** SSL connections work, non-SSL connections rejected  
**Verification:** All connections encrypted, SSL properly configured  

### Step 2: Role-Based Access Control Testing
**Action:** Validate user permissions and role enforcement  
**Commands:**
```bash
# Test read-only user
psql -h 192.168.10.35 -U citadel_readonly -d citadel_ai -c "SELECT COUNT(*) FROM ai_models;"
psql -h 192.168.10.35 -U citadel_readonly -d citadel_ai -c "INSERT INTO ai_models (model_name) VALUES ('test');" 2>&1

# Test application user
psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "INSERT INTO inference_logs (model_id, result) VALUES (1, 'test');"
psql -h 192.168.10.35 -U citadel_app -d citadel_ai -c "DROP TABLE ai_models;" 2>&1

# Test admin user
psql -h 192.168.10.35 -U citadel_admin -d citadel_ai -c "CREATE TABLE test_admin (id INT);"
psql -h 192.168.10.35 -U citadel_admin -d citadel_ai -c "DROP TABLE test_admin;"
```
**Expected Result:** Permissions enforced per role  
**Verification:** Read-only cannot write, app user limited, admin has full access  

### Step 3: Redis Authentication Testing
**Action:** Verify Redis AUTH requirement  
**Commands:**
```bash
# Test connection without auth (should fail)
redis-cli -h 192.168.10.35 -p 6379 ping 2>&1

# Test with correct auth
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" ping

# Test with wrong auth
redis-cli -h 192.168.10.35 -p 6379 -a "wrongpassword" ping 2>&1

# Verify ACL configuration
redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" ACL LIST
```
**Expected Result:** Authentication required and working  
**Verification:** Unauthorized access blocked, valid credentials work  

### Step 4: Network Security Testing
**Action:** Validate firewall and network access controls  
**Commands:**
```bash
# Test PostgreSQL port access
nmap -p 5432 192.168.10.35

# Test Redis port access
nmap -p 6379 192.168.10.35

# Test from unauthorized network
nmap -p 5432,6379 192.168.10.35 --source-port 12345

# Check firewall rules
sudo ufw status verbose
sudo iptables -L -n
```
**Expected Result:** Only authorized ports/sources accessible  
**Verification:** Firewall rules properly restrict access  

### Step 5: Certificate Validation Testing
**Action:** Verify SSL certificate validity and management  
**Commands:**
```bash
# Check certificate validity
openssl s_client -connect 192.168.10.35:5432 -servername hx-sql-database-server < /dev/null 2>/dev/null | openssl x509 -noout -dates

# Verify certificate chain
openssl s_client -connect 192.168.10.35:5432 -showcerts < /dev/null 2>/dev/null

# Check certificate expiration
openssl x509 -in /etc/postgresql/17/main/server.crt -noout -enddate

# Test certificate rotation readiness
sudo postgresql-certificate-check.sh
```
**Expected Result:** Valid certificates with proper expiration dates  
**Verification:** Certificates valid, rotation procedures functional  

---

## Expected Results

**Primary Expected Result:** All security configurations properly implemented and functional

**Security Requirements:**
- **SSL/TLS:** All connections encrypted with TLS 1.2+
- **Authentication:** Strong passwords, multi-factor where required
- **Authorization:** RBAC properly enforced
- **Network Security:** Firewall rules restrict unauthorized access
- **Certificate Management:** Valid certificates with automated rotation

---

## Pass/Fail Criteria

**Pass Criteria:**
- [ ] SSL/TLS connections work and are enforced
- [ ] Non-encrypted connections are rejected
- [ ] User roles and permissions properly enforced
- [ ] Redis authentication required and working
- [ ] Firewall rules block unauthorized access
- [ ] SSL certificates valid and not near expiration
- [ ] Certificate rotation procedures functional
- [ ] No security vulnerabilities detected

**Fail Criteria:**
- [ ] Unencrypted connections allowed
- [ ] Permission bypass possible
- [ ] Authentication can be circumvented
- [ ] Unauthorized network access possible
- [ ] Invalid or expired certificates
- [ ] Security misconfigurations detected

---

## Automation Commands

```bash
#!/bin/bash
# Security Configuration Test Script

echo "=== Security Configuration Validation Test ==="

# Test 1: SSL Connection
echo "Testing SSL connections..."
ssl_test=$(psql "sslmode=require host=192.168.10.35 user=postgres dbname=citadel_ai" -c "SELECT 1;" 2>/dev/null)
if [ "$ssl_test" = " 1" ]; then
    echo "✅ SSL OK: Encrypted connections working"
else
    echo "❌ SSL FAIL: SSL connections not working"
fi

# Test 2: SSL Enforcement
echo "Testing SSL enforcement..."
no_ssl_test=$(psql "sslmode=disable host=192.168.10.35 user=postgres dbname=citadel_ai" -c "SELECT 1;" 2>&1 | grep -i "ssl required")
if [ -n "$no_ssl_test" ]; then
    echo "✅ SSL Enforcement OK: Non-SSL connections rejected"
else
    echo "❌ SSL Enforcement FAIL: Non-SSL connections allowed"
fi

# Test 3: Redis Authentication
echo "Testing Redis authentication..."
redis_auth_fail=$(redis-cli -h 192.168.10.35 -p 6379 ping 2>&1 | grep -i "auth")
redis_auth_success=$(redis-cli -h 192.168.10.35 -p 6379 -a "$REDIS_PASSWORD" ping 2>/dev/null)

if [ -n "$redis_auth_fail" ] && [ "$redis_auth_success" = "PONG" ]; then
    echo "✅ Redis Auth OK: Authentication required and working"
else
    echo "❌ Redis Auth FAIL: Authentication not properly configured"
fi

# Test 4: Certificate Validity
echo "Testing certificate validity..."
cert_expiry=$(openssl x509 -in /etc/postgresql/17/main/server.crt -noout -checkend 86400 2>/dev/null && echo "valid" || echo "invalid")
if [ "$cert_expiry" = "valid" ]; then
    echo "✅ Certificate OK: SSL certificate valid"
else
    echo "❌ Certificate FAIL: SSL certificate invalid or expiring"
fi

# Test 5: Firewall Rules
echo "Testing firewall configuration..."
firewall_active=$(sudo ufw status | grep "Status: active")
if [ -n "$firewall_active" ]; then
    echo "✅ Firewall OK: Firewall active and configured"
else
    echo "❌ Firewall FAIL: Firewall not active"
fi

# Test 6: Port Security
echo "Testing port accessibility..."
pg_port_open=$(nmap -p 5432 192.168.10.35 2>/dev/null | grep "5432/tcp open")
redis_port_status=$(nmap -p 6379 192.168.10.35 2>/dev/null | grep "6379/tcp")

if [ -n "$pg_port_open" ]; then
    echo "✅ PostgreSQL Port: Accessible from authorized network"
else
    echo "❌ PostgreSQL Port: Not accessible (check firewall rules)"
fi

echo "=== Security Test Complete ==="
```

---

## Security Test Data

**Test Users:**
- `citadel_readonly`: Read-only access to AI data
- `citadel_app`: Application user with limited write access
- `citadel_admin`: Administrative access for management
- `citadel_backup`: Backup operations only

**Test Scenarios:**
- Privilege escalation attempts
- SQL injection testing
- Brute force authentication testing
- Network scanning from unauthorized sources

---

## Notes

- Security testing should be conducted in isolated environment
- Test credentials should be rotated after testing
- All security tests should be documented and reviewed
- Penetration testing may be required for production deployment
- Compliance requirements should be validated separately

---

**Related Test Cases:**
- Test_1.1_Validate_PostgreSQL_Installation.md
- Test_1.2_Validate_Redis_Installation.md
- Test_4.1_Validate_Backup_Recovery.md
- Test_5.1_Validate_Citadel_Integration.md
