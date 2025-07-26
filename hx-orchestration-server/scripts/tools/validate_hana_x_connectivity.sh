#!/bin/bash
# File: /scripts/tools/validate_hana_x_connectivity.sh
# Citadel AI Operating System - HANA-X Lab Connectivity Validation

echo "=== Citadel AI Operating System - HANA-X Lab Connectivity Test ==="
echo "Date: $(date)"
echo "Server: $(hostname) ($(hostname -I | awk '{print $1}'))"
echo

# Define HANA-X Lab Infrastructure
declare -A HANA_X_SERVERS=(
    ["llm-01"]="192.168.10.29:8080"
    ["llm-02"]="192.168.10.28:8080"
    ["vectordb"]="192.168.10.30:6333"
    ["orca"]="192.168.10.31:8000"
    ["sql-db"]="192.168.10.35:5432"
    ["dev"]="192.168.10.33:22"
    ["test"]="192.168.10.34:22"
    ["devops"]="192.168.10.36:22"
    ["metrics"]="192.168.10.37:9090"
    ["web"]="192.168.10.38:80"
)

echo "🔗 Testing connectivity to HANA-X Lab Infrastructure:"
echo

# Test Connectivity
success_count=0
total_count=${#HANA_X_SERVERS[@]}

for server in "${!HANA_X_SERVERS[@]}"; do
    address="${HANA_X_SERVERS[$server]}"
    host="${address%:*}"
    port="${address#*:}"
    
    printf "%-10s %-20s " "$server" "($address)"
    
    if timeout 5 bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
        echo "✅ Connection successful"
        ((success_count++))
    else
        echo "❌ Connection failed"
    fi
done

echo
echo "📊 Connectivity Summary:"
echo "  ✅ Successful: $success_count/$total_count"
echo "  ❌ Failed: $((total_count - success_count))/$total_count"

if [ $success_count -eq $total_count ]; then
    echo "🎯 All HANA-X Lab servers accessible - Enterprise Infrastructure ready!"
    echo
    echo "🏗️  HANA-X Lab Architecture Status:"
    echo "  • LLM Servers: hx-llm-server-01 (192.168.10.29) + hx-llm-server-02 (192.168.10.28)"
    echo "  • Vector Database: hx-vector-database-server (192.168.10.30)"
    echo "  • SQL Database: hx-sql-database-server (192.168.10.35)"
    echo "  • Development: hx-development-server (192.168.10.33)"
    echo "  • Testing: hx-test-server (192.168.10.34)"
    echo "  • DevOps: hx-devops-server (192.168.10.36)"
    echo "  • Metrics: hx-metric-server (192.168.10.37)"
    echo "  • Web: hx-web-server (192.168.10.38)"
    echo "  • Orchestration: hx-orchestration-server (192.168.10.31) [CURRENT]"
    echo
    echo "Next Steps:"
    echo "  • Proceed with FastAPI application setup (Task-02)"
    echo "  • Initialize business process automation modules"
    echo "  • Configure enterprise AI runtime environment"
    echo "  • Setup dual LLM server load balancing"
    exit 0
else
    echo "⚠️  Some HANA-X Lab servers are not accessible"
    echo "   Please verify network connectivity and server status"
    exit 1
fi
