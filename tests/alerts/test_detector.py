import pytest

from stravit_companion.alerts.detector import detect_alert_events
from stravit_companion.alerts.models import AlertKind
from stravit_companion.parsing.leaderboard import LeaderboardItem


def item(
    name: str,
    rank: int,
    distance: float,
) -> LeaderboardItem:
    return LeaderboardItem(
        name=name,
        rank=rank,
        distance=distance,
        elevation=0,
        longest=0,
        count=0,
    )


def test_position_change_creates_event():
    prev = [
        item("Alice", 1, 20.0),
        item("Mario", 2, 18.0),
    ]
    curr = [
        item("Mario", 1, 21.0),
        item("Alice", 2, 20.5),
    ]

    events = detect_alert_events(prev, curr, my_name="Mario")

    assert len(events) == 1
    event = events[0]

    assert event.kind is AlertKind.POSITION_CHANGE
    assert event.prev_value == 2
    assert event.curr_value == 1


def test_gap_change_ahead_only_when_position_stable():
    prev = [
        item("Alice", 1, 20.0),
        item("Mario", 2, 18.0),
    ]
    curr = [
        item("Alice", 1, 20.2),
        item("Mario", 2, 18.5),
    ]

    events = detect_alert_events(prev, curr, my_name="Mario")

    assert len(events) == 1
    event = events[0]

    assert event.kind is AlertKind.GAP_CHANGE_AHEAD
    assert event.name == "Alice"
    assert event.prev_value == pytest.approx(2.0)
    assert event.curr_value == pytest.approx(1.7)
