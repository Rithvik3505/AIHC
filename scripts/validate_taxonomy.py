from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.taxonomy_engine.validation import validate_all


def main() -> int:
    issues = validate_all()
    if issues:
        print("taxonomy validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("taxonomy validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
