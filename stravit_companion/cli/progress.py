"""Terminal progress presentation, kept separate from chart rendering."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn


def format_elapsed(seconds: float) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"


@contextmanager
def animation_progress() -> Iterator[Callable[[str], None]]:
    """Animate on stderr in a terminal; log each stage once otherwise."""
    console = Console(stderr=True)
    if not console.is_terminal or console.is_dumb_terminal:
        yield lambda message: click.echo(message, err=True)
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}", markup=False),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("", total=None)

        def report_stage(message: str) -> None:
            progress.reset(task, description=message, total=None)

        yield report_stage
