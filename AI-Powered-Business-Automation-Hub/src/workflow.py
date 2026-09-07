"""Phase 1 business task workflow."""

from .database_manager import DatabaseManager
from .ai_analyzer import AIAnalyzer
from .action_executor import ActionExecutor
from .automation_rules import AutomationRulesEngine
from .integration_router import IntegrationRouter
from .exceptions import DuplicateTaskError, WorkflowError
from .logger import get_logger
from .models import AutomationResult, BusinessTask, ProcessingMetadata, TaskLifecycle, WorkflowStatus
from datetime import datetime, timezone
from .validators import validate_business_task


class Workflow:
    """Validate, analyze, and persist business tasks."""

    def __init__(
        self,
        database_manager: DatabaseManager,
        analyzer: AIAnalyzer | None = None,
        rules_engine: AutomationRulesEngine | None = None,
        action_executor: ActionExecutor | None = None,
    ) -> None:
        self.database_manager = database_manager
        self.analyzer = analyzer or AIAnalyzer(database_manager.settings)
        self.rules_engine = rules_engine or AutomationRulesEngine()
        self.logger = get_logger(log_directory=database_manager.settings.logs_dir)
        self.integration_router = IntegrationRouter(database_manager.settings, self.logger)
        self.action_executor = action_executor or ActionExecutor(self.logger, self.integration_router)

    def process(self, task: BusinessTask) -> AutomationResult:
        """Validate, analyze, plan, execute, and persist one business task."""
        processing_started_at: datetime | None = None
        try:
            self.logger.info("Task received: %s", task.task_id)
            validate_business_task(task)
            if self.database_manager.task_exists(task.task_id):
                raise DuplicateTaskError(f"Task ID '{task.task_id}' already exists.")
            self.database_manager.save_task(task)
            processing_started_at = datetime.now(timezone.utc)
            processing = ProcessingMetadata(
                lifecycle_status=TaskLifecycle.PROCESSING,
                processing_started_at=processing_started_at,
            )
            self.database_manager.save_processing(task.task_id, processing)
            analysis = self.analyzer.analyze(task)
            self.logger.info("Analysis completed: %s", task.task_id)
            self.database_manager.save_analysis(task.task_id, analysis)
            planned_actions = self.rules_engine.plan_actions(analysis)
            self.logger.info("Automation actions planned: %s", task.task_id)
            execution = self.action_executor.execute(
                task.task_id,
                planned_actions,
                task=task,
                analysis=analysis,
            )
            self.database_manager.save_actions(task.task_id, execution.actions)
            status = WorkflowStatus.COMPLETED if not execution.failed_actions else WorkflowStatus.FAILED
            completed_at = datetime.now(timezone.utc)
            processing = ProcessingMetadata(
                lifecycle_status=TaskLifecycle.COMPLETED if status is WorkflowStatus.COMPLETED else TaskLifecycle.FAILED,
                processing_started_at=processing_started_at,
                processing_completed_at=completed_at,
                processing_duration_ms=(completed_at - processing_started_at).total_seconds() * 1000
                if processing_started_at
                else None,
                failure_message="One or more actions failed." if execution.failed_actions else None,
            )
            self.database_manager.save_processing(task.task_id, processing, planned_actions, execution)
            return AutomationResult(
                task_id=task.task_id,
                status=status,
                message="Task validated, analyzed, executed, and stored successfully.",
                actions=["validated", "stored"],
                analysis=analysis,
                planned_actions=planned_actions,
                execution_result=execution,
                processing_metadata=processing,
            )
        except Exception as error:
            if processing_started_at is not None:
                completed_at = datetime.now(timezone.utc)
                failure = ProcessingMetadata(
                    lifecycle_status=TaskLifecycle.FAILED,
                    processing_started_at=processing_started_at,
                    processing_completed_at=completed_at,
                    processing_duration_ms=(completed_at - processing_started_at).total_seconds() * 1000,
                    failure_message="Task processing failed.",
                )
                try:
                    self.database_manager.save_processing(task.task_id, failure)
                except Exception:
                    self.logger.exception("Could not persist failure state for %s", task.task_id)
            self.logger.exception("Task processing failed: %s", task.task_id)
            if isinstance(error, DuplicateTaskError):
                raise
            if isinstance(error, WorkflowError):
                raise
            raise WorkflowError(f"Could not process task '{task.task_id}': {error}") from error
