#!/bin/bash

echo "🧪 Validating HX-Server-02 Monitoring Configuration"
echo "=================================================="

# Check configuration files
echo "📋 Checking configuration files..."

if [ -f "/opt/citadel-02/config/services/monitoring/prometheus.yaml" ]; then
    echo "✅ Prometheus configuration exists"
    # Validate YAML syntax
    if python3 -c "import yaml; yaml.safe_load(open('/opt/citadel-02/config/services/monitoring/prometheus.yaml'))" 2>/dev/null; then
        echo "✅ Prometheus YAML syntax is valid"
    else
        echo "❌ Prometheus YAML syntax error"
    fi
else
    echo "❌ Prometheus configuration missing"
fi

if [ -f "/opt/citadel-02/config/services/monitoring/grafana.yaml" ]; then
    echo "✅ Grafana configuration exists"
    if python3 -c "import yaml; yaml.safe_load(open('/opt/citadel-02/config/services/monitoring/grafana.yaml'))" 2>/dev/null; then
        echo "✅ Grafana YAML syntax is valid"
    else
        echo "❌ Grafana YAML syntax error"
    fi
else
    echo "❌ Grafana configuration missing"
fi

if [ -f "/opt/citadel-02/config/services/monitoring/alerting.yaml" ]; then
    echo "✅ Alerting configuration exists"
    if python3 -c "import yaml; yaml.safe_load(open('/opt/citadel-02/config/services/monitoring/alerting.yaml'))" 2>/dev/null; then
        echo "✅ Alerting YAML syntax is valid"
    else
        echo "❌ Alerting YAML syntax error"
    fi
else
    echo "❌ Alerting configuration missing"
fi

# Check dashboard directories
echo ""
echo "📁 Checking dashboard directories..."

if [ -d "/opt/citadel-02/frameworks/monitoring/dashboards" ]; then
    echo "✅ Main dashboards directory exists"
else
    echo "❌ Main dashboards directory missing"
fi

if [ -d "/opt/citadel-02/frameworks/monitoring/local-dashboards" ]; then
    echo "✅ Local dashboards directory exists"
    dashboard_count=$(find /opt/citadel-02/frameworks/monitoring/local-dashboards -name "*.json" | wc -l)
    echo "📊 Found ${dashboard_count} dashboard file(s)"
else
    echo "❌ Local dashboards directory missing"
fi

if [ -d "/opt/citadel-02/config/services/monitoring/rules" ]; then
    echo "✅ Alert rules directory exists"
else
    echo "❌ Alert rules directory missing"
fi

# Check service endpoints for metrics
echo ""
echo "🔍 Testing local metrics endpoints..."

echo "Testing Citadel Gateway metrics (localhost:8001/metrics)..."
if curl -s -f http://localhost:8001/metrics > /dev/null 2>&1; then
    echo "✅ Citadel Gateway metrics endpoint accessible"
else
    echo "⚠️  Citadel Gateway metrics endpoint not accessible (service may be down)"
fi

echo "Testing Ollama metrics (localhost:11434/metrics)..."
if curl -s -f http://localhost:11434/metrics > /dev/null 2>&1; then
    echo "✅ Ollama metrics endpoint accessible"
else
    echo "⚠️  Ollama metrics endpoint not accessible (service may be down)"
fi

echo "Testing Node Exporter (localhost:9100/metrics)..."
if curl -s -f http://localhost:9100/metrics > /dev/null 2>&1; then
    echo "✅ Node Exporter metrics endpoint accessible"
else
    echo "⚠️  Node Exporter not accessible (may need installation)"
fi

# Test central metrics server connectivity
echo ""
echo "🌐 Testing central metrics server connectivity..."

echo "Testing central Prometheus (192.168.10.37:9090)..."
if curl -s -f http://192.168.10.37:9090/api/v1/status/config > /dev/null 2>&1; then
    echo "✅ Central Prometheus accessible"
else
    echo "⚠️  Central Prometheus not accessible"
fi

echo "Testing central Grafana (192.168.10.37:3000)..."
if curl -s -f http://192.168.10.37:3000/api/health > /dev/null 2>&1; then
    echo "✅ Central Grafana accessible"
else
    echo "⚠️  Central Grafana not accessible"
fi

echo "Testing central Alertmanager (192.168.10.37:9093)..."
if curl -s -f http://192.168.10.37:9093/api/v1/status > /dev/null 2>&1; then
    echo "✅ Central Alertmanager accessible"
else
    echo "⚠️  Central Alertmanager not accessible"
fi

echo ""
echo "📖 Configuration Summary:"
echo "  • Prometheus config: /opt/citadel-02/config/services/monitoring/prometheus.yaml"
echo "  • Grafana config: /opt/citadel-02/config/services/monitoring/grafana.yaml"
echo "  • Alerting config: /opt/citadel-02/config/services/monitoring/alerting.yaml"
echo "  • Dashboards: /opt/citadel-02/frameworks/monitoring/dashboards/"
echo "  • Local dashboards: /opt/citadel-02/frameworks/monitoring/local-dashboards/"
echo ""
echo "🎯 Next Steps:"
echo "  1. Ensure Node Exporter is installed: sudo apt install prometheus-node-exporter"
echo "  2. Configure central metrics server to scrape HX-Server-02 endpoints"
echo "  3. Import dashboard JSON files to Grafana"
echo "  4. Test alert routing to central Alertmanager"
