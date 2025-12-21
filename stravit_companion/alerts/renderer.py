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


def _render_gap_status(event: AlertEvent) -> str:
    name = _display_name(event.name)
    rank = event.rank
    curr_gap = float(event.curr_value)

    curr_str = f"{abs(curr_gap):.2f}"

    # nowy rywal - brak poprzedniego gapu
    if event.prev_value is None:
        return f"P{rank} {name} → {curr_str} km (new)"

    prev_gap = float(event.prev_value)
    prev_str = f"{abs(prev_gap):.2f}"

    diff = curr_gap - prev_gap
    diff_str = f"{diff:+.2f}"

    return f"P{rank} {name} {prev_str} → {curr_str} km ({diff_str})"


def _render_position_change(event: AlertEvent) -> str:
    if event.prev_value is None:
        raise ValueError("POSITION_CHANGE requires prev_value")

    prev_rank = int(event.prev_value)
    curr_rank = int(event.curr_value)

    delta = prev_rank - curr_rank
    arrow = "⬆️" if delta > 0 else "⬇️"

    return f"{arrow} Pozycja: {prev_rank} → {curr_rank} ({delta:+d})"


def render_event(event: AlertEvent) -> str:
    match event.kind:
        case AlertKind.POSITION_CHANGE:
            return _render_position_change(event)
        case AlertKind.GAP_STATUS:
            return _render_gap_status(event)
        case _:
            raise ValueError(f"Unsupported alert kind: {event.kind}")


def render_alert(events: list[AlertEvent]) -> str:
    lines = [render_event(e) for e in events]
    return "\n".join(lines)
