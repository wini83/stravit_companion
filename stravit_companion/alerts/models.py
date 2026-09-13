from dataclasses import dataclass
from enum import StrEnum


class AlertKind(StrEnum):
    POSITION_CHANGE = "position_change"
    GAP_STATUS = "gap_status"


@dataclass(frozen=True)
class AlertEvent:
    kind: AlertKind
    display_name: str | None
    rank: int | None  # jego pozycja
    prev_value: float | int | None
    curr_value: float | int
