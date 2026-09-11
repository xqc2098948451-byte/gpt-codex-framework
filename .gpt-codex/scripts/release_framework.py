#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from kernel_rules import KERNEL_VERSION, SCHEMA_VERSION
from consumer_projection import (
    ProjectionValidationError,
    compare_projection_to_zip,
    load_projection_manifest,
    scan_consumer_boundary,
    stage_consumer_projection,
)
from release_archive import ensure_release_record, load_release_index

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
EXCLUDED_PARTS = {".git", "dist", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".idea", ".vscode"}
EXCLUDED_NAMES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip", ".sha256"}
EXCLUDED_RELATIVE_PATHS = {
    PurePosixPath(".gpt-codex/CONTROL.json"),
    PurePosixPath(".gpt-codex/STATE.json"),
    PurePosixPath(".gitignore"),
}
VERSIONED_FRAMEWORK_FOLDER = re.compile(
    r"^gpt-codex-framework-v\d+(?:\.\d+){1,2}(?:-[0-9A-Za-z.-]+)?-bootstrap$"
)


def read_version(root: Path) -> str:
    value = (Path(root) / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(value):
        raise ValueError(f"VERSION must be SemVer, got: {value!r}")
    return value


def artifact_basename(version: str) -> str:
    if not SEMVER.fullmatch(version):
        raise ValueError(f"invalid SemVer: {version!r}")
    return f"gpt-codex-framework-v{version}-bootstrap"


def should_exclude(relative_path: Path) -> bool:
    p = PurePosixPath(relative_path.as_posix())
    if p in EXCLUDED_RELATIVE_PATHS:
        return True
    if len(p.parts) >= 2 and p.parts[:2] == (".gpt-codex", "evidence"):
        return True
    if any(part in EXCLUDED_PARTS for part in p.parts):
        return True
    if any(VERSIONED_FRAMEWORK_FOLDER.fullmatch(part) for part in p.parts):
        return True
    if p.name in EXCLUDED_NAMES:
        return True
    if any(p.name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
        return True
    return False


def collect_files(root: Path) -> list[Path]:
    root = Path(root)
    return sorted(
        (p for p in root.rglob("*") if p.is_file() and not should_exclude(p.relative_to(root))),
        key=lambda p: p.relative_to(root).as_posix(),
    )


def _zip_write_deterministic(zf: zipfile.ZipFile, source: Path, archive_name: str) -> None:
    info = zipfile.ZipInfo(archive_name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o755 if source.stat().st_mode & 0o111 else 0o644) << 16
    zf.writestr(info, source.read_bytes())


def clean_output_dir(output_dir: Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    patterns = (
        "gpt-codex-framework-v*-bootstrap.zip",
        "gpt-codex-framework-v*-bootstrap.zip.sha256",
        "gpt-codex-framework-v*-release.json",
    )
    for pattern in patterns:
        for path in output_dir.glob(pattern):
            if path.is_file():
                path.unlink()


def _previous_recorded_version(releases_dir: Path, current_version: str) -> str | None:
    index = load_release_index(releases_dir)
    versions = [item.get("version") for item in index.get("releases", []) if item.get("version") != current_version]
    versions = [v for v in versions if v]
    if not versions:
        return None
    def key(v: str):
        parts = [int(x) for x in v.split(".")]
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])
    return sorted(versions, key=key)[-1]

def package_release(
    root: Path,
    output_dir: Path,
    kernel_version: str,
    schema_version: int,
    validation_summary: dict[str, str],
) -> dict[str, str]:
    root = Path(root).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    version = read_version(root)
    base = artifact_basename(version)
    zip_path = output_dir / f"{base}.zip"
    sha_path = output_dir / f"{base}.zip.sha256"
    manifest_path = output_dir / f"gpt-codex-framework-v{version}-release.json"

    manifest = load_projection_manifest(root)
    with tempfile.TemporaryDirectory(prefix="gpt-codex-consumer-projection-") as temp:
        staging_root = Path(temp)
        files = stage_consumer_projection(root, staging_root, manifest)
        boundary = scan_consumer_boundary(staging_root, manifest)
        boundary_failures = [item for values in boundary.values() for item in values]
        if boundary_failures:
            raise ProjectionValidationError(json.dumps(boundary, ensure_ascii=False, sort_keys=True))
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for relative in files:
                source = staging_root / Path(*PurePosixPath(relative).parts)
                _zip_write_deterministic(source=source, zf=zf, archive_name=f"{base}/{relative}")
            bad = zf.testzip()
            if bad is not None:
                raise RuntimeError(f"ZIP integrity failure at {bad}")
        comparison = compare_projection_to_zip(staging_root, zip_path, base)
        if not comparison["match"]:
            raise ProjectionValidationError(json.dumps(comparison, ensure_ascii=False, sort_keys=True))

    sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    sha_path.write_text(f"{sha256}  {zip_path.name}\n", encoding="utf-8")
    validation = dict(validation_summary)
    validation["zip_integrity"] = "PASS"
    validation["release_hygiene"] = "PASS"
    manifest = {
        "framework_version": version,
        "kernel_version": kernel_version,
        "schema_version": schema_version,
        "artifact": zip_path.name,
        "sha256": sha256,
        "validation": validation,
        "file_count": len(files),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "zip_path": str(zip_path),
        "sha256_path": str(sha_path),
        "manifest_path": str(manifest_path),
        "sha256": sha256,
    }


def _run(command: list[str], cwd: Path) -> None:
    proc = subprocess.run(command, cwd=cwd, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"validation command failed: {' '.join(command)}")


def validate_release_source(root: Path) -> dict[str, str]:
    root = Path(root).resolve()
    version = read_version(root)
    index_path = root / ".gpt-codex" / "builtins" / "INDEX.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if index.get("framework_version") != version:
        raise RuntimeError(
            f"framework version mismatch: VERSION={version}, builtins/INDEX.json={index.get('framework_version')}"
        )
    changelog = (root / ".gpt-codex" / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## v{version}" not in changelog:
        raise RuntimeError(f"CHANGELOG missing release heading for v{version}")
    _run([sys.executable, ".gpt-codex/scripts/validate_framework.py"], root)
    _run([sys.executable, "-m", "unittest", "discover", "-s", ".gpt-codex/tests", "-p", "test_*.py"], root)
    return {"framework": "PASS", "tests": "PASS", "release_hygiene": "PASS"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and package a GPT–Codex Framework release.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = (args.output_dir or root / "dist").resolve()
    releases_dir = root / "releases"
    current_version = read_version(root)
    previous_version = _previous_recorded_version(releases_dir, current_version)
    ensure_release_record(releases_dir, current_version, KERNEL_VERSION, SCHEMA_VERSION, previous_version)
    validation = validate_release_source(root)
    clean_output_dir(output_dir)
    result = package_release(root, output_dir, KERNEL_VERSION, SCHEMA_VERSION, validation)
    ensure_release_record(
        releases_dir,
        current_version,
        KERNEL_VERSION,
        SCHEMA_VERSION,
        previous_version,
        artifact_sha256=result["sha256"],
        artifact_size_bytes=Path(result["zip_path"]).stat().st_size,
    )
    print("RESULT: PASS")
    print("ARTIFACT:", result["zip_path"])
    print("SHA256:", result["sha256"])
    print("MANIFEST:", result["manifest_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
