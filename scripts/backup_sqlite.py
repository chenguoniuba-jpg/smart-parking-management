"""Create and validate a transactionally consistent SQLite backup."""

from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote


def sqlite_path_from_url(database_url: str) -> Path:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise ValueError("backup_sqlite.py supports only sqlite:/// DATABASE_URL values")

    raw_path = unquote(database_url[len(prefix) :])
    if not raw_path or raw_path == ":memory:":
        raise ValueError("DATABASE_URL must point to a file-backed SQLite database")
    return Path(raw_path).expanduser().resolve()


def create_backup(source: Path, output_dir: Path) -> Path:
    if not source.is_file():
        raise FileNotFoundError(f"SQLite database not found: {source}")

    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = output_dir.resolve() / f"{source.stem}-{stamp}.sqlite3"
    if destination == source:
        raise ValueError("Backup destination must differ from the source database")

    with sqlite3.connect(source) as source_db, sqlite3.connect(destination) as backup_db:
        source_db.backup(backup_db)
        result = backup_db.execute("PRAGMA integrity_check").fetchone()

    if result != ("ok",):
        destination.unlink(missing_ok=True)
        raise RuntimeError(f"Backup failed SQLite integrity check: {result!r}")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", "sqlite:///./ai_parking.db"),
        help="SQLAlchemy SQLite URL; defaults to DATABASE_URL or sqlite:///./ai_parking.db",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("backups"),
        help="Directory for timestamped backups (default: backups)",
    )
    args = parser.parse_args()

    source = sqlite_path_from_url(args.database_url)
    destination = create_backup(source, args.output_dir)
    print(f"Backup created and verified: {destination}")


if __name__ == "__main__":
    main()
