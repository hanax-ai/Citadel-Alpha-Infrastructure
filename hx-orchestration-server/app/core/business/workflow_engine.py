"""
Workflow Orchestration Engine
Provides enterprise-grade business process automation with AI-powered decision points
"""

import asyncio
import uuid
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from app.common.base_classes import BaseService

logger = logging.getLogger("hx_orchestration.workflow_engine")

class ProcessStatus(Enum):
    """Workflow and step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class WorkflowPriority(Enum):
    """Workflow execution priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class WorkflowContext:
    """Workflow execution context with shared data"""
    workflow_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_metrics: Dict[str, Any] = field(default_factory=dict)

class WorkflowStep:
    """Individual workflow step with execution logic and retry capabilities"""
    
    def __init__(
        self,
        step_id: str,
        name: str,
        action: Callable[[WorkflowContext], Any],
        retry_count: int = 3,
        timeout: int = 300,
        dependencies: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.step_id = step_id
        self.name = name
        self.action = action
        self.retry_count = retry_count
        self.timeout = timeout
        self.dependencies = dependencies or []
        self.metadata = metadata or {}
        
        # Execution state
        self.status = ProcessStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.attempt_count = 0
        self.execution_history: List[Dict[str, Any]] = []
    
    async def execute(self, context: WorkflowContext) -> Any:
        """Execute workflow step with retry logic and timeout"""
        self.status = ProcessStatus.RUNNING
        self.started_at = datetime.utcnow()
        
        for attempt in range(self.retry_count + 1):
            self.attempt_count = attempt + 1
            
            try:
                logger.info(f"Executing step {self.step_id} (attempt {self.attempt_count})")
                
                # Execute step action with timeout
                if asyncio.iscoroutinefunction(self.action):
                    self.result = await asyncio.wait_for(
                        self.action(context),
                        timeout=self.timeout
                    )
                else:
                    self.result = await asyncio.wait_for(
                        asyncio.to_thread(self.action, context),
                        timeout=self.timeout
                    )
                
                # Record successful execution
                self.status = ProcessStatus.COMPLETED
                self.completed_at = datetime.utcnow()
                self._record_execution(success=True)
                
                logger.info(f"Step {self.step_id} completed successfully")
                return self.result
                
            except asyncio.TimeoutError:
                error_msg = f"Step timed out after {self.timeout} seconds"
                self.error = error_msg
                self._record_execution(success=False, error=error_msg)
                logger.warning(f"Step {self.step_id} timed out (attempt {attempt + 1})")
                
            except Exception as e:
                error_msg = str(e)
                self.error = error_msg
                self._record_execution(success=False, error=error_msg)
                logger.error(f"Step {self.step_id} failed: {error_msg} (attempt {attempt + 1})")
            
            # Exponential backoff before retry
            if attempt < self.retry_count:
                backoff_time = min(2 ** attempt, 30)  # Max 30 seconds
                await asyncio.sleep(backoff_time)
        
        # All retries exhausted
        self.status = ProcessStatus.FAILED
        self.completed_at = datetime.utcnow()
        logger.error(f"Step {self.step_id} failed after {self.retry_count + 1} attempts")
        raise Exception(f"Step {self.step_id} failed: {self.error}")
    
    def _record_execution(self, success: bool, error: str = None):
        """Record execution attempt in history"""
        self.execution_history.append({
            "attempt": self.attempt_count,
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "error": error,
            "duration": (datetime.utcnow() - self.started_at).total_seconds()
        })

class BusinessWorkflow:
    """Enterprise business workflow with dependency management and monitoring"""
    
    def __init__(
        self,
        workflow_id: str,
        name: str,
        description: str,
        priority: WorkflowPriority = WorkflowPriority.NORMAL,
        metadata: Dict[str, Any] = None
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.priority = priority
        self.metadata = metadata or {}
        
        # Workflow components
        self.steps: Dict[str, WorkflowStep] = {}
        self.context = WorkflowContext(workflow_id)
        
        # Execution state
        self.status = ProcessStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.total_duration = None
        
        # Execution tracking
        self.execution_order: List[str] = []
        self.failed_steps: List[str] = []
        self.completed_steps: List[str] = []
    
    def add_step(self, step: WorkflowStep) -> None:
        """Add step to workflow"""
        if step.step_id in self.steps:
            raise ValueError(f"Step {step.step_id} already exists in workflow")
        
        self.steps[step.step_id] = step
        logger.info(f"Added step {step.step_id} to workflow {self.workflow_id}")
    
    def add_steps(self, steps: List[WorkflowStep]) -> None:
        """Add multiple steps to workflow"""
        for step in steps:
            self.add_step(step)
    
    async def execute(self, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute workflow with dependency management"""
        logger.info(f"Starting execution of workflow {self.workflow_id}: {self.name}")
        
        self.status = ProcessStatus.RUNNING
        self.started_at = datetime.utcnow()
        
        # Initialize context
        if initial_context:
            self.context.data.update(initial_context)
        
        try:
            # Resolve execution order based on dependencies
            self.execution_order = self._resolve_dependencies()
            logger.info(f"Execution order: {self.execution_order}")
            
            # Execute steps in order
            for step_id in self.execution_order:
                step = self.steps[step_id]
                
                try:
                    # Execute step
                    result = await step.execute(self.context)
                    
                    # Store result in context
                    self.context.data[f"step_{step_id}_result"] = result
                    self.completed_steps.append(step_id)
                    
                    logger.info(f"Step {step_id} completed in workflow {self.workflow_id}")
                    
                except Exception as e:
                    self.failed_steps.append(step_id)
                    error_msg = f"Step {step_id} failed: {str(e)}"
                    logger.error(error_msg)
                    
                    # Check if failure should stop workflow
                    if step.metadata.get("critical", True):
                        self.status = ProcessStatus.FAILED
                        return self._build_result(error=error_msg)
            
            # All steps completed successfully
            self.status = ProcessStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            self.total_duration = (self.completed_at - self.started_at).total_seconds()
            
            logger.info(f"Workflow {self.workflow_id} completed successfully in {self.total_duration:.2f}s")
            return self._build_result()
            
        except Exception as e:
            self.status = ProcessStatus.FAILED
            self.completed_at = datetime.utcnow()
            self.total_duration = (self.completed_at - self.started_at).total_seconds()
            
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(error_msg)
            return self._build_result(error=error_msg)
    
    def _resolve_dependencies(self) -> List[str]:
        """Resolve step execution order based on dependencies"""
        # Topological sort for dependency resolution
        visited = set()
        temp_visited = set()
        execution_order = []
        
        def visit(step_id: str):
            if step_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving step {step_id}")
            if step_id in visited:
                return
            
            temp_visited.add(step_id)
            
            # Visit dependencies first
            for dep_id in self.steps[step_id].dependencies:
                if dep_id not in self.steps:
                    raise ValueError(f"Step {step_id} depends on non-existent step {dep_id}")
                visit(dep_id)
            
            temp_visited.remove(step_id)
            visited.add(step_id)
            execution_order.append(step_id)
        
        # Visit all steps
        for step_id in self.steps:
            if step_id not in visited:
                visit(step_id)
        
        return execution_order
    
    def _build_result(self, error: str = None) -> Dict[str, Any]:
        """Build workflow execution result"""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_duration": self.total_duration,
            "steps_completed": len(self.completed_steps),
            "steps_failed": len(self.failed_steps),
            "execution_order": self.execution_order,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "context_data": self.context.data,
            "error": error,
            "step_details": {
                step_id: {
                    "status": step.status.value,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "attempt_count": step.attempt_count,
                    "error": step.error
                }
                for step_id, step in self.steps.items()
            }
        }
    
    async def pause(self) -> None:
        """Pause workflow execution"""
        if self.status == ProcessStatus.RUNNING:
            self.status = ProcessStatus.PAUSED
            logger.info(f"Workflow {self.workflow_id} paused")
    
    async def resume(self) -> None:
        """Resume paused workflow execution"""
        if self.status == ProcessStatus.PAUSED:
            self.status = ProcessStatus.RUNNING
            logger.info(f"Workflow {self.workflow_id} resumed")
    
    async def cancel(self) -> None:
        """Cancel workflow execution"""
        self.status = ProcessStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        self.total_duration = (self.completed_at - self.started_at).total_seconds() if self.started_at else 0
        logger.info(f"Workflow {self.workflow_id} cancelled")

class WorkflowEngine(BaseService):
    """Enterprise workflow orchestration engine"""
    
    def __init__(self, name: str = "workflow_engine"):
        super().__init__(name)
        self.active_workflows: Dict[str, BusinessWorkflow] = {}
        self.workflow_history: List[Dict[str, Any]] = []
        self.execution_queue: List[str] = []
        self.max_concurrent_workflows = 10
        
    async def initialize(self) -> bool:
        """Initialize workflow engine"""
        try:
            logger.info("Initializing workflow engine")
            
            # Initialize workflow storage and monitoring
            self._health_status = "healthy"
            self._initialized = True
            
            logger.info("Workflow engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize workflow engine: {e}")
            self._health_status = "unhealthy"
            return False
    
    async def create_workflow(
        self,
        name: str,
        description: str,
        steps: List[WorkflowStep],
        priority: WorkflowPriority = WorkflowPriority.NORMAL,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create new business workflow"""
        workflow_id = str(uuid.uuid4())
        
        workflow = BusinessWorkflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            priority=priority,
            metadata=metadata
        )
        
        # Add steps to workflow
        workflow.add_steps(steps)
        
        # Store workflow
        self.active_workflows[workflow_id] = workflow
        
        logger.info(f"Created workflow {workflow_id}: {name} with {len(steps)} steps")
        return workflow_id
    
    async def execute_workflow(
        self,
        workflow_id: str,
        initial_context: Dict[str, Any] = None,
        background: bool = False
    ) -> Union[Dict[str, Any], str]:
        """Execute workflow synchronously or asynchronously"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        
        if background:
            # Execute asynchronously
            asyncio.create_task(self._execute_workflow_async(workflow, initial_context))
            return {"status": "execution_started", "workflow_id": workflow_id}
        else:
            # Execute synchronously
            return await workflow.execute(initial_context)
    
    async def _execute_workflow_async(self, workflow: BusinessWorkflow, initial_context: Dict[str, Any] = None):
        """Execute workflow asynchronously"""
        try:
            result = await workflow.execute(initial_context)
            
            # Move to history
            self.workflow_history.append(result)
            
            # Clean up from active workflows
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]
                
        except Exception as e:
            logger.error(f"Async workflow execution failed: {e}")
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return workflow._build_result()
        
        # Check history
        for result in self.workflow_history:
            if result["workflow_id"] == workflow_id:
                return result
        
        raise ValueError(f"Workflow {workflow_id} not found")
    
    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows"""
        return [
            {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "priority": workflow.priority.value,
                "created_at": workflow.created_at.isoformat(),
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None
            }
            for workflow in self.active_workflows.values()
        ]
    
    async def pause_workflow(self, workflow_id: str) -> None:
        """Pause workflow execution"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        await self.active_workflows[workflow_id].pause()
    
    async def resume_workflow(self, workflow_id: str) -> None:
        """Resume workflow execution"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        await self.active_workflows[workflow_id].resume()
    
    async def cancel_workflow(self, workflow_id: str) -> None:
        """Cancel workflow execution"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        await self.active_workflows[workflow_id].cancel()
    
    async def health_check(self) -> Dict[str, Any]:
        """Workflow engine health check"""
        return {
            "service": self.name,
            "status": self._health_status,
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len(self.workflow_history),
            "uptime_seconds": self.uptime
        }
    
    async def shutdown(self) -> None:
        """Graceful shutdown of workflow engine"""
        logger.info("Shutting down workflow engine")
        
        # Cancel all active workflows
        for workflow_id in list(self.active_workflows.keys()):
            await self.cancel_workflow(workflow_id)
        
        await super().shutdown()
        logger.info("Workflow engine shut down gracefully")
