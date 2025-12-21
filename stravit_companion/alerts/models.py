from dataclasses import dataclass
from enum import Enum


class AlertKind(str, Enum):
    POSITION_CHANGE = "position_change"
    GAP_STATUS = "gap_status"


@dataclass(frozen=True)
class AlertEvent:
    kind: AlertKind
    name: str | None  # display_name sąsiada
    rank: int | None  # jego pozycja
    prev_value: float | int | None
    curr_value: float | int
