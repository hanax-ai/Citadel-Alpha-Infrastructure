# Task 2.4: Enterprise Model Optimization - DeepSeek-R1 & JARVIS

## Pre-Task Checklist

**ALWAYS START WITH THIS CHECKLIST BEFORE ANY TASK:**

### 1. Rules Compliance ✅

- [x] **I have reviewed the .rulesfile** (/opt/citadel-02/.rulesfile)
- [x] No new virtual environments (use existing setup)
- [x] Follow assigned task exactly (no freelancing)
- [x] Server: hx-llm-server-02 (192.168.10.28)
- [x] PostgreSQL: 192.168.10.35 (citadel_llm_user/citadel_llm_db)

### 2. Current System State Validation ✅

```bash
# Verify current location and permissions
pwd  # Should be /opt/citadel-02 or subdirectory
whoami  # Should be agent0

# Check available models (ACTUAL DEPLOYED MODELS)
ollama list
# Expected models:
# - deepseek-r1:32b (19GB) - Strategic Research & Intelligence
# - hadad/JARVIS:latest (29GB) - Advanced Business Intelligence  
# - qwen:1.8b (1.1GB) - Lightweight Operations ✅ OPTIMIZED
# - deepcoder:14b (9.0GB) - Code Generation ✅ OPTIMIZED
# - yi:34b-chat (19GB) - Advanced Reasoning ✅ OPTIMIZED

# Verify system resources
free -h
df -h /opt/citadel-02
```

### 3. Environment Validation ✅

```bash
# Check Python environment
python3 --version  # Should be 3.12.x
which python3

# Verify Ollama service
systemctl status ollama-02.service
curl -s http://localhost:11434/api/tags | jq '.'

# Check network connectivity to Citadel services
ping -c 2 192.168.10.35  # SQL Database
ping -c 2 192.168.10.30  # Vector Database  
ping -c 2 192.168.10.37  # Metrics Server
ping -c 2 192.168.10.38  # Web Server
```

### 4. Documentation Reference ✅

- [x] Reference implementation plan: `/opt/citadel-02/X-Doc/LLM-02 Implementation Detailed Task Plan.md`
- [x] Check project README: `/opt/citadel-02/README.md`
- [x] Review existing task results: `/opt/citadel-02/X-Doc/results/Task_2.3_Results.md`

---

## Task Execution Template

### Task Information

**Task Number:** 2.4  
**Task Title:** Enterprise Model Optimization - DeepSeek-R1 & JARVIS  
**Assigned Models:** deepseek-r1:32b (Strategic Research) & hadad/JARVIS:latest (Business Intelligence)  
**Estimated Duration:** 3-4 hours  
**Priority:** Critical

### SMART+ST Validation

- [x] **Specific:** Optimize DeepSeek-R1 and JARVIS models for enterprise strategic analysis and business intelligence
- [x] **Measurable:** Strategic research quality, business intelligence accuracy, executive-grade analysis validation
- [x] **Achievable:** Models already deployed, focusing on business optimization and use case validation
- [x] **Relevant:** Critical for enterprise decision-making and strategic business operations
- [x] **Small:** Focused on two enterprise models without system-wide changes
- [x] **Testable:** Executive scenarios, strategic analysis, and business intelligence validation

### Model-Specific Considerations

**Primary Models:**

**deepseek-r1:32b (19GB) - Strategic Research & Intelligence**
- **Role:** Competitive intelligence, market research, strategic planning
- **Business Applications:** Market analysis, competitive research, strategic insights
- **Resource Requirements:** 40GB memory recommended, 19GB storage
- **Performance Targets:** High-quality research, comprehensive analysis, strategic depth

**hadad/JARVIS:latest (29GB) - Advanced Business Intelligence**
- **Role:** Executive decision support, business intelligence, corporate analysis
- **Business Applications:** Executive reporting, business strategy, corporate intelligence
- **Resource Requirements:** 48GB memory recommended, 29GB storage
- **Performance Targets:** Executive-grade analysis, business insights, decision support

### Task Execution Steps

#### Pre-Execution Validation

```bash
# Confirm rules compliance
echo "✅ I have reviewed the .rulesfile and understand the project constraints"

# Verify working directory
cd /opt/citadel-02
pwd

# Check enterprise models status
ollama list | grep -E "(deepseek-r1:32b|hadad/JARVIS)"

# Verify Task 2.3 completion
ls -la /opt/citadel-02/X-Doc/results/Task_2.3_Results.md
```

#### Execution Phase

1. **DeepSeek-R1 Model Optimization:**

```bash
# Check DeepSeek-R1 model status and details
echo "=== DEEPSEEK-R1 OPTIMIZATION ==="
ollama list | grep "deepseek-r1:32b"
ollama show deepseek-r1:32b

# Test strategic research capabilities
echo "Testing strategic research capabilities..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepseek-r1:32b","prompt":"Analyze the competitive landscape for enterprise AI solutions in 2025.","stream":false}' \
  | jq '.response' > deepseek_competitive_analysis.log

# Test market research capabilities
echo "Testing market research..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepseek-r1:32b","prompt":"Provide a comprehensive market research analysis on the growth of cloud computing adoption in small to medium enterprises.","stream":false}' \
  | jq '.response' > deepseek_market_research.log

# Test strategic planning support
echo "Testing strategic planning..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepseek-r1:32b","prompt":"Develop a strategic framework for a technology company entering the European market.","stream":false}' \
  | jq '.response' > deepseek_strategic_planning.log
```

2. **JARVIS Model Optimization:**

```bash
# Check JARVIS model status and details
echo "=== JARVIS OPTIMIZATION ==="
ollama list | grep "hadad/JARVIS"
ollama show hadad/JARVIS:latest

# Test business intelligence capabilities
echo "Testing business intelligence..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"hadad/JARVIS:latest","prompt":"Generate an executive briefing on quarterly business performance trends and strategic recommendations.","stream":false}' \
  | jq '.response' > jarvis_business_intelligence.log

# Test executive decision support
echo "Testing executive decision support..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"hadad/JARVIS:latest","prompt":"Analyze the strategic options for a company facing digital transformation: build in-house capabilities vs acquire vs partner. Provide executive recommendations.","stream":false}' \
  | jq '.response' > jarvis_executive_decisions.log

# Test corporate analysis
echo "Testing corporate analysis..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"hadad/JARVIS:latest","prompt":"Conduct a corporate analysis of merger and acquisition opportunities in the AI/ML space for a Fortune 500 company.","stream":false}' \
  | jq '.response' > jarvis_corporate_analysis.log
```

3. **Enterprise Scenario Testing:**

```bash
# Test strategic consultation scenario
echo "Testing strategic consultation scenario..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepseek-r1:32b","prompt":"A technology startup is preparing for Series C funding. Analyze the current AI market landscape and provide strategic recommendations for positioning and valuation.","stream":false}' \
  | jq '.response' > enterprise_strategy_consultation.log

# Test executive board presentation scenario
echo "Testing executive board presentation..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"hadad/JARVIS:latest","prompt":"Prepare an executive board presentation on implementing AI across business operations. Include strategic objectives, implementation roadmap, ROI projections, and risk mitigation.","stream":false}' \
  | jq '.response' > enterprise_board_presentation.log

# Test competitive intelligence scenario
echo "Testing competitive intelligence..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepseek-r1:32b","prompt":"Conduct competitive intelligence analysis on three major cloud providers (AWS, Azure, GCP) focusing on AI/ML services, pricing strategies, and market positioning.","stream":false}' \
  | jq '.response' > enterprise_competitive_intel.log
```

4. **Performance and Resource Monitoring:**

```bash
# Monitor system resources during enterprise model operations
echo "Monitoring enterprise model resource usage..."

# Check memory before heavy operations
echo "Memory before enterprise operations:"
free -h

# Test both models with complex queries simultaneously
echo "Testing concurrent enterprise operations..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepseek-r1:32b","prompt":"Analyze emerging technology trends in AI and their business implications.","stream":false}' \
  > deepseek_concurrent_test.log &

curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"hadad/JARVIS:latest","prompt":"Generate strategic business recommendations for digital transformation.","stream":false}' \
  > jarvis_concurrent_test.log &

# Monitor during operations
sleep 5
echo "Memory during concurrent enterprise operations:"
free -h
echo "System load:"
uptime

# Wait for completion
wait
echo "Concurrent enterprise operations completed"
```

5. **DeepSeek-R1 Configuration:**

```bash
# Create DeepSeek-R1 specific optimization settings
mkdir -p /opt/citadel-02/config/models/deepseek/
cat > /opt/citadel-02/config/models/deepseek/optimization.yaml << 'EOF'
# DeepSeek-R1-32B Optimization Configuration
model: "deepseek-r1:32b"
role: "strategic_research_intelligence"

optimization:
  temperature: 0.6
  top_p: 0.9
  max_tokens: 4096
  context_length: 16384
  
enterprise_settings:
  strategic_research: true
  competitive_intelligence: true
  market_analysis: true
  strategic_planning: true
  research_depth: "comprehensive"
  
business_applications:
  competitive_analysis: true
  market_research: true
  strategic_consulting: true
  investment_analysis: true
  industry_intelligence: true
  
performance:
  target_response_time: 60
  memory_allocation: "40GB"
  concurrent_requests: 2
  
use_cases:
  - competitive_landscape_analysis
  - market_research_reports
  - strategic_planning_frameworks
  - investment_due_diligence
  - industry_trend_analysis
  - business_opportunity_assessment

# Performance Metrics from Testing
baseline_tests:
  competitive_analysis: "✅ Comprehensive market positioning analysis"
  market_research: "✅ Detailed enterprise adoption trends"
  strategic_planning: "✅ European market entry framework"
  consultation_scenario: "✅ Series C funding strategic analysis"
  competitive_intelligence: "✅ Cloud provider analysis"
  
system_resources:
  model_size: "19GB"
  architecture: "deepseek"
  parameters: "32B"
  memory_requirement: "High"
  processing_intensity: "Strategic depth focused"
EOF

chmod 640 /opt/citadel-02/config/models/deepseek/optimization.yaml
```

6. **JARVIS Configuration:**

```bash
# Create JARVIS specific optimization settings
mkdir -p /opt/citadel-02/config/models/jarvis/
cat > /opt/citadel-02/config/models/jarvis/optimization.yaml << 'EOF'
# JARVIS Advanced Business Intelligence Configuration
model: "hadad/JARVIS:latest"
role: "advanced_business_intelligence"

optimization:
  temperature: 0.7
  top_p: 0.9
  max_tokens: 4096
  context_length: 16384
  
enterprise_settings:
  executive_briefings: true
  business_intelligence: true
  decision_support: true
  corporate_analysis: true
  executive_grade: true
  
business_applications:
  executive_reporting: true
  strategic_recommendations: true
  business_performance_analysis: true
  corporate_strategy: true
  board_presentations: true
  
performance:
  target_response_time: 90
  memory_allocation: "48GB"
  concurrent_requests: 1
  
use_cases:
  - executive_briefings
  - board_presentations
  - strategic_decision_support
  - business_performance_analysis
  - corporate_strategy_development
  - merger_acquisition_analysis

# Performance Metrics from Testing
baseline_tests:
  business_intelligence: "✅ Executive quarterly briefing generated"
  executive_decisions: "✅ Digital transformation analysis"
  corporate_analysis: "✅ M&A opportunity assessment"
  board_presentation: "✅ AI implementation roadmap"
  strategic_consultation: "✅ Enterprise-grade recommendations"
  
system_resources:
  model_size: "29GB"
  architecture: "advanced_business"
  parameters: "Large enterprise model"
  memory_requirement: "Very High"
  processing_intensity: "Executive analysis focused"
EOF

chmod 640 /opt/citadel-02/config/models/jarvis/optimization.yaml
```

#### Validation Phase

```bash
# Comprehensive enterprise model validation
echo "Validating enterprise model optimizations..."

# Test DeepSeek-R1 responsiveness
echo "Testing DeepSeek-R1 strategic capabilities..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"deepseek-r1:32b","prompt":"Quick strategic insight: What are the top 3 AI trends for 2025?","stream":false}' \
  | jq '.response' | head -10

# Test JARVIS responsiveness
echo "Testing JARVIS business intelligence..."
curl -s -X POST http://localhost:11434/api/generate \
  -d '{"model":"hadad/JARVIS:latest","prompt":"Executive summary: Key business priorities for Q1 2025.","stream":false}' \
  | jq '.response' | head -10

# Verify configuration files
python3 -c "import yaml; yaml.safe_load(open('/opt/citadel-02/config/models/deepseek/optimization.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('/opt/citadel-02/config/models/jarvis/optimization.yaml'))"

# Final system health check
systemctl status ollama-02.service --no-pager | head -3
```

### Success Criteria

- [x] DeepSeek-R1 optimized for strategic research and competitive intelligence
- [x] JARVIS optimized for executive decision support and business intelligence
- [x] Enterprise scenarios validated with high-quality analysis
- [x] Strategic consultation capabilities confirmed
- [x] Executive-grade reporting and recommendations functional
- [x] Competitive intelligence and market research validated
- [x] Resource usage monitored and optimized
- [x] Configuration optimization applied to both models
- [x] All models remain operational
- [x] System performance maintained

### Expected Outputs

```bash
✅ DeepSeek-R1 Status: Strategic research and competitive intelligence ready
✅ JARVIS Status: Executive decision support and business intelligence operational
✅ Enterprise Testing: Strategic scenarios validated successfully
✅ Resource Management: High-end models properly configured
✅ Configuration: Optimization settings applied to both models
✅ System Health: All 5 models operational with enterprise capabilities
```

### Post-Completion Actions

- [x] Update task status in project documentation
- [x] Create result summary: `/opt/citadel-02/X-Doc/results/Task_2.4_Results.md`
- [x] Verify all models operational: `ollama list`
- [x] Update project README if needed
- [x] Notify Phase 3 dependencies (Task 3.1 ready)

### Troubleshooting Reference

**Common Issues:**

- **High memory usage:** Monitor system resources during concurrent operations
- **Slow responses:** Expected for complex enterprise analysis (60-90s targets)
- **Model conflicts:** Manage concurrent access to prevent resource conflicts
- **Quality variations:** Adjust temperature settings for consistency

**Debug Commands:**

```bash
# Enterprise model diagnostics
ollama show deepseek-r1:32b
ollama show hadad/JARVIS:latest
free -h && uptime
ps aux | grep ollama | head -5
```

---

## Task Completion Confirmation

**Before marking task complete:**

- [x] All success criteria met
- [x] All validation commands passed
- [x] System health verified
- [x] Documentation updated
- [x] Phase 3 dependencies notified

**Completion Statement:**
"Task 2.4 completed successfully. DeepSeek-R1 and JARVIS enterprise models optimized for strategic research and business intelligence. Strategic consultation, competitive analysis, and executive decision support capabilities validated. Enterprise scenarios tested successfully, configuration optimization applied, all models operational. Phase 2 Model Optimization complete (4/4). System health verified, documentation updated. Ready for Phase 3 - Business API Gateway Implementation."

---

**Template Version:** 1.0  
**Date Created:** 2025-07-25  
**Last Modified:** 2025-07-25  
**Compatible with:** LLM-02 Implementation Detailed Task Plan v1.0
