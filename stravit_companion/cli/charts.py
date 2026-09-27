from pathlib import Path

import click

from stravit_companion.charts import (
    render_bar_race,
    render_distance_history,
    render_ranking_history,
)
from stravit_companion.db.session import Session
from stravit_companion.history import get_leaderboard_history


@click.group()
def charts() -> None:
    """Generate charts and animations from stored leaderboard snapshots."""


@charts.command("ranking-history")
@click.option(
    "--top",
    type=click.IntRange(min=1),
    default=10,
    show_default=True,
    help="Include participants in the current top N.",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path, dir_okay=False),
    default=Path("ranking.png"),
    show_default=True,
    help="Destination PNG or SVG file.",
)
def ranking_history(top: int, output: Path) -> None:
    """Plot participant rank changes across stored snapshots."""
    with Session() as session:
        history = get_leaderboard_history(session, top=top)

    try:
        written_path = render_ranking_history(history, output)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Chart written to {written_path}")


@charts.command("distance-history")
@click.option(
    "--top",
    type=click.IntRange(min=1),
    default=10,
    show_default=True,
    help="Include participants in the current top N.",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path, dir_okay=False),
    default=Path("distance.png"),
    show_default=True,
    help="Destination PNG or SVG file.",
)
def distance_history(top: int, output: Path) -> None:
    """Plot cumulative participant distance across stored snapshots."""
    with Session() as session:
        history = get_leaderboard_history(session, top=top)

    try:
        written_path = render_distance_history(history, output)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Chart written to {written_path}")


@charts.command("bar-race")
@click.option(
    "--top",
    type=click.IntRange(min=1),
    default=10,
    show_default=True,
    help="Show the leading N participants in each frame.",
)
@click.option(
    "--fps",
    type=click.IntRange(min=1, max=60),
    default=20,
    show_default=True,
    help="Video frames per second.",
)
@click.option(
    "--duration",
    type=click.FloatRange(min=0, min_open=True),
    default=20.0,
    show_default=True,
    help="Total video duration in seconds.",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path, dir_okay=False),
    default=Path("leaderboard.mp4"),
    show_default=True,
    help="Destination MP4 file.",
)
def bar_race(top: int, fps: int, duration: float, output: Path) -> None:
    """Animate the cumulative-distance leaderboard over time."""
    with Session() as session:
        history = get_leaderboard_history(session)

    try:
        written_path = render_bar_race(
            history,
            output,
            top=top,
            fps=fps,
            duration=duration,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Animation written to {written_path}")
