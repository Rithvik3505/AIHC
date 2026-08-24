from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


REGISTRY_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=16)
def load_registry(name: str) -> dict[str, Any]:
    path = REGISTRY_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def registry_items(name: str, key: str) -> list[dict[str, Any]]:
    payload = load_registry(name)
    value = payload.get(key, [])
    return value if isinstance(value, list) else []
