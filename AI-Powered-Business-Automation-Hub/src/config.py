"""Application configuration and project paths."""

from dataclasses import dataclass, field
import os
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Settings:
    """Runtime settings with safe, local defaults for demo mode."""

    project_root: Path | None = None
    database_name: str | None = None
    log_level: str | None = None
    demo_mode: bool | None = None
    ai_provider: str | None = None
    integration_simulation_mode: bool | None = None
    enable_webhook_delivery: bool | None = None
    output_directory: Path | None = None
    data_input_dir: Path = field(init=False)
    data_output_dir: Path = field(init=False)
    database_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    database_path: Path = field(init=False)

    def __post_init__(self) -> None:
        load_dotenv()
        self.project_root = Path(
            self.project_root
            or os.getenv("AUTOMATION_HUB_ROOT")
            or Path(__file__).resolve().parents[1]
        ).resolve()
        self.database_name = self.database_name or os.getenv(
            "AUTOMATION_HUB_DB_NAME", "automation_hub.db"
        )
        self.log_level = (self.log_level or os.getenv("AUTOMATION_HUB_LOG_LEVEL", "INFO")).upper()
        self.demo_mode = self._parse_bool(
            self.demo_mode if self.demo_mode is not None else os.getenv("DEMO_MODE"),
            default=True,
        )
        self.ai_provider = self.ai_provider or os.getenv("AI_PROVIDER", "demo")
        self.integration_simulation_mode = self._parse_bool(
            self.integration_simulation_mode
            if self.integration_simulation_mode is not None
            else os.getenv("INTEGRATION_SIMULATION_MODE"),
            default=True,
        )
        self.enable_webhook_delivery = self._parse_bool(
            self.enable_webhook_delivery
            if self.enable_webhook_delivery is not None
            else os.getenv("ENABLE_WEBHOOK_DELIVERY"),
            default=False,
        )

        self.data_input_dir = self.project_root / "data" / "input"
        self.data_output_dir = self.project_root / "data" / "output"
        self.database_dir = self.project_root / "database"
        self.logs_dir = self.project_root / "logs"
        configured_output = self.output_directory or os.getenv("OUTPUT_DIRECTORY")
        self.output_directory = Path(configured_output) if configured_output else self.project_root / "data" / "output"
        if not self.output_directory.is_absolute():
            self.output_directory = self.project_root / self.output_directory
        self.database_path = self.database_dir / self.database_name
        self.create_directories()

    def create_directories(self) -> None:
        """Create directories required by the application."""
        for directory in (
            self.data_input_dir,
            self.data_output_dir,
            self.database_dir,
            self.logs_dir,
            self.output_directory,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _parse_bool(value: bool | str | None, default: bool) -> bool:
        """Parse common environment boolean values with a safe default."""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return value.strip().lower() in {"1", "true", "yes", "on"}
