# Task 0.2: Security Framework & Access Control Setup

## Task Information

**Task Number:** 0.2  
**Task Title:** Security Framework & Access Control Setup  
**Created:** 2025-07-12  
**Assigned To:** Security Team  
**Priority:** High  
**Estimated Duration:** 90 minutes  

## Task Description

Establish enterprise security policies and access controls for the hx-sql-database-server. This task implements role-based access control (RBAC), SSL/TLS encryption, authentication integration, and audit logging framework to ensure enterprise-grade security before database service deployment.

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅ | Enterprise security configuration with defined authentication, encryption, and access controls |
| **Measurable** | ✅ | Success criteria include certificate verification, authentication tests, access validation |
| **Achievable** | ✅ | Standard enterprise security practices using proven tools and procedures |
| **Relevant** | ✅ | Critical security prerequisite for database deployment and enterprise integration |
| **Small** | ✅ | Focused on security framework setup only, no database-specific configuration |
| **Testable** | ✅ | Specific validation commands and expected security outcomes defined |

## Prerequisites

**Hard Dependencies:**
- Task 0.1: Hardware & Network Infrastructure Validation (must be 100% complete)

**Soft Dependencies:**
- None

**Conditional Dependencies:**
- None

## Configuration Requirements

**Environment Variables (.env):**
```
SERVER_IP=192.168.10.35
DOMAIN_NAME=citadel.local
CA_CERT_PATH=/etc/ssl/certs/citadel-ca.crt
SSL_CERT_PATH=/etc/ssl/certs/hx-sql-database.crt
SSL_KEY_PATH=/etc/ssl/private/hx-sql-database.key
LDAP_SERVER=192.168.10.40
AUDIT_LOG_PATH=/var/log/citadel-audit
```

**Configuration Files (.json/.yaml):**
```
config/security-policy.yaml - Enterprise security policies and rules
config/rbac-roles.json - Role-based access control definitions
config/ssl-config.yaml - SSL/TLS certificate and encryption settings
config/audit-logging.conf - Audit logging configuration
```

**External Resources:**
- Enterprise CA certificate authority
- LDAP/Active Directory authentication server
- Certificate management system
- Audit log aggregation service

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| 0.2.1 | SSL/TLS Certificate Installation | `sudo mkdir -p /etc/ssl/certs /etc/ssl/private`<br>`sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/hx-sql-database.key -out /etc/ssl/certs/hx-sql-database.crt` | Certificates generated, proper permissions set (600 for key, 644 for cert) |
| 0.2.2 | Enterprise Authentication Setup | `sudo apt install libpam-ldap libnss-ldap -y`<br>`sudo dpkg-reconfigure ldap-auth-config` | LDAP authentication configured, test user login successful |
| 0.2.3 | Role-Based Access Control (RBAC) | `sudo groupadd citadel-db-admin`<br>`sudo groupadd citadel-db-user`<br>`sudo groupadd citadel-db-readonly` | User groups created, sudo rules configured, access policies defined |
| 0.2.4 | Audit Logging Framework | `sudo mkdir -p /var/log/citadel-audit`<br>`sudo apt install auditd -y`<br>`sudo systemctl enable auditd` | Audit daemon running, log directory created, basic rules configured |
| 0.2.5 | Firewall Security Rules | `sudo ufw allow from 192.168.10.0/24 to any port 5432`<br>`sudo ufw allow from 192.168.10.0/24 to any port 6379`<br>`sudo ufw reload` | Database ports accessible from subnet only, external access blocked |

## Success Criteria

**Primary Objectives:**
- [ ] SSL/TLS certificates installed and properly configured
- [ ] Enterprise authentication integration functional
- [ ] Role-based access control framework implemented
- [ ] Audit logging framework operational
- [ ] Firewall rules configured for database security

**Validation Commands:**
```bash
# Verify SSL certificates
ssh citadel@192.168.10.35 'sudo openssl x509 -in /etc/ssl/certs/hx-sql-database.crt -text -noout | grep "Subject:"'

# Test LDAP authentication
ssh citadel@192.168.10.35 'getent passwd | grep citadel'

# Verify user groups
ssh citadel@192.168.10.35 'getent group | grep citadel-db'

# Check audit daemon
ssh citadel@192.168.10.35 'sudo systemctl status auditd'

# Verify firewall rules
ssh citadel@192.168.10.35 'sudo ufw status numbered | grep -E "(5432|6379)"'
```

**Expected Outputs:**
```
SSL: Subject: CN=hx-sql-database.citadel.local
LDAP: citadel users listed in passwd
Groups: citadel-db-admin, citadel-db-user, citadel-db-readonly
Audit: auditd.service - Linux Audit daemon (active/running)
Firewall: Rules allowing ports 5432 and 6379 from 192.168.10.0/24
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| SSL certificate configuration errors | Medium | High | Use automated certificate generation, verify with multiple validation commands |
| LDAP authentication failures | Medium | High | Test with known good credentials, fallback to local authentication |
| Access control misconfigurations | Low | High | Implement least-privilege principle, test all access scenarios |
| Audit logging failures | Low | Medium | Configure multiple audit targets, verify log rotation |
| Firewall blocking legitimate access | Medium | Medium | Test connectivity from all required services, document access patterns |

## Rollback Procedures

**If Task Fails:**
1. Remove SSL certificates: `sudo rm -f /etc/ssl/certs/hx-sql-database.* /etc/ssl/private/hx-sql-database.*`
2. Disable LDAP authentication: `sudo pam-auth-update --remove ldap`
3. Remove user groups: `sudo groupdel citadel-db-admin citadel-db-user citadel-db-readonly`
4. Stop audit daemon: `sudo systemctl stop auditd && sudo systemctl disable auditd`
5. Reset firewall: `sudo ufw --force reset`

**Rollback Validation:**
```bash
# Verify SSL cleanup
ssh citadel@192.168.10.35 'ls -la /etc/ssl/certs/hx-sql-database.* /etc/ssl/private/hx-sql-database.*'  # Should show "No such file"

# Check LDAP removal
ssh citadel@192.168.10.35 'pam-auth-update --package --remove ldap; echo $?'  # Should return 0

# Verify group cleanup
ssh citadel@192.168.10.35 'getent group | grep citadel-db'  # Should be empty

# Check audit daemon
ssh citadel@192.168.10.35 'systemctl is-active auditd'  # Should show inactive

# Verify firewall reset
ssh citadel@192.168.10.35 'sudo ufw status'  # Should show inactive
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| 2025-07-12 | Task Created | Ready | Template applied, ready for execution after Task 0.1 |

## Dependencies This Task Enables

**Next Tasks:**
- Task 1.1: PostgreSQL 17.5 Installation & Base Configuration
- Task 1.2: Redis 8.0.3 Installation & Base Configuration
- Task 1.3: Initial Database Schema & Configuration Management

**Parallel Candidates:**
- None (security must be established before database installation)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| SSL certificate generation fails | OpenSSL errors, permission denied | Check disk space, verify /etc/ssl directory permissions, run as root |
| LDAP authentication not working | User logins fail, getent returns empty | Verify LDAP server connectivity, check configuration syntax |
| User groups not created properly | Group commands fail, permission denied | Ensure sudo access, check for existing conflicting groups |
| Audit daemon won't start | Service fails to start, journalctl errors | Check auditd configuration, verify log directory permissions |
| Firewall rules not applied | Rules missing from ufw status | Reload firewall rules, check rule syntax, verify ufw enabled |

**Debug Commands:**
```bash
# Check SSL certificate details
ssh citadel@192.168.10.35 'sudo openssl x509 -in /etc/ssl/certs/hx-sql-database.crt -text -noout'

# Test LDAP connectivity
ssh citadel@192.168.10.35 'ldapsearch -x -H ldap://192.168.10.40 -D "cn=admin,dc=citadel,dc=local" -W'

# Check user group memberships
ssh citadel@192.168.10.35 'groups citadel; id citadel'

# Examine audit daemon logs
ssh citadel@192.168.10.35 'sudo journalctl -u auditd -n 20'

# Test firewall connectivity
ssh citadel@192.168.10.35 'sudo ufw status verbose'
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status in `02-HXP-SQL-Database-Server-Task-List.md`
- [ ] Create result summary document: `Task_0.2_Security_Framework_Access_Control_Setup_Results.md`
- [ ] Update security documentation with implemented controls

**Result Document Location:**
- Save to: `/0.0-HANA-X-Program/0.0.4-HXP-Projects/0.0.4.1-HXP-SQL-Database-Server/tasks/results/Task_0.2_Results.md`

**Notification Requirements:**
- [ ] Notify database teams that security framework is ready
- [ ] Update security compliance dashboard
- [ ] Communicate authentication integration status to enterprise teams

## Notes

Security framework must be fully operational before any database software installation. This task establishes the security foundation that all database services will depend on. All security configurations should be tested thoroughly and documented for audit purposes.

The RBAC implementation provides three levels of database access: admin (full control), user (read/write), and readonly (select only). These roles will be mapped to database-specific permissions in subsequent tasks.

---

**Template Version:** 1.0  
**Last Updated:** 2025-07-12  
**Template Source:** Based on SMART+ST principles from hx-task-creation.md
