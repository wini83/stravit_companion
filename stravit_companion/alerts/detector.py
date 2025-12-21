from stravit_companion.alerts.models import AlertEvent, AlertKind
from stravit_companion.parsing.leaderboard import LeaderboardItem


def _index_by_name(
    items: list[LeaderboardItem],
) -> dict[str, LeaderboardItem]:
    return {i.name: i for i in items}


def detect_alert_events(
    prev_items: list[LeaderboardItem],
    curr_items: list[LeaderboardItem],
    my_name: str,
    window: int = 2,
) -> list[AlertEvent]:
    events: list[AlertEvent] = []

    prev_idx = _index_by_name(prev_items)
    curr_idx = _index_by_name(curr_items)

    prev_me = prev_idx.get(my_name)
    curr_me = curr_idx.get(my_name)

    if not prev_me or not curr_me:
        return events

    # ==========================================================
    # 1️⃣ CZYSTA INFORMACJA O ZMIANIE POZYCJI (FAKT)
    # ==========================================================
    if prev_me.rank != curr_me.rank:
        events.append(
            AlertEvent(
                kind=AlertKind.POSITION_CHANGE,
                name=None,
                rank=curr_me.rank,
                prev_value=prev_me.rank,
                curr_value=curr_me.rank,
            )
        )

    # ==========================================================
    # 2️⃣ OKNO RYWALI Z AKTUALNEGO SNAPSHOTA
    #    gapy liczone user-centric + delta vs prev snapshot
    # ==========================================================
    curr_window = [
        i
        for i in curr_items
        if abs(i.rank - curr_me.rank) <= window and i.name != my_name
    ]

    for rival in curr_window:
        prev_rival = prev_idx.get(rival.name)

        # gap = rival - me (zawsze user-centric)
        curr_gap = rival.distance - curr_me.distance

        # rywal nowy względem poprzedniego snapshotu
        prev_gap = prev_rival.distance - prev_me.distance if prev_rival else None

        # brak zmiany? nie spamujemy
        if prev_gap is not None and prev_gap == curr_gap:
            continue

        events.append(
            AlertEvent(
                kind=AlertKind.GAP_STATUS,
                name=rival.name,
                rank=rival.rank,
                prev_value=prev_gap,
                curr_value=curr_gap,
            )
        )

    return events
