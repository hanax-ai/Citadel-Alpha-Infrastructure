# TC-L1-COMP-MIXTRAL-001: Mixtral Service Initialization

**Test Case ID:** `TC-L1-COMP-MIXTRAL-001`  
**Test Case Name:** `Mixtral Service Initialization`  
**Test Category:** `Component`  
**Certification Level:** `Level 1`  
**Priority:** `Critical`  
**Test Type:** `Functional`  

### **Component Mapping**
- **Architecture Component:** `AI Model Service`  
- **Service Name:** `mixtral`  
- **Module Path:** `hxp_enterprise_llm.services.ai_models.mixtral.service`  
- **Configuration Schema:** `MixtralServiceConfig`  

### **Traceability**
- **Requirements Reference:** `PRD Section 3.3 - AI Model Hosting and Inference Requirements`  
- **User Story:** `As a system administrator, I want the Mixtral service to initialize correctly with valid configuration`  
- **Architecture Document Section:** `Section 3.1 - AI Model Service Component Design`  
- **High-Level Task Reference:** `Phase-1 Task 1.2 - Mixtral-8x7B Model Deployment and Configuration`  

---

## 🎯 **TEST OBJECTIVE**

### **Primary Objective**
Validate that the Mixtral-8x7B service initializes correctly with proper configuration validation, resource allocation, and service state management.

### **Success Criteria**
- **Functional:** Service initializes without errors and validates all configuration parameters
- **Performance:** Initialization completes within 30 seconds
- **Quality:** All configuration parameters are correctly applied and validated
- **Integration:** Service registers with monitoring and health check systems

### **Business Value**
Ensures reliable service startup and configuration management, preventing deployment failures and configuration-related issues in production environments.

---

## 📊 **TEST SPECIFICATIONS**

### **Test Environment**
- **Environment Type:** `Development`  
- **Infrastructure Requirements:**
  - **CPU:** `8 cores minimum`  
  - **Memory:** `90GB minimum`  
  - **Storage:** `10GB minimum`  
  - **Network:** `1Gbps connectivity`  
- **Dependencies:**
  - **External Services:** `PostgreSQL (192.168.10.35:5432), Prometheus (192.168.10.37:9090)`  
  - **Test Data:** `Mixtral configuration test data`  
  - **Mock Services:** `Mock monitoring service`  

### **Test Data Requirements**
- **Input Data:** `Valid Mixtral service configuration with all required parameters`  
- **Expected Output:** `Service initialization success with proper state management`  
- **Test Fixtures:** `test_mixtral_config.yaml`  
- **Data Generation:** `Configuration generator with validation rules`  

### **Performance Targets**
- **Latency Target:** `30 seconds maximum initialization time`  
- **Throughput Target:** `N/A (initialization test)`  
- **Resource Utilization:** `90GB memory limit, 8 CPU cores limit`  
- **Concurrent Users:** `N/A (initialization test)`  

---

## 🔧 **TEST IMPLEMENTATION**

### **Pre-conditions**
1. System has sufficient resources (CPU, memory, storage)
2. PostgreSQL database is accessible and configured
3. Prometheus monitoring service is running
4. Mixtral model files are available in the specified path
5. Python environment is properly configured with required dependencies

### **Test Setup**
```python
import pytest
import asyncio
import yaml
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from hxp_enterprise_llm.services.ai_models.mixtral.service import MixtralService
from hxp_enterprise_llm.schemas.configuration.service_schemas import MixtralServiceConfig
from hxp_enterprise_llm.testing.utilities.test_environment_manager import TestEnvironmentManager
from hxp_enterprise_llm.testing.utilities.test_data_generator import TestDataGenerator

class TestMixtralServiceInitialization:
    """Test class for Mixtral service initialization testing."""
    
    @pytest.fixture(scope="class")
    async def test_environment(self):
        """Setup test environment."""
        env_manager = TestEnvironmentManager()
        await env_manager.setup_environment()
        yield env_manager
        await env_manager.teardown_environment()
    
    @pytest.fixture
    def valid_config(self):
        """Generate valid Mixtral configuration."""
        return MixtralServiceConfig(
            port=11400,
            memory_limit_gb=90,
            cpu_cores=8,
            target_latency_ms=2000,
            target_throughput_rps=50,
            model_path="/opt/models/mixtral-8x7b",
            max_concurrent_requests=10,
            max_tokens=4096,
            temperature=0.7,
            database_url="postgresql://user:pass@192.168.10.35:5432/hana_x_llm",
            monitoring_url="http://192.168.10.37:9090"
        )
    
    @pytest.fixture
    async def mixtral_service(self, valid_config):
        """Fixture for Mixtral service with test configuration."""
        service = MixtralService(valid_config)
        yield service
        await service.cleanup()
    
    @pytest.fixture
    def test_data(self):
        """Generate test data."""
        generator = TestDataGenerator()
        return generator.generate_configuration_data({
            "data_type": "mixtral_config",
            "count": 1,
            "parameters": {
                "port_range": [11400, 11499],
                "memory_range": [64, 128],
                "cpu_range": [4, 16]
            }
        })
```

### **Test Steps**
1. **Step 1:** Validate configuration parameters
   ```python
   async def test_configuration_validation(self, valid_config):
       """Test configuration parameter validation."""
       assert valid_config.port == 11400
       assert valid_config.memory_limit_gb == 90
       assert valid_config.cpu_cores == 8
       assert valid_config.target_latency_ms == 2000
       assert valid_config.target_throughput_rps == 50
       assert valid_config.model_path == "/opt/models/mixtral-8x7b"
   ```

2. **Step 2:** Initialize service with valid configuration
   ```python
   async def test_service_initialization(self, mixtral_service):
       """Test service initialization with valid configuration."""
       assert mixtral_service is not None
       assert mixtral_service.config is not None
       assert mixtral_service.is_initialized() is False
       
       # Initialize service
       await mixtral_service.initialize()
       
       # Verify initialization
       assert mixtral_service.is_initialized() is True
       assert mixtral_service.status == "initialized"
   ```

3. **Step 3:** Validate resource allocation
   ```python
   async def test_resource_allocation(self, mixtral_service):
       """Test resource allocation during initialization."""
       await mixtral_service.initialize()
       
       # Check memory allocation
       memory_usage = await mixtral_service.get_memory_usage()
       assert memory_usage <= 90 * 1024 * 1024 * 1024  # 90GB limit
       
       # Check CPU allocation
       cpu_usage = await mixtral_service.get_cpu_usage()
       assert cpu_usage <= 8  # 8 CPU cores limit
   ```

4. **Step 4:** Validate service state management
   ```python
   async def test_service_state_management(self, mixtral_service):
       """Test service state management during initialization."""
       # Check initial state
       assert mixtral_service.status == "uninitialized"
       
       # Initialize service
       await mixtral_service.initialize()
       assert mixtral_service.status == "initialized"
       
       # Check state transitions
       state_history = mixtral_service.get_state_history()
       assert "uninitialized" in state_history
       assert "initializing" in state_history
       assert "initialized" in state_history
   ```

5. **Step 5:** Validate monitoring integration
   ```python
   async def test_monitoring_integration(self, mixtral_service):
       """Test monitoring integration during initialization."""
       await mixtral_service.initialize()
       
       # Check monitoring registration
       monitoring_status = await mixtral_service.get_monitoring_status()
       assert monitoring_status.registered is True
       assert monitoring_status.endpoint == "http://192.168.10.37:9090"
       
       # Check metrics collection
       metrics = await mixtral_service.get_metrics()
       assert "initialization_time" in metrics
       assert "memory_usage" in metrics
       assert "cpu_usage" in metrics
   ```

### **Main Test Method**
```python
@pytest.mark.asyncio
@pytest.mark.component
async def test_mixtral_service_initialization(self, mixtral_service, test_data, test_environment):
    """
    Test Case: Mixtral Service Initialization
    Objective: Validate service initialization with proper configuration and resource allocation
    Level: Level 1 - Component Certification
    """
    
    # Test execution
    try:
        # Step 1: Configuration validation
        config_result = await self._validate_configuration(mixtral_service)
        assert config_result.valid is True, "Configuration validation failed"
        
        # Step 2: Service initialization
        init_result = await self._initialize_service(mixtral_service)
        assert init_result.success is True, "Service initialization failed"
        assert init_result.status == "initialized", f"Unexpected status: {init_result.status}"
        
        # Step 3: Resource allocation validation
        resource_result = await self._validate_resource_allocation(mixtral_service)
        assert resource_result.memory_ok is True, f"Memory allocation failed: {resource_result.memory_usage}GB"
        assert resource_result.cpu_ok is True, f"CPU allocation failed: {resource_result.cpu_usage} cores"
        
        # Step 4: State management validation
        state_result = await self._validate_state_management(mixtral_service)
        assert state_result.state_transitions_ok is True, "State transitions failed"
        
        # Step 5: Monitoring integration validation
        monitoring_result = await self._validate_monitoring_integration(mixtral_service)
        assert monitoring_result.registered is True, "Monitoring registration failed"
        assert monitoring_result.metrics_collected is True, "Metrics collection failed"
        
        # Performance validation
        if hasattr(init_result, 'initialization_time'):
            assert init_result.initialization_time < 30000, f"Initialization time exceeded: {init_result.initialization_time}ms"
        
        # Quality validation
        if hasattr(init_result, 'quality_score'):
            assert init_result.quality_score >= 0.95, f"Quality threshold not met: {init_result.quality_score}"
        
    except Exception as e:
        pytest.fail(f"Test execution failed: {str(e)}")
    
    finally:
        # Cleanup
        await self._cleanup_test_resources(mixtral_service)

async def _validate_configuration(self, service):
    """Validate service configuration."""
    config = service.config
    return {
        "valid": all([
            config.port == 11400,
            config.memory_limit_gb == 90,
            config.cpu_cores == 8,
            config.target_latency_ms == 2000,
            config.target_throughput_rps == 50
        ])
    }

async def _initialize_service(self, service):
    """Initialize the service."""
    start_time = time.time()
    await service.initialize()
    initialization_time = (time.time() - start_time) * 1000
    
    return {
        "success": service.is_initialized(),
        "status": service.status,
        "initialization_time": initialization_time
    }

async def _validate_resource_allocation(self, service):
    """Validate resource allocation."""
    memory_usage = await service.get_memory_usage()
    cpu_usage = await service.get_cpu_usage()
    
    return {
        "memory_ok": memory_usage <= 90 * 1024 * 1024 * 1024,
        "cpu_ok": cpu_usage <= 8,
        "memory_usage": memory_usage / (1024 * 1024 * 1024),
        "cpu_usage": cpu_usage
    }

async def _validate_state_management(self, service):
    """Validate state management."""
    state_history = service.get_state_history()
    expected_states = ["uninitialized", "initializing", "initialized"]
    
    return {
        "state_transitions_ok": all(state in state_history for state in expected_states)
    }

async def _validate_monitoring_integration(self, service):
    """Validate monitoring integration."""
    monitoring_status = await service.get_monitoring_status()
    metrics = await service.get_metrics()
    
    return {
        "registered": monitoring_status.registered,
        "metrics_collected": len(metrics) > 0
    }

async def _cleanup_test_resources(self, service):
    """Cleanup test resources."""
    if service.is_initialized():
        await service.cleanup()
```

---

## 📋 **EXPECTED RESULTS**

### **Pass Criteria**
- ✅ Service initializes successfully within 30 seconds
- ✅ All configuration parameters are correctly applied
- ✅ Resource allocation respects specified limits
- ✅ Service state transitions occur correctly
- ✅ Monitoring integration is established
- ✅ No critical errors or exceptions occur

### **Fail Criteria**
- ❌ Service initialization takes longer than 30 seconds
- ❌ Configuration validation fails
- ❌ Resource allocation exceeds specified limits
- ❌ Service state transitions are incorrect
- ❌ Monitoring integration fails
- ❌ Critical errors or exceptions occur

### **Test Data**
```yaml
# test_mixtral_config.yaml
service:
  name: "mixtral-8x7b"
  port: 11400
  memory_limit_gb: 90
  cpu_cores: 8
  target_latency_ms: 2000
  target_throughput_rps: 50
  model_path: "/opt/models/mixtral-8x7b"
  max_concurrent_requests: 10
  max_tokens: 4096
  temperature: 0.7

database:
  url: "postgresql://user:pass@192.168.10.35:5432/hana_x_llm"
  pool_size: 10
  max_overflow: 20

monitoring:
  url: "http://192.168.10.37:9090"
  metrics_interval: 30
  health_check_interval: 60
```

---

## 🔍 **VALIDATION CHECKLIST**

- [ ] Configuration parameters are correctly validated
- [ ] Service initializes without errors
- [ ] Resource allocation is within specified limits
- [ ] Service state transitions occur correctly
- [ ] Monitoring integration is established
- [ ] Performance targets are met
- [ ] Error handling works correctly
- [ ] Cleanup procedures execute properly

---

**Test Case Status:** Ready for Implementation  
**Created:** 2025-01-18  
**Last Updated:** 2025-01-18  
**Next Review:** After implementation 