"""
Orchestration API Endpoints

Workflow orchestration endpoints for coordinating AI tasks across services.
Provides workflow management, task routing, and state coordination.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.core.orchestration.workflow_manager import WorkflowManager
from app.core.orchestration.task_router import TaskRouter
from app.models.workflow_models import WorkflowDefinition, WorkflowExecution

router = APIRouter()


class OrchestrationRequest(BaseModel):
    """Orchestration request model"""
    workflow_id: str = Field(..., description="Workflow identifier")
    input_data: Dict[str, Any] = Field(..., description="Input data for workflow")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Execution context")
    priority: int = Field(default=5, description="Task priority (1-10)")


class OrchestrationResponse(BaseModel):
    """Orchestration response model"""
    execution_id: str
    workflow_id: str
    status: str
    created_at: datetime
    estimated_completion: Optional[datetime]


@router.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate_workflow(request: OrchestrationRequest):
    """
    Execute a workflow orchestration
    
    Args:
        request: Orchestration request with workflow and input data
        
    Returns:
        OrchestrationResponse: Execution information
    """
    try:
        workflow_manager = WorkflowManager()
        task_router = TaskRouter()
        
        # Create execution ID
        execution_id = str(uuid.uuid4())
        
        # Start workflow execution
        execution = await workflow_manager.start_workflow(
            workflow_id=request.workflow_id,
            execution_id=execution_id,
            input_data=request.input_data,
            context=request.context,
            priority=request.priority
        )
        
        return OrchestrationResponse(
            execution_id=execution_id,
            workflow_id=request.workflow_id,
            status=execution.status,
            created_at=execution.created_at,
            estimated_completion=execution.estimated_completion
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration failed: {str(e)}"
        )


@router.get("/workflows")
async def list_workflows():
    """
    List available workflows
    
    Returns:
        List[Dict]: Available workflow definitions
    """
    try:
        workflow_manager = WorkflowManager()
        workflows = await workflow_manager.list_workflows()
        return {"workflows": workflows}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list workflows: {str(e)}"
        )


@router.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    """
    Get workflow execution status
    
    Args:
        execution_id: Execution identifier
        
    Returns:
        Dict: Execution status and details
    """
    try:
        workflow_manager = WorkflowManager()
        execution = await workflow_manager.get_execution(execution_id)
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "execution_id": execution_id,
            "workflow_id": execution.workflow_id,
            "status": execution.status,
            "progress": execution.progress,
            "created_at": execution.created_at,
            "updated_at": execution.updated_at,
            "result": execution.result if execution.status == "completed" else None,
            "error": execution.error if execution.status == "failed" else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get execution status: {str(e)}"
        )
