from datetime import UTC, datetime, timedelta

import pytest

from stravit_companion.db.models import LeaderboardSnapshot
from stravit_companion.history.service import get_leaderboard_history


def _save(session, timestamp, item):
    session.add(
        LeaderboardSnapshot(
            ts=timestamp,
            participant_id=item.participant_id,
            display_name=item.display_name,
            rank=item.rank,
            distance=item.distance,
            elevation=item.elevation,
            longest=item.longest,
            count=item.count,
        )
    )
    session.commit()


def test_history_orders_points_calculates_deltas_and_marks_missing_snapshots(
    db_session, item_factory
):
    first = (datetime.now(UTC) - timedelta(hours=2)).replace(tzinfo=None)
    second = first + timedelta(hours=1)
    third = first + timedelta(hours=2)
    jane_first = item_factory(name="Jane Doe", rank=2, distance=10)
    jane_second = item_factory(name="Jane Doe", rank=1, distance=12)
    jane_third = item_factory(name="Jane Doe", rank=1, distance=13)
    alice_first = item_factory(name="Alice Example", rank=1, distance=11)
    alice_third = item_factory(name="Alice Example", rank=2, distance=12)
    for timestamp, item in [
        (first, jane_first),
        (first, alice_first),
        (second, jane_second),
        (third, jane_third),
        (third, alice_third),
    ]:
        _save(db_session, timestamp, item)

    history = get_leaderboard_history(db_session)

    assert history.snapshot_times == (first, second, third)
    jane, alice = history.participants
    assert jane.display_name == "Jane D."
    assert [point.distance_delta for point in jane.points] == [None, 2, 1]
    assert [point.rank_delta for point in jane.points] == [None, -1, 0]
    assert alice.missing_snapshot_times == (second,)
    assert [point.distance_delta for point in alice.points] == [None, None]


def test_history_filters_range_and_top_participants(db_session, item_factory):
    first = (datetime.now(UTC) - timedelta(hours=1)).replace(tzinfo=None)
    second = datetime.now(UTC).replace(tzinfo=None)
    for timestamp, item in [
        (first, item_factory(name="Jane Doe", rank=1, distance=10)),
        (first, item_factory(name="Alice Example", rank=2, distance=9)),
        (second, item_factory(name="Alice Example", rank=1, distance=11)),
        (second, item_factory(name="Jane Doe", rank=2, distance=10)),
    ]:
        _save(db_session, timestamp, item)

    history = get_leaderboard_history(
        db_session, from_snapshot=second, to_snapshot=second, top=1
    )

    assert history.snapshot_times == (second,)
    assert [participant.display_name for participant in history.participants] == [
        "Alice E."
    ]


def test_history_rejects_invalid_filters(db_session):
    now = datetime.now(UTC)

    with pytest.raises(ValueError, match="top"):
        get_leaderboard_history(db_session, top=0)
    with pytest.raises(ValueError, match="from_snapshot"):
        get_leaderboard_history(
            db_session,
            from_snapshot=now,
            to_snapshot=now - timedelta(seconds=1),
        )


def test_history_returns_empty_typed_result_without_snapshots(db_session):
    assert get_leaderboard_history(db_session).snapshot_times == ()
    assert get_leaderboard_history(db_session).participants == ()
