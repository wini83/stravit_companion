from datetime import datetime, timedelta

import pytest

from stravit_companion.charts.distance_history import (
    _distance_series,
    render_distance_history,
)
from stravit_companion.history import (
    LeaderboardHistory,
    ParticipantHistory,
    ParticipantHistoryPoint,
)


def _history() -> LeaderboardHistory:
    first = datetime(2026, 9, 27, 10)
    second = first + timedelta(hours=1)
    return LeaderboardHistory(
        snapshot_times=(first, second),
        participants=(
            ParticipantHistory(
                participant_id="jane",
                display_name="Jane D.",
                points=(
                    ParticipantHistoryPoint(first, 2, 10.0, None, None),
                    ParticipantHistoryPoint(second, 1, 12.5, -1, 2.5),
                ),
                missing_snapshot_times=(),
            ),
        ),
    )


def test_render_distance_history_writes_png(tmp_path) -> None:
    output = tmp_path / "nested" / "distance.png"

    assert render_distance_history(_history(), output) == output
    assert output.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_distance_series_uses_cumulative_values_without_summing() -> None:
    history = _history()

    assert _distance_series(
        history.participants[0], history.snapshot_times
    ) == pytest.approx((10.0, 12.5))


def test_render_distance_history_requires_multiple_snapshots(tmp_path) -> None:
    history = LeaderboardHistory(snapshot_times=(), participants=())

    with pytest.raises(ValueError, match="At least two leaderboard snapshots"):
        render_distance_history(history, tmp_path / "distance.png")
