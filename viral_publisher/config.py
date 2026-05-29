from pathlib import Path

import yaml
from dotenv import load_dotenv


DEFAULT_CONFIG_PATH = Path("config.example.yaml")


def load_config(path: str | None = None) -> dict:
    load_dotenv()
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}
