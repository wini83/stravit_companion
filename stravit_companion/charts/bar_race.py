"""Adapt leaderboard history to the bar-chart-race library."""

from __future__ import annotations

import shutil
import warnings
from collections import Counter
from pathlib import Path

import bar_chart_race as bcr
import matplotlib as mpl
import pandas as pd

from stravit_companion.history import LeaderboardHistory


def render_bar_race(
    history: LeaderboardHistory,
    output: Path,
    *,
    top: int = 10,
    fps: int = 20,
    duration: float = 20.0,
) -> Path:
    """Render an MP4 distance race using bar-chart-race and FFmpeg."""
    _validate_options(history, output, top=top, fps=fps, duration=duration)
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        raise ValueError(
            "FFmpeg is required to generate MP4 files; install ffmpeg and retry"
        )

    frame = _history_frame(history)
    frame = _sample_periods(frame, fps=fps, duration=duration)
    steps_per_period, period_length = _animation_timing(
        periods=len(frame),
        fps=fps,
        duration=duration,
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        with (
            mpl.rc_context(
                {
                    "animation.ffmpeg_path": ffmpeg_path,
                    "animation.ffmpeg_args": [
                        "-pix_fmt",
                        "yuv420p",
                        "-movflags",
                        "+faststart",
                    ],
                }
            ),
            warnings.catch_warnings(),
        ):
            warnings.filterwarnings(
                "ignore",
                message=r"set_ticklabels\(\) should only be used",
                category=UserWarning,
                module=r"bar_chart_race\._make_chart",
            )
            bcr.bar_chart_race(
                df=frame,
                filename=str(output),
                orientation="h",
                sort="desc",
                n_bars=top,
                fixed_order=False,
                fixed_max=False,
                steps_per_period=steps_per_period,
                period_length=period_length,
                interpolate_period=True,
                label_bars=True,
                bar_size=0.9,
                period_label={
                    "x": 0.98,
                    "y": 0.12,
                    "ha": "right",
                    "va": "center",
                    "size": 14,
                    "weight": "bold",
                },
                period_fmt="%Y-%m-%d %H:%M",
                figsize=(12.8, 7.2),
                dpi=100,
                cmap="tab20",
                title="Cumulative distance leaderboard (km)",
                bar_label_size=10,
                tick_label_size=10,
                shared_fontdict={"family": "DejaVu Sans", "color": ".1"},
                bar_kwargs={"alpha": 0.9},
                filter_column_colors=True,
            )
    except Exception as exc:
        raise ValueError(f"Unable to generate {output} with FFmpeg: {exc}") from exc
    return output


def _history_frame(history: LeaderboardHistory) -> pd.DataFrame:
    """Return wide cumulative-distance data expected by bar-chart-race."""
    labels = _participant_labels(history)
    distances: dict[str, list[float]] = {}
    for participant in history.participants:
        values_by_time = {
            point.snapshot_time: point.distance for point in participant.points
        }
        distances[labels[participant.participant_id]] = [
            float(values_by_time.get(snapshot_time, 0.0))
            for snapshot_time in history.snapshot_times
        ]

    return pd.DataFrame(
        distances,
        index=pd.DatetimeIndex(history.snapshot_times, name="snapshot_time"),
    )


def _participant_labels(history: LeaderboardHistory) -> dict[str, str]:
    """Keep labels unique when two pseudonymous display names collide."""
    name_counts = Counter(
        participant.display_name for participant in history.participants
    )
    duplicate_indexes: Counter[str] = Counter()
    labels: dict[str, str] = {}
    for participant in sorted(
        history.participants,
        key=lambda item: item.participant_id,
    ):
        display_name = participant.display_name
        if name_counts[display_name] > 1:
            duplicate_indexes[display_name] += 1
            display_name = f"{display_name} ({duplicate_indexes[display_name]})"
        labels[participant.participant_id] = display_name
    return labels


def _animation_timing(
    *,
    periods: int,
    fps: int,
    duration: float,
) -> tuple[int, float]:
    """Translate total target duration and FPS to bar-chart-race timing."""
    transitions = periods - 1
    steps_per_period = max(1, round(duration * fps / transitions))
    period_length = steps_per_period * 1000 / fps
    return steps_per_period, period_length


def _sample_periods(
    frame: pd.DataFrame,
    *,
    fps: int,
    duration: float,
) -> pd.DataFrame:
    """Bound source periods so the requested duration remains achievable."""
    target_transitions = max(1, round(duration * fps))
    preferred_steps = min(10, target_transitions)
    maximum_periods = target_transitions // preferred_steps + 1
    if len(frame) <= maximum_periods:
        return frame

    last_index = len(frame) - 1
    positions = [
        round(index * last_index / (maximum_periods - 1))
        for index in range(maximum_periods)
    ]
    return frame.iloc[positions]


def _validate_options(
    history: LeaderboardHistory,
    output: Path,
    *,
    top: int,
    fps: int,
    duration: float,
) -> None:
    if len(history.snapshot_times) < 2:
        raise ValueError("At least two leaderboard snapshots are required")
    if not history.participants:
        raise ValueError("At least one participant is required")
    if output.suffix.lower() != ".mp4":
        raise ValueError("Output path must have an .mp4 extension")
    if top < 1:
        raise ValueError("top must be at least 1")
    if fps < 1:
        raise ValueError("fps must be at least 1")
    if duration <= 0:
        raise ValueError("duration must be greater than 0")
