"""Custom exceptions used by the automation hub."""


class AutomationHubError(Exception):
    """Base exception for expected application errors."""


class ValidationError(AutomationHubError):
    """Raised when a business task fails validation."""


class DatabaseError(AutomationHubError):
    """Raised when a database operation cannot be completed."""


class DuplicateTaskError(AutomationHubError):
    """Raised when a task ID already exists."""


class WorkflowError(AutomationHubError):
    """Raised when workflow processing cannot be completed."""


class IngestionError(AutomationHubError):
    """Base exception for external input ingestion errors."""


class UnsupportedInputError(IngestionError):
    """Raised when an input format or file type is unsupported."""


class InputValidationError(IngestionError):
    """Raised when external input fails validation."""


class IntegrationError(AutomationHubError):
    """Base exception for integration-layer failures."""


class UnsupportedIntegrationError(IntegrationError):
    """Raised when no connector supports an action."""


class ConnectorExecutionError(IntegrationError):
    """Raised when a connector cannot execute an integration request."""
