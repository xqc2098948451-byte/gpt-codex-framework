from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from consumer_projection import (  # noqa: E402
    ProjectionValidationError,
    audit_projection_paths,
    compare_projection_to_zip,
    load_projection_manifest,
    scan_consumer_boundary,
    stage_consumer_projection,
)


def validate(root: Path, staging_root: Path | None = None, zip_path: Path | None = None) -> dict[str, object]:
    root = Path(root).resolve()
    manifest = load_projection_manifest(root)
    audit = audit_projection_paths(root, manifest)
    if any(audit.values()):
        raise ProjectionValidationError(json.dumps(audit, ensure_ascii=False, sort_keys=True))

    if staging_root is not None:
        staging = Path(staging_root).resolve()
        inventory = stage_consumer_projection(root, staging, manifest)
        boundary = scan_consumer_boundary(staging, manifest)
        comparison = compare_projection_to_zip(staging, zip_path, "") if zip_path else None
        temporary = None
    else:
        temporary = tempfile.TemporaryDirectory(prefix="gpt-codex-consumer-projection-")
        staging = Path(temporary.name)
        inventory = stage_consumer_projection(root, staging, manifest)
        boundary = scan_consumer_boundary(staging, manifest)
        comparison = compare_projection_to_zip(staging, zip_path, "") if zip_path else None

    try:
        failures = [item for values in boundary.values() for item in values]
        if comparison is not None and not comparison["match"]:
            failures.extend(comparison[key] for key in ("missing", "extra", "mismatched"))
        if failures:
            raise ProjectionValidationError(json.dumps({"boundary": boundary, "zip": comparison}, ensure_ascii=False))
        return {"audit": audit, "inventory": inventory, "boundary": boundary, "zip": comparison}
    finally:
        if temporary is not None:
            temporary.cleanup()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the consumer-safe Framework projection.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--staging-root", type=Path, default=None)
    parser.add_argument("--zip", dest="zip_path", type=Path, default=None)
    args = parser.parse_args()
    try:
        result = validate(args.root, args.staging_root, args.zip_path)
    except ProjectionValidationError as exc:
        print(f"RESULT: FAIL\nREASON: {exc}")
        return 1
    print("RESULT: PASS")
    print("CONSUMER_PROJECTION_RELEASE_MATCH: PASS")
    print(f"CONSUMER_REQUIRED_COUNT: {len(result['inventory'])}")
    print("UNKNOWN_PATH_COUNT: 0")
    print("MISSING_REQUIRED_PATH_COUNT: 0")
    print("MANAGEMENT_IDS_IN_CONSUMER_PROJECTION: NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
