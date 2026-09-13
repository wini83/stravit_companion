# runner.py
import sys
import tomllib

import click
from loguru import logger

from stravit_companion.alerts.detector import detect_alert_events
from stravit_companion.alerts.factory import build_alert_from_events
from stravit_companion.alerts.pushover import send
from stravit_companion.client.fetcher import fetch_leaderboard_safe
from stravit_companion.config import settings
from stravit_companion.db.base import Base
from stravit_companion.db.session import Session, engine
from stravit_companion.snapshots.service import (
    load_snapshot,
    save_snapshot_if_changed,
)


def configure_logging(debug: bool):
    logger.remove()
    logger.add(
        sys.stdout,
        level="DEBUG" if debug else "INFO",
        format="{time:YYYY-MM-DD HH:mm:ss!UTC}Z | {level} | {message}",
    )


def get_version() -> str:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


# =========================
# CLI ROOT
# =========================
@click.group(invoke_without_command=True)
@click.option("--refresh", is_flag=True, help="Fetch fresh data from Stravit")
@click.option("--dry-run", is_flag=True, help="Detect alerts but do not send")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option(
    "--offset",
    type=int,
    default=0,
    show_default=True,
    help="Snapshot offset used for comparison",
)
@click.pass_context
def main(ctx, refresh: bool, dry_run: bool, debug: bool, offset: int):
    """Stravit Companion CLI"""
    ctx.ensure_object(dict)
    ctx.obj.update(
        refresh=refresh,
        dry_run=dry_run,
        debug=debug,
        offset=offset,
    )

    if ctx.invoked_subcommand is None:
        ctx.invoke(run)


# =========================
# DEFAULT COMMAND (run)
# =========================
@main.command()
@click.pass_context
def run(ctx):
    """Run alert detection (default behaviour)"""
    refresh = ctx.obj["refresh"]
    dry_run = ctx.obj["dry_run"]
    debug = ctx.obj["debug"]
    offset = ctx.obj["offset"]

    configure_logging(debug)
    logger.debug(f"db_path = {settings.db_path}")
    Base.metadata.create_all(engine)
    logger.info(f"run_started (v{get_version()})")

    rows = []
    saved: bool = False

    if refresh:
        rows = fetch_leaderboard_safe()

        with Session() as session:
            saved = save_snapshot_if_changed(session, rows)
            logger.info("snapshot_saved" if saved else "no_changes_detected")

    with Session() as session:
        if rows:
            if not saved:
                return
            curr = load_snapshot(session, offset=0)
            prev = load_snapshot(session, offset=1)
        else:
            curr = load_snapshot(session, offset=offset)
            prev = load_snapshot(session, offset=offset + 1)

    if not prev or not curr:
        logger.warning("insufficient_snapshots")
        return

    events = detect_alert_events(
        prev_items=prev,
        curr_items=curr,
        my_name=settings.my_name,
    )

    if not events:
        logger.info("no_alerts")
        return

    alert = build_alert_from_events(events)
    if not alert:
        return

    if dry_run:
        logger.info("dry_run_alert", message=alert.message)
        return

    send(alert)


# =========================
# REGISTER EXTRA COMMANDS
# =========================
from stravit_companion.cli.diff import diff  # noqa: E402

main.add_command(diff)


# =========================
# ENTRYPOINT
# =========================
if __name__ == "__main__":
    # Backward compatibility: `stravit` == `stravit run`
    if len(sys.argv) == 1:
        sys.argv.append("run")
    main()
