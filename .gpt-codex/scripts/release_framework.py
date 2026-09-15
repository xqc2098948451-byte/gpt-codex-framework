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
from typing import Any, Mapping

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
from release_archive import _version_key, ensure_release_record, load_release_index

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
_IMMUTABLE_SHA = re.compile(r"^[0-9a-fA-F]{40}$")
_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
_REQUIRED_PUBLICATION_CAPABILITIES = ("TAG_WRITE", "RELEASE_WRITE", "ASSET_UPLOAD")


def read_version(root: Path) -> str:
    value = (Path(root) / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(value):
        raise ValueError(f"VERSION must be SemVer, got: {value!r}")
    return value


def artifact_basename(version: str) -> str:
    if not SEMVER.fullmatch(version):
        raise ValueError(f"invalid SemVer: {version!r}")
    return f"gpt-codex-framework-v{version}-bootstrap"


def _valid_canonical_artifact_ref(value: object, source_version: str | None = None) -> bool:
    if not isinstance(value, str) or value.count(":") != 1:
        return False
    revision, relative = value.split(":")
    if not _IMMUTABLE_SHA.fullmatch(revision) or not _valid_git_relative_path(relative):
        return False
    match = re.fullmatch(r"dist/gpt-codex-framework-v(.+)-bootstrap\.zip", relative)
    return bool(match and SEMVER.fullmatch(match.group(1)) and (source_version is None or match.group(1) == source_version))


def _valid_git_relative_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or any(char in value for char in "*?[]"):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and "." not in path.parts and ".." not in path.parts and path.as_posix() == value


def evaluate_publication_preflight(
    facts: Mapping[str, Any],
    required_capabilities: frozenset[str] = frozenset(_REQUIRED_PUBLICATION_CAPABILITIES),
) -> list[str]:
    facts = facts if isinstance(facts, Mapping) else {}
    errors: list[str] = []
    source_version = facts.get("source_version")
    if not isinstance(source_version, str) or not SEMVER.fullmatch(source_version) or facts.get("source_version_closed") is not True:
        errors.append("SOURCE_VERSION_NOT_CLOSED")
    for key, code in (
        ("projection_closed", "PROJECTION_NOT_CLOSED"),
        ("release_record_ready", "RELEASE_RECORD_NOT_READY"),
        ("canonical_lf_verified", "CANONICAL_LF_NOT_VERIFIED"),
        ("repository_identity_verified", "REPOSITORY_IDENTITY_NOT_VERIFIED"),
        ("work_main_ancestry_verified", "WORK_MAIN_ANCESTRY_NOT_VERIFIED"),
    ):
        if facts.get(key) is not True:
            errors.append(code)
    if facts.get("tag_conflict") is not False:
        errors.append("TAG_CONFLICT")
    if facts.get("release_conflict") is not False:
        errors.append("RELEASE_CONFLICT")
    if facts.get("publication_mechanism_available") is not True:
        errors.append("PUBLICATION_MECHANISM_UNAVAILABLE")
    if not _valid_canonical_artifact_ref(facts.get("canonical_artifact_ref"), source_version if isinstance(source_version, str) and SEMVER.fullmatch(source_version) else None):
        errors.append("CANONICAL_ARTIFACT_REF_INVALID")
    if not isinstance(facts.get("artifact_sha256"), str) or not _SHA256.fullmatch(facts["artifact_sha256"]):
        errors.append("ARTIFACT_SHA256_INVALID")
    size = facts.get("artifact_size_bytes")
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        errors.append("ARTIFACT_SIZE_INVALID")
    available = facts.get("available_capabilities")
    if not isinstance(available, (set, frozenset, list, tuple)) or not all(isinstance(item, str) for item in available):
        available = ()
    for capability in _REQUIRED_PUBLICATION_CAPABILITIES:
        if capability in required_capabilities and capability not in available:
            errors.append(f"MISSING_CAPABILITY_{capability}")
    return errors


def materialize_verified_git_artifact(
    root: Path,
    revision: str,
    relative_path: str,
    expected_sha256: str,
    expected_size_bytes: int,
    destination_dir: Path,
) -> Path:
    if not _IMMUTABLE_SHA.fullmatch(revision) or not _valid_git_relative_path(relative_path):
        raise ValueError("CANONICAL_ARTIFACT_REF_INVALID")
    if not isinstance(expected_sha256, str) or not _SHA256.fullmatch(expected_sha256):
        raise ValueError("ARTIFACT_SHA256_INVALID")
    if isinstance(expected_size_bytes, bool) or not isinstance(expected_size_bytes, int) or expected_size_bytes <= 0:
        raise ValueError("ARTIFACT_SIZE_INVALID")
    proc = subprocess.run(
        ["git", "show", f"{revision}:{relative_path}"], cwd=Path(root).resolve(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if proc.returncode != 0:
        raise ValueError("CANONICAL_ARTIFACT_LOOKUP_FAILED")
    data = proc.stdout
    if hashlib.sha256(data).hexdigest().lower() != expected_sha256.lower():
        raise ValueError("ARTIFACT_SHA256_MISMATCH")
    if len(data) != expected_size_bytes:
        raise ValueError("ARTIFACT_SIZE_MISMATCH")
    destination = Path(destination_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / PurePosixPath(relative_path).name
    if target.parent != destination:
        raise ValueError("CANONICAL_ARTIFACT_REF_INVALID")
    with target.open("xb") as artifact:
        artifact.write(data)
    return target


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
    return sorted(versions, key=_version_key)[-1]

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
    sha_path.write_bytes(f"{sha256}  {zip_path.name}\n".encode("utf-8"))
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
    manifest_path.write_bytes((json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
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
    return {"framework": "PASS", "tests": "PENDING", "release_hygiene": "PASS"}


def validate_release_artifact(root: Path) -> None:
    _run([sys.executable, "-m", "unittest", "discover", "-s", ".gpt-codex/tests", "-p", "test_*.py"], root)


def finalize_release_manifest(manifest_path: Path) -> None:
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validation = manifest.get("validation")
    if not isinstance(validation, dict) or validation.get("tests") != "PENDING":
        raise RuntimeError("release manifest must await artifact-dependent test validation")
    validation["tests"] = "PASS"
    manifest_path.write_bytes((json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


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
    validate_release_artifact(root)
    finalize_release_manifest(result["manifest_path"])
    print("RESULT: PASS")
    print("ARTIFACT:", result["zip_path"])
    print("SHA256:", result["sha256"])
    print("MANIFEST:", result["manifest_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
