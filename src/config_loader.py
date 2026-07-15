from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml


def load_settings(path: Union[str, Path, None] = None) -> Dict[str, Any]:
    """Load YAML settings from a file path and return a dictionary."""
    if path is None:
        path = Path(__file__).resolve().parents[1] / "config" / "settings.yaml"

    path = Path(path)
    with path.open("r", encoding="utf-8") as stream:
        contents = yaml.safe_load(stream)

    return contents if contents is not None else {}
