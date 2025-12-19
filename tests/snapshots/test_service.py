from datetime import datetime, timedelta

from sqlalchemy import func, select

from stravit_companion.db.models import LeaderboardSnapshot
from stravit_companion.snapshots.service import (
    index,
    load_snapshot,
    save_snapshot_if_changed,
)


def _insert_snapshot(session, items, ts):
    records = [
        LeaderboardSnapshot(
            ts=ts,
            name=item.name,
            rank=item.rank,
            distance=item.distance,
            elevation=item.elevation,
            longest=item.longest,
            count=item.count,
        )
        for item in items
    ]
    session.add_all(records)
    session.commit()


def test_load_snapshot_empty_returns_none(db_session):
    assert load_snapshot(db_session) is None


def test_save_snapshot_first_run_persists_and_returns_true(db_session, item_factory):
    items = [
        item_factory(name="Alice Example", rank=1, distance=10.0),
        item_factory(name="Jane Doe", rank=2, distance=9.5),
    ]

    saved = save_snapshot_if_changed(db_session, items)

    assert saved is True
    loaded = load_snapshot(db_session)
    assert loaded is not None
    assert index(loaded) == index(items)


def test_save_snapshot_no_change_returns_false(db_session, item_factory):
    items = [
        item_factory(name="Alice Example", rank=1, distance=10.0),
        item_factory(name="Jane Doe", rank=2, distance=9.5),
    ]

    first = save_snapshot_if_changed(db_session, items)
    second = save_snapshot_if_changed(db_session, items)

    assert first is True
    assert second is False

    ts_count = db_session.scalar(select(func.count(LeaderboardSnapshot.ts.distinct())))
    assert ts_count == 1


def test_load_snapshot_with_offset_returns_previous(db_session, item_factory):
    items_v1 = [
        item_factory(name="Alice Example", rank=1, distance=10.0),
        item_factory(name="Jane Doe", rank=2, distance=9.5),
    ]
    items_v2 = [
        item_factory(name="Alice Example", rank=1, distance=11.0),
        item_factory(name="Jane Doe", rank=2, distance=10.2),
    ]

    ts1 = datetime.utcnow() - timedelta(hours=1)
    ts2 = datetime.utcnow()
    _insert_snapshot(db_session, items_v1, ts1)
    _insert_snapshot(db_session, items_v2, ts2)

    latest = load_snapshot(db_session, offset=0)
    previous = load_snapshot(db_session, offset=1)

    assert latest is not None
    assert previous is not None
    assert index(latest) == index(items_v2)
    assert index(previous) == index(items_v1)
