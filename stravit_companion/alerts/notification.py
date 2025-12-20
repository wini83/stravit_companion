from dataclasses import dataclass


@dataclass(frozen=True)
class Alert:
    title: str
    message: str
    priority: int

    @classmethod
    def from_lines(
        cls,
        *,
        title: str,
        lines: list[str],
        priority: int,
    ) -> "Alert":
        return cls(
            title=title,
            message="\n".join(lines),
            priority=priority,
        )
