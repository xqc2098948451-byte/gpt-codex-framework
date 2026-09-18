from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
import shutil
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


@dataclass(frozen=True)
class BoundedDiagnostic:
    command_identity: str
    process_started: bool
    exit_code: int | None
    stdout: str
    stderr: str
    stdout_truncated: bool
    stderr_truncated: bool
    completion: str


_FULL_NAME = re.compile(r"^[^/\s]+/[^/\s]+$")
_DIAGNOSTIC_LIMIT = 4096


def _bounded_text(value: object) -> tuple[str, bool]:
    text = value if isinstance(value, str) else ""
    return text[:_DIAGNOSTIC_LIMIT], len(text) > _DIAGNOSTIC_LIMIT


def _run_bounded_diagnostic(command: list[str], command_identity: str, *, runner: Any = subprocess.run, timeout: int = 5, **kwargs: Any) -> BoundedDiagnostic:
    """Run a probe without persisting argv or unbounded process output."""
    try:
        proc = runner(command, capture_output=True, text=True, check=False, timeout=timeout, **kwargs)
    except subprocess.TimeoutExpired as exc:
        stdout, out_cut = _bounded_text(exc.stdout)
        stderr, err_cut = _bounded_text(exc.stderr)
        return BoundedDiagnostic(command_identity, True, None, stdout, stderr, out_cut, err_cut, "INCOMPLETE")
    except OSError as exc:
        stderr, err_cut = _bounded_text(str(exc))
        return BoundedDiagnostic(command_identity, False, None, "", stderr, False, err_cut, "LAUNCH_FAILED")
    stdout, out_cut = _bounded_text(getattr(proc, "stdout", ""))
    stderr, err_cut = _bounded_text(getattr(proc, "stderr", ""))
    return BoundedDiagnostic(command_identity, True, getattr(proc, "returncode", None), stdout, stderr, out_cut, err_cut, "COMPLETE")


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
        return BindingDecision("DENY", "PROJECT_IDENTITY_INVALID", False, False)
    if str(observed.repository_id) != binding.repository_id:
        return BindingDecision("DENY", "GITHUB_REPOSITORY_MISMATCH", False, False)
    if (
        observed.repository_full_name not in (None, "")
        and str(observed.repository_full_name).strip() != binding.repository_full_name
    ):
        return BindingDecision("DENY", "GITHUB_REPOSITORY_MISMATCH", False, False)
    return BindingDecision("ALLOW", "GITHUB_REPOSITORY_ID_MATCH", True, True)


def repository_evidence_matches_identity(identity: Mapping[str, Any], evidence: Mapping[str, Any] | None) -> bool:
    """Verify supplied repository evidence against an already explicit identity."""
    if not isinstance(identity, Mapping) or not isinstance(evidence, Mapping):
        return False
    return (
        isinstance(identity.get("repository_id"), str)
        and isinstance(identity.get("repository_full_name"), str)
        and identity["repository_id"] == evidence.get("repository_id")
        and identity["repository_full_name"] == evidence.get("repository_full_name")
    )


def _git(repo_root: Path, *args: str) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="surrogateescape",
            check=False,
        )
    except OSError as exc:
        return 127, "", str(exc)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _bounded_version_probe(executable: str) -> tuple[int, str, str]:
    """Probe only a version line; never retain process environment or secret output."""
    try:
        diagnostic = _run_bounded_diagnostic([executable, "--version"], "VERSION_PROBE")
    except Exception:
        return 127, "", ""
    if diagnostic.exit_code is None:
        return 127, "", ""
    return diagnostic.exit_code, diagnostic.stdout.splitlines()[0][:256] if diagnostic.stdout else "", ""


def _read_only_remote_probe() -> bool:
    """Check Git remote reachability without prompting or mutating credentials."""
    try:
        proc = subprocess.run(
            ["git", "ls-remote", "--exit-code", "origin", "HEAD"], capture_output=True,
            text=True, check=False, timeout=5, env={"GIT_TERMINAL_PROMPT": "0"},
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0


def _command_observation(executable: str | None, version_probe: Any, available: str) -> dict[str, str]:
    if not executable:
        return {"status": "UNAVAILABLE" if available == "AVAILABLE" else "ABSENT"}
    try:
        code, stdout, _stderr = version_probe(executable)
    except Exception:
        return {"status": "UNAVAILABLE"}
    if not isinstance(code, int) or code != 0 or not isinstance(stdout, str):
        return {"status": "UNAVAILABLE"}
    return {"status": available, "version": stdout[:256]}


def _filesystem_path_round_trip(path: object) -> bool:
    """Observe the platform's actual path encode/decode behavior without I/O."""
    try:
        original = os.fspath(path)
        if not isinstance(original, str):
            return False
        decoded = os.fsdecode(os.fsencode(original))
        return os.path.normcase(os.path.normpath(decoded)) == os.path.normcase(os.path.normpath(original))
    except (TypeError, ValueError, UnicodeError):
        return False


def observe_execution_capabilities(
    *, executable_lookup: Any = shutil.which, version_probe: Any = _bounded_version_probe,
    remote_probe: Any = _read_only_remote_probe, path: object | None = None,
    path_probe: Any = _filesystem_path_round_trip,
) -> dict[str, Any]:
    """Return bounded, read-only A1 capability facts from injectable probes."""
    pwsh = executable_lookup("pwsh")
    powershell = _command_observation(pwsh, version_probe, "AVAILABLE")
    if powershell.get("status") == "AVAILABLE":
        powershell["status"] = "SUPPORTED" if re.search(r"PowerShell\s+7(?:\.|\b)", powershell.get("version", ""), re.I) else "UNSUPPORTED"
    observed = {
        "powershell": powershell,
        "python": _command_observation(executable_lookup("python"), version_probe, "AVAILABLE"),
        "git": _command_observation(executable_lookup("git"), version_probe, "AVAILABLE"),
        "gh": _command_observation(executable_lookup("gh"), version_probe, "AVAILABLE"),
    }
    if observed["gh"].get("status") == "UNAVAILABLE":
        observed["gh"]["status"] = "ABSENT"
    try:
        observed["remote"] = {"available": remote_probe() is True}
    except Exception:
        observed["remote"] = {"available": False}
    try:
        observed["unicode_path_round_trip"] = path_probe(Path.cwd() if path is None else path) is True
    except Exception:
        observed["unicode_path_round_trip"] = False
    return observed


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
    if github_metadata is not None and not isinstance(github_metadata, Mapping):
        return {"classification": "PROJECT_IDENTITY_INVALID", "mutated": False}
    metadata = github_metadata or {}
    configured_id = metadata.get("repository_id") if isinstance(metadata, Mapping) else None
    observed = metadata.get("observed_repository_id") if isinstance(metadata, Mapping) else None
    configured_full_name = metadata.get("repository_full_name")
    if (
        configured_id not in (None, "")
        and (not isinstance(configured_id, str) or not configured_id.strip())
    ) or (
        configured_full_name not in (None, "")
        and (not isinstance(configured_full_name, str) or not _FULL_NAME.fullmatch(configured_full_name.strip()))
    ):
        return {"classification": "PROJECT_IDENTITY_INVALID", "mutated": False}
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
        return {"classification": "GITHUB_REPOSITORY_MISMATCH", "canonical_remote": canonical, "mutated": False}
    return {"classification": "ALREADY_BOUND", "canonical_remote": canonical, "remote_name": remote_name, "mutated": False}
