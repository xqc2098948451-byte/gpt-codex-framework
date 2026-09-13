from __future__ import annotations

from dataclasses import dataclass
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse


@dataclass(frozen=True)
class RepositoryBinding:
    repository_id: str
    repository_full_name: str
    default_branch: str


@dataclass(frozen=True)
class ObservedRepository:
    repository_id: str
    repository_full_name: str | None
    local_remote_name: str
    canonical_remote: str


@dataclass(frozen=True)
class BindingDecision:
    decision: str
    reason: str
    identity_match: bool
    mutation_allowed: bool


_FULL_NAME = re.compile(r"^[^/\s]+/[^/\s]+$")


def canonicalize_remote_url(url: str) -> str:
    """Return a provider-qualified GitHub repository target, never an ID."""
    value = str(url).strip()
    if not value:
        raise ValueError("remote URL is empty")
    host = ""
    path = ""
    if value.startswith("git@") and ":" in value:
        user_host, path = value.split(":", 1)
        host = user_host.split("@", 1)[1]
    else:
        parsed = urlparse(value)
        if parsed.scheme not in {"https", "http", "ssh"}:
            raise ValueError("unsupported remote URL")
        host = parsed.hostname or ""
        path = parsed.path
    if host.lower() != "github.com":
        raise ValueError("remote is not GitHub")
    path = path.strip().strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    if not _FULL_NAME.fullmatch(path):
        raise ValueError("malformed GitHub repository path")
    owner, name = path.split("/", 1)
    return f"github:{owner}/{name}"


def _binding_from_control(control: Mapping[str, Any]) -> RepositoryBinding | None:
    github = control.get("github")
    if not isinstance(github, Mapping):
        return None
    values = [github.get(key) for key in ("repository_id", "repository_full_name", "default_branch")]
    if not all(isinstance(value, str) and value.strip() for value in values):
        return None
    return RepositoryBinding(*(value.strip() for value in values))


def compare_repository_binding(control: Mapping[str, Any], observed: ObservedRepository) -> BindingDecision:
    github = control.get("github")
    if not isinstance(github, Mapping):
        return BindingDecision("DENY", "GITHUB_REPOSITORY_UNBOUND", False, False)
    binding = _binding_from_control(control)
    if binding is None:
        return BindingDecision("DENY", "REPOSITORY_CONFLICT", False, False)
    if str(observed.repository_id) != binding.repository_id:
        return BindingDecision("DENY", "GITHUB_REPOSITORY_MISMATCH", False, False)
    if (
        observed.repository_full_name not in (None, "")
        and str(observed.repository_full_name).strip() != binding.repository_full_name
    ):
        return BindingDecision("DENY", "GITHUB_REPOSITORY_MISMATCH", False, False)
    return BindingDecision("ALLOW", "GITHUB_REPOSITORY_ID_MATCH", True, True)


def _git(repo_root: Path, *args: str) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True, check=False)
    except OSError as exc:
        return 127, "", str(exc)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def scan_repository_compatibility(repo_root: Path, github_metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    """Read-only compatibility classification; never edits Git or CONTROL."""
    root = Path(repo_root)
    code, _, _ = _git(root, "rev-parse", "--is-inside-work-tree")
    if code != 0:
        return {"classification": "LOCAL_GIT_ONLY", "git_available": False, "mutated": False}
    _, remotes_text, _ = _git(root, "remote")
    remotes = [line for line in remotes_text.splitlines() if line]
    if not remotes:
        return {"classification": "LOCAL_GIT_ONLY", "git_available": True, "mutated": False}
    metadata = github_metadata or {}
    configured_id = metadata.get("repository_id") if isinstance(metadata, Mapping) else None
    observed = metadata.get("observed_repository_id") if isinstance(metadata, Mapping) else None
    if len(remotes) > 1 and not metadata.get("selected_remote_name"):
        return {"classification": "MULTIPLE_REMOTE_REVIEW_REQUIRED", "remotes": remotes, "mutated": False}
    remote_name = metadata.get("selected_remote_name", remotes[0])
    _, url, _ = _git(root, "remote", "get-url", str(remote_name))
    try:
        canonical = canonicalize_remote_url(url)
    except ValueError:
        return {"classification": "NON_GITHUB_REMOTE", "remote_name": remote_name, "mutated": False}
    if not configured_id:
        return {"classification": "GITHUB_BINDING_REQUIRED", "canonical_remote": canonical, "mutated": False}
    if observed is not None and str(observed) != str(configured_id):
        return {"classification": "REPOSITORY_CONFLICT", "canonical_remote": canonical, "mutated": False}
    return {"classification": "ALREADY_BOUND", "canonical_remote": canonical, "remote_name": remote_name, "mutated": False}
