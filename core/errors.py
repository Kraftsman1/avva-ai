from typing import Any, Dict, Optional


class CoreErrorException(Exception):
    """Structured exception that can be serialized into a `core.error` payload."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        severity: str = "error",
        retry_allowed: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.severity = severity
        self.retry_allowed = retry_allowed
        self.context = context or {}


class BrainManagerError(CoreErrorException):
    """Structured error for Brain manager operations."""

    pass
