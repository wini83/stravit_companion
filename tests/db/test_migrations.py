from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, inspect, text

from stravit_companion.db.migrations import migrate_leaderboard_snapshots
from stravit_companion.identity import participant_id


def _legacy_engine(tmp_path):
    db_path = tmp_path / "legacy.db"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE leaderboard_snapshots ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, ts DATETIME NOT NULL, "
                "name VARCHAR NOT NULL, rank INTEGER NOT NULL, "
                "distance FLOAT NOT NULL, elevation INTEGER NOT NULL, "
                "longest FLOAT NOT NULL, count INTEGER NOT NULL, "
                "CONSTRAINT uq_snapshot_name UNIQUE (ts, name))"
            )
        )
        first = datetime.now(UTC) - timedelta(hours=1)
        second = datetime.now(UTC)
        connection.execute(
            text(
                "INSERT INTO leaderboard_snapshots "
                "(ts, name, rank, distance, elevation, longest, count) VALUES "
                "(:ts, :name, :rank, :distance, :elevation, :longest, :count)"
            ),
            [
                {
                    "ts": first,
                    "name": "Jane Doe",
                    "rank": 1,
                    "distance": 10,
                    "elevation": 100,
                    "longest": 5,
                    "count": 1,
                },
                {
                    "ts": first,
                    "name": "Alice Example",
                    "rank": 2,
                    "distance": 9,
                    "elevation": 90,
                    "longest": 4,
                    "count": 1,
                },
                {
                    "ts": second,
                    "name": "Jane Doe",
                    "rank": 1,
                    "distance": 11,
                    "elevation": 110,
                    "longest": 5.5,
                    "count": 2,
                },
            ],
        )
    return engine, db_path


def test_migration_preserves_history_and_removes_plaintext(tmp_path):
    engine, db_path = _legacy_engine(tmp_path)

    migrate_leaderboard_snapshots(engine, "migration-key")

    columns = {
        column["name"]
        for column in inspect(engine).get_columns("leaderboard_snapshots")
    }
    assert "name" not in columns
    assert {"participant_id", "display_name"} <= columns
    backup = db_path.with_suffix(".db.pre-pseudonymization.bak")
    assert backup.exists()
    backup_engine = create_engine(f"sqlite:///{backup}", future=True)
    assert "name" in {
        column["name"]
        for column in inspect(backup_engine).get_columns("leaderboard_snapshots")
    }
    with engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT participant_id, display_name, distance "
                "FROM leaderboard_snapshots ORDER BY id"
            )
        ).all()
        assert len(rows) == 3
        assert (
            connection.scalar(
                text("SELECT COUNT(DISTINCT ts) FROM leaderboard_snapshots")
            )
            == 2
        )
    assert rows[0].participant_id == participant_id("Jane Doe", "migration-key")
    assert rows[0].display_name == "Jane D."
    assert rows[0].distance == 10

    migrate_leaderboard_snapshots(engine, "another-key")
    with engine.connect() as connection:
        assert (
            connection.scalar(text("SELECT COUNT(*) FROM leaderboard_snapshots")) == 3
        )


def test_failed_migration_keeps_legacy_table_and_backup(tmp_path, monkeypatch):
    engine, db_path = _legacy_engine(tmp_path)
    monkeypatch.setattr(
        "stravit_companion.db.migrations.participant_id", lambda *_: "same"
    )

    with pytest.raises(Exception):
        migrate_leaderboard_snapshots(engine, "migration-key")

    columns = {
        column["name"]
        for column in inspect(engine).get_columns("leaderboard_snapshots")
    }
    assert "name" in columns
    assert db_path.with_suffix(".db.pre-pseudonymization.bak").exists()
