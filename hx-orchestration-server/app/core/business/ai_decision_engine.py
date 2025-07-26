"""
AI-Powered Business Decision Engine
Provides intelligent decision-making capabilities for business process automation
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
import httpx

from app.common.base_classes import BaseService

logger = logging.getLogger("hx_orchestration.ai_decision_engine")

@dataclass
class DecisionContext:
    """Context for AI decision making"""
    business_context: Dict[str, Any]
    decision_criteria: Dict[str, Any]
    historical_decisions: List[Dict[str, Any]]
    constraints: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class DecisionResult:
    """Result of AI decision analysis"""
    decision_id: str
    decision: str
    confidence: float
    reasoning: str
    next_steps: List[str]
    alternatives: List[Dict[str, Any]]
    model_used: str
    server_used: str
    processing_time: float
    timestamp: datetime

class DecisionComplexity:
    """Decision complexity levels for model selection"""
    SIMPLE = "simple"      # Basic yes/no, categorical decisions
    MODERATE = "moderate"  # Multi-factor analysis
    COMPLEX = "complex"    # Deep analysis with multiple variables
    CRITICAL = "critical"  # High-stakes decisions requiring best models

class AIDecisionEngine(BaseService):
    """Enterprise AI decision engine for business process automation"""
    
    def __init__(self, service_discovery=None, name: str = "ai_decision_engine"):
        super().__init__(name)
        self.service_discovery = service_discovery
        self.decision_history: List[DecisionResult] = []
        self.model_routing = {
            DecisionComplexity.SIMPLE: ["phi3", "llama3"],
            DecisionComplexity.MODERATE: ["mixtral", "phi3"],
            DecisionComplexity.COMPLEX: ["mixtral", "claude"],
            DecisionComplexity.CRITICAL: ["mixtral", "gpt-4"]
        }
        self.default_timeout = 30.0
        
    async def initialize(self) -> bool:
        """Initialize AI decision engine"""
        try:
            logger.info("Initializing AI decision engine")
            
            # Validate service discovery
            if not self.service_discovery:
                logger.warning("No service discovery provided - decisions will route to localhost")
            
            self._health_status = "healthy"
            self._initialized = True
            
            logger.info("AI decision engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI decision engine: {e}")
            self._health_status = "unhealthy"
            return False
    
    async def make_business_decision(
        self,
        context: Dict[str, Any],
        decision_criteria: Dict[str, Any],
        complexity: str = DecisionComplexity.MODERATE,
        require_explanation: bool = True,
        historical_context: List[Dict[str, Any]] = None
    ) -> DecisionResult:
        """Make AI-powered business decision"""
        start_time = datetime.utcnow()
        decision_id = str(uuid.uuid4())
        
        logger.info(f"Making business decision {decision_id} with complexity: {complexity}")
        
        try:
            # Select optimal model for decision complexity
            model = await self._select_optimal_model(complexity)
            
            # Route to optimal server
            server_info = await self._select_optimal_server(model)
            
            # Build decision prompt
            decision_context = DecisionContext(
                business_context=context,
                decision_criteria=decision_criteria,
                historical_decisions=historical_context or [],
                constraints=decision_criteria.get("constraints", {}),
                metadata={"complexity": complexity, "require_explanation": require_explanation}
            )
            
            prompt = self._build_decision_prompt(decision_context)
            
            # Get AI decision
            ai_response = await self._call_ai_model(server_info, model, prompt)
            
            # Parse and validate decision
            decision_data = self._parse_ai_decision(ai_response)
            
            # Create decision result
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = DecisionResult(
                decision_id=decision_id,
                decision=decision_data.get("decision", "no_decision"),
                confidence=float(decision_data.get("confidence", 0.5)),
                reasoning=decision_data.get("reasoning", "No reasoning provided"),
                next_steps=decision_data.get("next_steps", []),
                alternatives=decision_data.get("alternatives", []),
                model_used=model,
                server_used=server_info.get("id", "unknown"),
                processing_time=processing_time,
                timestamp=start_time
            )
            
            # Store decision in history
            self.decision_history.append(result)
            
            logger.info(f"Decision {decision_id} completed in {processing_time:.2f}s with confidence {result.confidence}")
            return result
            
        except Exception as e:
            logger.error(f"Decision making failed: {e}")
            
            # Return fallback decision
            return DecisionResult(
                decision_id=decision_id,
                decision="error",
                confidence=0.0,
                reasoning=f"Decision making failed: {str(e)}",
                next_steps=["review_error", "retry_decision"],
                alternatives=[],
                model_used="none",
                server_used="none",
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                timestamp=start_time
            )
    
    async def _select_optimal_model(self, complexity: str) -> str:
        """Select optimal AI model based on decision complexity"""
        available_models = self.model_routing.get(complexity, ["phi3"])
        
        # For now, return first available model
        # TODO: Implement server capacity checking
        return available_models[0]
    
    async def _select_optimal_server(self, model: str) -> Dict[str, Any]:
        """Select optimal server for model execution"""
        if self.service_discovery:
            try:
                return await self.service_discovery.select_optimal_server(model)
            except Exception as e:
                logger.warning(f"Service discovery failed: {e}, using fallback")
        
        # Fallback to known server endpoints
        fallback_servers = {
            "phi3": {"id": "llm_01", "hostname": "192.168.10.34", "port": 8002},
            "mixtral": {"id": "llm_02", "hostname": "192.168.10.28", "port": 8000},
            "llama3": {"id": "llm_01", "hostname": "192.168.10.34", "port": 8002}
        }
        
        return fallback_servers.get(model, {"id": "local", "hostname": "localhost", "port": 8000})
    
    def _build_decision_prompt(self, context: DecisionContext) -> str:
        """Build comprehensive decision prompt for AI model"""
        
        prompt = f"""You are an enterprise business decision engine. Analyze the provided context and make a structured business decision.

BUSINESS CONTEXT:
{json.dumps(context.business_context, indent=2)}

DECISION CRITERIA:
{json.dumps(context.decision_criteria, indent=2)}

CONSTRAINTS:
{json.dumps(context.constraints, indent=2)}

HISTORICAL DECISIONS (for reference):
{json.dumps(context.historical_decisions[-5:], indent=2) if context.historical_decisions else "None"}

INSTRUCTIONS:
1. Analyze the business context thoroughly
2. Consider all decision criteria and constraints
3. Evaluate potential risks and benefits
4. Provide a clear, actionable decision
5. Include confidence level (0.0-1.0)
6. Explain your reasoning step by step
7. Suggest next steps for implementation
8. Consider alternative approaches

REQUIRED RESPONSE FORMAT (JSON):
{{
    "decision": "clear_actionable_decision",
    "confidence": 0.85,
    "reasoning": "step-by-step explanation of decision logic",
    "next_steps": ["specific_action_1", "specific_action_2", "specific_action_3"],
    "alternatives": [
        {{
            "option": "alternative_approach_1",
            "pros": ["benefit_1", "benefit_2"],
            "cons": ["drawback_1", "drawback_2"],
            "confidence": 0.7
        }}
    ],
    "risk_assessment": {{
        "high_risk_factors": ["factor_1", "factor_2"],
        "mitigation_strategies": ["strategy_1", "strategy_2"]
    }},
    "success_metrics": ["metric_1", "metric_2", "metric_3"]
}}

Respond only with valid JSON. Ensure all fields are present and properly formatted."""

        return prompt
    
    async def _call_ai_model(self, server_info: Dict[str, Any], model: str, prompt: str) -> Dict[str, Any]:
        """Call AI model for decision analysis"""
        url = f"http://{server_info['hostname']}:{server_info['port']}/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a business decision engine. Analyze business contexts and provide structured decisions in JSON format. Be precise, analytical, and actionable."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1,  # Low temperature for consistent decisions
            "response_format": {"type": "json_object"}
        }
        
        async with httpx.AsyncClient(timeout=self.default_timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    
    def _parse_ai_decision(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate AI decision response"""
        try:
            # Extract content from AI response
            content = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            
            # Parse JSON content
            decision_data = json.loads(content)
            
            # Validate required fields
            required_fields = ["decision", "confidence", "reasoning", "next_steps"]
            for field in required_fields:
                if field not in decision_data:
                    logger.warning(f"Missing required field in AI decision: {field}")
                    decision_data[field] = self._get_default_value(field)
            
            # Validate confidence score
            confidence = decision_data.get("confidence", 0.5)
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                logger.warning(f"Invalid confidence score: {confidence}, using 0.5")
                decision_data["confidence"] = 0.5
            
            # Ensure next_steps is a list
            if not isinstance(decision_data.get("next_steps"), list):
                decision_data["next_steps"] = [str(decision_data.get("next_steps", "review_decision"))]
            
            return decision_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI decision JSON: {e}")
            return self._get_fallback_decision("json_parse_error")
        
        except Exception as e:
            logger.error(f"Error parsing AI decision: {e}")
            return self._get_fallback_decision("parse_error")
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing fields"""
        defaults = {
            "decision": "require_manual_review",
            "confidence": 0.5,
            "reasoning": "Insufficient information for automated decision",
            "next_steps": ["manual_review", "gather_more_data"],
            "alternatives": [],
            "risk_assessment": {"high_risk_factors": [], "mitigation_strategies": []},
            "success_metrics": []
        }
        return defaults.get(field, "unknown")
    
    def _get_fallback_decision(self, error_type: str) -> Dict[str, Any]:
        """Get fallback decision for error cases"""
        return {
            "decision": "error_fallback",
            "confidence": 0.0,
            "reasoning": f"Decision making failed due to {error_type}",
            "next_steps": ["manual_review", "retry_with_different_approach"],
            "alternatives": [],
            "risk_assessment": {
                "high_risk_factors": ["automated_decision_failure"],
                "mitigation_strategies": ["manual_oversight", "process_review"]
            },
            "success_metrics": ["decision_accuracy", "process_reliability"]
        }
    
    async def analyze_decision_patterns(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Analyze decision patterns and performance"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        recent_decisions = [
            d for d in self.decision_history 
            if d.timestamp >= cutoff_time
        ]
        
        if not recent_decisions:
            return {"status": "no_recent_decisions", "time_window_hours": time_window_hours}
        
        # Calculate metrics
        total_decisions = len(recent_decisions)
        avg_confidence = sum(d.confidence for d in recent_decisions) / total_decisions
        avg_processing_time = sum(d.processing_time for d in recent_decisions) / total_decisions
        
        # Model usage statistics
        model_usage = {}
        for decision in recent_decisions:
            model = decision.model_used
            model_usage[model] = model_usage.get(model, 0) + 1
        
        # Decision types
        decision_types = {}
        for decision in recent_decisions:
            decision_type = decision.decision
            decision_types[decision_type] = decision_types.get(decision_type, 0) + 1
        
        return {
            "time_window_hours": time_window_hours,
            "total_decisions": total_decisions,
            "average_confidence": round(avg_confidence, 3),
            "average_processing_time": round(avg_processing_time, 3),
            "model_usage": model_usage,
            "decision_types": decision_types,
            "high_confidence_decisions": len([d for d in recent_decisions if d.confidence > 0.8]),
            "low_confidence_decisions": len([d for d in recent_decisions if d.confidence < 0.5])
        }
    
    async def get_decision_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent decision history"""
        recent_decisions = self.decision_history[-limit:] if limit else self.decision_history
        
        return [
            {
                "decision_id": d.decision_id,
                "decision": d.decision,
                "confidence": d.confidence,
                "reasoning": d.reasoning,
                "model_used": d.model_used,
                "processing_time": d.processing_time,
                "timestamp": d.timestamp.isoformat()
            }
            for d in recent_decisions
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """AI decision engine health check"""
        return {
            "service": self.name,
            "status": self._health_status,
            "total_decisions": len(self.decision_history),
            "uptime_seconds": self.uptime,
            "service_discovery_available": self.service_discovery is not None
        }
    
    async def shutdown(self) -> None:
        """Graceful shutdown of AI decision engine"""
        logger.info("Shutting down AI decision engine")
        await super().shutdown()
        logger.info("AI decision engine shut down gracefully")
