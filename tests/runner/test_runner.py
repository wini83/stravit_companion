from datetime import UTC, datetime, timedelta

from click.testing import CliRunner

from stravit_companion.db.models import LeaderboardSnapshot


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


def test_runner_dry_run_does_not_send_alert(
    monkeypatch, session_factory, sqlite_engine, item_factory
):
    from stravit_companion import runner

    items_prev = [
        item_factory(name="Alice Example", rank=1, distance=15.0),
        item_factory(name="Jane Doe", rank=2, distance=13.0),
        item_factory(name="Bob Example", rank=3, distance=12.0),
    ]
    items_curr = [
        item_factory(name="Jane Doe", rank=1, distance=16.0),
        item_factory(name="Alice Example", rank=2, distance=15.5),
        item_factory(name="Bob Example", rank=3, distance=12.0),
    ]

    with session_factory() as session:
        ts1 = datetime.now(UTC) - timedelta(hours=1)
        ts2 = datetime.now(UTC)
        _insert_snapshot(session, items_prev, ts1)
        _insert_snapshot(session, items_curr, ts2)

    monkeypatch.setattr(runner, "engine", sqlite_engine)
    monkeypatch.setattr(runner, "Session", session_factory)

    sent = {"called": False}

    def fake_send(alert):
        sent["called"] = True

    monkeypatch.setattr(runner, "send", fake_send)

    result = CliRunner().invoke(runner.main, ["--dry-run"])

    assert result.exit_code == 0
    assert "dry_run_alert" in result.output
    assert sent["called"] is False


def test_runner_no_data_skips_processing(monkeypatch, sqlite_engine, session_factory):
    from stravit_companion import runner

    monkeypatch.setattr(runner, "engine", sqlite_engine)
    monkeypatch.setattr(runner, "Session", session_factory)
    monkeypatch.setattr(runner, "fetch_leaderboard_safe", lambda: [])

    sent = {"called": False}

    def fake_send(alert):
        sent["called"] = True

    monkeypatch.setattr(runner, "send", fake_send)

    result = CliRunner().invoke(runner.main, [])

    assert result.exit_code == 0
    assert sent["called"] is False
