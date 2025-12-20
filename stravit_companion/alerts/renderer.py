from stravit_companion.alerts.models import AlertEvent, AlertKind
from stravit_companion.parsing.leaderboard import LeaderboardItem


def _display_name(raw_name: str | None) -> str:
    if not raw_name:
        return ""

    dummy = LeaderboardItem(
        name=raw_name,
        rank=0,
        distance=0.0,
        elevation=0,
        longest=0.0,
        count=0,
    )
    return dummy.display_name


def render_alert(event: AlertEvent) -> str:
    match event.kind:
        case AlertKind.POSITION_CHANGE:
            delta = event.prev_value - event.curr_value
            return (
                f"🏁 Pozycja: {event.prev_value} → {event.curr_value} "
                f"({'+' if delta > 0 else ''}{delta})"
            )

        case AlertKind.GAP_CHANGE_AHEAD:
            diff = event.curr_value - event.prev_value
            name = _display_name(event.name)
            return (
                f"⬆️ {name} (P{event.rank}): "
                f"{event.prev_value:.2f} → {event.curr_value:.2f} km "
                f"({'+' if diff > 0 else ''}{diff:.2f})"
            )

        case AlertKind.GAP_CHANGE_BEHIND:
            diff = event.curr_value - event.prev_value
            name = _display_name(event.name)
            return (
                f"⬇️ {name} (P{event.rank}): "
                f"{event.prev_value:.2f} → {event.curr_value:.2f} km "
                f"({'+' if diff > 0 else ''}{diff:.2f})"
            )

        case _:
            raise ValueError("Unknown AlertKind")
