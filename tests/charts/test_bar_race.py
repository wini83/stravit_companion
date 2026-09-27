from dataclasses import replace
from datetime import datetime, timedelta

import pandas as pd
import pytest

from stravit_companion.charts import bar_race as bar_race_module
from stravit_companion.charts.bar_race import (
    _animation_timing,
    _history_frame,
    _sample_periods,
    render_bar_race,
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
                participant_id="alice",
                display_name="Alice E.",
                points=(
                    ParticipantHistoryPoint(first, 2, 10.0, None, None),
                    ParticipantHistoryPoint(second, 1, 20.0, -1, 10.0),
                ),
                missing_snapshot_times=(),
            ),
            ParticipantHistory(
                participant_id="jane",
                display_name="Jane D.",
                points=(
                    ParticipantHistoryPoint(first, 1, 15.0, None, None),
                    ParticipantHistoryPoint(second, 2, 16.0, 1, 1.0),
                ),
                missing_snapshot_times=(),
            ),
        ),
    )


def test_history_frame_contains_wide_cumulative_values() -> None:
    frame = _history_frame(_history())

    assert list(frame.columns) == ["Alice E.", "Jane D."]
    assert frame.index.name == "snapshot_time"
    assert frame["Alice E."].tolist() == pytest.approx([10.0, 20.0])
    assert frame["Jane D."].tolist() == pytest.approx([15.0, 16.0])


def test_history_frame_disambiguates_duplicate_display_names() -> None:
    history = _history()
    duplicate_names = LeaderboardHistory(
        snapshot_times=history.snapshot_times,
        participants=tuple(
            replace(participant, display_name="Same N.")
            for participant in history.participants
        ),
    )

    frame = _history_frame(duplicate_names)

    assert list(frame.columns) == ["Same N. (1)", "Same N. (2)"]


def test_animation_timing_preserves_requested_fps() -> None:
    steps, period_length = _animation_timing(periods=5, fps=20, duration=2)

    assert steps == 10
    assert 1000 / period_length * steps == pytest.approx(20)


def test_sample_periods_bounds_video_duration_and_keeps_endpoints() -> None:
    frame = _history_frame(_history())
    expanded = frame.reindex(
        pd.date_range(frame.index[0], frame.index[-1], periods=101)
    ).interpolate()

    sampled = _sample_periods(expanded, fps=10, duration=3)
    _steps, period_length = _animation_timing(periods=len(sampled), fps=10, duration=3)

    assert len(sampled) == 4
    assert sampled.index[0] == expanded.index[0]
    assert sampled.index[-1] == expanded.index[-1]
    assert (len(sampled) - 1) * period_length / 1000 == pytest.approx(3)


def test_render_bar_race_calls_library_with_reordering(monkeypatch, tmp_path) -> None:
    calls = {}
    output = tmp_path / "leaderboard.mp4"
    monkeypatch.setattr(
        bar_race_module.shutil,
        "which",
        lambda executable: "/usr/bin/ffmpeg",
    )

    def render(**kwargs):
        calls.update(kwargs)
        output.write_bytes(b"video")

    monkeypatch.setattr(bar_race_module.bcr, "bar_chart_race", render)

    assert render_bar_race(_history(), output, top=1, fps=10, duration=2) == output
    assert calls["n_bars"] == 1
    assert calls["fixed_order"] is False
    assert calls["interpolate_period"] is True
    assert calls["filename"] == str(output)


def test_render_bar_race_reports_missing_ffmpeg(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(bar_race_module.shutil, "which", lambda executable: None)

    with pytest.raises(ValueError, match="FFmpeg is required"):
        render_bar_race(_history(), tmp_path / "leaderboard.mp4")


def test_render_bar_race_wraps_library_failure(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        bar_race_module.shutil,
        "which",
        lambda executable: "/usr/bin/ffmpeg",
    )
    monkeypatch.setattr(
        bar_race_module.bcr,
        "bar_chart_race",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("encoding failed")),
    )

    with pytest.raises(ValueError, match=r"Unable to generate.*encoding failed"):
        render_bar_race(_history(), tmp_path / "leaderboard.mp4")


def test_render_bar_race_rejects_non_mp4_output(tmp_path) -> None:
    with pytest.raises(ValueError, match=r"\.mp4 extension"):
        render_bar_race(_history(), tmp_path / "leaderboard.gif")


@pytest.mark.parametrize(
    ("history", "options", "message"),
    [
        (LeaderboardHistory((), ()), {}, "At least two leaderboard snapshots"),
        (
            LeaderboardHistory(_history().snapshot_times, ()),
            {},
            "At least one participant",
        ),
        (_history(), {"top": 0}, "top must be at least 1"),
        (_history(), {"fps": 0}, "fps must be at least 1"),
        (_history(), {"duration": 0}, "duration must be greater than 0"),
    ],
)
def test_render_bar_race_rejects_invalid_options(
    history, options, message, tmp_path
) -> None:
    with pytest.raises(ValueError, match=message):
        render_bar_race(history, tmp_path / "leaderboard.mp4", **options)
