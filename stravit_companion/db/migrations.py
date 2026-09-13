"""Explicit, fail-closed SQLite migrations for persisted snapshots."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import Engine, inspect, text

from stravit_companion.identity import abbreviate_name, participant_id

_TABLE = "leaderboard_snapshots"
_OLD_COLUMNS = {"id", "ts", "name", "rank", "distance", "elevation", "longest", "count"}
_NEW_COLUMNS = {
    "id",
    "ts",
    "participant_id",
    "display_name",
    "rank",
    "distance",
    "elevation",
    "longest",
    "count",
}


def _backup_database(engine: Engine) -> Path:
    if engine.url.get_backend_name() != "sqlite" or not engine.url.database:
        raise RuntimeError(
            "Snapshot migration only supports file-based SQLite databases"
        )

    source = Path(engine.url.database)
    if not source.exists():
        raise RuntimeError(f"Cannot back up missing database: {source}")
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    backup = source.with_name(
        f"{source.stem}.pre-pseudonymization-{timestamp}{source.suffix}"
    )
    # SQLite's backup API includes committed WAL data, unlike a file copy.
    with (
        sqlite3.connect(source) as source_connection,
        sqlite3.connect(backup) as backup_connection,
    ):
        source_connection.backup(backup_connection)
    return backup


def _drop_stale_temporary_table(engine: Engine) -> None:
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS leaderboard_snapshots_new"))
        connection.commit()


def migrate_leaderboard_snapshots(engine: Engine, identity_hash_key: str) -> None:
    """Migrate legacy name rows once, preserving history and a recoverable backup.

    Any error leaves the old table in place because all schema changes happen in one
    SQLite transaction; the on-disk backup is created before that transaction.
    """
    table_names = set(inspect(engine).get_table_names())
    if _TABLE not in table_names:
        return

    columns = {column["name"] for column in inspect(engine).get_columns(_TABLE)}
    if columns == _NEW_COLUMNS:
        return
    if columns != _OLD_COLUMNS:
        raise RuntimeError(
            f"Unsupported {_TABLE} schema; refusing migration: {columns}"
        )

    _drop_stale_temporary_table(engine)
    _backup_database(engine)
    try:
        with engine.begin() as connection:
            source_count = connection.scalar(
                text("SELECT COUNT(*) FROM leaderboard_snapshots")
            )
            source_snapshots = connection.scalar(
                text("SELECT COUNT(DISTINCT ts) FROM leaderboard_snapshots")
            )
            source_rows = list(
                connection.execute(
                    text(
                        "SELECT id, ts, name, rank, distance, elevation, "
                        "longest, count "
                        "FROM leaderboard_snapshots"
                    )
                ).mappings()
            )

            connection.execute(
                text(
                    "CREATE TABLE leaderboard_snapshots_new ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "ts DATETIME NOT NULL, participant_id VARCHAR NOT NULL, "
                    "display_name VARCHAR NOT NULL, rank INTEGER NOT NULL, "
                    "distance FLOAT NOT NULL, elevation INTEGER NOT NULL, "
                    "longest FLOAT NOT NULL, count INTEGER NOT NULL, "
                    "CONSTRAINT uq_snapshot_participant_id UNIQUE (ts, participant_id)"
                    ")"
                )
            )
            for row in source_rows:
                connection.execute(
                    text(
                        "INSERT INTO leaderboard_snapshots_new "
                        "(id, ts, participant_id, display_name, rank, distance, "
                        "elevation, "
                        "longest, count) VALUES "
                        "(:id, :ts, :participant_id, :display_name, :rank, :distance, "
                        ":elevation, :longest, :count)"
                    ),
                    {
                        **row,
                        "participant_id": participant_id(
                            row["name"], identity_hash_key
                        ),
                        "display_name": abbreviate_name(row["name"]),
                    },
                )

            migrated_count = connection.scalar(
                text("SELECT COUNT(*) FROM leaderboard_snapshots_new")
            )
            migrated_snapshots = connection.scalar(
                text("SELECT COUNT(DISTINCT ts) FROM leaderboard_snapshots_new")
            )
            duplicates = connection.scalar(
                text(
                    "SELECT COUNT(*) FROM (SELECT ts, participant_id "
                    "FROM leaderboard_snapshots_new "
                    "GROUP BY ts, participant_id HAVING COUNT(*) > 1)"
                )
            )
            if (migrated_count, migrated_snapshots, duplicates) != (
                source_count,
                source_snapshots,
                0,
            ):
                raise RuntimeError(
                    "Snapshot migration validation failed; original table retained"
                )

            connection.execute(text("DROP TABLE leaderboard_snapshots"))
            connection.execute(
                text(
                    "ALTER TABLE leaderboard_snapshots_new "
                    "RENAME TO leaderboard_snapshots"
                )
            )
            connection.execute(
                text(
                    "CREATE INDEX ix_snapshot_participant_id "
                    "ON leaderboard_snapshots (ts, participant_id)"
                )
            )
    except Exception:
        _drop_stale_temporary_table(engine)
        raise

    final_columns = {column["name"] for column in inspect(engine).get_columns(_TABLE)}
    if final_columns != _NEW_COLUMNS or "name" in final_columns:
        raise RuntimeError("Snapshot migration did not remove plaintext name storage")
