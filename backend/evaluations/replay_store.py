from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


REPLAY_DIR = Path(__file__).resolve().parent / "replays"
REPLAY_DIR.mkdir(parents=True, exist_ok=True)


def _json_default(value: Any) -> Any:
    if hasattr(value, "dict"):
        return value.dict()
    if hasattr(value, "value"):
        return value.value
    return str(value)


def write_replay(workflow_id: str, payload: dict[str, Any]) -> dict[str, str]:
    replay_id = f"{workflow_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    path = REPLAY_DIR / f"{replay_id}.json"
    replay = {
        "replay_id": replay_id,
        "workflow_id": workflow_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    path.write_text(json.dumps(replay, indent=2, default=_json_default), encoding="utf-8")
    return {"replay_id": replay_id, "path": str(path)}


def list_replays() -> list[dict[str, str]]:
    return [{"replay_id": path.stem, "path": str(path)} for path in sorted(REPLAY_DIR.glob("*.json"))]

