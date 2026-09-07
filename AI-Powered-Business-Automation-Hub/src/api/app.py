"""FastAPI application for the automation hub."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ..exceptions import AutomationHubError, DatabaseError, DuplicateTaskError, WorkflowError
from .routes import router
from .schemas import ErrorResponse


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AI-Powered Business Automation Hub",
        description="A local REST API over the structured business automation workflow.",
        version="6.0.0",
    )
    app.include_router(router)

    @app.exception_handler(AutomationHubError)
    async def handle_application_error(request: Request, error: AutomationHubError) -> JSONResponse:
        """Map expected domain errors to a safe client error."""
        if isinstance(error, DuplicateTaskError):
            return JSONResponse(
                status_code=409,
                content={"error": "duplicate_task", "detail": "A task with this ID already exists."},
            )
        if isinstance(error, DatabaseError):
            return JSONResponse(
                status_code=500,
                content={"error": "database_error", "detail": "The task could not be processed."},
            )
        if isinstance(error, WorkflowError):
            return JSONResponse(
                status_code=400,
                content={"error": "workflow_error", "detail": "Task processing failed."},
            )
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(error="application_error", detail=str(error)).model_dump()
            if hasattr(ErrorResponse, "model_dump")
            else ErrorResponse(error="application_error", detail=str(error)).dict(),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(request: Request, error: RequestValidationError) -> JSONResponse:
        """Return structured request validation errors without a traceback."""
        return JSONResponse(
            status_code=422,
            content={"error": "request_validation_error", "detail": error.errors()},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
        """Return a generic response for unexpected failures."""
        logging.getLogger("automation_hub").exception("Unhandled API error", exc_info=error)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "detail": "An unexpected error occurred."},
        )

    return app


app = create_app()
