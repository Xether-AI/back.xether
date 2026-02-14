"""Custom system exceptions."""

from typing import Any, Dict, Optional

class XetherError(Exception):
    """Base exception for all system errors."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

class ForbiddenError(XetherError):
    """Raised when access is denied."""
    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="FORBIDDEN", status_code=403, details=details)

class NotFoundError(XetherError):
    """Raised when a resource is not found."""
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            f"{resource} with id {resource_id} not found",
            code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "id": resource_id}
        )

class ValidationError(XetherError):
    """Raised on invalid input data."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_ERROR", status_code=400, details=details)

class ConflictError(XetherError):
    """Raised when there is a state conflict."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CONFLICT", status_code=409, details=details)
