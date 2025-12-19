from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Alert:
    title: str
    message: str
    priority: int = 0  # pushover: -2..2

    @classmethod
    def from_strings(cls, title: str, items: List[str], priority: int = 0) -> "Alert":
        message = "\n".join(items)
        return cls(title=title, message=message, priority=priority)
