from collections.abc import Iterable
from datetime import UTC, datetime

import click
from tabulate import tabulate

from stravit_companion.db.models import LeaderboardSnapshot
from stravit_companion.db.session import Session
from stravit_companion.parsing.leaderboard import LeaderboardItem


def _to_items(rows: Iterable[LeaderboardSnapshot]) -> list[LeaderboardItem]:
    return [
        LeaderboardItem(
            name=r.name,
            rank=r.rank,
            distance=r.distance,
            elevation=r.elevation,
            longest=r.longest,
            count=r.count,
        )
        for r in rows
    ]


def resolve_snapshot(session, ref: str) -> tuple[datetime, list[LeaderboardItem]]:
    rows = (
        session.query(LeaderboardSnapshot).order_by(LeaderboardSnapshot.ts.desc()).all()
    )

    if not rows:
        raise click.ClickException("No snapshots in database")

    if ref.startswith("latest"):
        offset = int(ref.split("-")[1]) if "-" in ref else 0
        unique_ts = sorted({r.ts for r in rows}, reverse=True)

        try:
            ts = unique_ts[offset]
        except IndexError:
            raise click.ClickException(f"Snapshot '{ref}' not found") from None

        snap = [r for r in rows if r.ts == ts]
        return ts, _to_items(snap)

    try:
        ts = datetime.fromisoformat(ref)
    except ValueError:
        raise click.ClickException(f"Invalid snapshot reference: {ref}") from None

    snap = [r for r in rows if r.ts == ts]
    if not snap:
        raise click.ClickException(f"No snapshot at {ts}") from None

    return ts, _to_items(snap)


@click.command()
@click.argument("from_ref")
@click.argument("to_ref")
def diff(from_ref: str, to_ref: str) -> None:
    """Compare two snapshots"""
    with Session() as session:
        prev_ts, prev_items = resolve_snapshot(session, from_ref)
        curr_ts, curr_items = resolve_snapshot(session, to_ref)

    prev_by_name = {i.name: i for i in prev_items}
    curr_by_name = {i.name: i for i in curr_items}

    rows: list[list[str | int | float]] = []

    for name in sorted(prev_by_name.keys() & curr_by_name.keys()):
        p = prev_by_name[name]
        c = curr_by_name[name]

        if (
            p.rank == c.rank
            and p.distance == c.distance
            and p.elevation == c.elevation
            and p.count == c.count
        ):
            continue

        rows.append(
            [
                c.display_name,
                p.rank,
                c.rank,
                c.rank - p.rank,
                round(c.distance - p.distance, 2),
            ]
        )

    if not rows:
        click.echo("No changes detected")
        return

    click.echo(
        click.style(
            f"Snapshot diff: "
            f"{prev_ts.astimezone(UTC):%Y-%m-%d %H:%M UTC}"
            f"  →  "
            f"{curr_ts.astimezone(UTC):%Y-%m-%d %H:%M UTC}",
            bold=True,
        )
    )

    click.echo(
        tabulate(
            rows,
            headers=["Name", "Rank prev", "Rank curr", "Δ rank", "Δ distance"],
            tablefmt="rounded_grid",
        )
    )
