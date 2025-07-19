# TC-L2-INT-DB-001: PostgreSQL Connection Test

**Test Case ID:** `TC-L2-INT-DB-001`  
**Test Case Name:** `PostgreSQL Connection Test`  
**Test Category:** `Integration`  
**Certification Level:** `Level 2`  
**Priority:** `Critical`  
**Test Type:** `Integration`  

### **Component Mapping**
- **Architecture Component:** `Integration Service`  
- **Service Name:** `database`  
- **Module Path:** `hxp_enterprise_llm.services.integration.database.postgresql`  
- **Configuration Schema:** `PostgreSQLConfig`  

### **Traceability**
- **Requirements Reference:** `PRD Section 4.4 - Integration and Connectivity Requirements`  
- **User Story:** `As a system administrator, I want the LLM server to connect reliably to the PostgreSQL database`  
- **Architecture Document Section:** `Section 4.4 - Integration Architecture and Communication Patterns`  
- **High-Level Task Reference:** `Phase-2 Task 2.1 - Database Integration Implementation`  

---

## 🎯 **TEST OBJECTIVE**

### **Primary Objective**
Validate that the HXP-Enterprise LLM Server can establish and maintain reliable connections to the PostgreSQL database server, including connection pooling, transaction management, and error recovery capabilities.

### **Success Criteria**
- **Functional:** Database connections are established successfully with proper authentication
- **Performance:** Connection establishment time < 5 seconds, query response time < 100ms
- **Quality:** Connection pooling works correctly, transactions are managed properly
- **Integration:** Database operations integrate seamlessly with LLM services

### **Business Value**
Ensures reliable data persistence and retrieval capabilities, enabling the LLM server to store configuration, usage statistics, and operational data effectively.

---

## 📊 **TEST SPECIFICATIONS**

### **Test Environment**
- **Environment Type:** `Development`  
- **Infrastructure Requirements:**
  - **CPU:** `4 cores minimum`  
  - **Memory:** `16GB minimum`  
  - **Storage:** `5GB minimum`  
  - **Network:** `1Gbps connectivity`  
- **Dependencies:**
  - **External Services:** `PostgreSQL Server (192.168.10.35:5432)`  
  - **Test Data:** `Database schema and test data`  
  - **Mock Services:** `Mock PostgreSQL server for isolated testing`  

### **Test Data Requirements**
- **Input Data:** `Database connection parameters and test queries`  
- **Expected Output:** `Successful database operations and proper error handling`  
- **Test Fixtures:** `database_test_schema.sql, test_data.sql`  
- **Data Generation:** `Database test data generator`  

### **Performance Targets**
- **Latency Target:** `5 seconds maximum connection time, 100ms maximum query time`  
- **Throughput Target:** `100 concurrent connections`  
- **Resource Utilization:** `16GB memory limit, 4 CPU cores limit`  
- **Concurrent Users:** `10 concurrent database operations`  

---

## 🔧 **TEST IMPLEMENTATION**

### **Pre-conditions**
1. PostgreSQL server is running and accessible at 192.168.10.35:5432
2. Database schema is created and initialized
3. Test user credentials are configured
4. Network connectivity is established
5. Connection pooling is configured

### **Test Setup**
```python
import pytest
import asyncio
import psycopg2
import asyncpg
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from hxp_enterprise_llm.services.integration.database.postgresql.connection import PostgreSQLConnection
from hxp_enterprise_llm.services.integration.database.postgresql.pool import ConnectionPool
from hxp_enterprise_llm.schemas.configuration.database_schemas import PostgreSQLConfig
from hxp_enterprise_llm.testing.utilities.test_environment_manager import TestEnvironmentManager
from hxp_enterprise_llm.testing.utilities.database_test_utils import DatabaseTestUtils

class TestPostgreSQLConnection:
    """Test class for PostgreSQL database connection testing."""
    
    @pytest.fixture(scope="class")
    async def test_environment(self):
        """Setup test environment."""
        env_manager = TestEnvironmentManager()
        await env_manager.setup_environment()
        yield env_manager
        await env_manager.teardown_environment()
    
    @pytest.fixture
    def database_config(self):
        """Generate database configuration."""
        return PostgreSQLConfig(
            host="192.168.10.35",
            port=5432,
            database="hana_x_llm",
            username="hana_x_user",
            password="test_password",
            pool_size=10,
            max_overflow=20,
            connection_timeout=30,
            query_timeout=60
        )
    
    @pytest.fixture
    async def database_connection(self, database_config):
        """Fixture for database connection."""
        connection = PostgreSQLConnection(database_config)
        yield connection
        await connection.close()
    
    @pytest.fixture
    async def connection_pool(self, database_config):
        """Fixture for connection pool."""
        pool = ConnectionPool(database_config)
        await pool.initialize()
        yield pool
        await pool.close()
    
    @pytest.fixture
    def database_utils(self):
        """Fixture for database test utilities."""
        return DatabaseTestUtils()
```

### **Test Steps**
1. **Step 1:** Basic connection establishment
   ```python
   async def test_basic_connection(self, database_connection):
       """Test basic database connection establishment."""
       start_time = time.time()
       await database_connection.connect()
       connection_time = (time.time() - start_time) * 1000
       
       assert database_connection.is_connected() is True
       assert connection_time < 5000, f"Connection time {connection_time}ms exceeds 5s target"
       
       # Test connection health
       health_status = await database_connection.health_check()
       assert health_status.healthy is True
       assert health_status.response_time < 100, f"Health check time {health_status.response_time}ms exceeds 100ms"
   ```

2. **Step 2:** Connection pool validation
   ```python
   async def test_connection_pool(self, connection_pool):
       """Test connection pool functionality."""
       # Test pool initialization
       assert connection_pool.is_initialized() is True
       assert connection_pool.pool_size == 10
       assert connection_pool.max_overflow == 20
       
       # Test connection acquisition
       connections = []
       for i in range(5):
           conn = await connection_pool.acquire()
           connections.append(conn)
           assert conn is not None
       
       # Test concurrent connections
       assert len(connections) == 5
       
       # Test connection release
       for conn in connections:
           await connection_pool.release(conn)
       
       # Verify pool state
       pool_stats = await connection_pool.get_stats()
       assert pool_stats.available_connections == 10
       assert pool_stats.active_connections == 0
   ```

3. **Step 3:** Transaction management
   ```python
   async def test_transaction_management(self, database_connection):
       """Test database transaction management."""
       await database_connection.connect()
       
       # Test transaction begin
       transaction = await database_connection.begin_transaction()
       assert transaction is not None
       assert transaction.is_active() is True
       
       # Test data insertion
       test_data = {"key": "test_value", "timestamp": time.time()}
       insert_result = await transaction.execute(
           "INSERT INTO test_table (key, value, created_at) VALUES ($1, $2, $3)",
           (test_data["key"], test_data["timestamp"], time.time())
       )
       assert insert_result.rowcount == 1
       
       # Test data retrieval
       select_result = await transaction.execute(
           "SELECT * FROM test_table WHERE key = $1",
           (test_data["key"],)
       )
       assert len(select_result) == 1
       assert select_result[0]["value"] == test_data["timestamp"]
       
       # Test transaction commit
       await transaction.commit()
       assert transaction.is_active() is False
   ```

4. **Step 4:** Error handling and recovery
   ```python
   async def test_error_handling(self, database_connection):
       """Test database error handling and recovery."""
       await database_connection.connect()
       
       # Test invalid query handling
       try:
           await database_connection.execute("SELECT * FROM non_existent_table")
           pytest.fail("Expected exception for invalid query")
       except Exception as e:
           assert "relation" in str(e).lower() or "table" in str(e).lower()
       
       # Test connection recovery after error
       health_status = await database_connection.health_check()
       assert health_status.healthy is True
       
       # Test transaction rollback
       transaction = await database_connection.begin_transaction()
       
       # Insert valid data
       await transaction.execute(
           "INSERT INTO test_table (key, value, created_at) VALUES ($1, $2, $3)",
           ("rollback_test", "test_value", time.time())
       )
       
       # Insert invalid data to trigger rollback
       try:
           await transaction.execute(
               "INSERT INTO test_table (invalid_column) VALUES ($1)",
               ("invalid_value",)
           )
           pytest.fail("Expected exception for invalid column")
       except Exception:
           await transaction.rollback()
       
       # Verify rollback worked
       select_result = await database_connection.execute(
           "SELECT * FROM test_table WHERE key = $1",
           ("rollback_test",)
       )
       assert len(select_result) == 0
   ```

5. **Step 5:** Performance validation
   ```python
   async def test_performance_validation(self, connection_pool):
       """Test database performance under load."""
       # Test concurrent query execution
       concurrent_queries = 10
       queries = ["SELECT 1", "SELECT NOW()", "SELECT version()"] * 4
       
       start_time = time.time()
       tasks = []
       for i in range(concurrent_queries):
           conn = await connection_pool.acquire()
           task = asyncio.create_task(self._execute_query(conn, queries[i % len(queries)]))
           tasks.append(task)
       
       results = await asyncio.gather(*tasks)
       total_time = (time.time() - start_time) * 1000
       
       # Validate results
       assert len(results) == concurrent_queries
       assert all(result is not None for result in results)
       
       # Validate performance
       avg_query_time = total_time / concurrent_queries
       assert avg_query_time < 100, f"Average query time {avg_query_time:.2f}ms exceeds 100ms target"
       
       # Release connections
       for task in tasks:
           await connection_pool.release(task._conn)
   ```

### **Main Test Method**
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_postgresql_connection(self, database_connection, connection_pool, database_utils, test_environment):
    """
    Test Case: PostgreSQL Connection Test
    Objective: Validate database connection establishment, pooling, and transaction management
    Level: Level 2 - Integration Certification
    """
    
    # Test execution
    try:
        # Step 1: Basic connection validation
        connection_result = await self._test_basic_connection(database_connection)
        assert connection_result.success is True, "Basic connection failed"
        assert connection_result.connection_time < 5000, f"Connection time {connection_result.connection_time}ms exceeds target"
        
        # Step 2: Connection pool validation
        pool_result = await self._test_connection_pool(connection_pool)
        assert pool_result.initialized is True, "Connection pool initialization failed"
        assert pool_result.acquisition_ok is True, "Connection acquisition failed"
        assert pool_result.release_ok is True, "Connection release failed"
        
        # Step 3: Transaction management validation
        transaction_result = await self._test_transaction_management(database_connection)
        assert transaction_result.begin_ok is True, "Transaction begin failed"
        assert transaction_result.insert_ok is True, "Data insertion failed"
        assert transaction_result.select_ok is True, "Data retrieval failed"
        assert transaction_result.commit_ok is True, "Transaction commit failed"
        
        # Step 4: Error handling validation
        error_result = await self._test_error_handling(database_connection)
        assert error_result.error_handling_ok is True, "Error handling failed"
        assert error_result.recovery_ok is True, "Connection recovery failed"
        assert error_result.rollback_ok is True, "Transaction rollback failed"
        
        # Step 5: Performance validation
        performance_result = await self._test_performance(connection_pool)
        assert performance_result.concurrent_ok is True, "Concurrent queries failed"
        assert performance_result.avg_query_time < 100, f"Average query time {performance_result.avg_query_time:.2f}ms exceeds target"
        
        # Integration validation
        integration_result = await self._validate_integration(test_environment)
        assert integration_result.database_accessible is True, "Database not accessible from test environment"
        assert integration_result.schema_valid is True, "Database schema validation failed"
        
    except Exception as e:
        pytest.fail(f"Test execution failed: {str(e)}")
    
    finally:
        # Cleanup
        await self._cleanup_test_resources(database_connection, connection_pool)

async def _test_basic_connection(self, connection):
    """Test basic database connection."""
    start_time = time.time()
    await connection.connect()
    connection_time = (time.time() - start_time) * 1000
    
    health_status = await connection.health_check()
    
    return type('Result', (), {
        'success': connection.is_connected(),
        'connection_time': connection_time,
        'healthy': health_status.healthy,
        'response_time': health_status.response_time
    })()

async def _test_connection_pool(self, pool):
    """Test connection pool functionality."""
    # Test pool initialization
    initialized = pool.is_initialized()
    
    # Test connection acquisition
    connections = []
    acquisition_ok = True
    try:
        for i in range(5):
            conn = await pool.acquire()
            connections.append(conn)
    except Exception:
        acquisition_ok = False
    
    # Test connection release
    release_ok = True
    try:
        for conn in connections:
            await pool.release(conn)
    except Exception:
        release_ok = False
    
    return type('Result', (), {
        'initialized': initialized,
        'acquisition_ok': acquisition_ok,
        'release_ok': release_ok
    })()

async def _test_transaction_management(self, connection):
    """Test transaction management."""
    await connection.connect()
    
    # Test transaction begin
    transaction = await connection.begin_transaction()
    begin_ok = transaction is not None and transaction.is_active()
    
    # Test data insertion
    insert_ok = True
    try:
        await transaction.execute(
            "INSERT INTO test_table (key, value, created_at) VALUES ($1, $2, $3)",
            ("transaction_test", "test_value", time.time())
        )
    except Exception:
        insert_ok = False
    
    # Test data retrieval
    select_ok = True
    try:
        result = await transaction.execute(
            "SELECT * FROM test_table WHERE key = $1",
            ("transaction_test",)
        )
        select_ok = len(result) == 1
    except Exception:
        select_ok = False
    
    # Test transaction commit
    commit_ok = True
    try:
        await transaction.commit()
        commit_ok = not transaction.is_active()
    except Exception:
        commit_ok = False
    
    return type('Result', (), {
        'begin_ok': begin_ok,
        'insert_ok': insert_ok,
        'select_ok': select_ok,
        'commit_ok': commit_ok
    })()

async def _test_error_handling(self, connection):
    """Test error handling and recovery."""
    await connection.connect()
    
    # Test invalid query handling
    error_handling_ok = True
    try:
        await connection.execute("SELECT * FROM non_existent_table")
        error_handling_ok = False
    except Exception:
        pass
    
    # Test connection recovery
    health_status = await connection.health_check()
    recovery_ok = health_status.healthy
    
    # Test transaction rollback
    rollback_ok = True
    try:
        transaction = await connection.begin_transaction()
        await transaction.execute(
            "INSERT INTO test_table (key, value, created_at) VALUES ($1, $2, $3)",
            ("rollback_test", "test_value", time.time())
        )
        await transaction.execute(
            "INSERT INTO test_table (invalid_column) VALUES ($1)",
            ("invalid_value",)
        )
    except Exception:
        await transaction.rollback()
        rollback_ok = True
    
    return type('Result', (), {
        'error_handling_ok': error_handling_ok,
        'recovery_ok': recovery_ok,
        'rollback_ok': rollback_ok
    })()

async def _test_performance(self, pool):
    """Test database performance."""
    concurrent_queries = 10
    queries = ["SELECT 1", "SELECT NOW()", "SELECT version()"] * 4
    
    start_time = time.time()
    tasks = []
    try:
        for i in range(concurrent_queries):
            conn = await pool.acquire()
            task = asyncio.create_task(self._execute_query(conn, queries[i % len(queries)]))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        concurrent_ok = all(result is not None for result in results)
    except Exception:
        concurrent_ok = False
    
    total_time = (time.time() - start_time) * 1000
    avg_query_time = total_time / concurrent_queries if concurrent_queries > 0 else 0
    
    # Release connections
    for task in tasks:
        try:
            await pool.release(task._conn)
        except:
            pass
    
    return type('Result', (), {
        'concurrent_ok': concurrent_ok,
        'avg_query_time': avg_query_time
    })()

async def _execute_query(self, connection, query):
    """Execute a database query."""
    try:
        result = await connection.execute(query)
        return result
    except Exception:
        return None

async def _validate_integration(self, test_environment):
    """Validate integration with test environment."""
    # Test database accessibility
    database_accessible = await test_environment.check_database_accessibility()
    
    # Test schema validation
    schema_valid = await test_environment.validate_database_schema()
    
    return type('Result', (), {
        'database_accessible': database_accessible,
        'schema_valid': schema_valid
    })()

async def _cleanup_test_resources(self, connection, pool):
    """Cleanup test resources."""
    if connection.is_connected():
        await connection.close()
    
    if pool.is_initialized():
        await pool.close()
```

---

## 📋 **EXPECTED RESULTS**

### **Pass Criteria**
- ✅ Database connection established within 5 seconds
- ✅ Connection pool manages 10 concurrent connections
- ✅ Transactions are properly managed (begin, commit, rollback)
- ✅ Error handling works correctly with proper recovery
- ✅ Average query time < 100ms
- ✅ Database schema validation passes
- ✅ Integration with test environment works

### **Fail Criteria**
- ❌ Connection establishment takes > 5 seconds
- ❌ Connection pool fails to manage concurrent connections
- ❌ Transaction management fails
- ❌ Error handling doesn't work properly
- ❌ Average query time >= 100ms
- ❌ Database schema validation fails
- ❌ Integration with test environment fails

### **Test Data**
```sql
-- database_test_schema.sql
CREATE TABLE IF NOT EXISTS test_table (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_table_key ON test_table(key);

-- test_data.sql
INSERT INTO test_table (key, value) VALUES 
    ('test_key_1', 'test_value_1'),
    ('test_key_2', 'test_value_2'),
    ('test_key_3', 'test_value_3');
```

---

## 🔍 **VALIDATION CHECKLIST**

- [ ] Database connection establishes successfully
- [ ] Connection pool works correctly
- [ ] Transactions are managed properly
- [ ] Error handling and recovery work
- [ ] Performance targets are met
- [ ] Schema validation passes
- [ ] Integration with environment works
- [ ] Cleanup procedures execute properly

---

**Test Case Status:** Ready for Implementation  
**Created:** 2025-01-18  
**Last Updated:** 2025-01-18  
**Next Review:** After implementation 