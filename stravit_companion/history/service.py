"""Typed historical leaderboard queries, independent from presentation libraries."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from stravit_companion.db.models import LeaderboardSnapshot


@dataclass(frozen=True)
class ParticipantHistoryPoint:
    snapshot_time: datetime
    rank: int
    distance: float
    rank_delta: int | None
    distance_delta: float | None


@dataclass(frozen=True)
class ParticipantHistory:
    participant_id: str
    display_name: str
    points: tuple[ParticipantHistoryPoint, ...]
    missing_snapshot_times: tuple[datetime, ...]


@dataclass(frozen=True)
class LeaderboardHistory:
    snapshot_times: tuple[datetime, ...]
    participants: tuple[ParticipantHistory, ...]


def get_leaderboard_history(
    session: Session,
    *,
    from_snapshot: datetime | None = None,
    to_snapshot: datetime | None = None,
    top: int | None = None,
) -> LeaderboardHistory:
    """Return ordered history for charts, tables, or animations.

    ``top`` selects participants ranked in the top N of the newest snapshot in the
    requested range. Participants absent in individual snapshots are represented by
    ``missing_snapshot_times``; no synthetic score or rank is invented for them.
    """
    if top is not None and top < 1:
        raise ValueError("top must be at least 1")
    if (
        from_snapshot is not None
        and to_snapshot is not None
        and from_snapshot > to_snapshot
    ):
        raise ValueError("from_snapshot must not be after to_snapshot")

    statement = select(LeaderboardSnapshot)
    if from_snapshot is not None:
        statement = statement.where(LeaderboardSnapshot.ts >= from_snapshot)
    if to_snapshot is not None:
        statement = statement.where(LeaderboardSnapshot.ts <= to_snapshot)
    rows = session.scalars(
        statement.order_by(
            LeaderboardSnapshot.ts,
            LeaderboardSnapshot.rank,
            LeaderboardSnapshot.participant_id,
        )
    ).all()

    snapshot_times = tuple(sorted({row.ts for row in rows}))
    if not snapshot_times:
        return LeaderboardHistory(snapshot_times=(), participants=())

    latest_time = snapshot_times[-1]
    latest_rows = [row for row in rows if row.ts == latest_time]
    selected_ids = {row.participant_id for row in latest_rows[:top] if top is not None}
    if top is None:
        selected_ids = {row.participant_id for row in rows}

    rows_by_participant: dict[str, list[LeaderboardSnapshot]] = {}
    for row in rows:
        if row.participant_id in selected_ids:
            rows_by_participant.setdefault(row.participant_id, []).append(row)

    participants = tuple(
        _to_participant_history(participant_rows, snapshot_times)
        for _, participant_rows in sorted(
            rows_by_participant.items(),
            key=lambda item: (item[1][-1].rank, item[0]),
        )
    )
    return LeaderboardHistory(
        snapshot_times=snapshot_times,
        participants=participants,
    )


def _to_participant_history(
    rows: list[LeaderboardSnapshot], snapshot_times: tuple[datetime, ...]
) -> ParticipantHistory:
    rows_by_time = {row.ts: row for row in rows}
    points: list[ParticipantHistoryPoint] = []
    previous_row: LeaderboardSnapshot | None = None
    for snapshot_time in snapshot_times:
        row = rows_by_time.get(snapshot_time)
        if row is None:
            previous_row = None
            continue
        points.append(
            ParticipantHistoryPoint(
                snapshot_time=snapshot_time,
                rank=row.rank,
                distance=row.distance,
                rank_delta=row.rank - previous_row.rank if previous_row else None,
                distance_delta=(
                    row.distance - previous_row.distance if previous_row else None
                ),
            )
        )
        previous_row = row

    first_row = rows[0]
    return ParticipantHistory(
        participant_id=first_row.participant_id,
        display_name=first_row.display_name,
        points=tuple(points),
        missing_snapshot_times=tuple(
            snapshot_time
            for snapshot_time in snapshot_times
            if snapshot_time not in rows_by_time
        ),
    )
