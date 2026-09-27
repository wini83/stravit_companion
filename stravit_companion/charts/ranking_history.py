"""Render leaderboard rank history without requiring a display server."""

from datetime import datetime
from math import nan
from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from stravit_companion.history import LeaderboardHistory, ParticipantHistory

_OUTPUT_FORMATS = {".png": "png", ".svg": "svg"}


def render_ranking_history(
    history: LeaderboardHistory,
    output: Path,
) -> Path:
    """Render participant ranks over time and return the written output path."""
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
            _rank_series(participant, history.snapshot_times),
            marker="o",
            linewidth=2,
            markersize=4,
            label=participant.display_name,
        )

    maximum_rank = max(point.rank for item in participants for point in item.points)
    locator = AutoDateLocator()
    axes.xaxis.set_major_locator(locator)
    axes.xaxis.set_major_formatter(ConciseDateFormatter(locator))
    axes.yaxis.set_major_locator(MaxNLocator(integer=True, min_n_ticks=2))
    axes.set_ylim(maximum_rank + 0.5, 0.5)
    axes.set_title("Leaderboard ranking history")
    axes.set_xlabel("Snapshot time")
    axes.set_ylabel("Rank")
    axes.grid(visible=True, alpha=0.25)
    axes.legend(
        title="Participant",
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
    )

    figure.savefig(output, format=output_format, dpi=160)
    figure.clear()
    return output


def _rank_series(
    participant: ParticipantHistory,
    snapshot_times: tuple[datetime, ...],
) -> tuple[float, ...]:
    """Align ranks to all snapshots, leaving visible gaps for missing data."""
    ranks_by_time = {point.snapshot_time: point.rank for point in participant.points}
    return tuple(
        float(ranks_by_time.get(snapshot_time, nan)) for snapshot_time in snapshot_times
    )
