from dataclasses import dataclass
from enum import Enum


class AlertKind(Enum):
    POSITION_CHANGE = "position_change"
    GAP_CHANGE_AHEAD = "gap_change_ahead"
    GAP_CHANGE_BEHIND = "gap_change_behind"


@dataclass(frozen=True)
class AlertEvent:
    kind: AlertKind
    name: str | None  # display_name sąsiada
    rank: int | None  # jego pozycja
    prev_value: float | int
    curr_value: float | int
