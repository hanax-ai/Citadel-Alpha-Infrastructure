# Database Credentials Configuration Guide

## Overview
This document provides comprehensive configuration details for all database connections in the Citadel LLM infrastructure.

## PostgreSQL Configuration

### Primary Database Server
- **Host**: `192.168.10.35`
- **Port**: `5432`
- **Database**: `postgres`
- **Authentication**: Simple username/password
- **Connection String**: `postgresql://username:password@192.168.10.35:5432/postgres`

### Multi-Server Setup
The Citadel infrastructure supports a multi-server PostgreSQL configuration:

#### HX-Server-01 (Primary)
- **IP**: `192.168.10.31`
- **Role**: Primary database server
- **Services**: Main PostgreSQL instance

#### HX-Server-02 (Secondary)
- **IP**: `192.168.10.36`
- **Role**: Secondary/replica database server
- **Services**: Backup PostgreSQL instance

## Database Users and Roles

### Administrative Users
Query the database for current users:
```sql
SELECT usename as "User name",
       usecreatedb as "Create DB",
       usesuper as "Superuser",
       userepl as "Replication"
FROM pg_user
ORDER BY usename;
```

### Common Database Operations

#### Connection Testing
```bash
# Test connection to primary database
psql -h 192.168.10.35 -p 5432 -U username -d postgres

# Test connection via Python
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='192.168.10.35',
        port=5432,
        database='postgres',
        user='username',
        password='password'
    )
    print('Connection successful')
    conn.close()
except Exception as e:
    print(f'Connection failed: {e}')
"
```

#### User Management
```sql
-- Create new user
CREATE USER new_username WITH PASSWORD 'secure_password';

-- Grant database privileges
GRANT ALL PRIVILEGES ON DATABASE postgres TO new_username;

-- Create read-only user
CREATE USER readonly_user WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE postgres TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
```

## Security Considerations

### Password Management
- Use strong, unique passwords for each database user
- Rotate passwords regularly according to your security policy
- Consider using environment variables for sensitive credentials:
  ```bash
  export POSTGRES_HOST="192.168.10.35"
  export POSTGRES_PORT="5432"
  export POSTGRES_DB="postgres"
  export POSTGRES_USER="your_username"
  export POSTGRES_PASSWORD="your_password"
  ```

### Network Security
- Database access is restricted to the internal network (192.168.10.x)
- Ensure proper firewall rules are in place
- Consider using SSL/TLS for database connections in production

### Connection Pooling
For high-traffic applications, implement connection pooling:
```python
from psycopg2 import pool

# Create connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,  # min and max connections
    host='192.168.10.35',
    port=5432,
    database='postgres',
    user='username',
    password='password'
)
```

## Monitoring Integration

### Database Metrics
The external monitoring system (192.168.10.37) can be configured to monitor PostgreSQL:

#### Prometheus PostgreSQL Exporter
```yaml
# Add to prometheus.yml
- job_name: 'postgres'
  static_configs:
    - targets: ['192.168.10.35:9187']
  metrics_path: /metrics
```

#### Common Monitoring Queries
```sql
-- Active connections
SELECT count(*) as active_connections FROM pg_stat_activity;

-- Database size
SELECT pg_size_pretty(pg_database_size('postgres')) as database_size;

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Backup and Recovery

### Automated Backups
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/opt/citadel/var/backup"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h 192.168.10.35 -p 5432 -U username postgres > $BACKUP_DIR/postgres_backup_$DATE.sql
```

### Recovery Procedures
```bash
# Restore from backup
psql -h 192.168.10.35 -p 5432 -U username -d postgres < backup_file.sql
```

## Application Integration

### Python Configuration
```python
# config/database.py
DATABASE_CONFIG = {
    'host': '192.168.10.35',
    'port': 5432,
    'database': 'postgres',
    'user': 'your_username',
    'password': 'your_password',
    'pool_size': 10,
    'max_overflow': 20
}
```

### Environment Variables
```bash
# .env file
POSTGRES_HOST=192.168.10.35
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

## Troubleshooting

### Common Issues
1. **Connection Timeout**: Check network connectivity and firewall rules
2. **Authentication Failed**: Verify username/password and user permissions
3. **Database Not Found**: Ensure the database exists and user has access
4. **Too Many Connections**: Implement connection pooling or increase max_connections

### Diagnostic Commands
```bash
# Check PostgreSQL service status
systemctl status postgresql

# View PostgreSQL logs
journalctl -u postgresql -f

# Check active connections
psql -h 192.168.10.35 -c "SELECT * FROM pg_stat_activity;"
```

## Related Documentation
- [PostgreSQL Setup Instructions](llm02-postgres-setup-instructions.md)
- [External Monitoring Integration](external-monitoring-integration.md)
- [Service Dependency Analysis](service-dependency-analysis.md)

---
*Document Version*: 1.0  
*Last Updated*: $(date)  
*Next Review*: $(date -d '+30 days')

*For immediate database issues, check the operational dashboards at http://192.168.10.37:3000 or contact the system administrator.*
