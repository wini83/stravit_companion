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

    # 1️⃣ zmiana pozycji
    if prev_me.rank != curr_me.rank:
        events.append(
            AlertEvent(
                kind=AlertKind.POSITION_CHANGE,
                name=None,
                rank=None,
                prev_value=prev_me.rank,
                curr_value=curr_me.rank,
            )
        )
        # kluczowa decyzja: po zmianie pozycji NIE liczymy gapów
        return events

    # 2️⃣ sąsiedzi (tylko jeśli pozycja stabilna)
    def neighbors(items: list[LeaderboardItem]) -> dict[int, LeaderboardItem]:
        return {
            i.rank: i
            for i in items
            if abs(i.rank - curr_me.rank) <= window and i.name != my_name
        }

    prev_neighbors = neighbors(prev_items)
    curr_neighbors = neighbors(curr_items)

    for rank, curr in curr_neighbors.items():
        prev = prev_neighbors.get(rank)
        if not prev:
            continue

        if rank < curr_me.rank:
            # przed tobą
            prev_gap = prev.distance - prev_me.distance
            curr_gap = curr.distance - curr_me.distance
            kind = AlertKind.GAP_CHANGE_AHEAD
        else:
            # za tobą
            prev_gap = prev_me.distance - prev.distance
            curr_gap = curr_me.distance - curr.distance
            kind = AlertKind.GAP_CHANGE_BEHIND

        if prev_gap != curr_gap:
            events.append(
                AlertEvent(
                    kind=kind,
                    name=curr.name,
                    rank=curr.rank,
                    prev_value=prev_gap,
                    curr_value=curr_gap,
                )
            )

    return events
