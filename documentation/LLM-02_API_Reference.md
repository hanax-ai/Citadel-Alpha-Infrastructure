# LLM-02 API Reference Guide

## Overview

The LLM-02 API provides access to 5 specialized AI models through a unified REST interface. This guide covers all business intelligence endpoints, authentication, and integration patterns.

## Base Configuration

### Endpoint Base URL
```
http://192.168.10.28:8000/api/v2/
```

### Authentication
All requests require API key authentication:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     http://192.168.10.28:8000/api/v2/endpoint
```

## Core Business Intelligence Endpoints

### Strategic Analysis API

**Endpoint:** `/strategic-analysis`
**Model:** Yi-34B (Strategic Analysis Specialist)
**Purpose:** Executive-level strategic planning and market analysis

#### Request Format
```json
{
  "query": "Analyze our competitive position in the cloud services market",
  "context": {
    "industry": "Technology",
    "timeframe": "Q4 2024",
    "focus_areas": ["market_share", "competitive_advantage", "growth_opportunities"]
  },
  "response_format": "executive_summary",
  "max_length": 2000
}
```

#### Response Format
```json
{
  "status": "success",
  "model": "yi:34b",
  "response_time": 3.2,
  "analysis": {
    "executive_summary": "Comprehensive strategic analysis...",
    "key_insights": [
      "Market position analysis",
      "Competitive advantages",
      "Strategic recommendations"
    ],
    "confidence_score": 0.89,
    "data_sources": ["market_research", "competitive_intelligence"]
  },
  "timestamp": "2024-12-28T10:30:00Z"
}
```

#### Example Usage
```bash
curl -X POST http://192.168.10.28:8000/api/v2/strategic-analysis \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Evaluate market entry strategy for European expansion",
    "context": {
      "industry": "SaaS",
      "target_markets": ["Germany", "France", "UK"],
      "budget_range": "$5M-$10M"
    },
    "response_format": "detailed_analysis"
  }'
```

### Code Generation API

**Endpoint:** `/code-generation`
**Model:** DeepCoder-14B (Business Automation Specialist)
**Purpose:** Generate business automation code and technical solutions

#### Request Format
```json
{
  "query": "Create a REST API for customer data management",
  "requirements": {
    "language": "Python",
    "framework": "FastAPI",
    "database": "PostgreSQL",
    "features": ["CRUD operations", "authentication", "data validation"]
  },
  "code_style": "enterprise",
  "include_tests": true
}
```

#### Response Format
```json
{
  "status": "success",
  "model": "deepcoder:14b",
  "response_time": 2.1,
  "code_generation": {
    "main_code": "# FastAPI Customer Management System\n...",
    "supporting_files": {
      "models.py": "# Database models\n...",
      "tests.py": "# Unit tests\n...",
      "requirements.txt": "fastapi==0.104.1\n..."
    },
    "documentation": "API documentation and usage guide",
    "quality_score": 0.92
  },
  "timestamp": "2024-12-28T10:30:00Z"
}
```

#### Example Usage
```bash
curl -X POST http://192.168.10.28:8000/api/v2/code-generation \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Build an automated reporting system for sales metrics",
    "requirements": {
      "data_source": "PostgreSQL",
      "output_format": "PDF reports",
      "schedule": "daily",
      "recipients": "email_list"
    },
    "include_deployment": true
  }'
```

### Operational Efficiency API

**Endpoint:** `/operational-efficiency`
**Model:** Qwen-1.8B (Performance Optimization Specialist)
**Purpose:** Quick operational queries and efficiency optimization

#### Request Format
```json
{
  "query": "Optimize database query performance for user analytics",
  "current_performance": {
    "avg_response_time": "2.5s",
    "queries_per_second": 150,
    "resource_usage": "high"
  },
  "optimization_goals": ["reduce_latency", "improve_throughput"],
  "constraints": ["minimal_downtime", "existing_schema"]
}
```

#### Response Format
```json
{
  "status": "success",
  "model": "qwen:1.8b",
  "response_time": 0.8,
  "optimization": {
    "recommendations": [
      "Add composite index on user_id, timestamp",
      "Implement query result caching",
      "Optimize JOIN operations"
    ],
    "expected_improvement": "60% faster queries",
    "implementation_steps": ["Step-by-step guide"],
    "risk_assessment": "low"
  },
  "timestamp": "2024-12-28T10:30:00Z"
}
```

#### Example Usage
```bash
curl -X POST http://192.168.10.28:8000/api/v2/operational-efficiency \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Reduce server response times for API endpoints",
    "current_metrics": {
      "avg_response_time": "500ms",
      "p95_response_time": "1.2s",
      "error_rate": "0.5%"
    },
    "target_improvement": "50% faster responses"
  }'
```

### Competitive Intelligence API

**Endpoint:** `/competitive-intelligence`
**Model:** DeepSeek-R1 (Market Analysis Specialist)
**Purpose:** Competitive analysis and market intelligence

#### Request Format
```json
{
  "query": "Analyze competitor pricing strategies in the CRM market",
  "competitors": ["Salesforce", "HubSpot", "Pipedrive"],
  "analysis_scope": {
    "pricing_models": true,
    "feature_comparison": true,
    "market_positioning": true,
    "customer_segments": true
  },
  "time_period": "last_12_months"
}
```

#### Response Format
```json
{
  "status": "success",
  "model": "deepseek-r1",
  "response_time": 4.5,
  "intelligence": {
    "competitive_landscape": "Detailed market analysis...",
    "pricing_analysis": {
      "salesforce": {"tier_1": "$25/user", "tier_2": "$75/user"},
      "hubspot": {"starter": "$50/month", "professional": "$500/month"},
      "pipedrive": {"essential": "$15/user", "advanced": "$29/user"}
    },
    "market_opportunities": ["Underserved segments", "Pricing gaps"],
    "strategic_recommendations": "Competitive positioning advice",
    "confidence_level": 0.87
  },
  "timestamp": "2024-12-28T10:30:00Z"
}
```

#### Example Usage
```bash
curl -X POST http://192.168.10.28:8000/api/v2/competitive-intelligence \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare feature sets of leading project management tools",
    "competitors": ["Asana", "Monday.com", "Notion"],
    "focus_areas": ["collaboration", "automation", "reporting"],
    "market_segment": "enterprise"
  }'
```

### Executive Intelligence API

**Endpoint:** `/executive-intelligence`
**Model:** JARVIS (Executive Decision Support Specialist)
**Purpose:** Executive decision support and business intelligence

#### Request Format
```json
{
  "query": "Should we acquire TechStart Inc. to expand our AI capabilities?",
  "decision_context": {
    "acquisition_target": "TechStart Inc.",
    "asking_price": "$50M",
    "strategic_rationale": "AI technology acquisition",
    "timeline": "Q1 2025"
  },
  "analysis_framework": "strategic_fit_financial_impact",
  "stakeholder_perspectives": ["CEO", "CTO", "CFO"]
}
```

#### Response Format
```json
{
  "status": "success",
  "model": "jarvis",
  "response_time": 3.1,
  "executive_brief": {
    "recommendation": "Proceed with acquisition",
    "confidence_score": 0.84,
    "key_factors": {
      "strategic_fit": "High - aligns with AI roadmap",
      "financial_impact": "Positive ROI within 18 months",
      "risk_assessment": "Medium - integration challenges"
    },
    "decision_framework": {
      "pros": ["Technology acquisition", "Talent retention", "Market position"],
      "cons": ["Integration costs", "Cultural alignment", "Market uncertainty"]
    },
    "next_steps": ["Due diligence", "Integration planning", "Board approval"],
    "implementation_timeline": "6-month integration plan"
  },
  "timestamp": "2024-12-28T10:30:00Z"
}
```

#### Example Usage
```bash
curl -X POST http://192.168.10.28:8000/api/v2/executive-intelligence \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Evaluate the business case for expanding into the Asian market",
    "context": {
      "target_markets": ["Japan", "Singapore", "South Korea"],
      "investment_budget": "$20M",
      "timeline": "2025-2026"
    },
    "decision_criteria": ["market_size", "competition", "regulatory_environment"]
  }'
```

## Utility Endpoints

### Health Check
```bash
# Basic health check
curl http://192.168.10.28:8000/health

# Detailed system status
curl http://192.168.10.28:8000/api/v2/health/detailed
```

### Model Status
```bash
# Check all model availability
curl http://192.168.10.28:8000/api/v2/models/status

# Check specific model
curl http://192.168.10.28:8000/api/v2/models/yi:34b/status
```

### Performance Metrics
```bash
# System performance metrics
curl http://192.168.10.28:8000/api/v2/metrics

# Model-specific metrics
curl http://192.168.10.28:8000/api/v2/metrics/models
```

## Batch Processing Endpoints

### Batch Analysis
```json
{
  "requests": [
    {
      "endpoint": "strategic-analysis",
      "query": "Market analysis for Q1",
      "id": "request_1"
    },
    {
      "endpoint": "competitive-intelligence",
      "query": "Competitor pricing review",
      "id": "request_2"
    }
  ],
  "priority": "normal",
  "callback_url": "https://your-system.com/batch-callback"
}
```

### Batch Response
```json
{
  "batch_id": "batch_12345",
  "status": "completed",
  "results": [
    {
      "request_id": "request_1",
      "status": "success",
      "response": "Analysis results..."
    },
    {
      "request_id": "request_2",
      "status": "success",
      "response": "Intelligence report..."
    }
  ],
  "processing_time": 12.3,
  "timestamp": "2024-12-28T10:35:00Z"
}
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: query",
    "details": {
      "field": "query",
      "expected_type": "string",
      "provided": null
    },
    "timestamp": "2024-12-28T10:30:00Z",
    "request_id": "req_12345"
  }
}
```

### Common Error Codes
- `INVALID_REQUEST`: Missing or invalid request parameters
- `MODEL_UNAVAILABLE`: Requested model is not available
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded
- `AUTHENTICATION_FAILED`: Invalid or missing API key
- `INTERNAL_ERROR`: Server-side processing error

## Rate Limiting

### Default Limits
- **Strategic Analysis**: 10 requests/minute
- **Code Generation**: 20 requests/minute
- **Operational Efficiency**: 100 requests/minute
- **Competitive Intelligence**: 15 requests/minute
- **Executive Intelligence**: 10 requests/minute

### Rate Limit Headers
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1640995200
```

## WebSocket Streaming

### Real-time Streaming
```javascript
const ws = new WebSocket('ws://192.168.10.28:8000/api/v2/stream');

ws.send(JSON.stringify({
  endpoint: 'strategic-analysis',
  query: 'Real-time market analysis',
  stream: true
}));

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Streaming response:', data.content);
};
```

## Integration Examples

### Python Client
```python
import requests
import json

class LLM02Client:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def strategic_analysis(self, query, context=None):
        endpoint = f"{self.base_url}/strategic-analysis"
        data = {"query": query}
        if context:
            data["context"] = context
        
        response = requests.post(endpoint, headers=self.headers, json=data)
        return response.json()
    
    def code_generation(self, query, requirements=None):
        endpoint = f"{self.base_url}/code-generation"
        data = {"query": query}
        if requirements:
            data["requirements"] = requirements
        
        response = requests.post(endpoint, headers=self.headers, json=data)
        return response.json()

# Usage
client = LLM02Client("http://192.168.10.28:8000/api/v2", "your_api_key")
result = client.strategic_analysis("Analyze market trends for Q1 2025")
```

### JavaScript Client
```javascript
class LLM02Client {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async strategicAnalysis(query, context = null) {
        const endpoint = `${this.baseUrl}/strategic-analysis`;
        const data = { query };
        if (context) data.context = context;
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
    
    async codeGeneration(query, requirements = null) {
        const endpoint = `${this.baseUrl}/code-generation`;
        const data = { query };
        if (requirements) data.requirements = requirements;
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
}

// Usage
const client = new LLM02Client("http://192.168.10.28:8000/api/v2", "your_api_key");
const result = await client.strategicAnalysis("Competitive analysis for cloud services");
```

## Best Practices

### Query Optimization
1. **Be Specific**: Provide clear, detailed queries for better results
2. **Include Context**: Add relevant business context for more accurate analysis
3. **Use Appropriate Models**: Choose the right endpoint for your use case
4. **Batch Similar Requests**: Use batch processing for multiple related queries

### Performance Optimization
1. **Cache Results**: Cache frequent queries to reduce API calls
2. **Use Streaming**: For real-time applications, use WebSocket streaming
3. **Monitor Rate Limits**: Implement proper rate limiting in your client
4. **Handle Errors Gracefully**: Implement retry logic with exponential backoff

### Security Best Practices
1. **Secure API Keys**: Store API keys securely and rotate regularly
2. **Use HTTPS**: Always use encrypted connections in production
3. **Validate Input**: Sanitize and validate all input data
4. **Monitor Usage**: Track API usage for security and cost management

This API reference provides comprehensive guidance for integrating with the LLM-02 business intelligence platform. For additional support, refer to the operations manual and system architecture documentation.
