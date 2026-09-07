"""Shared pytest fixtures."""

import pytest

from src.config import Settings
from src.database_manager import DatabaseManager


@pytest.fixture
def settings(tmp_path):
    return Settings(
        project_root=tmp_path,
        database_name="test.db",
        demo_mode=True,
        ai_provider="demo",
    )


@pytest.fixture
def database(settings):
    manager = DatabaseManager(settings)
    manager.initialize()
    return manager
