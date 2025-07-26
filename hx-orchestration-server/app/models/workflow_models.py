"""
Workflow Models

Pydantic models for workflow definitions and executions.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskDefinition(BaseModel):
    """Individual task definition"""
    id: str = Field(..., description="Unique task identifier")
    type: str = Field(..., description="Task type (embedding, llm, etc.)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")


class WorkflowDefinition(BaseModel):
    """Workflow definition model"""
    id: Optional[str] = Field(None, description="Workflow identifier")
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    tasks: List[TaskDefinition] = Field(..., description="List of tasks in workflow")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class WorkflowExecution(BaseModel):
    """Workflow execution model"""
    id: Optional[str] = Field(None, description="Execution identifier")
    workflow_id: str = Field(..., description="Associated workflow ID")
    status: WorkflowStatus = Field(default=WorkflowStatus.PENDING, description="Execution status")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Execution inputs")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Execution outputs")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class TaskExecution(BaseModel):
    """Individual task execution"""
    id: str = Field(..., description="Task execution ID")
    task_id: str = Field(..., description="Associated task definition ID")
    workflow_execution_id: str = Field(..., description="Parent workflow execution ID")
    status: WorkflowStatus = Field(default=WorkflowStatus.PENDING, description="Task status")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Task inputs")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Task outputs")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
