from datetime import UTC, datetime, timedelta

import pytest

from stravit_companion.charts.ranking_history import render_ranking_history
from stravit_companion.history import (
    LeaderboardHistory,
    ParticipantHistory,
    ParticipantHistoryPoint,
)


def _history() -> LeaderboardHistory:
    first = datetime(2026, 9, 27, 10, tzinfo=UTC).replace(tzinfo=None)
    second = first + timedelta(hours=1)
    return LeaderboardHistory(
        snapshot_times=(first, second),
        participants=(
            ParticipantHistory(
                participant_id="jane",
                display_name="Jane D.",
                points=(
                    ParticipantHistoryPoint(first, 2, 10.0, None, None),
                    ParticipantHistoryPoint(second, 1, 12.0, -1, 2.0),
                ),
                missing_snapshot_times=(),
            ),
        ),
    )


@pytest.mark.parametrize(
    ("filename", "signature"),
    [("ranking.png", b"\x89PNG\r\n\x1a\n"), ("ranking.svg", b"<?xml")],
)
def test_render_ranking_history_writes_supported_format(
    tmp_path, filename, signature
) -> None:
    output = tmp_path / "nested" / filename

    assert render_ranking_history(_history(), output) == output
    assert output.read_bytes().startswith(signature)


def test_render_ranking_history_requires_multiple_snapshots(tmp_path) -> None:
    history = LeaderboardHistory(snapshot_times=(), participants=())

    with pytest.raises(ValueError, match="At least two leaderboard snapshots"):
        render_ranking_history(history, tmp_path / "ranking.png")


def test_render_ranking_history_rejects_unknown_format(tmp_path) -> None:
    with pytest.raises(ValueError, match=r"\.png or \.svg"):
        render_ranking_history(_history(), tmp_path / "ranking.pdf")
