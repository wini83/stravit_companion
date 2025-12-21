# runner.py
import sys

import click
from loguru import logger

from stravit_companion.alerts.detector import detect_alert_events
from stravit_companion.alerts.factory import build_alert_from_events
from stravit_companion.alerts.pushover import send
from stravit_companion.client.session import StravitSession
from stravit_companion.config import settings
from stravit_companion.db.base import Base, Session, engine
from stravit_companion.parsing.leaderboard import parse_leaderboard
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


@click.command()
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
def main(refresh: bool, dry_run: bool, debug: bool, offset: int):
    configure_logging(debug)
    logger.debug(f"db_path = {settings.db_path}")
    Base.metadata.create_all(engine)
    logger.info("run_started")

    rows = []
    saved: bool = False

    if refresh:
        logger.info("Fetching new data from Stravit")
        client = StravitSession()
        client.login()
        csv_text = client.fetch_csv()
        rows = parse_leaderboard(csv_text)

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

    # 🔁 ZMIANA 1: domena → eventy
    events = detect_alert_events(
        prev_items=prev,
        curr_items=curr,
        my_name=settings.my_name,
    )

    if not events:
        logger.info("no_alerts")
        return

    # 🔁 ZMIANA 2: eventy → Alert (pushover DTO)
    alert = build_alert_from_events(events)
    if not alert:
        return

    if dry_run:
        logger.info("dry_run_alert", message=alert.message)
        return

    send(alert)


if __name__ == "__main__":
    main()
