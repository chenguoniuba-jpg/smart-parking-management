"""Fail when common local secrets or runtime artifacts enter the public package."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_NAMES = {
    ".DS_Store",
    ".env",
    "ai_parking.db",
}
FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".pem", ".key"}
IGNORED_PARTS = {".git", ".venv", "venv", "backups", "__pycache__"}


def find_forbidden_files() -> list[Path]:
    findings: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(path.relative_to(ROOT))
        elif path.name.startswith("~$") or path.name.startswith(".~"):
            findings.append(path.relative_to(ROOT))
    return sorted(findings)


def main() -> None:
    findings = find_forbidden_files()
    if findings:
        print("Public-package check failed. Remove these local or sensitive files:")
        for path in findings:
            print(f"- {path}")
        raise SystemExit(1)
    print("Public-package check passed: no common secret or runtime artifacts found.")


if __name__ == "__main__":
    main()
