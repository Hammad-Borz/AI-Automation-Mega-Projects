"""Shared FastAPI service dependencies."""

from functools import lru_cache

from ..config import Settings
from ..analytics import AnalyticsService
from ..database_manager import DatabaseManager
from ..workflow import Workflow


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide application settings."""
    return Settings()


@lru_cache
def get_database_manager() -> DatabaseManager:
    """Return an initialized process-wide database manager."""
    manager = DatabaseManager(get_settings())
    manager.initialize()
    return manager


@lru_cache
def get_workflow() -> Workflow:
    """Return the process-wide workflow service."""
    return Workflow(get_database_manager())


@lru_cache
def get_analytics_service() -> AnalyticsService:
    """Return the process-wide analytics service."""
    return AnalyticsService(get_database_manager())
