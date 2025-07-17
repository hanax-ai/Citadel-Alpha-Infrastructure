#!/bin/bash

# Cross-Server Communication Validation Script
# For Vector Database Server Infrastructure Integration
# Tests communication between all servers in the distributed deployment

echo "=== CITADEL ALPHA INFRASTRUCTURE - CROSS-SERVER COMMUNICATION TEST ==="
echo "Testing communication between servers for distributed WebUI deployment"
echo "Date: $(date)"
echo ""

# Server Configuration
VECTOR_DB_SERVER="192.168.10.30"
DATABASE_SERVER="192.168.10.35"
METRIC_SERVER="192.168.10.37"

# Port Configuration
QDRANT_REST_PORT="6333"
QDRANT_GRPC_PORT="6334"
API_GATEWAY_PORT="8000"
GRAPHQL_PORT="8081"
WEBUI_PORT="8080"
POSTGRESQL_PORT="5432"
REDIS_PORT="6379"
PROMETHEUS_PORT="9090"
GRAFANA_PORT="3000"

echo "=== 1. NETWORK CONNECTIVITY TESTS ==="

# Test basic network connectivity
echo "Testing network connectivity..."
servers=("$VECTOR_DB_SERVER" "$DATABASE_SERVER" "$METRIC_SERVER")
for server in "${servers[@]}"; do
    echo -n "Ping $server: "
    if ping -c 3 -W 3 "$server" > /dev/null 2>&1; then
        echo "✅ SUCCESS"
    else
        echo "❌ FAILED"
    fi
done

echo ""
echo "=== 2. VECTOR DATABASE SERVER TESTS (192.168.10.30) ==="

# Test Qdrant services
echo "Testing Qdrant REST API..."
if curl -s -f "http://$VECTOR_DB_SERVER:$QDRANT_REST_PORT/collections" > /dev/null; then
    echo "✅ Qdrant REST API ($VECTOR_DB_SERVER:$QDRANT_REST_PORT) - ACCESSIBLE"
else
    echo "❌ Qdrant REST API ($VECTOR_DB_SERVER:$QDRANT_REST_PORT) - FAILED"
fi

echo "Testing Qdrant gRPC service..."
if timeout 5 bash -c "</dev/tcp/$VECTOR_DB_SERVER/$QDRANT_GRPC_PORT" 2>/dev/null; then
    echo "✅ Qdrant gRPC ($VECTOR_DB_SERVER:$QDRANT_GRPC_PORT) - ACCESSIBLE"
else
    echo "❌ Qdrant gRPC ($VECTOR_DB_SERVER:$QDRANT_GRPC_PORT) - FAILED"
fi

echo "Testing API Gateway..."
if curl -s -f "http://$VECTOR_DB_SERVER:$API_GATEWAY_PORT/health" > /dev/null; then
    echo "✅ API Gateway ($VECTOR_DB_SERVER:$API_GATEWAY_PORT) - ACCESSIBLE"
else
    echo "❌ API Gateway ($VECTOR_DB_SERVER:$API_GATEWAY_PORT) - FAILED"
fi

echo "Testing GraphQL endpoint..."
if curl -s -f "http://$VECTOR_DB_SERVER:$GRAPHQL_PORT/graphql" > /dev/null; then
    echo "✅ GraphQL API ($VECTOR_DB_SERVER:$GRAPHQL_PORT) - ACCESSIBLE"
else
    echo "❌ GraphQL API ($VECTOR_DB_SERVER:$GRAPHQL_PORT) - FAILED"
fi

echo ""
echo "=== 3. DATABASE SERVER TESTS (192.168.10.35) ==="

# Test PostgreSQL
echo "Testing PostgreSQL connectivity..."
if timeout 5 bash -c "</dev/tcp/$DATABASE_SERVER/$POSTGRESQL_PORT" 2>/dev/null; then
    echo "✅ PostgreSQL ($DATABASE_SERVER:$POSTGRESQL_PORT) - ACCESSIBLE"
else
    echo "❌ PostgreSQL ($DATABASE_SERVER:$POSTGRESQL_PORT) - FAILED"
fi

# Test Redis
echo "Testing Redis connectivity..."
if timeout 5 bash -c "</dev/tcp/$DATABASE_SERVER/$REDIS_PORT" 2>/dev/null; then
    echo "✅ Redis ($DATABASE_SERVER:$REDIS_PORT) - ACCESSIBLE"
else
    echo "❌ Redis ($DATABASE_SERVER:$REDIS_PORT) - FAILED"
fi

echo ""
echo "=== 4. METRIC SERVER TESTS (192.168.10.37) ==="

# Test WebUI deployment target
echo "Testing WebUI deployment endpoint..."
if curl -s -f "http://$METRIC_SERVER:$WEBUI_PORT/" > /dev/null; then
    echo "✅ WebUI Endpoint ($METRIC_SERVER:$WEBUI_PORT) - ACCESSIBLE"
else
    echo "❌ WebUI Endpoint ($METRIC_SERVER:$WEBUI_PORT) - FAILED (Expected for new deployment)"
fi

# Test Prometheus
echo "Testing Prometheus..."
if curl -s -f "http://$METRIC_SERVER:$PROMETHEUS_PORT/api/v1/status/config" > /dev/null; then
    echo "✅ Prometheus ($METRIC_SERVER:$PROMETHEUS_PORT) - ACCESSIBLE"
else
    echo "❌ Prometheus ($METRIC_SERVER:$PROMETHEUS_PORT) - FAILED"
fi

# Test Grafana
echo "Testing Grafana..."
if curl -s -f "http://$METRIC_SERVER:$GRAFANA_PORT/api/health" > /dev/null; then
    echo "✅ Grafana ($METRIC_SERVER:$GRAFANA_PORT) - ACCESSIBLE"
else
    echo "❌ Grafana ($METRIC_SERVER:$GRAFANA_PORT) - FAILED"
fi

echo ""
echo "=== 5. CROSS-SERVER API INTEGRATION TESTS ==="

# Test API calls from Metric Server to Vector Database Server
echo "Testing cross-server API calls (Metric Server → Vector Database Server)..."

# Test REST API cross-server call
echo -n "REST API cross-server call: "
if curl -s -f "http://$VECTOR_DB_SERVER:$API_GATEWAY_PORT/api/v1/collections" > /dev/null; then
    echo "✅ SUCCESS"
else
    echo "❌ FAILED"
fi

# Test GraphQL cross-server call
echo -n "GraphQL cross-server call: "
if curl -s -f -X POST "http://$VECTOR_DB_SERVER:$GRAPHQL_PORT/graphql" \
    -H "Content-Type: application/json" \
    -d '{"query":"query { __schema { types { name } } }"}' > /dev/null; then
    echo "✅ SUCCESS"
else
    echo "❌ FAILED"
fi

echo ""
echo "=== 6. CORS CONFIGURATION TESTS ==="

# Test CORS headers for cross-origin requests
echo "Testing CORS configuration for WebUI cross-origin requests..."

cors_test_result=$(curl -s -I -H "Origin: http://$METRIC_SERVER:$WEBUI_PORT" \
    -H "Access-Control-Request-Method: GET" \
    -H "Access-Control-Request-Headers: X-Requested-With" \
    -X OPTIONS "http://$VECTOR_DB_SERVER:$API_GATEWAY_PORT/api/v1/collections" 2>/dev/null)

if echo "$cors_test_result" | grep -q "Access-Control-Allow-Origin"; then
    echo "✅ CORS Headers Present"
else
    echo "❌ CORS Headers Missing (Configuration Required)"
fi

echo ""
echo "=== 7. SHARED LIBRARY INTEGRATION TESTS ==="

# Test shared library availability
echo "Testing HANA-X Vector Database Shared Library..."

if [ -d "/home/agent0/Citadel-Alpha-Infrastructure/0.1-Project-Execution/0.1.2-HXP-Shared-Library" ]; then
    echo "✅ Shared Library Directory Present"
    
    # Test key shared library components
    shared_lib_components=(
        "hana_x_vector/__init__.py"
        "hana_x_vector/gateway/__init__.py"
        "hana_x_vector/vector_ops/__init__.py"
        "hana_x_vector/qdrant/__init__.py"
        "hana_x_vector/monitoring/__init__.py"
        "hana_x_vector/utils/__init__.py"
        "hana_x_vector/schemas/__init__.py"
        "requirements.txt"
        "README.md"
    )
    
    for component in "${shared_lib_components[@]}"; do
        if [ -f "/home/agent0/Citadel-Alpha-Infrastructure/0.1-Project-Execution/0.1.2-HXP-Shared-Library/$component" ]; then
            echo "✅ $component - Present"
        else
            echo "❌ $component - Missing"
        fi
    done
else
    echo "❌ Shared Library Directory Missing"
fi

echo ""
echo "=== 8. LATENCY AND PERFORMANCE TESTS ==="

# Test cross-server latency
echo "Testing cross-server communication latency..."

# Vector Database Server latency
echo -n "Vector DB Server latency: "
latency=$(curl -w "%{time_total}" -s -o /dev/null "http://$VECTOR_DB_SERVER:$API_GATEWAY_PORT/health" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "${latency}s"
else
    echo "❌ FAILED"
fi

# Database Server latency (Redis ping)
echo -n "Database Server latency: "
if command -v redis-cli > /dev/null; then
    redis_latency=$(timeout 5 redis-cli -h "$DATABASE_SERVER" -p "$REDIS_PORT" ping 2>/dev/null)
    if [ "$redis_latency" = "PONG" ]; then
        echo "✅ Redis responding"
    else
        echo "❌ Redis not responding"
    fi
else
    echo "⚠️  redis-cli not available"
fi

echo ""
echo "=== 9. INFRASTRUCTURE READINESS SUMMARY ==="

echo "Infrastructure Component Status:"
echo "• Vector Database Server (192.168.10.30): Target for Qdrant and API Gateway"
echo "• Database Server (192.168.10.35): PostgreSQL and Redis operational"
echo "• Metric Server (192.168.10.37): Target for WebUI deployment"
echo ""
echo "Required Configurations:"
echo "• CORS configuration on Vector Database Server for WebUI access"
echo "• WebUI deployment on Metric Server with cross-server API endpoints"
echo "• Shared library integration across all Vector Database Server components"
echo ""
echo "Next Steps:"
echo "1. Deploy WebUI on Metric Server (192.168.10.37:8080)"
echo "2. Configure CORS on Vector Database Server for cross-origin requests"
echo "3. Update all task files to reference shared library imports"
echo "4. Test end-to-end functionality with distributed deployment"

echo ""
echo "=== CROSS-SERVER COMMUNICATION TEST COMPLETED ==="
echo "Date: $(date)"
