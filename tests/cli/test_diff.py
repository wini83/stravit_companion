from datetime import UTC, datetime, timedelta

from click.testing import CliRunner

from stravit_companion.cli import diff as diff_module
from stravit_companion.db.models import LeaderboardSnapshot


def _save(session, ts, item):
    session.add(
        LeaderboardSnapshot(
            ts=ts,
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


def test_diff_matches_participant_ids_and_renders_display_name(
    monkeypatch, session_factory, item_factory
):
    first = datetime.now(UTC) - timedelta(hours=1)
    second = datetime.now(UTC)
    with session_factory() as session:
        _save(session, first, item_factory(name="Jane Doe", rank=2, distance=10))
        _save(session, second, item_factory(name="Jane Doe", rank=1, distance=12))

    monkeypatch.setattr(diff_module, "Session", session_factory)
    result = CliRunner().invoke(diff_module.diff, ["latest-1", "latest"])

    assert result.exit_code == 0
    assert "Jane D." in result.output
    assert "-1" in result.output


def test_diff_reports_no_changes_and_invalid_references(
    monkeypatch, session_factory, item_factory
):
    timestamp = datetime.now(UTC)
    with session_factory() as session:
        _save(session, timestamp, item_factory())

    monkeypatch.setattr(diff_module, "Session", session_factory)
    runner = CliRunner()

    unchanged = runner.invoke(diff_module.diff, ["latest", "latest"])
    invalid = runner.invoke(diff_module.diff, ["not-a-time", "latest"])
    missing = runner.invoke(diff_module.diff, ["latest-1", "latest"])

    assert unchanged.exit_code == 0
    assert "No changes detected" in unchanged.output
    assert invalid.exit_code != 0
    assert "Invalid snapshot reference" in invalid.output
    assert missing.exit_code != 0
    assert "not found" in missing.output
