#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ARCHIVE_NAME = re.compile(r"^gpt-codex-framework-v(?P<version>\d+\.\d+(?:\.\d+)?)-bootstrap\.zip$")
INDEX_SCHEMA_VERSION = 1


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _version_key(value: str) -> tuple[int, int, int]:
    parts = [int(x) for x in value.split(".")]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_release_index(releases_dir: Path) -> dict:
    releases_dir = Path(releases_dir)
    index_path = releases_dir / "INDEX.json"
    if not index_path.exists():
        return {
            "schema_version": INDEX_SCHEMA_VERSION,
            "archive_policy": "METADATA_ONLY",
            "latest_recorded_version": None,
            "releases": [],
        }
    return json.loads(index_path.read_text(encoding="utf-8"))


def _record_summary(record: dict) -> dict:
    summary = {
        "version": record["version"],
        "artifact": record["artifact"],
        "record": f"records/v{record['version']}.json",
    }
    if "artifact_sha256" in record:
        summary["artifact_sha256"] = record["artifact_sha256"]
    summary.update(
        {
            "archive_policy": record["archive_policy"],
            "record_status": record["record_status"],
        }
    )
    return summary


def upsert_release_record(releases_dir: Path, record: dict) -> dict:
    releases_dir = Path(releases_dir)
    records_dir = releases_dir / "records"
    _write_json(records_dir / f"v{record['version']}.json", record)

    index = load_release_index(releases_dir)
    summaries = [item for item in index.get("releases", []) if item.get("version") != record["version"]]
    summaries.append(_record_summary(record))
    summaries.sort(key=lambda item: _version_key(item["version"]))
    index.update(
        {
            "schema_version": INDEX_SCHEMA_VERSION,
            "archive_policy": "METADATA_ONLY",
            "latest_recorded_version": summaries[-1]["version"] if summaries else None,
            "releases": summaries,
        }
    )
    _write_json(releases_dir / "INDEX.json", index)
    return record


def archive_release_artifact(artifact_path: Path, releases_dir: Path) -> dict:
    artifact_path = Path(artifact_path).resolve()
    match = ARCHIVE_NAME.fullmatch(artifact_path.name)
    if not match:
        raise ValueError(f"unsupported release artifact name: {artifact_path.name}")
    if not artifact_path.is_file():
        raise FileNotFoundError(artifact_path)
    try:
        with zipfile.ZipFile(artifact_path) as zf:
            bad = zf.testzip()
            if bad is not None:
                raise ValueError(f"corrupt release archive member: {bad}")
    except zipfile.BadZipFile as exc:
        raise ValueError(f"invalid release ZIP: {artifact_path.name}") from exc
    version = match.group("version")
    record = {
        "version": version,
        "artifact": artifact_path.name,
        "artifact_sha256": hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
        "artifact_size_bytes": artifact_path.stat().st_size,
        "artifact_hash_location": "RECORDED_FROM_EXTERNAL_ARCHIVE",
        "kernel_version": None,
        "schema_version": None,
        "previous_version": None,
        "archive_policy": "METADATA_ONLY",
        "record_status": "IMPORTED_ARCHIVE",
        "recorded_at": _now_iso(),
        "source": "EXTERNAL_RELEASE_ARCHIVE",
    }
    return upsert_release_record(releases_dir, record)


def ensure_release_record(
    releases_dir: Path,
    version: str,
    kernel_version: str,
    schema_version: int,
    previous_version: str | None,
    artifact_sha256: str | None = None,
    artifact_size_bytes: int | None = None,
) -> dict:
    releases_dir = Path(releases_dir)
    record_path = releases_dir / "records" / f"v{version}.json"
    existing = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else {}
    record = {
        "version": version,
        "artifact": f"gpt-codex-framework-v{version}-bootstrap.zip",
        "artifact_sha256": artifact_sha256 if artifact_sha256 is not None else existing.get("artifact_sha256"),
        "artifact_size_bytes": artifact_size_bytes if artifact_size_bytes is not None else existing.get("artifact_size_bytes"),
        "artifact_hash_location": existing.get("artifact_hash_location", "EXTERNAL_RELEASE_SIDECAR"),
        "kernel_version": kernel_version,
        "schema_version": schema_version,
        "previous_version": previous_version,
        "archive_policy": "METADATA_ONLY",
        "record_status": "FRAMEWORK_RELEASE",
        "recorded_at": existing.get("recorded_at", _now_iso()),
        "source": "FRAMEWORK_SOURCE",
    }
    for key, value in existing.items():
        if key not in record:
            record[key] = value
    return upsert_release_record(releases_dir, record)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record release archive metadata without embedding release ZIPs.")
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--releases-dir", type=Path, required=True)
    args = parser.parse_args()
    record = archive_release_artifact(args.artifact, args.releases_dir)
    print("RESULT: PASS")
    print("VERSION:", record["version"])
    print("SHA256:", record["artifact_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
