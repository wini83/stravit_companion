# alerts/pushover.py
import requests
from loguru import logger

from stravit_companion.config import settings

from .models import Alert

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"


def send(alert: Alert) -> None:
    payload = {
        "token": settings.pushover_token,
        "user": settings.pushover_user,
        "title": alert.title,
        "message": alert.message,
        "priority": alert.priority,
    }

    resp = requests.post(PUSHOVER_URL, data=payload, timeout=10)

    if not resp.ok:
        logger.error(
            "pushover_failed",
            status=resp.status_code,
            body=resp.text,
        )
        resp.raise_for_status()

    logger.info("pushover_sent", title=alert.title)
