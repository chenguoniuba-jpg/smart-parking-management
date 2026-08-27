import sqlite3

import pytest

from scripts.backup_sqlite import create_backup, sqlite_path_from_url


def test_sqlite_url_parser_supports_relative_and_absolute_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert sqlite_path_from_url("sqlite:///./parking.db") == tmp_path / "parking.db"
    assert sqlite_path_from_url(f"sqlite:///{tmp_path}/absolute.db") == tmp_path / "absolute.db"


def test_sqlite_url_parser_rejects_non_sqlite_database():
    with pytest.raises(ValueError):
        sqlite_path_from_url("postgresql://localhost/parking")


def test_backup_is_consistent_and_readable(tmp_path):
    source = tmp_path / "source.db"
    with sqlite3.connect(source) as db:
        db.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
        db.execute("INSERT INTO sample(value) VALUES ('kept')")
        db.commit()

    destination = create_backup(source, tmp_path / "backups")
    assert destination.is_file()

    with sqlite3.connect(destination) as backup:
        assert backup.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert backup.execute("SELECT value FROM sample").fetchone() == ("kept",)
