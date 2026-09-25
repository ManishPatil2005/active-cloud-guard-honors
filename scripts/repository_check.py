"""Bounded documentation and Git-publication checks; never print secret values."""

from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "AGENTS.md",
    "RULES.md",
    "TASKS.md",
    "CHANGELOG.md",
    "README.md",
    "docs/INDEX.md",
    "docs/PRD.md",
    "docs/ARCHITECTURE.md",
    "docs/DESIGN.md",
    "docs/TEST_PLAN.md",
    "docs/SECURITY.md",
    "docs/DECISIONS.md",
    "docs/MEMORY.md",
    "docs/WORK_LOG.md",
    "docs/INCIDENTS.md",
    "docs/EVIDENCE.md",
    "docs/DOCUMENTATION_WORKFLOW.md",
    "docs/source/README.md",
]
PATTERNS = [
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def forbidden(path):
    parts = PurePosixPath(path).parts
    if any(
        p in {".venv", "__pycache__", ".pytest_cache", ".ruff_cache", ".git"}
        for p in parts
    ):
        return True
    if path.startswith(
        (
            "testbed/secrets/",
            "output/chroma/",
            "output/audit-cache/",
            "output/runtime-raw/",
            "tmp/",
        )
    ):
        return True
    name = parts[-1]
    return (name == ".env" or name.startswith(".env.")) and name != ".env.example"


def suspected_secret(payload):
    return any(pattern.search(payload) for pattern in PATTERNS)


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=check)


def split_paths(payload):
    return [p.decode("utf-8") for p in payload.split(b"\0") if p]


def local_links(text):
    # Handles this repository's ordinary Markdown file links, not arbitrary HTML.
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        target = match.group(1).strip().strip("<>")
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            continue
        yield unquote(target.split("#", 1)[0])


def main():
    errors = []
    indexed = set(split_paths(git("ls-files", "-z").stdout))
    untracked = set(
        split_paths(git("ls-files", "--others", "--exclude-standard", "-z").stdout)
    )
    candidates = sorted(indexed | untracked)
    if not candidates:
        errors.append("No publication candidates found")
    secret_values = []
    secret_dir = ROOT / "testbed/secrets"
    if secret_dir.exists():
        for path in secret_dir.glob("*.txt"):
            value = path.read_bytes().strip()
            if len(value) >= 16:
                secret_values.append(value)
    for required in REQUIRED:
        if required not in candidates:
            errors.append(f"Missing required publication document: {required}")
    for name in candidates:
        if forbidden(name):
            errors.append(f"Forbidden publication path: {name}")
            continue
        payload = (
            git("show", ":" + name).stdout
            if name in indexed
            else (ROOT / name).read_bytes()
        )
        if len(payload) > 20_000_000:
            errors.append(f"Oversize publication file requires review: {name}")
        if suspected_secret(payload) or any(
            value in payload for value in secret_values
        ):
            errors.append(f"Potential credential material: {name} (value suppressed)")
        if name.endswith(".md"):
            text = payload.decode("utf-8")
            for target in local_links(text):
                resolved = ((ROOT / name).parent / target).resolve()
                if not resolved.exists():
                    errors.append(f"Broken local link in {name}: {target}")
                elif resolved.is_relative_to(ROOT):
                    relative = resolved.relative_to(ROOT).as_posix()
                    if resolved.is_file() and relative not in candidates:
                        errors.append(
                            f"Link target excluded from publication in {name}: {target}"
                        )
    if git("rev-parse", "--verify", "HEAD", check=False).returncode == 0:
        changed = set(split_paths(git("diff", "--cached", "--name-only", "-z").stdout))
        if any(
            p.endswith(".py") or p in {"pyproject.toml", "testbed/compose.yaml"}
            for p in changed
        ):
            for required in [
                "docs/WORK_LOG.md",
                "docs/MEMORY.md",
                "TASKS.md",
                "CHANGELOG.md",
            ]:
                if required not in changed:
                    errors.append(
                        f"Staged code change needs workflow update: {required}"
                    )
    for error in errors:
        print(error)
    if errors:
        raise SystemExit(1)
    print(
        f"PASS: {len(candidates)} publication files; required docs/links/exclusions and bounded credential checks passed."
    )
    print("This is not a comprehensive secret scan or proof of documentation accuracy.")


if __name__ == "__main__":
    main()
