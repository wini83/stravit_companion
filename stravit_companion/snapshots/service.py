from datetime import UTC, datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from stravit_companion.db.models import LeaderboardSnapshot
from stravit_companion.parsing.leaderboard import LeaderboardItem


def index(items: list[LeaderboardItem]) -> dict[str, LeaderboardItem]:
    return {i.name: i for i in items}


def load_snapshot(
    session: Session,
    offset: int = 0,
) -> list[LeaderboardItem] | None:
    ts = session.scalar(
        select(LeaderboardSnapshot.ts)
        .distinct()
        .order_by(desc(LeaderboardSnapshot.ts))
        .offset(offset)
        .limit(1)
    )

    if not ts:
        return None

    rows = session.scalars(
        select(LeaderboardSnapshot).where(LeaderboardSnapshot.ts == ts)
    ).all()

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


def save_snapshot_if_changed(
    session: Session,
    current_items: list[LeaderboardItem],
) -> bool:
    # 1️⃣ Ostatni snapshot jako domena
    previous_items = load_snapshot(session)

    # 2️⃣ Brak snapshotów → zapisujemy zawsze
    if previous_items is None:
        _insert_snapshot(session, current_items)
        return True

    # 3️⃣ Porównanie domenowe (czyste)
    if index(previous_items) == index(current_items):
        return False

    # 4️⃣ Różnice → zapis
    _insert_snapshot(session, current_items)
    return True


def _insert_snapshot(
    session: Session,
    items: list[LeaderboardItem],
) -> None:
    ts_new = datetime.now(UTC)

    records = [
        LeaderboardSnapshot(
            ts=ts_new,
            name=item.name,
            rank=item.rank,
            distance=item.distance,
            elevation=item.elevation,
            longest=item.longest,
            count=item.count,
        )
        for item in items
    ]

    session.add_all(records)
    session.commit()
