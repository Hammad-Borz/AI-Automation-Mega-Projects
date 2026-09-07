from pathlib import Path

from src.config import Settings


def test_settings_create_required_directories(tmp_path):
    settings = Settings(project_root=tmp_path)

    assert settings.project_root == Path(tmp_path).resolve()
    assert settings.data_input_dir.is_dir()
    assert settings.data_output_dir.is_dir()
    assert settings.database_dir.is_dir()
    assert settings.logs_dir.is_dir()
    assert settings.database_path == settings.database_dir / "automation_hub.db"
