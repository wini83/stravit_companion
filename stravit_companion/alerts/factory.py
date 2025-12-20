from stravit_companion.alerts.models import AlertEvent
from stravit_companion.alerts.notification import Alert
from stravit_companion.alerts.renderer import render_alert
from stravit_companion.config import settings


def build_alert_from_events(
    events: list[AlertEvent],
    *,
    title: str = settings.pushover_title,
    priority: int = settings.pushover_priority,
) -> Alert | None:
    if not events:
        return None

    lines = [render_alert(e) for e in events]

    return Alert.from_lines(
        title=title,
        lines=lines,
        priority=priority,
    )
