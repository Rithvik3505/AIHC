from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.registries.taxonomy_sync import TaxonomyRegistryDriftError, check_registry, write_registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize taxonomy_registry.json from executable taxonomy.py")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write deterministic registry output")
    mode.add_argument("--check", action="store_true", help="check registry drift without writing")
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=None,
        help="optional registry path for validation tests; defaults to backend/registries/taxonomy_registry.json",
    )
    args = parser.parse_args()
    try:
        if args.write:
            write_registry(args.registry_path) if args.registry_path else write_registry()
            print("taxonomy registry synchronized")
        else:
            check_registry(args.registry_path) if args.registry_path else check_registry()
            print("taxonomy registry is synchronized")
    except TaxonomyRegistryDriftError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"taxonomy registry synchronization failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
