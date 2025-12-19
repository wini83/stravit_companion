from stravit_companion.alerts.models import Alert
from stravit_companion.config import settings
from stravit_companion.parsing.leaderboard import LeaderboardItem


def get_neighbors(
    items: list[LeaderboardItem],
    my_name: str,
    window: int = 2,
) -> tuple[
    LeaderboardItem | None,
    list[LeaderboardItem],
    list[LeaderboardItem],
]:
    """
    Zwraca:
    - me
    - listę zawodników przed (max `window`)
    - listę zawodników za (max `window`)
    """
    idx = {i.name: i for i in items}
    me = idx.get(my_name)
    if not me:
        return None, [], []

    ahead = sorted(
        (i for i in items if me.rank - window <= i.rank < me.rank),
        key=lambda i: i.rank,
    )

    behind = sorted(
        (i for i in items if me.rank < i.rank <= me.rank + window),
        key=lambda i: i.rank,
    )

    return me, ahead, behind


def detect_alerts(
    prev_items: list[LeaderboardItem],
    curr_items: list[LeaderboardItem],
    my_name: str,
    window: int = 2,
) -> list[str]:
    alerts: list[str] = []

    prev_me, prev_ahead, prev_behind = get_neighbors(prev_items, my_name, window)
    curr_me, curr_ahead, curr_behind = get_neighbors(curr_items, my_name, window)

    if not prev_me or not curr_me:
        return alerts

    # 1️⃣ Zmiana pozycji
    if prev_me.rank != curr_me.rank:
        delta = prev_me.rank - curr_me.rank
        alerts.append(
            f"🏁 Pozycja: {prev_me.rank} → {curr_me.rank} "
            f"({'+' if delta > 0 else ''}{delta})"
        )

    # 2️⃣ Przed tobą (N osób)
    for p, c in zip(prev_ahead, curr_ahead):
        prev_gap = p.distance - prev_me.distance
        curr_gap = c.distance - curr_me.distance
        diff = curr_gap - prev_gap

        if diff != 0:
            alerts.append(
                f"⬆️ {c.display_name} (P{c.rank}): "
                f"{prev_gap:.2f} → {curr_gap:.2f} km "
                f"({'+' if diff > 0 else ''}{diff:.2f})"
            )

    # 3️⃣ Za tobą (N osób)
    for p, c in zip(prev_behind, curr_behind):
        prev_gap = prev_me.distance - p.distance
        curr_gap = curr_me.distance - c.distance
        diff = curr_gap - prev_gap

        if diff != 0:
            alerts.append(
                f"⬇️ {c.display_name} (P{c.rank}): "
                f"{prev_gap:.2f} → {curr_gap:.2f} km "
                f"({'+' if diff > 0 else ''}{diff:.2f})"
            )

    return alerts


def build_alert_from_detected(
    messages: list[str],
    title: str = settings.pushover_title,
    priority: int = settings.pushover_priority,
) -> Alert | None:
    if not messages:
        return None

    return Alert.from_strings(
        title=title,
        items=messages,
        priority=priority,
    )
