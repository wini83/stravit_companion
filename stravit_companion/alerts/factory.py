from stravit_companion.alerts.models import AlertEvent
from stravit_companion.alerts.notification import Alert
from stravit_companion.alerts.renderer import render_alert
from stravit_companion.config import settings


def build_alert_from_events(events: list[AlertEvent]) -> Alert | None:
    if not events:
        return None

    message = render_alert(events)

    return Alert(
        title=settings.pushover_title,
        message=message,
        priority=settings.pushover_priority,
    )
