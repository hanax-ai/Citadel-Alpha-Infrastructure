"""
Business Process Automation API Endpoints
Provides RESTful API for enterprise business workflow management and AI-powered automation
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, UploadFile, File
from pydantic import BaseModel, Field

from app.core.business.workflow_engine import (
    WorkflowEngine, BusinessWorkflow, WorkflowStep, ProcessStatus, WorkflowPriority, WorkflowContext
)
from app.core.business.ai_decision_engine import AIDecisionEngine, DecisionComplexity
from app.core.business.document_processor import DocumentProcessor, DocumentType

logger = logging.getLogger("hx_orchestration.business_automation")

# Initialize global instances (will be properly injected in production)
workflow_engine = WorkflowEngine()
ai_decision_engine = AIDecisionEngine()
document_processor = DocumentProcessor()

# Pydantic Models for API Requests/Responses
class WorkflowDefinitionRequest(BaseModel):
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    priority: str = Field(default="normal", description="Workflow priority: low, normal, high, critical")
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps configuration")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class WorkflowExecutionRequest(BaseModel):
    initial_context: Optional[Dict[str, Any]] = Field(default=None, description="Initial workflow context")
    background: bool = Field(default=False, description="Execute in background")

class DecisionAnalysisRequest(BaseModel):
    context: Dict[str, Any] = Field(..., description="Business context for decision")
    criteria: Dict[str, Any] = Field(..., description="Decision criteria and constraints")
    complexity: str = Field(default="moderate", description="Decision complexity: simple, moderate, complex, critical")
    require_explanation: bool = Field(default=True, description="Require detailed explanation")

class DocumentProcessingRequest(BaseModel):
    content: str = Field(..., description="Document content to process")
    document_type: str = Field(default="general", description="Type of document")
    processing_requirements: Optional[Dict[str, Any]] = Field(default=None, description="Processing requirements")
    generate_embeddings: bool = Field(default=True, description="Generate embeddings for semantic analysis")

# API Router
router = APIRouter(prefix="/business", tags=["Business Automation"])

# Workflow Management Endpoints

@router.post("/workflows/create")
async def create_business_workflow(request: WorkflowDefinitionRequest) -> Dict[str, Any]:
    """Create new business workflow with AI-powered steps"""
    try:
        logger.info(f"Creating business workflow: {request.name}")
        
        # Validate priority
        priority_map = {
            "low": WorkflowPriority.LOW,
            "normal": WorkflowPriority.NORMAL,
            "high": WorkflowPriority.HIGH,
            "critical": WorkflowPriority.CRITICAL
        }
        priority = priority_map.get(request.priority.lower(), WorkflowPriority.NORMAL)
        
        # Create workflow steps from configuration
        workflow_steps = []
        for step_config in request.steps:
            step = await _create_workflow_step(step_config)
            workflow_steps.append(step)
        
        # Create workflow
        workflow_id = await workflow_engine.create_workflow(
            name=request.name,
            description=request.description,
            steps=workflow_steps,
            priority=priority,
            metadata=request.metadata
        )
        
        logger.info(f"Created workflow {workflow_id} with {len(workflow_steps)} steps")
        
        return {
            "workflow_id": workflow_id,
            "name": request.name,
            "status": "created",
            "step_count": len(workflow_steps),
            "priority": request.priority,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow creation failed: {str(e)}")

@router.post("/workflows/{workflow_id}/execute")
async def execute_business_workflow(
    workflow_id: str,
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Execute business workflow with optional background processing"""
    try:
        logger.info(f"Executing workflow {workflow_id}")
        
        # Execute workflow
        if request.background:
            # Execute in background
            background_tasks.add_task(
                _execute_workflow_background,
                workflow_id,
                request.initial_context
            )
            
            return {
                "workflow_id": workflow_id,
                "status": "execution_started",
                "background": True,
                "started_at": datetime.utcnow().isoformat()
            }
        else:
            # Execute synchronously
            result = await workflow_engine.execute_workflow(
                workflow_id=workflow_id,
                initial_context=request.initial_context,
                background=False
            )
            
            return {
                "workflow_id": workflow_id,
                "execution_result": result,
                "background": False
            }
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@router.get("/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """Get detailed workflow execution status"""
    try:
        status = await workflow_engine.get_workflow_status(workflow_id)
        return status
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@router.get("/workflows/active")
async def list_active_workflows() -> Dict[str, Any]:
    """List all active business workflows"""
    try:
        workflows = await workflow_engine.list_active_workflows()
        
        return {
            "active_workflows": workflows,
            "total_count": len(workflows),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow listing failed: {str(e)}")

@router.post("/workflows/{workflow_id}/pause")
async def pause_workflow(workflow_id: str) -> Dict[str, Any]:
    """Pause workflow execution"""
    try:
        await workflow_engine.pause_workflow(workflow_id)
        
        return {
            "workflow_id": workflow_id,
            "action": "paused",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to pause workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow pause failed: {str(e)}")

@router.post("/workflows/{workflow_id}/resume")
async def resume_workflow(workflow_id: str) -> Dict[str, Any]:
    """Resume paused workflow execution"""
    try:
        await workflow_engine.resume_workflow(workflow_id)
        
        return {
            "workflow_id": workflow_id,
            "action": "resumed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to resume workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow resume failed: {str(e)}")

@router.delete("/workflows/{workflow_id}")
async def cancel_workflow(workflow_id: str) -> Dict[str, Any]:
    """Cancel workflow execution"""
    try:
        await workflow_engine.cancel_workflow(workflow_id)
        
        return {
            "workflow_id": workflow_id,
            "action": "cancelled",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow cancellation failed: {str(e)}")

# AI Decision Making Endpoints

@router.post("/decisions/analyze")
async def analyze_business_decision(request: DecisionAnalysisRequest) -> Dict[str, Any]:
    """AI-powered business decision analysis"""
    try:
        logger.info("Performing AI business decision analysis")
        
        # Validate complexity
        if request.complexity not in [DecisionComplexity.SIMPLE, DecisionComplexity.MODERATE, 
                                    DecisionComplexity.COMPLEX, DecisionComplexity.CRITICAL]:
            request.complexity = DecisionComplexity.MODERATE
        
        # Make AI decision
        decision_result = await ai_decision_engine.make_business_decision(
            context=request.context,
            decision_criteria=request.criteria,
            complexity=request.complexity,
            require_explanation=request.require_explanation
        )
        
        return {
            "analysis_id": decision_result.decision_id,
            "decision": decision_result.decision,
            "confidence": decision_result.confidence,
            "reasoning": decision_result.reasoning,
            "next_steps": decision_result.next_steps,
            "alternatives": decision_result.alternatives,
            "model_used": decision_result.model_used,
            "processing_time": decision_result.processing_time,
            "timestamp": decision_result.timestamp.isoformat(),
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Decision analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Decision analysis failed: {str(e)}")

@router.get("/decisions/history")
async def get_decision_history(limit: int = 100) -> Dict[str, Any]:
    """Get AI decision history"""
    try:
        history = await ai_decision_engine.get_decision_history(limit=limit)
        
        return {
            "decision_history": history,
            "total_count": len(history),
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get decision history: {e}")
        raise HTTPException(status_code=500, detail=f"Decision history retrieval failed: {str(e)}")

@router.get("/decisions/analytics")
async def get_decision_analytics(time_window_hours: int = 24) -> Dict[str, Any]:
    """Get AI decision analytics and patterns"""
    try:
        analytics = await ai_decision_engine.analyze_decision_patterns(time_window_hours)
        
        return {
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get decision analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Decision analytics failed: {str(e)}")

# Document Processing Endpoints

@router.post("/documents/process")
async def process_business_document(request: DocumentProcessingRequest) -> Dict[str, Any]:
    """Process business document with AI analysis"""
    try:
        logger.info(f"Processing business document of type: {request.document_type}")
        
        # Process document
        result = await document_processor.process_business_document(
            document_content=request.content,
            document_type=request.document_type,
            processing_requirements=request.processing_requirements,
            generate_embeddings=request.generate_embeddings
        )
        
        return {
            "processing_id": result.processing_id,
            "document_type": result.document_type,
            "extracted_information": {
                "key_entities": result.extracted_information.key_entities,
                "dates": result.extracted_information.dates,
                "financial_figures": result.extracted_information.financial_figures,
                "action_items": result.extracted_information.action_items,
                "stakeholders": result.extracted_information.stakeholders,
                "topics": result.extracted_information.topics
            },
            "business_insights": {
                "summary": result.business_insights.summary,
                "key_findings": result.business_insights.key_findings,
                "opportunities": result.business_insights.opportunities,
                "risks": result.business_insights.risks,
                "sentiment_analysis": result.business_insights.sentiment_analysis,
                "priority_level": result.business_insights.priority_level,
                "confidence_score": result.business_insights.confidence_score
            },
            "recommendations": result.recommendations,
            "embeddings_generated": result.embeddings_generated,
            "processing_time": result.processing_time,
            "timestamp": result.processing_timestamp.isoformat(),
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@router.post("/documents/upload")
async def upload_and_process_document(
    file: UploadFile = File(...),
    document_type: str = "general",
    generate_embeddings: bool = True
) -> Dict[str, Any]:
    """Upload and process document file"""
    try:
        # Read file content
        content = await file.read()
        
        # Handle different file types
        if file.content_type == "text/plain":
            document_content = content.decode('utf-8')
        else:
            # For now, only support text files
            raise HTTPException(status_code=400, detail="Only text files are currently supported")
        
        # Process document
        result = await document_processor.process_business_document(
            document_content=document_content,
            document_type=document_type,
            generate_embeddings=generate_embeddings
        )
        
        return {
            "filename": file.filename,
            "file_size": len(content),
            "processing_id": result.processing_id,
            "document_type": result.document_type,
            "processing_time": result.processing_time,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"File upload and processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@router.get("/documents/history")
async def get_document_processing_history(limit: int = 50) -> Dict[str, Any]:
    """Get document processing history"""
    try:
        history = await document_processor.get_processing_history(limit=limit)
        
        return {
            "processing_history": history,
            "total_count": len(history),
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get processing history: {e}")
        raise HTTPException(status_code=500, detail=f"Processing history retrieval failed: {str(e)}")

# System Health and Status Endpoints

@router.get("/health")
async def get_business_automation_health() -> Dict[str, Any]:
    """Get comprehensive business automation system health"""
    try:
        # Get health from all components
        workflow_health = await workflow_engine.health_check()
        decision_health = await ai_decision_engine.health_check()
        document_health = await document_processor.health_check()
        
        overall_status = "healthy"
        if any(h.get("status") != "healthy" for h in [workflow_health, decision_health, document_health]):
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "workflow_engine": workflow_health,
            "ai_decision_engine": decision_health,
            "document_processor": document_health,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/metrics")
async def get_business_automation_metrics() -> Dict[str, Any]:
    """Get business automation performance metrics"""
    try:
        # Get metrics from workflow engine
        workflow_metrics = {
            "active_workflows": len(workflow_engine.active_workflows),
            "completed_workflows": len(workflow_engine.workflow_history)
        }
        
        # Get metrics from AI decision engine
        decision_metrics = {
            "total_decisions": len(ai_decision_engine.decision_history)
        }
        
        # Get metrics from document processor
        document_metrics = {
            "total_documents_processed": len(document_processor.processing_history)
        }
        
        return {
            "workflow_metrics": workflow_metrics,
            "decision_metrics": decision_metrics,
            "document_metrics": document_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

# Helper Functions

async def _create_workflow_step(step_config: Dict[str, Any]) -> WorkflowStep:
    """Create workflow step from configuration"""
    step_id = step_config.get("id", str(uuid.uuid4()))
    name = step_config.get("name", f"Step {step_id}")
    action_type = step_config.get("action_type", "generic")
    
    # Create step action based on type
    if action_type == "ai_decision":
        action = _create_ai_decision_action(step_config)
    elif action_type == "document_analysis":
        action = _create_document_analysis_action(step_config)
    elif action_type == "data_processing":
        action = _create_data_processing_action(step_config)
    else:
        action = _create_generic_action(step_config)
    
    return WorkflowStep(
        step_id=step_id,
        name=name,
        action=action,
        retry_count=step_config.get("retry_count", 3),
        timeout=step_config.get("timeout", 300),
        dependencies=step_config.get("dependencies", []),
        metadata=step_config.get("metadata", {})
    )

def _create_ai_decision_action(config: Dict[str, Any]):
    """Create AI decision action"""
    async def ai_decision_action(context: WorkflowContext) -> Dict[str, Any]:
        decision_context = context.data.get("decision_context", {})
        criteria = config.get("criteria", {})
        
        result = await ai_decision_engine.make_business_decision(
            context=decision_context,
            decision_criteria=criteria,
            complexity=config.get("complexity", "moderate")
        )
        
        return {
            "decision": result.decision,
            "confidence": result.confidence,
            "reasoning": result.reasoning
        }
    
    return ai_decision_action

def _create_document_analysis_action(config: Dict[str, Any]):
    """Create document analysis action"""
    async def document_analysis_action(context: WorkflowContext) -> Dict[str, Any]:
        document_content = context.data.get("document_content", "")
        document_type = config.get("document_type", "general")
        
        result = await document_processor.process_business_document(
            document_content=document_content,
            document_type=document_type
        )
        
        return {
            "processing_id": result.processing_id,
            "key_findings": result.business_insights.key_findings,
            "recommendations": result.recommendations
        }
    
    return document_analysis_action

def _create_data_processing_action(config: Dict[str, Any]):
    """Create data processing action"""
    async def data_processing_action(context: WorkflowContext) -> Dict[str, Any]:
        # Simulate data processing
        input_data = context.data.get("input_data", {})
        processing_type = config.get("processing_type", "transform")
        
        # Simple data transformation
        if processing_type == "transform":
            result = {
                "processed_data": input_data,
                "transformation": config.get("transformation", "identity"),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            result = {
                "data": input_data,
                "processing_type": processing_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return result
    
    return data_processing_action

def _create_generic_action(config: Dict[str, Any]):
    """Create generic action"""
    async def generic_action(context: WorkflowContext) -> Dict[str, Any]:
        # Generic action implementation
        action_config = config.get("action_config", {})
        
        return {
            "step_completed": True,
            "config": action_config,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return generic_action

async def _execute_workflow_background(workflow_id: str, initial_context: Optional[Dict[str, Any]]):
    """Execute workflow in background"""
    try:
        result = await workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            initial_context=initial_context,
            background=False
        )
        logger.info(f"Background workflow {workflow_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Background workflow {workflow_id} failed: {e}")

# Initialize services on module load
async def initialize_business_services():
    """Initialize all business automation services"""
    try:
        await workflow_engine.initialize()
        await ai_decision_engine.initialize()
        await document_processor.initialize()
        logger.info("Business automation services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize business services: {e}")

# Call initialization (will be properly handled in main app)
# asyncio.create_task(initialize_business_services())
