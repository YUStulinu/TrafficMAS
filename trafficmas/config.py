"""Loading scenario and experiment files."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_yaml(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_absolute() and not p.exists():
        p = ROOT / p
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_scenario(path: str | Path) -> dict:
    cfg = load_yaml(path)
    cfg.setdefault("name", Path(path).stem)
    return cfg
