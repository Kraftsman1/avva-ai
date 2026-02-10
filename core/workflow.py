"""
Workflow Manager for Multi-Step Task Execution.

Handles breaking down complex user requests into sequential steps,
maintaining context across steps, and tracking execution progress.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid


class WorkflowStepStatus(Enum):
    """Status of individual workflow steps."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(Enum):
    """Overall workflow execution status."""
    CREATED = "created"
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Individual step in a workflow."""
    id: str
    description: str
    action: str  # What needs to be done
    intent: Optional[str] = None  # Skill intent to invoke
    arguments: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Step IDs this depends on
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "action": self.action,
            "intent": self.intent,
            "arguments": self.arguments,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "context": self.context,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class Workflow:
    """Complete workflow with multiple steps."""
    id: str
    title: str
    description: str
    original_request: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.CREATED
    current_step_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    global_context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "original_request": self.original_request,
            "steps": [step.to_dict() for step in self.steps],
            "status": self.status.value,
            "current_step_index": self.current_step_index,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "global_context": self.global_context,
        }

    def get_current_step(self) -> Optional[WorkflowStep]:
        """Get the currently executing step."""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def get_next_step(self) -> Optional[WorkflowStep]:
        """Get the next pending step to execute."""
        for i, step in enumerate(self.steps):
            if step.status == WorkflowStepStatus.PENDING:
                # Check if dependencies are met
                if self._dependencies_met(step):
                    self.current_step_index = i
                    return step
        return None

    def _dependencies_met(self, step: WorkflowStep) -> bool:
        """Check if all dependencies for a step are completed."""
        for dep_id in step.dependencies:
            dep_step = next((s for s in self.steps if s.id == dep_id), None)
            if not dep_step or dep_step.status != WorkflowStepStatus.COMPLETED:
                return False
        return True

    def get_progress(self) -> Dict[str, Any]:
        """Calculate workflow progress statistics."""
        total = len(self.steps)
        completed = sum(1 for s in self.steps if s.status == WorkflowStepStatus.COMPLETED)
        failed = sum(1 for s in self.steps if s.status == WorkflowStepStatus.FAILED)
        in_progress = sum(1 for s in self.steps if s.status == WorkflowStepStatus.IN_PROGRESS)

        return {
            "total_steps": total,
            "completed_steps": completed,
            "failed_steps": failed,
            "in_progress_steps": in_progress,
            "progress_percent": (completed / total * 100) if total > 0 else 0,
        }


class WorkflowManager:
    """Manages workflow creation, execution, and state tracking."""

    def __init__(self):
        self.active_workflows: Dict[str, Workflow] = {}
        self.callbacks = []

    def add_callback(self, callback):
        """Add event callback for workflow updates."""
        self.callbacks.append(callback)

    def _emit(self, event_type: str, data: Dict[str, Any]):
        """Emit workflow event to callbacks."""
        for cb in self.callbacks:
            try:
                cb(event_type, data)
            except Exception as e:
                print(f"Error in workflow callback: {e}")

    def create_workflow(
        self,
        title: str,
        description: str,
        original_request: str,
        steps: List[Dict[str, Any]]
    ) -> Workflow:
        """
        Create a new workflow from a plan.

        Args:
            title: Workflow title
            description: Overall description
            original_request: User's original command
            steps: List of step definitions

        Returns:
            Created Workflow instance
        """
        workflow_id = str(uuid.uuid4())

        workflow_steps = []
        for i, step_data in enumerate(steps):
            step = WorkflowStep(
                id=step_data.get("id", f"step_{i}"),
                description=step_data.get("description", ""),
                action=step_data.get("action", ""),
                intent=step_data.get("intent"),
                arguments=step_data.get("arguments", {}),
                dependencies=step_data.get("dependencies", []),
            )
            workflow_steps.append(step)

        workflow = Workflow(
            id=workflow_id,
            title=title,
            description=description,
            original_request=original_request,
            steps=workflow_steps,
            status=WorkflowStatus.AWAITING_APPROVAL,
        )

        self.active_workflows[workflow_id] = workflow
        self._emit("workflow.created", {"workflow": workflow.to_dict()})

        return workflow

    def approve_workflow(self, workflow_id: str) -> bool:
        """Approve a workflow for execution."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False

        workflow.status = WorkflowStatus.EXECUTING
        workflow.started_at = datetime.now()
        self._emit("workflow.approved", {"workflow": workflow.to_dict()})
        return True

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False

        workflow.status = WorkflowStatus.CANCELLED
        self._emit("workflow.cancelled", {"workflow_id": workflow_id})
        return True

    def start_step(self, workflow_id: str, step_id: str) -> bool:
        """Mark a step as started."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False

        step = next((s for s in workflow.steps if s.id == step_id), None)
        if not step:
            return False

        step.status = WorkflowStepStatus.IN_PROGRESS
        step.started_at = datetime.now()

        self._emit("workflow.step_started", {
            "workflow_id": workflow_id,
            "step": step.to_dict(),
            "progress": workflow.get_progress(),
        })
        return True

    def complete_step(
        self,
        workflow_id: str,
        step_id: str,
        result: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mark a step as completed with result."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False

        step = next((s for s in workflow.steps if s.id == step_id), None)
        if not step:
            return False

        step.status = WorkflowStepStatus.COMPLETED
        step.result = result
        step.completed_at = datetime.now()

        if context:
            step.context.update(context)
            workflow.global_context.update(context)

        self._emit("workflow.step_completed", {
            "workflow_id": workflow_id,
            "step": step.to_dict(),
            "progress": workflow.get_progress(),
        })

        # Check if workflow is complete
        if all(s.status in [WorkflowStepStatus.COMPLETED, WorkflowStepStatus.SKIPPED] for s in workflow.steps):
            self._complete_workflow(workflow_id)

        return True

    def fail_step(
        self,
        workflow_id: str,
        step_id: str,
        error: str
    ) -> bool:
        """Mark a step as failed."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False

        step = next((s for s in workflow.steps if s.id == step_id), None)
        if not step:
            return False

        step.status = WorkflowStepStatus.FAILED
        step.error = error
        step.completed_at = datetime.now()

        self._emit("workflow.step_failed", {
            "workflow_id": workflow_id,
            "step": step.to_dict(),
            "error": error,
        })

        # Mark workflow as failed
        workflow.status = WorkflowStatus.FAILED
        self._emit("workflow.failed", {
            "workflow_id": workflow_id,
            "error": f"Step '{step.description}' failed: {error}",
        })

        return True

    def _complete_workflow(self, workflow_id: str):
        """Mark workflow as completed."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return

        workflow.status = WorkflowStatus.COMPLETED
        workflow.completed_at = datetime.now()

        self._emit("workflow.completed", {
            "workflow": workflow.to_dict(),
            "summary": self._generate_summary(workflow),
        })

    def _generate_summary(self, workflow: Workflow) -> str:
        """Generate a summary of workflow execution."""
        completed = sum(1 for s in workflow.steps if s.status == WorkflowStepStatus.COMPLETED)
        total = len(workflow.steps)

        summary = f"Completed {completed}/{total} steps:\n"
        for step in workflow.steps:
            status_icon = "✅" if step.status == WorkflowStepStatus.COMPLETED else "❌"
            summary += f"\n{status_icon} {step.description}"
            if step.result:
                summary += f"\n   Result: {step.result[:100]}..."

        return summary

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        return self.active_workflows.get(workflow_id)


# Singleton instance
workflow_manager = WorkflowManager()
