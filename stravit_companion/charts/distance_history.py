"""Render cumulative leaderboard distance without requiring a display server."""

from datetime import datetime
from math import nan
from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
from matplotlib.figure import Figure

from stravit_companion.history import LeaderboardHistory, ParticipantHistory

_OUTPUT_FORMATS = {".png": "png", ".svg": "svg"}


def render_distance_history(
    history: LeaderboardHistory,
    output: Path,
) -> Path:
    """Render cumulative participant distance over time."""
    if len(history.snapshot_times) < 2:
        raise ValueError("At least two leaderboard snapshots are required")

    participants = tuple(
        participant
        for participant in history.participants
        if len(participant.points) >= 2
    )
    if not participants:
        raise ValueError(
            "At least one participant present in two snapshots is required"
        )

    output_format = _OUTPUT_FORMATS.get(output.suffix.lower())
    if output_format is None:
        raise ValueError("Output path must have a .png or .svg extension")

    output.parent.mkdir(parents=True, exist_ok=True)
    figure = Figure(figsize=(12, 7), layout="constrained")
    FigureCanvasAgg(figure)
    axes = figure.subplots()

    for participant in participants:
        axes.plot(
            history.snapshot_times,
            _distance_series(participant, history.snapshot_times),
            marker="o",
            linewidth=2,
            markersize=4,
            label=participant.display_name,
        )

    locator = AutoDateLocator()
    axes.xaxis.set_major_locator(locator)
    axes.xaxis.set_major_formatter(ConciseDateFormatter(locator))
    axes.set_ylim(bottom=0)
    axes.set_title("Cumulative leaderboard distance")
    axes.set_xlabel("Snapshot time")
    axes.set_ylabel("Distance (km)")
    axes.grid(visible=True, alpha=0.25)
    axes.legend(
        title="Participant",
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
    )

    figure.savefig(output, format=output_format, dpi=160)
    figure.clear()
    return output


def _distance_series(
    participant: ParticipantHistory,
    snapshot_times: tuple[datetime, ...],
) -> tuple[float, ...]:
    """Align cumulative distances, leaving gaps for missing snapshots."""
    distances_by_time = {
        point.snapshot_time: point.distance for point in participant.points
    }
    return tuple(
        float(distances_by_time.get(snapshot_time, nan))
        for snapshot_time in snapshot_times
    )
