# Complete Monitoring Stack Validation Suite
# Validates: Prometheus, Grafana, Alertmanager, Dashboards, and Alert Rules

#!/bin/bash

# Configuration
METRICS_SERVER="192.168.10.37"
HX_SERVER_02="192.168.10.28"
PROMETHEUS_PORT="9090"
GRAFANA_PORT="3000"
ALERTMANAGER_PORT="9093"
GATEWAY_PORT="8001"
DEPLOYMENT_DIR="/opt/citadel-02"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
LOG_FILE="${DEPLOYMENT_DIR}/logs/validation-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "${DEPLOYMENT_DIR}/logs"

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

test_connection() {
    local host=$1
    local port=$2
    local service=$3
    
    log "${BLUE}Testing connection to $service ($host:$port)...${NC}"
    
    if timeout 10 nc -z "$host" "$port" 2>/dev/null; then
        log "${GREEN}✓ $service is accessible${NC}"
        return 0
    else
        log "${RED}✗ $service is not accessible${NC}"
        return 1
    fi
}

test_http_endpoint() {
    local url=$1
    local service=$2
    local expected_pattern=$3
    
    log "${BLUE}Testing HTTP endpoint: $service${NC}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$url" 2>/dev/null)
    
    if [[ "$response" == "200" ]]; then
        log "${GREEN}✓ $service HTTP endpoint responding (200)${NC}"
        
        if [[ -n "$expected_pattern" ]]; then
            content=$(curl -s --connect-timeout 10 "$url" 2>/dev/null)
            if echo "$content" | grep -q "$expected_pattern"; then
                log "${GREEN}✓ $service content validation passed${NC}"
                return 0
            else
                log "${YELLOW}⚠ $service responding but content validation failed${NC}"
                return 1
            fi
        fi
        return 0
    else
        log "${RED}✗ $service HTTP endpoint failed (status: $response)${NC}"
        return 1
    fi
}

test_prometheus() {
    log "\n${BLUE}=== PROMETHEUS VALIDATION ===${NC}"
    
    # Test connection
    test_connection "$METRICS_SERVER" "$PROMETHEUS_PORT" "Prometheus"
    
    # Test HTTP endpoint
    test_http_endpoint "http://$METRICS_SERVER:$PROMETHEUS_PORT" "Prometheus Web UI" "Prometheus"
    
    # Test API endpoint
    test_http_endpoint "http://$METRICS_SERVER:$PROMETHEUS_PORT/api/v1/status/config" "Prometheus API" "yaml"
    
    # Test targets endpoint
    log "${BLUE}Testing Prometheus targets...${NC}"
    targets_response=$(curl -s "http://$METRICS_SERVER:$PROMETHEUS_PORT/api/v1/targets" 2>/dev/null)
    
    if echo "$targets_response" | jq -e '.data.activeTargets[] | select(.labels.instance=="'$HX_SERVER_02':8001")' >/dev/null 2>&1; then
        log "${GREEN}✓ HX-Server-02 target discovered${NC}"
    else
        log "${RED}✗ HX-Server-02 target not found${NC}"
    fi
    
    # Test metrics
    log "${BLUE}Testing key metrics availability...${NC}"
    metrics_to_test=("up" "citadel_requests_total" "citadel_response_time_seconds" "citadel_active_connections")
    
    for metric in "${metrics_to_test[@]}"; do
        metric_response=$(curl -s "http://$METRICS_SERVER:$PROMETHEUS_PORT/api/v1/query?query=$metric" 2>/dev/null)
        if echo "$metric_response" | jq -e '.data.result[0]' >/dev/null 2>&1; then
            log "${GREEN}✓ Metric '$metric' available${NC}"
        else
            log "${YELLOW}⚠ Metric '$metric' not found${NC}"
        fi
    done
}

test_grafana() {
    log "\n${BLUE}=== GRAFANA VALIDATION ===${NC}"
    
    # Test connection
    test_connection "$METRICS_SERVER" "$GRAFANA_PORT" "Grafana"
    
    # Test HTTP endpoint
    test_http_endpoint "http://$METRICS_SERVER:$GRAFANA_PORT" "Grafana Web UI" "Grafana"
    
    # Test API endpoint
    test_http_endpoint "http://$METRICS_SERVER:$GRAFANA_PORT/api/health" "Grafana API" "ok"
    
    # Test datasources
    log "${BLUE}Testing Grafana datasources...${NC}"
    datasources_response=$(curl -s -u admin:admin "http://$METRICS_SERVER:$GRAFANA_PORT/api/datasources" 2>/dev/null)
    
    if echo "$datasources_response" | jq -e '.[] | select(.type=="prometheus")' >/dev/null 2>&1; then
        log "${GREEN}✓ Prometheus datasource configured${NC}"
    else
        log "${RED}✗ Prometheus datasource not found${NC}"
    fi
    
    # Test dashboards
    log "${BLUE}Testing Grafana dashboards...${NC}"
    dashboards_response=$(curl -s -u admin:admin "http://$METRICS_SERVER:$GRAFANA_PORT/api/search?type=dash-db" 2>/dev/null)
    
    expected_dashboards=("LLM Performance Analytics" "Database Resource Monitoring")
    
    for dashboard in "${expected_dashboards[@]}"; do
        if echo "$dashboards_response" | jq -e '.[] | select(.title=="'$dashboard'")' >/dev/null 2>&1; then
            log "${GREEN}✓ Dashboard '$dashboard' found${NC}"
        else
            log "${YELLOW}⚠ Dashboard '$dashboard' not found${NC}"
        fi
    done
}

test_alertmanager() {
    log "\n${BLUE}=== ALERTMANAGER VALIDATION ===${NC}"
    
    # Test connection
    test_connection "$METRICS_SERVER" "$ALERTMANAGER_PORT" "Alertmanager"
    
    # Test HTTP endpoint
    test_http_endpoint "http://$METRICS_SERVER:$ALERTMANAGER_PORT" "Alertmanager Web UI" "Alertmanager"
    
    # Test API endpoint
    test_http_endpoint "http://$METRICS_SERVER:$ALERTMANAGER_PORT/api/v1/status" "Alertmanager API" "ready"
    
    # Test configuration
    log "${BLUE}Testing Alertmanager configuration...${NC}"
    config_response=$(curl -s "http://$METRICS_SERVER:$ALERTMANAGER_PORT/api/v1/status" 2>/dev/null)
    
    if echo "$config_response" | jq -e '.data.configYAML' >/dev/null 2>&1; then
        log "${GREEN}✓ Alertmanager configuration loaded${NC}"
    else
        log "${RED}✗ Alertmanager configuration not found${NC}"
    fi
}

test_hx_server_02() {
    log "\n${BLUE}=== HX-SERVER-02 VALIDATION ===${NC}"
    
    # Test gateway connection
    test_connection "$HX_SERVER_02" "$GATEWAY_PORT" "Citadel Gateway"
    
    # Test health endpoint
    test_http_endpoint "http://$HX_SERVER_02:$GATEWAY_PORT/health" "Gateway Health" "healthy"
    
    # Test metrics endpoint
    test_http_endpoint "http://$HX_SERVER_02:$GATEWAY_PORT/metrics" "Gateway Metrics" "citadel_"
    
    # Test service status
    log "${BLUE}Testing citadel-gateway service status...${NC}"
    if ssh -o ConnectTimeout=10 root@$HX_SERVER_02 "systemctl is-active citadel-gateway" >/dev/null 2>&1; then
        log "${GREEN}✓ citadel-gateway service is active${NC}"
    else
        log "${RED}✗ citadel-gateway service is not active${NC}"
    fi
    
    # Test auto-recovery configuration
    log "${BLUE}Testing auto-recovery configuration...${NC}"
    restart_config=$(ssh -o ConnectTimeout=10 root@$HX_SERVER_02 "systemctl show citadel-gateway | grep Restart=" 2>/dev/null)
    
    if echo "$restart_config" | grep -q "Restart=always"; then
        log "${GREEN}✓ Auto-recovery enabled (Restart=always)${NC}"
    else
        log "${RED}✗ Auto-recovery not properly configured${NC}"
    fi
}

test_alert_rules() {
    log "\n${BLUE}=== ALERT RULES VALIDATION ===${NC}"
    
    # Test alert rules endpoint
    rules_response=$(curl -s "http://$METRICS_SERVER:$PROMETHEUS_PORT/api/v1/rules" 2>/dev/null)
    
    if echo "$rules_response" | jq -e '.data.groups[0]' >/dev/null 2>&1; then
        log "${GREEN}✓ Alert rules loaded${NC}"
        
        # Count rules
        rule_count=$(echo "$rules_response" | jq '.data.groups | map(.rules | length) | add' 2>/dev/null)
        log "${GREEN}✓ Total alert rules: $rule_count${NC}"
        
        # Test specific rules
        critical_rules=("CitadelGatewayDown" "HighErrorRate" "DatabaseConnectionFailed")
        
        for rule in "${critical_rules[@]}"; do
            if echo "$rules_response" | jq -e '.data.groups[].rules[] | select(.name=="'$rule'")' >/dev/null 2>&1; then
                log "${GREEN}✓ Alert rule '$rule' found${NC}"
            else
                log "${YELLOW}⚠ Alert rule '$rule' not found${NC}"
            fi
        done
    else
        log "${RED}✗ No alert rules found${NC}"
    fi
}

test_integration() {
    log "\n${BLUE}=== INTEGRATION TESTING ===${NC}"
    
    # Test end-to-end monitoring flow
    log "${BLUE}Testing end-to-end monitoring flow...${NC}"
    
    # 1. Generate test metric
    test_metric_value=$(date +%s)
    test_response=$(curl -s -X POST "http://$HX_SERVER_02:$GATEWAY_PORT/test/metric" \
        -H "Content-Type: application/json" \
        -d "{\"value\": $test_metric_value}" 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        log "${GREEN}✓ Test metric generated${NC}"
        
        # 2. Wait and check if metric appears in Prometheus
        sleep 30
        
        prometheus_query="citadel_test_metric"
        metric_response=$(curl -s "http://$METRICS_SERVER:$PROMETHEUS_PORT/api/v1/query?query=$prometheus_query" 2>/dev/null)
        
        if echo "$metric_response" | jq -e '.data.result[0]' >/dev/null 2>&1; then
            log "${GREEN}✓ Test metric visible in Prometheus${NC}"
        else
            log "${YELLOW}⚠ Test metric not yet visible in Prometheus${NC}"
        fi
    else
        log "${YELLOW}⚠ Test metric generation skipped (endpoint not available)${NC}"
    fi
    
    # Test webhook delivery
    log "${BLUE}Testing webhook delivery...${NC}"
    webhook_response=$(curl -s -X POST "http://$HX_SERVER_02:$GATEWAY_PORT/webhooks/alerts/test" \
        -H "Content-Type: application/json" \
        -d '{"test": "alert"}' 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        log "${GREEN}✓ Webhook endpoint accessible${NC}"
    else
        log "${YELLOW}⚠ Webhook endpoint test skipped${NC}"
    fi
}

generate_report() {
    log "\n${BLUE}=== VALIDATION REPORT ===${NC}"
    
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    local warning_tests=0
    
    # Count results from log
    total_tests=$(grep -c "Testing\|✓\|✗\|⚠" "$LOG_FILE" | head -1)
    passed_tests=$(grep -c "✓" "$LOG_FILE")
    failed_tests=$(grep -c "✗" "$LOG_FILE")
    warning_tests=$(grep -c "⚠" "$LOG_FILE")
    
    log "\n${BLUE}SUMMARY:${NC}"
    log "${GREEN}✓ Passed: $passed_tests${NC}"
    log "${RED}✗ Failed: $failed_tests${NC}"
    log "${YELLOW}⚠ Warnings: $warning_tests${NC}"
    
    # Calculate success rate
    if [[ $total_tests -gt 0 ]]; then
        success_rate=$(( (passed_tests * 100) / (passed_tests + failed_tests) ))
        log "\n${BLUE}Success Rate: $success_rate%${NC}"
        
        if [[ $success_rate -gt 90 ]]; then
            log "${GREEN}🎉 Monitoring stack validation: EXCELLENT${NC}"
        elif [[ $success_rate -gt 80 ]]; then
            log "${YELLOW}👍 Monitoring stack validation: GOOD${NC}"
        elif [[ $success_rate -gt 60 ]]; then
            log "${YELLOW}⚠ Monitoring stack validation: FAIR${NC}"
        else
            log "${RED}❌ Monitoring stack validation: NEEDS ATTENTION${NC}"
        fi
    fi
    
    log "\n${BLUE}Full log available at: $LOG_FILE${NC}"
    
    # Generate recommendations
    if [[ $failed_tests -gt 0 ]]; then
        log "\n${YELLOW}RECOMMENDATIONS:${NC}"
        
        if grep -q "Prometheus.*not accessible" "$LOG_FILE"; then
            log "• Check Prometheus service on metrics server"
            log "• Verify firewall rules for port $PROMETHEUS_PORT"
        fi
        
        if grep -q "Grafana.*not accessible" "$LOG_FILE"; then
            log "• Check Grafana service on metrics server"
            log "• Verify firewall rules for port $GRAFANA_PORT"
        fi
        
        if grep -q "citadel-gateway.*not active" "$LOG_FILE"; then
            log "• Restart citadel-gateway service: systemctl restart citadel-gateway"
            log "• Check service logs: journalctl -u citadel-gateway -f"
        fi
        
        if grep -q "HX-Server-02 target not found" "$LOG_FILE"; then
            log "• Check Prometheus configuration for HX-Server-02 target"
            log "• Verify service discovery or static configuration"
        fi
    fi
}

main() {
    log "${BLUE}================================================${NC}"
    log "${BLUE}    CITADEL MONITORING STACK VALIDATION        ${NC}"
    log "${BLUE}================================================${NC}"
    log "${BLUE}Started: $(date)${NC}"
    log "${BLUE}Log file: $LOG_FILE${NC}"
    log "${BLUE}================================================${NC}"
    
    # Run all validation tests
    test_prometheus
    test_grafana
    test_alertmanager
    test_hx_server_02
    test_alert_rules
    test_integration
    
    # Generate final report
    generate_report
    
    log "\n${BLUE}Validation completed: $(date)${NC}"
}

# Check dependencies
if ! command -v curl >/dev/null 2>&1; then
    log "${RED}Error: curl is required but not installed${NC}"
    exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
    log "${RED}Error: jq is required but not installed${NC}"
    exit 1
fi

if ! command -v nc >/dev/null 2>&1; then
    log "${RED}Error: netcat (nc) is required but not installed${NC}"
    exit 1
fi

# Run main function
main "$@"
