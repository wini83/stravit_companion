from pathlib import Path

import click

from stravit_companion.charts import render_distance_history, render_ranking_history
from stravit_companion.db.session import Session
from stravit_companion.history import get_leaderboard_history


@click.group()
def charts() -> None:
    """Generate static charts from stored leaderboard snapshots."""


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
